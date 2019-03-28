# -*- coding: utf-8 -*-
"""Conservation filters."""
from django.contrib.gis.db import models as geo_models

import django_filters

from conservation.models import ConservationThreat, ConservationAction
from shared.filters import FILTER_OVERRIDES


class ConservationThreatFilter(django_filters.FilterSet):
    """Filter for ConservationThreat."""

    target_area = geo_models.PolygonField()

    class Meta:
        """Class opts."""

        model = ConservationThreat
        fields = [
            'target_area',
            'category',
            'current_impact',
            'potential_onset',
            'potential_impact'
        ]
        filter_overrides = FILTER_OVERRIDES


class ConservationActionFilter(django_filters.FilterSet):
    """Filter for ConservationAction."""

    target_area = geo_models.PolygonField()

    class Meta:
        """Class opts."""

        model = ConservationAction
        fields = ['target_area', 'category', 'status', ]
        filter_overrides = FILTER_OVERRIDES
