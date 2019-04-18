# -*- coding: utf-8 -*-
"""Taxonomy filters."""
# from django.contrib.auth.models import User
from django.contrib.gis.db import models as geo_models
from django.contrib.gis.db.models import Extent, Union, Collect  # noqa
from django.db.models import Q
import django_filters
from django_filters.widgets import BooleanWidget  # noqa
from django_filters.filters import (  # noqa
    BooleanFilter, CharFilter,
    ChoiceFilter, MultipleChoiceFilter,
    ModelChoiceFilter, ModelMultipleChoiceFilter)

from leaflet.forms.widgets import LeafletWidget

# from django import forms
from conservation import models as cons_models
from occurrence import models as occ_models
from taxonomy.models import Community, Taxon
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
    admin_areas = ModelMultipleChoiceFilter(
        label="DBCA Regions and Districts",
        queryset=Area.objects.filter(
            area_type__in=[
                Area.AREATYPE_DBCA_REGION,
                Area.AREATYPE_DBCA_DISTRICT]),
        method='taxa_occurring_in_area'
    )
    eoo = geo_models.PolygonField()
    aoo = CharFilter(
        label="Area of Occupancy (AOO) intersects",
        widget=LeafletWidget(),
        method="taxa_occurring_in_poly",
    )
    conservation_level = MultipleChoiceFilter(
        label="Conservation Level",
        choices=cons_models.ConservationCategory.LEVEL_CHOICES,
        method='taxon_conservation_level'
    )
    categories = ModelMultipleChoiceFilter(
        label="Conservation Listing Categories",
        queryset=cons_models.ConservationCategory.objects.filter(
            conservation_list__scope_species=True
        ).order_by(
            "conservation_list__code", "rank"
        ).prefetch_related(
            "conservation_list"
        ),
        method="taxa_with_conservation_criteria"
    )

    class Meta:
        """Class opts."""

        model = Taxon
        fields = [
            "paraphyletic_groups",
            "admin_areas",
            "eoo",
            "aoo",
            "conservation_level",
            "categories",
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
        """Return Taxa occurring in the given list of ``Area`` instances.

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

    def taxa_occurring_in_poly(self, queryset, name, value):
        """Return Taxa occurring in the given Area polygon.

        * The filter returns a ``value``
        * (magic) value becomes search area
        * The Taxon PKs are calculated from occurrences (TaxonAreaEncounters)
          ``intersect``ing the search_area
        * The queryset is filtered by the list of Taxon PKs with occurrences
        """
        if value:
            taxon_pks_in_area = set(
                [x["taxon__pk"]
                 for x in occ_models.TaxonAreaEncounter.objects.filter(
                    Q(point__intersects=value) | Q(geom__intersects=value)
                ).values("taxon__pk")]
            )
            return queryset.filter(pk__in=taxon_pks_in_area)
        else:
            return queryset

    def taxon_conservation_level(self, queryset, name, value):
        """Return Taxa matching a conservation level.

        * The filter returns a list of ConservationCategory levels as ``value``
        * The Taxon PKs are calculated from active, WA CommunityGazettals
          with categories matching the level
        * The queryset is filtered by the list of Taxon PKs with
          active taxon listings in WA  matching the conservation level
        """
        if value:
            taxon_pks = set([x["taxon__pk"] for x in
                             cons_models.TaxonGazettal.objects.filter(
                scope=cons_models.Gazettal.SCOPE_WESTERN_AUSTRALIA,
                status=cons_models.Gazettal.STATUS_EFFECTIVE,
                category__level__in=value
            ).values("taxon__pk")])
            return queryset.filter(pk__in=taxon_pks)
        else:
            return queryset

    def taxa_with_conservation_criteria(self, queryset, name, value):
        """Return Taxa matching a conservation level.

        * The filter returns a list of ConservationCategories as ``value``
        * The Taxon PKs are calculated from TaxonGazettals
          with categories matching the list of categories in ``value``
        * The queryset is filtered by the list of Taxon PKs
          matching the conservation level
        """
        if value:
            taxon_pks = set(
                [x["taxon__pk"] for x in
                 cons_models.TaxonGazettal.objects.filter(
                    category__in=value).values("taxon__pk")])
            return queryset.filter(pk__in=taxon_pks)
        else:
            return queryset


class CommunityFilter(django_filters.FilterSet):
    """Filter for Community."""

    admin_areas = ModelMultipleChoiceFilter(
        label="DBCA Regions and Districts",
        queryset=Area.objects.filter(
            area_type__in=[
                Area.AREATYPE_DBCA_REGION,
                Area.AREATYPE_DBCA_DISTRICT]),
        method='communities_occurring_in_area'
    )
    eoo = geo_models.PolygonField()
    aoo = CharFilter(
        label="Area of Occupancy (AOO) intersects",
        widget=LeafletWidget(),
        method="communities_occurring_in_poly",
    )
    conservation_level = MultipleChoiceFilter(
        label="Conservation Level",
        choices=cons_models.ConservationCategory.LEVEL_CHOICES,
        method='community_conservation_level'
    )
    categories = ModelMultipleChoiceFilter(
        label="Conservation Listing Categories",
        queryset=cons_models.ConservationCategory.objects.filter(
            conservation_list__scope_communities=True
        ).order_by(
            "conservation_list__code", "rank"
        ).prefetch_related(
            "conservation_list"
        ),
        method="communities_with_conservation_criteria"
    )

    class Meta:
        """Class opts."""

        model = Community
        fields = [
            "admin_areas",
            "eoo",
            "aoo",
            "conservation_level",
            "categories",
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
          in the matching areas
        """
        if value:
            area_pks = [area.pk for area in value]
            search_area = Area.objects.filter(
                pk__in=area_pks
            ).aggregate(Collect('geom'))["geom__collect"]
            pks = set([x["community__pk"] for x in
                       occ_models.CommunityAreaEncounter.objects.filter(
                Q(point__intersects=search_area) | Q(geom__intersects=search_area)
            ).values("community__pk")]
            )
            return queryset.filter(pk__in=pks)
        else:
            return queryset

    def communities_occurring_in_poly(self, queryset, name, value):
        """Return Communities occurring in the given Area polygon.

        * The filter returns a ``value``
        * (magic) value becomes search area
        * The Community PKs are calculated from occurrences (CommunityAreaEncounters)
          ``intersect``ing the search_area
        * The queryset is filtered by the list of Community PKs with occurrences
        """
        if value:
            pks = set(
                [x["community__pk"]
                 for x in occ_models.CommunityAreaEncounter.objects.filter(
                    Q(point__intersects=value) | Q(geom__intersects=value)
                ).values("community__pk")]
            )
            return queryset.filter(pk__in=pks)
        else:
            return queryset

    def community_conservation_level(self, queryset, name, value):
        """Return Communities matching a conservation level.

        * The filter returns a list of ConservationCategory levels as ``value``
        * The Community PKs are calculated from active, WA CommunityGazettals
          with categories matching the level
        * The queryset is filtered by the list of Community PKs with
          active community listings in WA  matching the conservation level
        """
        if value:
            pks = set([x["community__pk"] for x in
                       cons_models.CommunityGazettal.objects.filter(
                scope=cons_models.Gazettal.SCOPE_WESTERN_AUSTRALIA,
                status=cons_models.Gazettal.STATUS_EFFECTIVE,
                category__level__in=value).values("community__pk")])
            return queryset.filter(pk__in=pks)
        else:
            return queryset

    def communities_with_conservation_criteria(self, queryset, name, value):
        """Return Communities matching a conservation level.

        * The filter returns a list of ConservationCategories as ``value``
        * The Taxon PKs are calculated from CommunityGazettals
          with categories matching the list of categories in ``value``
        * The queryset is filtered by the list of Taxon PKs
          matching the conservation level
        """
        if value:
            pks = set([x["community__pk"] for x in
                       cons_models.CommunityGazettal.objects.filter(
                category__in=value).values("community__pk")])
            return queryset.filter(pk__in=pks)
        else:
            return queryset
