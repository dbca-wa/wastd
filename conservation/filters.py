# -*- coding: utf-8 -*-
"""Conservation filters."""
import django_filters
from conservation.models import ConservationAction
from django.contrib.gis.db import models as geo_models
from django.db import models
from django_filters.filters import BooleanFilter, ModelMultipleChoiceFilter
from django_filters.widgets import BooleanWidget
from leaflet.forms.widgets import LeafletWidget


FILTER_OVERRIDES = {
    models.CharField: {
        'filter_class': django_filters.CharFilter,
        'extra': lambda f: {'lookup_expr': 'icontains', },
    },
    models.TextField: {
        'filter_class': django_filters.CharFilter,
        'extra': lambda f: {'lookup_expr': 'icontains', },
    },
    geo_models.PolygonField: {
        'filter_class': django_filters.CharFilter,
        'extra': lambda f: {'lookup_expr': 'intersects',
                            'widget': LeafletWidget()},
    },
    geo_models.MultiPolygonField: {
        'filter_class': django_filters.CharFilter,
        'extra': lambda f: {'lookup_expr': 'intersects',
                            'widget': LeafletWidget()},
    }
}


class ConservationActionFilter(django_filters.FilterSet):
    """Filter for ConservationAction."""

    target_area = geo_models.PolygonField()

    class Meta:
        """Class opts."""

        model = ConservationAction
        fields = ['target_area', 'category', ]
        # widgets = {'eoo': LeafletWidget()}
        filter_overrides = FILTER_OVERRIDES
