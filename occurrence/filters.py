# -*- coding: utf-8 -*-
"""Occurrence filters."""
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models as geo_models

import django_filters

from occurrence import models as occ_models
from taxonomy import models as tax_models
from shared import filters as shared_filters


class TaxonAreaEncounterFilter(django_filters.FilterSet):
    """Filter for TaxonAreaEncounter."""

    taxon = django_filters.ModelChoiceFilter(
        queryset=tax_models.Taxon.objects.all(),
        widget=shared_filters.TaxonWidget()
    )
    encountered_by = django_filters.ModelChoiceFilter(
        queryset=get_user_model().objects.all(),
        widget=shared_filters.UserWidget()
    )

    class Meta:
        """Class opts."""

        model = occ_models.TaxonAreaEncounter
        fields = [
            'taxon',
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
        filter_overrides = shared_filters.FILTER_OVERRIDES


class CommunityAreaEncounterFilter(django_filters.FilterSet):
    """Filter for CommunityAreaEncounter."""

    geom = geo_models.PolygonField()
    point = geo_models.PointField()
    community = django_filters.ModelChoiceFilter(
        queryset=tax_models.Community.objects.all(),
        widget=shared_filters.CommunityWidget()
    )
    encountered_by = django_filters.ModelChoiceFilter(
        queryset=get_user_model().objects.all(),
        widget=shared_filters.UserWidget()
    )

    class Meta:
        """Class opts."""

        model = occ_models.CommunityAreaEncounter
        fields = [
            'community',
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
        filter_overrides = shared_filters.FILTER_OVERRIDES
