# -*- coding: utf-8 -*-
"""Shared API utilities."""
from collections import OrderedDict
import logging


from rest_framework.response import Response as RestResponse
from rest_framework import viewsets, status, pagination  # , serializers, routers

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
    """A ModelViewSet with custom create().

    Accepts request.data to be either a GeoJSON feature property dict,
    or a list of GeoJSON feature property dicts.

    `model` and `uid_field` are used to determine whether the object
    already exists. The `uid_field` can be the PK or any other
    unique field of the given `model`.

    Responds with status 200 if all went well, else 400.
    """

    pagination_class = pagination.LimitOffsetPagination
    model = None
    uid_field = None

    def build_unique_fields(self, data):
        """Return a dict with a set of unique fields.

        If your model has more than one unique field,
        get_or_create will fail on create.
        In this case, override build_unique_fields to
        return a dict of all unique fields.
        """
        return {self.uid_field: data[self.uid_field]}

    def create_one(self, data):
        """POST: Create or update exactly one model instance."""
        dd = self.build_unique_fields(data)
        if 'csrfmiddlewaretoken' in data:
            data.pop('csrfmiddlewaretoken')
        logger.debug('[API][create_one] data {0}'.format(dd))
        obj, created = self.model.objects.get_or_create(**dd)
        self.model.objects.filter(**dd).update(**data)
        return RestResponse(data, status=status.HTTP_200_OK)

    def create(self, request):
        """POST: Create or update one or many model instances.

        request.data must be:

        * a GeoJSON feature property dict, or
        * a list of GeoJSON feature property dicts.
        """
        if self.uid_field in request.data:
            res = self.create_one(request.data)
            logger.debug('[API][create] found one record')
            return res
        elif type(request.data) == list and self.uid_field in request.data[0]:
            res = [self.create_one(data) for data in request.data]
            logger.debug('[API][create] found batch of {0} records'.format(len(res)))
            return RestResponse(request.data, status=status.HTTP_200_OK)
        else:
            logger.debug("[BatchUpsertViewSet] data: {0}".format(request.data))
            return RestResponse(request.data, status=status.HTTP_400_BAD_REQUEST)


class FastBatchUpsertViewSet(BatchUpsertViewSet):
    """Viewset with LO pagination and page size 10."""

    pagination_class = FastLimitOffsetPagination
