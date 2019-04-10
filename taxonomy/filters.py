# -*- coding: utf-8 -*-
"""Taxonomy filters."""
# from django.contrib.auth.models import User
import django_filters
from conservation.models import ConservationCategory
from django.contrib.gis.db import models as geo_models
from django.contrib.gis.db.models import Extent, Union, Collect  # noqa
from django.db.models import Q
from django_filters.filters import (
    BooleanFilter, ModelChoiceFilter, ModelMultipleChoiceFilter)
from django_filters.widgets import BooleanWidget  # noqa

# from django import forms
from taxonomy.models import Community, Taxon
from occurrence import models as occ_models
from shared.filters import FILTER_OVERRIDES
from wastd.observations.models import Area


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
    taxon_gazettal__category = ModelChoiceFilter(
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
    admin_areas = ModelMultipleChoiceFilter(
        label="DBCA Regions and Districts",
        queryset=Area.objects.filter(
            area_type__in=[
                Area.AREATYPE_DBCA_REGION,
                Area.AREATYPE_DBCA_DISTRICT]),
        method='taxa_occurring_in_area'
    )

    class Meta:
        """Class opts."""

        model = Taxon
        fields = [
            "paraphyletic_groups",
            "admin_areas",
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

    def taxa_occurring_in_area(self, queryset, name, value):
        """Return Taxa occurring in the given Area.

        * The filter returns a list of Area objects as ``value``
        * We need to extract their PKs to create a queryset equivalent to
          the list of objects ``value``. Only querysets allow agggregation, not lists.
        * A search_area Multipolygon is collected from the geoms of Areas in ``value``
        * The Taxon PKs are calculated from occurrences (TaxonAreaEncounters)
          ``intersect``ing the search_area
        * The queryset is filtered by the list of Taxon PKs with occurrences
        """
        if value:
            area_pks = [area.pk for area in value]
            search_area = Area.objects.filter(
                pk__in=area_pks
            ).aggregate(Collect('geom'))["geom__collect"]
            taxon_pks_in_area = set(
                [x["taxon__pk"]
                 for x in occ_models.TaxonAreaEncounter.objects.filter(
                    Q(point__intersects=search_area) | Q(geom__intersects=search_area)
                ).values("taxon__pk")]
            )
            return queryset.filter(pk__in=taxon_pks_in_area)
        else:
            return queryset


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
    admin_areas = ModelMultipleChoiceFilter(
        label="DBCA Regions and Districts",
        queryset=Area.objects.filter(
            area_type__in=[
                Area.AREATYPE_DBCA_REGION,
                Area.AREATYPE_DBCA_DISTRICT]),
        method='communities_occurring_in_area'
    )

    class Meta:
        """Class opts."""

        model = Community
        fields = [
            "admin_areas",
            "eoo",
            "community_gazettal__category",
            "code",
            "name",
            "description",
        ]
        filter_overrides = FILTER_OVERRIDES

    def communities_occurring_in_area(self, queryset, name, value):
        """Return Communities occurring in the given Area.

        * The filter returns a list of Area objects as ``value``
        * We need to extract their PKs to create a queryset equivalent to
          the list of objects ``value``. Only querysets allow agggregation, not lists.
        * A search_area Multipolygon is collected from the geoms of Areas in ``value``
        * The Taxon PKs are calculated from occurrences (CommunityAreaEncounters)
          ``intersect``ing the search_area
        * The queryset is filtered by the list of Community PKs with occurrences
        """
        if value:
            area_pks = [area.pk for area in value]
            search_area = Area.objects.filter(
                pk__in=area_pks
            ).aggregate(Collect('geom'))["geom__collect"]
            com_pks_in_area = set(
                [x["community__pk"]
                 for x in occ_models.CommunityAreaEncounter.objects.filter(
                    Q(point__intersects=search_area) | Q(geom__intersects=search_area)
                ).values("community__pk")]
            )
            return queryset.filter(pk__in=com_pks_in_area)
        else:
            return queryset
