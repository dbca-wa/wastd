# -*- coding: utf-8 -*-
"""Shared filter utilities."""
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models as geo_models
from django.db import models

import django_filters
from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget
from leaflet.forms.widgets import LeafletWidget

from shared.admin import LEAFLET_SETTINGS
from taxonomy import models as tax_models

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


class UserWidget(ModelSelect2Widget):
    """User widget."""

    model = get_user_model()
    queryset = get_user_model().objects.all()
    search_fields = [
        "name__icontains",
        "username__icontains",
        "role__icontains",
        "email__icontains"
    ]


class TaxonWidget(ModelSelect2Widget):
    """A reusable Taxon ModelSelect2Widget."""

    model = tax_models.Taxon
    search_fields = [
        "taxonomic_name__icontains",
        "vernacular_names__icontains",
        "field_code__icontains"
    ]


class TaxonMultipleWidget(ModelSelect2MultipleWidget):
    """A reusable Taxon ModelSelect2MultipleWidget."""

    model = tax_models.Taxon
    search_fields = [
        "taxonomic_name__icontains",
        "vernacular_names__icontains",
        "field_code__icontains"
    ]


class CommunityWidget(ModelSelect2Widget):
    """Community Widget."""

    model = tax_models.Community
    search_fields = [
        "code__icontains",
        "name__icontains",
        "description__icontains",
    ]


class TaxonFilter(django_filters.ModelChoiceFilter):
    """A reusable ModelChoiceFilter for Taxon."""

    queryset = tax_models.Taxon.objects.all()
    model = tax_models.Taxon
    widget = TaxonWidget()


# class TaxonMultipleWidget(ModelSelect2MultipleWidget):
#     """A reusable Taxon ModelSelect2MultipleWidget."""

#     pass
