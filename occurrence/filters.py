# -*- coding: utf-8 -*-
"""Occurrence filters."""
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models as geo_models
from django.db import models
# from django_filters.filters import BooleanFilter, ModelMultipleChoiceFilter
# from django_filters.widgets import BooleanWidget
from django_select2.forms import ModelSelect2Widget

import django_filters
from leaflet.forms.widgets import LeafletWidget

from occurrence import models as occ_models
from taxonomy import models as tax_models
from shared.admin import LEAFLET_SETTINGS


FILTER_OVERRIDES = {
    models.CharField: {
        'filter_class': django_filters.CharFilter,
        'extra': lambda f: {'lookup_expr': 'icontains', },
    },
    models.TextField: {
        'filter_class': django_filters.CharFilter,
        'extra': lambda f: {'lookup_expr': 'icontains', },
    },
    geo_models.PointField: {
        'filter_class': django_filters.CharFilter,
        'extra': lambda f: {'lookup_expr': 'intersects',
                            'widget': LeafletWidget(attrs=LEAFLET_SETTINGS)},
    },
    geo_models.PolygonField: {
        'filter_class': django_filters.CharFilter,
        'extra': lambda f: {'lookup_expr': 'intersects',
                            'widget': LeafletWidget(attrs=LEAFLET_SETTINGS)},
    },
    geo_models.MultiPolygonField: {
        'filter_class': django_filters.CharFilter,
        'extra': lambda f: {'lookup_expr': 'intersects',
                            'widget': LeafletWidget(attrs=LEAFLET_SETTINGS)},
    }
}


class TaxonAreaEncounterFilter(django_filters.FilterSet):
    """Filter for TaxonAreaEncounter."""

    # geom = geo_models.PolygonField()
    # point = geo_models.PointField()
    taxon = django_filters.ModelChoiceFilter(
        queryset=tax_models.Taxon.objects.all(),
        # values(
        #     "taxonomic_name",
        #     "vernacular_names",),
        widget=ModelSelect2Widget(
            model=tax_models.Taxon,
            search_fields=[
                "taxonomic_name__icontains",
                "vernacular_names__icontains",
                "field_code__icontains"
            ]
        )
    )
    encountered_by = django_filters.ModelChoiceFilter(
        queryset=get_user_model().objects.all(),
        widget=ModelSelect2Widget(
            model=get_user_model(),
            search_fields=["name__icontains",
                           "username__icontains",
                           "role__icontains",
                           "email__icontains"
                           ]
        )
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
        widget=ModelSelect2Widget(
            model=tax_models.Community,
            search_fields=[
                "code__icontains",
                "name__icontains",
                "description__icontains",
            ]
        )
    )
    encountered_by = django_filters.ModelChoiceFilter(
        queryset=get_user_model().objects.all(),
        widget=ModelSelect2Widget(
            model=get_user_model(),
            search_fields=["name__icontains",
                           "username__icontains",
                           "role__icontains",
                           "email__icontains"
                           ]
        )
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
