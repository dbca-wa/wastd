# -*- coding: utf-8 -*-
"""Conservation filters."""
from django.contrib.gis.db import models as geo_models

import django_filters

from conservation.models import ConservationAction
from shared.filters import (  # noqa
    FILTER_OVERRIDES, TaxonWidget, UserWidget, CommunityWidget)


class ConservationActionFilter(django_filters.FilterSet):
    """Filter for ConservationAction."""

    target_area = geo_models.PolygonField()

    class Meta:
        """Class opts."""

        model = ConservationAction
        fields = ['target_area', 'category', 'status', ]
        filter_overrides = FILTER_OVERRIDES
