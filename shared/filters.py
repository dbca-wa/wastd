# -*- coding: utf-8 -*-
"""Shared filter utilities."""
from django.contrib.gis.db import models as geo_models
from django.db import models

import django_filters
from leaflet.forms.widgets import LeafletWidget

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
