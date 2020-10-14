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
from wastd.observations.models import Observation, Encounter

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
    uid_fields = ("source", "source_id", )

    def resolve_fks(self, data):
        """Resolve FKs from PK to object.

        Override in viewset inheriting from BatchUpsertViewSet.
        """
        return data

    def split_data(self, data):
        """Split data into unique fields and remaining data.

        Unique fields are used to get_or_create an object,
        remaining data is used to update that object.

        Unique fields and CSRF middleware token are removed from data.
        """
        logger.info(data)
        data = self.resolve_fks(data)
        logger.info(data)
        unique_fields = {x: data[x] for x in self.uid_fields}
        [data.pop(x) for x in self.uid_fields if x in data]
        if 'csrfmiddlewaretoken' in data:
            data.pop('csrfmiddlewaretoken')
        # Custom:
        # unique_fields["taxon"] = Taxon.objects.get(name_id=data["taxon"])

        return (unique_fields, data)

    def fetch_existing_records(self, new_records, model, source_field="source", source_id_field="source_id"):
        """Fetch pk, (status if QC mixin), and **uid_fields values from a model.

        The UID fields are hard-coded here, as it seems impossible to
        programmatically filter (with an ``__in``) clause using ``uid_fields``.

        Overwrite this method in your queryset if your uid_fields are not
        "source" and "source_id".

        A better way is show in Django admin filters:
        https://github.com/django/django/blob/master/django/contrib/admin/filters.py
        """
        qs = model.objects.filter(
            source__in=list(set([x[source_field] for x in new_records])),
            source_id__in=list(set([x[source_id_field] for x in new_records]))
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
            # TODO wastd.observations.Observation models
            # have Encounter(source, source_id) but update own fields
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
        # import ipdb; ipdb.set_trace()

        # Create one ---------------------------------------------------------#
        if self.uid_fields[0] in request.data:
            logger.info('[API][create] found one record, creating/updating...')
            return self.create_one(request.data)

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
            m = Encounter if issubclass(self.model, Observation) else self.model
            existing_records = self.fetch_existing_records(new_records, m)
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
                to_retain = []

            # Only UID fields of new records (request.data)
            # new_records_uid_only = [{rec[uid_field] for uid_field in self.uid_fields} for rec in new_records]

            existing_records_uid_only = [{rec[uid_field] for uid_field in self.uid_fields} for rec in existing_records]

            # Bucket "bulk_update": List of new_records where uid_fields match existing_objects
            records_to_update = [new_record for new_record in new_records
                                 if {new_record[uid_field] for uid_field in self.uid_fields}
                                 in existing_records_uid_only]

            # Bucket "bulk_create": List of new records without match in existing records
            records_to_create = [new_record for new_record in new_records
                                 if {new_record[uid_field] for uid_field in self.uid_fields}
                                 not in existing_records_uid_only]
            logger.info("[API][create] Done sorting records: {0} to retain, {1} to update, {2} to create.".format(
                len(to_retain), len(records_to_update), len(records_to_create)
            ))

            # Hammertime
            with transaction.atomic():
                if records_to_update:
                    logger.info("[API][create] Updating records...")
                    # logger.debug("[API][create] Updating records: {0}".format(str(records_to_update)))
                    # updated = self.model.objects.bulk_update(
                    #     [self.model(**x) for x in records_to_update], records_to_update[0].keys())
                    # updated = [self.create_one(x) for x in records_to_update]
                    for data in records_to_update:
                        unique_data, update_data = self.split_data(data)
                        self.model.objects.filter(**unique_data).update(**update_data)

                        # to update cached fields
                        # self.model.objects.filter(**unique_data).refresh_from_db()
                        # self.model.objects.filter(**unique_data).save()

                if records_to_create:
                    logger.info("[API][create] Creating records...")
                    # logger.debug("[API][create] Creating records: {0}".format(str(records_to_create)))
                    # Nice but doesn't work with multi table inherited models (TAE, CAE):
                    # created = self.model.objects.bulk_create([self.model(**self.resolve_fks(x)) for x in records_to_create])

                    # Slow:
                    # created = [self.create_one(x) for x in records_to_create]

                    # Mildly less slow but still not batch:
                    for data in records_to_create:
                        unique_data, update_data = self.split_data(data)
                        obj, created = self.model.objects.get_or_create(defaults=update_data, **unique_data)
                        # obj = self.model.objects.create(**data)
                        logger.info("[API][create] Creating record with unique fields "
                                    "{0}, update fields {1}, created: {2}".format(
                                        str(unique_data), str(update_data), created
                                    )
                                    )

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


class NameIDBatchUpsertViewSet(BatchUpsertViewSet):
    """A BatchUpsert ViewSet for uid fields "name_id"."""

    def fetch_existing_records(self, new_records, model):
        """Fetch pk, and **uid_fields values from a model."""

        qs = model.objects.filter(
            name_id__in=list(set([x["name_id"] for x in new_records]))
        )
        if issubclass(model, QualityControlMixin):
            return qs.values("pk", "name_id", "status")
        else:
            return qs.values("pk", "name_id", )


class OgcFidBatchUpsertViewSet(BatchUpsertViewSet):
    """A BatchUpsert ViewSet for uid fields "ogc_fid"."""

    def fetch_existing_records(self, new_records, model):
        """Fetch pk, (status if QC mixin), and **uid_fields values from a model."""

        qs = model.objects.filter(
            ogc_fid__in=list(set([x["ogc_fid"] for x in new_records]))
        )

        if issubclass(model, QualityControlMixin):
            return qs.values("pk", "ogc_fid", "status")
        else:
            return qs.values("pk", "ogc_fid", )


class ObservationBatchUpsertViewSet(BatchUpsertViewSet):
    """A viewset to upsert Observations linked to an Encounter."""

    def create_one(self, data):
        """POST: Create or update exactly one model instance.

        The ViewSet must have a method ``split_data`` returning a dict
        of the unique, mandatory fields to get_or_create,
        and a dict of the other optional values to update.

        Return RestResponse(content, status)
        """
        unique_data, update_data = self.split_data(data)
        update_data = {x:update_data[x] for x in update_data}

        # Early exit 1: None value in unique data
        if None in unique_data.values():
            msg = '[API][create_one] Skipping invalid data: {0} {1}'.format(
                str(update_data), str(unique_data))
            logger.warning(msg)
            content = {"msg": msg}
            return RestResponse(content, status=status.HTTP_406_NOT_ACCEPTABLE)

        logger.debug('[API][create_one] Received '
                     '{0} with unique fields {1} and update_data {2}'.format(
                         self.model._meta.verbose_name, str(unique_data), str(update_data)))

        # resolve Encounter
        if 'encounter_source' in update_data and 'encounter_source_id' in update_data:
            enc = Encounter.objects.filter(
                source__exact=update_data["encounter_source"],
                source_id__exact=update_data["encounter_source_id"]
                ).first()
            if enc:
                update_data["encounter_id"] = enc.pk
            update_data.pop("encounter_source")
            update_data.pop("encounter_source_id")


        logger.debug('[API][create_one] Creating '
                     '{0} with unique fields {1} and update_data {2}'.format(
                         self.model._meta.verbose_name, str(unique_data), str(update_data)))
        obj, created = self.model.objects.get_or_create(defaults=update_data, **unique_data)
        verb = "Created" if created else "Updated"

        # Early exit 2: retain locally changed data (status not NEW)
        if (not created and obj.encounter.status != QualityControlMixin.STATUS_NEW):
            msg = ('[API][create_one] Not overwriting locally changed data '
                   'with QA status: {0}'.format(obj.encounter.get_status_display()))
            logger.info(msg)
            content = {"msg": msg}
            return RestResponse(content, status=status.HTTP_200_OK)

        else:
            # Continue on happy trail: update if new or existing but unchanged
            # TODO wastd.observations.Observation models
            # have Encounter(source, source_id) but update own fields
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
        # import ipdb; ipdb.set_trace()

        # Create one ---------------------------------------------------------#
        if self.uid_fields[0] in request.data:
            logger.info('[API][create] found one record, creating/updating...')
            return self.create_one(request.data)


        # Create many --------------------------------------------------------#
        elif (
            type(request.data) == list and self.uid_fields[0] in request.data[0]
        ):
            logger.info('[API][create] found batch of {0} records,'
                        ' creating/updating...'.format(len(request.data)))

            new_records = request.data

            # ----------------------------------------------------------------#
            # Fetch existing Encounter valuess based on encounter_source_id
            logger.info("[API][create] Fetching existing Encounter records...")
            existing_records = self.fetch_existing_records(
                new_records,
                Observation,
                source_field="source",
                source_id_field="source_id"
            )
            # existing_records_source_ids = [
            #     r["source_id"] for r in existing_records
            # ]
            # Only UID fields of new records (request.data)
            # new_records_uid_only = [
            #     {rec[uid_field] for uid_field in self.uid_fields}
            #     for rec in new_records
            # ]
            # new_records_source_ids = [r["source_id"] for r in new_records]
            existing_records_uid_only = [
                {rec[uid_field] for uid_field in self.uid_fields}
                for rec in existing_records
            ]

            existing_encounters = self.fetch_existing_records(
                new_records,
                Encounter,
                source_field="encounter_source",
                source_id_field="encounter_source_id"
            )
            encounter_source_ids = [
                e["source_id"] for e in existing_encounters
            ]
            encounters_to_retain = [
                e["source_id"] for e in existing_encounters
                if e["status"] > QualityControlMixin.STATUS_NEW
            ]
            encounters_to_update = [
                e["source_id"] for e in existing_encounters
                if e["status"] == QualityControlMixin.STATUS_NEW
            ]
            encounter_dict = {
                "{}|{}".format(e["source"], e["source_id"]): e["pk"]
                for e in existing_encounters
            }

            logger.info(
                "[API][create] Found {0} existing Encounter records: "
                "{1} to retain, {2} to update".format(
                    len(existing_encounters),
                    len(encounters_to_retain),
                    len(encounters_to_update)
                )
            )

            # ----------------------------------------------------------------#
            # Observations without an existing Encounter are refused.
            # Create Encounters first, then corresponding Observations.
            to_refuse = [
                x for x in new_records
                if x["encounter_source_id"] not in encounter_source_ids
            ]
            logger.info(
                "[API][create] Found {0} records without matching Encounter. "
                .format(len(to_refuse))
            )

            # Bucket "retain": existing_objects with status > STATUS_NEW
            # to_retain = [t for t in existing_records if t["status"] > QualityControlMixin.STATUS_NEW]
            to_retain = [
                x for x in new_records
                if x["encounter_source_id"] in encounters_to_retain
            ]

            # TODO Log PKs (debug) or total number (info) of skipped records
            logger.info("[API][create] Skipping {0} QA'd records".format(len(to_retain)))
            logger.debug("[API][create] Skipping QA'd records: {0}".format(str(to_retain)))

            # Bucket "bulk_update": List of new_records where uid_fields match existing_objects
            # see https://github.com/dbca-wa/wastd/issues/330
            # TODO this contains records that should be created
            records_to_update = [
                new_record for new_record in new_records
                if {new_record[uid_field] for uid_field in self.uid_fields}
                in existing_records_uid_only
                and new_record["encounter_source_id"] in encounters_to_update  # noqa
            ]

            # Bucket "bulk_create": List of new records without match in existing records
            records_to_create = [
                new_record for new_record in new_records
                if {new_record[uid_field] for uid_field in self.uid_fields}
                not in existing_records_uid_only
                and new_record["encounter_source_id"] in encounter_source_ids  # noqa
            ]

            logger.info(
                "[API][create] Done sorting records: "
                "{0} refused (create Encounter first), {1} to retain, "
                "{2} to update, {1} to create.".format(
                    len(to_refuse),
                    len(to_retain),
                    len(records_to_update),
                    len(records_to_create)
                )
            )

            # import ipdb; ipdb.set_trace()

            # Hammertime
            with transaction.atomic():
                if records_to_update:
                    logger.info("[API][create] Updating records...")

                    # TODO debug cache miss in encounter_dict
                    for data in records_to_update:
                        data["encounter_id"] = encounter_dict[
                            "{}|{}".format(data["encounter_source"], data["encounter_source_id"])
                        ]
                        data.pop("encounter_source")
                        data.pop("encounter_source_id")
                        unique_data, update_data = self.split_data(data)
                        # logger.debug(str(unique_data))
                        obj, created = self.model.objects.update_or_create(**unique_data, defaults=update_data)

                        # self.model.objects.filter(**unique_data).update(**update_data)
                        # logger.debug(obj)

                if records_to_create:
                    logger.info("[API][create] Creating records...")
                    for data in records_to_create:
                        data["encounter_id"] = encounter_dict[
                            "{}|{}".format(data["encounter_source"], data["encounter_source_id"])
                        ]
                        data.pop("encounter_source")
                        data.pop("encounter_source_id")
                        unique_data, update_data = self.split_data(data)
                        obj, created = self.model.objects.get_or_create(
                            defaults=update_data, **unique_data
                        )
                        # obj = self.model.objects.create(**data)
                        logger.info("[API][create] Creating record with unique fields "
                                    "{0}, update fields {1}, created: {2}".format(
                                        str(unique_data), str(update_data), created))

                        # to update cached fields
                        obj.refresh_from_db()
                        obj.save()

            logger.info("[API][create] Finished.")
            msg = "Refused {0}, retained {1}, updated {2}, created {3} records.".format(
                len(to_refuse),
                len(to_retain),
                len(records_to_update),
                len(records_to_create)
            )
            logger.info(msg)

            return RestResponse(msg, status=status.HTTP_200_OK)

        # Create none --------------------------------------------------------#
        else:
            msg = ("[API][BatchUpsertViewSet] unknown data format:"
                   "{0}".format(str(request.data)))
            logger.warning(msg)
            return RestResponse({"msg": msg}, status=status.HTTP_406_NOT_ACCEPTABLE)
