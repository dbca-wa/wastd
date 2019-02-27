# -*- coding: utf-8 -*-
"""Shared admin."""
from __future__ import unicode_literals

from django.contrib.gis.db import models as geo_models

from django_fsm_log.admin import StateLogInline
from leaflet.forms.widgets import LeafletWidget

# Fix collapsing widget width
# https://github.com/applegrew/django-select2/issues/252
S2ATTRS = {'data-width': '50em'}

LEAFLET_SETTINGS = {
    'widget': LeafletWidget(attrs={
        'map_height': '400px',
        'map_width': '100%',
        'display_raw': 'true',
        'map_srid': 4326,
    })}

FORMFIELD_OVERRIDES = {
    geo_models.PointField: LEAFLET_SETTINGS,
    geo_models.LineStringField: LEAFLET_SETTINGS,
    geo_models.PolygonField: LEAFLET_SETTINGS,
    geo_models.MultiPolygonField: LEAFLET_SETTINGS,
}


class CustomStateLogInline(StateLogInline):
    """Custom StateLogInline."""

    classes = ('grp-collapse', 'grp-closed', 'wide', 'extrapretty', )
