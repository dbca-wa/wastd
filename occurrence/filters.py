# -*- coding: utf-8 -*-
"""Occurrence filters."""
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models as geo_models
from django.contrib.gis.db.models import Extent, Union, Collect  # noqa
from django.db.models import Q

import django_filters

from occurrence import models as occ_models
from taxonomy import models as tax_models
from taxonomy import widgets as tax_widgets
from shared.filters import FILTER_OVERRIDES
from wastd.observations.models import Area
from wastd.users import widgets as usr_widgets


class TaxonAreaEncounterFilter(django_filters.FilterSet):
    """Filter for TaxonAreaEncounter."""

    taxon = django_filters.ModelChoiceFilter(
        queryset=tax_models.Taxon.objects.all(),
        widget=tax_widgets.TaxonWidget()
    )
    encountered_by = django_filters.ModelChoiceFilter(
        queryset=get_user_model().objects.all(),
        widget=usr_widgets.UserWidget()
    )
    admin_areas = django_filters.ModelMultipleChoiceFilter(
        label="DBCA Regions and Districts",
        queryset=Area.objects.filter(
            area_type__in=[
                Area.AREATYPE_DBCA_REGION,
                Area.AREATYPE_DBCA_DISTRICT]),
        method='occurring_in_area'
    )

    class Meta:
        """Class opts."""

        model = occ_models.TaxonAreaEncounter
        fields = [
            "status",
            "admin_areas",
            "taxon__paraphyletic_groups",
            "taxon",
            "area_type",
            "code",
            "name",
            "description",
            "point",
            "geom",
            "accuracy",
            "source",
            "source_id",
            "encountered_on",
            "encountered_by",
        ]
        filter_overrides = FILTER_OVERRIDES

    def occurring_in_area(self, queryset, name, value):
        """Return Taxa occurring in the given Area.

        * The filter returns a list of Area objects as ``value``
        * We need to extract their PKs to create a queryset equivalent to
          the list of objects ``value``. Only querysets allow agggregation, not lists.
        * A search_area Multipolygon is collected from the geoms of Areas in ``value``
        * The queryset is filtered by intersection of its point or geom with the search area
        """
        if value:
            search_area = Area.objects.filter(
                pk__in=[area.pk for area in value]
            ).aggregate(Collect('geom'))["geom__collect"]
            return queryset.filter(
                Q(point__intersects=search_area) |
                Q(geom__intersects=search_area)
            )
        else:
            return queryset


class CommunityAreaEncounterFilter(django_filters.FilterSet):
    """Filter for CommunityAreaEncounter."""

    geom = geo_models.PolygonField()
    point = geo_models.PointField()
    community = django_filters.ModelChoiceFilter(
        queryset=tax_models.Community.objects.all(),
        widget=tax_widgets.CommunityWidget()
    )
    encountered_by = django_filters.ModelChoiceFilter(
        queryset=get_user_model().objects.all(),
        widget=usr_widgets.UserWidget()
    )
    admin_areas = django_filters.ModelMultipleChoiceFilter(
        label="DBCA Regions and Districts",
        queryset=Area.objects.filter(
            area_type__in=[
                Area.AREATYPE_DBCA_REGION,
                Area.AREATYPE_DBCA_DISTRICT]),
        method='occurring_in_area'
    )

    class Meta:
        """Class opts."""

        model = occ_models.CommunityAreaEncounter
        fields = [
            "status",
            "admin_areas",
            "community",
            "area_type",
            "code",
            "name",
            "description",
            "point",
            "geom",
            "accuracy",
            "source",
            "source_id",
            "encountered_on",
            "encountered_by",
        ]
        filter_overrides = FILTER_OVERRIDES

    def occurring_in_area(self, queryset, name, value):
        """Return occurrences in the given Area.

        * The filter returns a list of Area objects as ``value``
        * We need to extract their PKs to create a queryset equivalent to
          the list of objects ``value``. Only querysets allow agggregation, not lists.
        * A search_area Multipolygon is collected from the geoms of Areas in ``value``
        * The queryset is filtered by intersection of its point or geom with the search area
        """
        if value:
            search_area = Area.objects.filter(
                pk__in=[area.pk for area in value]
            ).aggregate(Collect('geom'))["geom__collect"]
            return queryset.filter(
                Q(point__intersects=search_area) |
                Q(geom__intersects=search_area)
            )
        else:
            return queryset
