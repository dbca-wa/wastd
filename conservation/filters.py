# -*- coding: utf-8 -*-
"""Conservation filters."""
from django.contrib.gis.db import models as geo_models

import django_filters

from conservation import models as cons_models
from taxonomy import models as tax_models
from taxonomy import widgets as tax_widgets
from shared.filters import FILTER_OVERRIDES


class ConservationThreatFilter(django_filters.FilterSet):
    """Filter for ConservationThreat."""

    target_area = geo_models.PolygonField()
    taxa = django_filters.ModelMultipleChoiceFilter(
        queryset=tax_models.Taxon.objects.all(),
        widget=tax_widgets.TaxonMultipleWidget()
    )
    communities = django_filters.ModelMultipleChoiceFilter(
        queryset=tax_models.Community.objects.all(),
        widget=tax_widgets.CommunityMultipleWidget()
    )

    class Meta:
        """Class opts."""

        model = cons_models.ConservationThreat
        filter_overrides = FILTER_OVERRIDES
        fields = [
            "taxa",
            "taxa__paraphyletic_groups",
            "communities",
            'target_area',
            'category',
            'current_impact',
            'potential_onset',
            'potential_impact'
        ]


class ConservationActionFilter(django_filters.FilterSet):
    """Filter for ConservationAction."""

    target_area = geo_models.PolygonField()
    taxa = django_filters.ModelMultipleChoiceFilter(
        queryset=tax_models.Taxon.objects.all(),
        widget=tax_widgets.TaxonMultipleWidget()
    )
    communities = django_filters.ModelMultipleChoiceFilter(
        queryset=tax_models.Community.objects.all(),
        widget=tax_widgets.CommunityMultipleWidget()
    )

    class Meta:
        """Class opts."""

        model = cons_models.ConservationAction
        filter_overrides = FILTER_OVERRIDES
        fields = ["taxa",
                  "taxa__paraphyletic_groups",
                  "communities",
                  'target_area',
                  'category',
                  'status', ]


class DocumentFilter(django_filters.FilterSet):
    """Filter for Document."""

    taxa = django_filters.ModelMultipleChoiceFilter(
        queryset=tax_models.Taxon.objects.all(),
        widget=tax_widgets.TaxonMultipleWidget()
    )
    communities = django_filters.ModelMultipleChoiceFilter(
        queryset=tax_models.Community.objects.all(),
        widget=tax_widgets.CommunityMultipleWidget()
    )

    class Meta:
        """Class opts."""

        model = cons_models.Document
        filter_overrides = FILTER_OVERRIDES
        fields = [
            "document_type",
            "taxa",
            "taxa__paraphyletic_groups",
            "communities",
            "effective_from",
            "effective_to",
            "effective_from_commonwealth",
            "effective_to_commonwealth",
            "last_reviewed_on",
            "review_due",
            "status"
        ]
