# -*- coding: utf-8 -*-
"""Taxonomy filters."""
# from django.contrib.auth.models import User
import django_filters
from conservation.models import ConservationCategory
from django.contrib.gis.db import models as geo_models
from django_filters.filters import BooleanFilter, ModelMultipleChoiceFilter  # noqa
from django_filters.widgets import BooleanWidget  # noqa

# from django import forms
from .models import Community, Taxon
from shared.filters import FILTER_OVERRIDES


class TaxonFilter(django_filters.FilterSet):
    """Filter for Taxon."""

    is_terminal_taxon = BooleanFilter(
        label="Terminal Taxon",
        widget=BooleanWidget(),
        method="filter_leaf_nodes"
    )
    current = BooleanFilter(
        label="Taxonomic name is current",
        widget=BooleanWidget()
    )
    taxon_gazettal__category = ModelMultipleChoiceFilter(
        label="Conservation listed as",
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
            "paraphyletic_groups",
            "eoo",
            "taxon_gazettal__category",
            "taxonomic_name",
            "vernacular_names",
            "rank",
            "is_terminal_taxon",
            "current",
            "publication_status",
            "name_id",
            "field_code"
        ]
        filter_overrides = FILTER_OVERRIDES

    def filter_leaf_nodes(self, queryset, name, value):
        """Return terminal taxa (leaf nodes) if value is true."""
        return queryset.filter(children__isnull=value)


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
