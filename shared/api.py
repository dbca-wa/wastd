# -*- coding: utf-8 -*-
"""Shared API utilities."""
import logging
from collections import OrderedDict

from django.db import transaction

from rest_framework import pagination, status, viewsets  # , serializers, routers
from rest_framework.response import Response as RestResponse
from rest_framework_csv.renderers import CSVRenderer
from rest_framework.settings import api_settings

from shared.models import QualityControlMixin

# from taxonomy.models import Taxon

logger = logging.getLogger(__name__)


class CustomCSVRenderer(CSVRenderer):
    """Custom CSV Renderer."""

    def render(self, data, media_type=None, renderer_context={}, writer_opts=None):
        """Discard pagination cruft before rendering."""
        if "results" in data:
            content = data["results"]
        elif "features" in data:
            content = data["features"]
        else:
            content = data
        return super().render(
            content,
            media_type=media_type,
            renderer_context=renderer_context,
            writer_opts=writer_opts)


class CustomLimitOffsetPagination(pagination.LimitOffsetPagination):
    """Opt-out LimitOffset pagination.

    Include GET parameter ``no_page`` to deactivate pagination.
    """

    def paginate_queryset(self, queryset, request, view=None):
        """Turn off pagination based on query param ``no_page``."""
        if 'no_page' in request.query_params:
            return None
        return super().paginate_queryset(queryset, request, view)


class MyGeoJsonPagination(CustomLimitOffsetPagination):
    """
    Paginate GeoJSON with LimitOffset.

    Attempt to un-break HTML filter controls in browsable API.

    https://github.com/tomchristie/django-rest-framework/issues/4812
    """

    def get_paginated_response(self, data):
        """Return a GeoJSON FeatureCollection with pagination links."""
        # if "format" in self.request.query_params and self.request.query_params["format"] == "json":
        if "features" in data:
            results = data["features"]
        elif "results" in data:
            results = data["results"]
        else:
            results = data
        return RestResponse(
            OrderedDict([
                ('type', 'FeatureCollection'),
                ('count', self.count),
                ('next', self.get_next_link()),
                ('previous', self.get_previous_link()),
                ('features', results),
            ])
        )

        # return super().get_paginated_response(self, data)


class FastLimitOffsetPagination(pagination.LimitOffsetPagination):
    """GeoJSON pagination with page size of 10."""

    page_size = 10


