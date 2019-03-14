# -*- coding: utf-8 -*-
"""Taxonomy filters."""
# from django.contrib.auth.models import User
import django_filters
from conservation.models import ConservationCategory
from django.contrib.gis.db import models as geo_models
from django.db import models
from django_filters.filters import BooleanFilter, ModelMultipleChoiceFilter
from django_filters.widgets import BooleanWidget
from leaflet.forms.widgets import LeafletWidget

# from django import forms
from .models import Community, Taxon

FILTER_OVERRIDES = {
    models.CharField: {
        "filter_class": django_filters.CharFilter,
        "extra": lambda f: {"lookup_expr": "icontains", },
    },
    models.TextField: {
        "filter_class": django_filters.CharFilter,
        "extra": lambda f: {"lookup_expr": "icontains", },
    },
    geo_models.PolygonField: {
        "filter_class": django_filters.CharFilter,
        "extra": lambda f: {"lookup_expr": "intersects",
                            "widget": LeafletWidget()},
    }
}


class TaxonFilter(django_filters.FilterSet):
    """Filter for Taxon."""

    current = BooleanFilter(widget=BooleanWidget())
    taxon_gazettal__category = ModelMultipleChoiceFilter(
        queryset=ConservationCategory.objects.filter(
            conservation_list__scope_species=True
        ).order_by(
            "conservation_list__code", "rank"
        ).prefetch_related(
            "conservation_list"
        )
    )
    eoo = geo_models.PolygonField()

    class Meta:
        """Class opts."""

        model = Taxon
        fields = [
            "eoo",
            "taxon_gazettal__category",
            "taxonomic_name",
            "vernacular_names",
            "rank",
            "current",
            "publication_status",
            "name_id",
            "field_code"
        ]
        filter_overrides = FILTER_OVERRIDES


class CommunityFilter(django_filters.FilterSet):
    """Filter for Community."""

    community_gazettal__category = ModelMultipleChoiceFilter(
        queryset=ConservationCategory.objects.filter(
            conservation_list__scope_communities=True
        ).order_by(
            "conservation_list__code",
            "rank"
        ).prefetch_related(
            "conservation_list"
        )
    )
    eoo = geo_models.PolygonField()

    class Meta:
        """Class opts."""

        model = Community
        fields = [
            "eoo",
            "community_gazettal__category",
            "code",
            "name",
            "description",
        ]
        # widgets = {"eoo": LeafletWidget()}
        filter_overrides = FILTER_OVERRIDES
