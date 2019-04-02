# -*- coding: utf-8 -*-
"""Conservation filters."""
from django.contrib.gis.db import models as geo_models

import django_filters

from conservation import models as cons_models
from shared.filters import FILTER_OVERRIDES


class ConservationThreatFilter(django_filters.FilterSet):
    """Filter for ConservationThreat."""

    target_area = geo_models.PolygonField()

    class Meta:
        """Class opts."""

        model = cons_models.ConservationThreat
        filter_overrides = FILTER_OVERRIDES
        fields = [
            'target_area',
            'category',
            'current_impact',
            'potential_onset',
            'potential_impact'
        ]


class ConservationActionFilter(django_filters.FilterSet):
    """Filter for ConservationAction."""

    target_area = geo_models.PolygonField()

    class Meta:
        """Class opts."""

        model = cons_models.ConservationAction
        filter_overrides = FILTER_OVERRIDES
        fields = ['target_area', 'category', 'status', ]


class DocumentFilter(django_filters.FilterSet):
    """Filter for Document."""

    class Meta:
        """Class opts."""

        model = cons_models.Document
        filter_overrides = FILTER_OVERRIDES
        fields = [
            "document_type",
            "taxa",
            "communities",
            "effective_from",
            "effective_to",
            "effective_from_commonwealth",
            "effective_to_commonwealth",
            "last_reviewed_on",
            "review_due",
            "status"
        ]