class BatchUpsertViewSet(viewsets.ModelViewSet):
    """A BatchUpsert ViewSet.

    Override split_data for nested serializers, e.g. TaxonAreaEncounters.taxon.
    """

    pagination_class = MyGeoJsonPagination
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (CustomCSVRenderer, )
    model = None
    uid_fields = ()

    def split_data(self, data):
        """Split data into unique fields and remaining data.

        Unique fields are used to get_or_create an object,
        remaining data is used to update that object.

        Unique fields and CSRF middleware token are removed from data.
        """
        unique_fields = {x: data[x] for x in self.uid_fields}
        [data.pop(x) for x in self.uid_fields if x in data]
        if 'csrfmiddlewaretoken' in data:
            data.pop('csrfmiddlewaretoken')
        # Custom:
        # unique_fields["taxon"] = Taxon.objects.get(name_id=data["taxon"])

        return (unique_fields, data)

    def fetch_existing_records(self, new_records, model):
        """Fetch pk, (status if QC mixin), and **uid_fields values from a model.

        The UID fields are hard-coded here, as it seems impossible to 
        programmatically filter (with an ``__in``) clause using ``uid_fields``.

        Overwrite this method in your queryset if your uid_fields are not 
        "source" and "source_id".

        A better way is show in Django admin filters:
        https://github.com/django/django/blob/master/django/contrib/admin/filters.py
        """
        qs = model.objects.filter(
            source__in=list(set([x["source"] for x in new_records])), 
            source_id__in=list(set([x["source_id"] for x in new_records]))
        )
        if issubclass(model, QualityControlMixin):
            return qs.values("pk", "source", "source_id", "status")
        else:
            return qs.values("pk", "source", "source_id")

    def create_one(self, data):
        """POST: Create or update exactly one model instance.

        The ViewSet must have a method ``split_data`` returning a dict
        of the unique, mandatory fields to get_or_create,
        and a dict of the other optional values to update.

        Return RestResponse(content, status)
        """
        unique_data, update_data = self.split_data(data)

        # Early exit 1: None value in unique data
        if None in unique_data.values():
            msg = '[API][create_one] Skipping invalid data: {0} {1}'.format(
                str(update_data), str(unique_data))
            logger.warning(msg)
            content = {"msg": msg}
            return RestResponse(content, status=status.HTTP_406_NOT_ACCEPTABLE)

        logger.debug('[API][create_one] Received '
                     '{0} with unique fields {1}'.format(
                         self.model._meta.verbose_name, str(unique_data)))


        obj, created = self.model.objects.get_or_create(defaults=update_data, **unique_data)
        verb = "Created" if created else "Updated"

        # Early exit 2: retain locally changed data (status not NEW)
        if (not created and obj.status != QualityControlMixin.STATUS_NEW):
            msg = ('[API][create_one] Not overwriting locally changed data '
                   'with QA status: {0}'.format(obj.get_status_display()))
            logger.info(msg)
            content = {"msg": msg}
            return RestResponse(content, status=status.HTTP_200_OK)

        else:
            # Continue on happy trail: update if new or existing but unchanged
            self.model.objects.filter(**unique_data).update(**update_data)

        obj.refresh_from_db()
        obj.save()  # to update cached fields

        verb = "Created" if created else "Updated"
        st = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        msg = '[API][create_one] {0} {1}'.format(verb, obj.__str__())
        content = {"id": obj.id, "msg": msg}
        logger.info(msg)
        return RestResponse(content, status=st)

    def create(self, request):
        """POST: Create or update one or many model instances.

        request.data must be a dict or a list of dicts.

        Return RestResponse(result, status)

        result:

        * Warning message if invalid data (status 406 not acceptable)
        * Dict of object_id and message if one record
        * List of one-record dicts if several records
        """

        # Create one ---------------------------------------------------------#
        if self.uid_fields[0] in request.data:
            logger.info('[API][create] found one record, creating/updating...')
            res = self.create_one(request.data).__dict__         
            return RestResponse(res, status=st)

        # Create many --------------------------------------------------------#
        elif (type(request.data) == list and 
              self.uid_fields[0] in request.data[0]):
            logger.info('[API][create] found batch of {0} records,'
                        ' creating/updating...'.format(len(request.data)))

            # The slow way:
            # res = [getattr(self.create_one(data), "__dict__", None) for data in request.data]

            # A new hope: bulk update/create 
            # https://github.com/dbca-wa/wastd/issues/205

            # Existing vs new
            new_records = request.data
            logger.info("[API][create] Fetching existing records...")
            existing_records = self.fetch_existing_records(new_records, self.model)
            logger.info("[API][create] Done fetching existing records.")

            # Having QA status or not decides what to update or retain
            logger.info("[API][create] Sorting records into retain/update/create...")
            if issubclass(self.model, QualityControlMixin):
                # Bucket "retain": existing_objects with status > STATUS_NEW
                to_retain = [t for t in existing_records if t["status"] > QualityControlMixin.STATUS_NEW]
                # TODO Log PKs (debug) or total number (info) of skipped records
                logger.info("[API][create] Skipping {0} locally changed records".format(len(to_retain)))
                logger.debug("[API][create] Skipping locally changed records: {0}".format(str(to_retain)))

                # With QA: update if existing but unchanged (QA status "NEW")                
                to_update = [t for t in existing_records if t["status"] == QualityControlMixin.STATUS_NEW]
            else:
                # Without QA: update if existing
                to_update = existing_records
                
            # Bucket "bulk_update": List of new_records where uid_fields match existing_objects
            records_to_update = [d for d in new_records if ([d[x] for x in self.uid_fields]) in to_update]

            # Bucket "bulk_create": List of new records without match in existing records
            records_to_create = [d for d in new_records if ([d[x] for x in self.uid_fields]) not in to_update]
            logger.info("[API][create] Done sorting records.")

            updated = []
            created = []

            # Hammertime
            with transaction.atomic():
                if records_to_update:
                    logger.info("[API][create] Updating records...")
                    # updated = self.model.objects.bulk_update(
                    #     [self.model(**x) for x in records_to_update], records_to_update[0].keys())
                    # updated = [self.create_one(x) for x in records_to_update]
                    for data in records_to_update:
                        unique_data, update_data = self.split_data(data)
                        self.model.objects.filter(**unique_data).update(**update_data)

                        # to update cached fields
                        obj.refresh_from_db()
                        obj.save()  

                if records_to_create:
                    logger.info("[API][create] Creating records...")
                    # created = self.model.objects.bulk_create([self.model(**x) for x in records_to_create])
                    # created = [self.create_one(x) for x in records_to_create]
                    for data in records_to_create:
                        unique_data, update_data = self.split_data(data)
                        obj, created = self.model.objects.get_or_create(defaults=update_data, **unique_data)

                        # to update cached fields
                        obj.refresh_from_db()
                        obj.save()  

            logger.info("[API][create] Finished.")
            msg = "Retained {0}, updated {1}, created {2} records.".format(
                len(to_retain), len(records_to_update), len(records_to_create)
            )
            logger.info(msg)

            return RestResponse(msg, status=status.HTTP_200_OK)

        # Create none --------------------------------------------------------#
        else:
            msg = ("[API][BatchUpsertViewSet] unknown data format:"
                   "{0}".format(str(request.data)))
            logger.warning(msg)
            return RestResponse({"msg": msg}, status=status.HTTP_406_NOT_ACCEPTABLE)


class FastBatchUpsertViewSet(BatchUpsertViewSet):
    """Viewset with LO pagination and page size 10."""

    pagination_class = FastLimitOffsetPagination
