# -*- coding: utf-8 -*-
"""Shared API utilities."""
from collections import OrderedDict
import logging


from rest_framework.response import Response as RestResponse
from rest_framework import viewsets, status, pagination  # , serializers, routers

from shared.models import QualityControlMixin
# from taxonomy.models import Taxon

logger = logging.getLogger(__name__)


class MyGeoJsonPagination(pagination.LimitOffsetPagination):
    """
    A geoJSON implementation of a LimitOffset pagination serializer.

    Attempt to un-break HTML filter controls in browsable API.

    https://github.com/tomchristie/django-rest-framework/issues/4812
    """

    def get_paginated_response(self, data):
        """Return a GeoJSON FeatureCollection with pagination links."""
        return RestResponse(OrderedDict([
            ('type', 'FeatureCollection'),
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('features', data['features']),
        ]))


class FastLimitOffsetPagination(pagination.LimitOffsetPagination):
    """GeoJSON pagination with page size of 10."""

    page_size = 10


class BatchUpsertViewSet(viewsets.ModelViewSet):
    """A BatchUpsert ViewSet.

    Override split_data for nested serializers, e.g. TaxonAreaEncounters.taxon.
    """

    pagination_class = pagination.LimitOffsetPagination
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
            msg = '[API][create_one] Skipping invalid data: {0}'.format(str(data))
            logger.warning(msg)
            content = {"msg": msg}
            return RestResponse(content, status=status.HTTP_406_NOT_ACCEPTABLE)

        logger.debug('[API][create_one] Update or create '
                     '{0} with unique fields {1}'.format(
                         self.model._meta.verbose_name, str(unique_data)))

        # Without the QA status deciding whether to update existing data:
        # obj, created = self.model.objects.update_or_create(defaults=update_data, **unique_data)
        # Since we need to inspect existing records' QA status:
        obj, created = self.model.objects.get_or_create(**unique_data)

        # Early exit 2: retain locally changed data (status not NEW)
        if (not created and obj.status != QualityControlMixin.STATUS_NEW):
            msg = ('[API][create_one] Not overwriting locally changed data '
                   'with QA status: {0}'.format(obj.get_status_display()))
            logger.info(msg)
            content = {"msg": msg}
            return RestResponse(content, status=status.HTTP_200_OK)
        else:
            # Continue on happy trail: New or existing but unchanged gets updated
            self.model.objects.filter(**unique_data).update(**update_data)

            obj = self.model.objects.get(**unique_data)
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
        if self.uid_fields[0] in request.data:
            logger.info('[API][create] found one record, creating/updating...')
            res = self.create_one(request.data).__dict__
            return RestResponse(res, status=status.HTTP_200_OK)
        elif type(request.data) == list and self.uid_fields[0] in request.data[0]:
            logger.info('[API][create] found batch of {0} records,'
                        ' creating/updating...'.format(len(request.data)))
            res = [self.create_one(data).__dict__ for data in request.data]
            return RestResponse(res, status=status.HTTP_200_OK)
        else:
            msg = ("[API][BatchUpsertViewSet] unknown data format:"
                   "{0}".format(str(request.data)))
            logger.warning(msg)
            return RestResponse({"msg": msg}, status=status.HTTP_406_NOT_ACCEPTABLE)


class FastBatchUpsertViewSet(BatchUpsertViewSet):
    """Viewset with LO pagination and page size 10."""

    pagination_class = FastLimitOffsetPagination
