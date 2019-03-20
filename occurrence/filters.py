# -*- coding: utf-8 -*-
"""Occurrence filters."""
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models as geo_models

import django_filters

from occurrence import models as occ_models
from taxonomy import models as tax_models
from taxonomy import widgets as tax_widgets
from wastd.users import widgets as usr_widgets
from shared.filters import FILTER_OVERRIDES


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
        filter_overrides = FILTER_OVERRIDES


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
        filter_overrides = FILTER_OVERRIDES
