# -*- coding: utf-8 -*-
"""Shared API utilities."""
from collections import OrderedDict
import logging


from rest_framework.response import Response as RestResponse
from rest_framework import viewsets, status, pagination  # , serializers, routers

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

        Return RestResponse(data, status)
        """
        unique_data, update_data = self.split_data(data)

        if None in unique_data.values():
            logger.warning('[API][create_one] Skipping invalid data: {0}'.format(str(data)))
            return RestResponse(data, status=status.HTTP_400_BAD_REQUEST)

        logger.debug('[API][create_one] Creating/updating with unique fields {0}'.format(str(unique_data)))
        obj, created = self.model.objects.get_or_create(**unique_data)
        verb = "created" if created else "updated"
        self.model.objects.filter(**unique_data).update(**update_data)
        obj = self.model.objects.get(**unique_data)
        obj.save()  # to update caches
        # if created:
        logger.info('[API][create_one] {0} {1}: {2}'.format(verb, self.model._meta.verbose_name, str(unique_data)))
        # else:
        # logger.info('[API][create_one] {0} {1} ({2}): {3}'.format(verb, self.model._meta.verbose_name, obj.pk, obj))
        return RestResponse(data, status=status.HTTP_200_OK)

        #         try:
#             obj, created = self.model.objects.get_or_create(**dd)
#             verb = "created" if created else "updated"
#             self.model.objects.filter(**dd).update(**data)
#             logger.info('[API][create_one] {0}: {1}'.format(verb, obj))
#             return RestResponse(data, status=status.HTTP_200_OK)
#         except Exception as e:
#             logger.warning('[API][create_one] Raised {0} with data {1}'.format(e, str(data)))
#             return RestResponse(data, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        """POST: Create or update one or many model instances.

        request.data must be:

        * a GeoJSON feature property dict, or
        * a list of GeoJSON feature property dicts.
        """
        if self.uid_fields[0] in request.data:
            res = self.create_one(request.data)
            logger.info('[API][create] found one record')
            return res
        elif type(request.data) == list and self.uid_fields[0] in request.data[0]:
            res = [self.create_one(data) for data in request.data]
            logger.info('[API][create] found batch of {0} records'.format(len(res)))
            return RestResponse(request.data, status=status.HTTP_200_OK)
        else:
            logger.debug("[API][BatchUpsertViewSet] unknown data format: {0}".format(str(request.data)))
            return RestResponse(request.data, status=status.HTTP_400_BAD_REQUEST)


class FastBatchUpsertViewSet(BatchUpsertViewSet):
    """Viewset with LO pagination and page size 10."""

    pagination_class = FastLimitOffsetPagination
