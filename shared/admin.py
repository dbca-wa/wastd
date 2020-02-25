# -*- coding: utf-8 -*-
"""Shared admin."""
from __future__ import unicode_literals

from django.contrib.gis.db import models as geo_models
from django.utils.translation import ugettext_lazy as _

from django_fsm_log.admin import StateLogInline
from leaflet.forms.widgets import LeafletWidget
from reversion.admin import VersionAdmin


# Fix collapsing widget width
# https://github.com/applegrew/django-select2/issues/252
S2ATTRS = {'data-width': '50em'}

LEAFLET_WIDGET_ATTRS = {
    'map_height': '500px',
    'map_width': '100%',
    'display_raw': 'true',
    'map_srid': 4326,
}
LEAFLET_SETTINGS = {'widget': LeafletWidget(attrs=LEAFLET_WIDGET_ATTRS)}

FORMFIELD_OVERRIDES = {
    geo_models.PointField: LEAFLET_SETTINGS,
    geo_models.MultiPointField: LEAFLET_SETTINGS,
    geo_models.LineStringField: LEAFLET_SETTINGS,
    geo_models.MultiLineStringField: LEAFLET_SETTINGS,
    geo_models.PolygonField: LEAFLET_SETTINGS,
    geo_models.MultiPolygonField: LEAFLET_SETTINGS,
}


class CustomStateLogInline(StateLogInline):
    """Custom StateLogInline."""

    classes = ('grp-collapse', 'grp-closed', 'wide', 'extrapretty', )
    sortable_field_name = "timestamp"


class CodeLabelDescriptionAdmin(VersionAdmin):
    """VersionAdmin for CodeLabelDescriptionMixin models."""

    # Change list
    list_display = ["code", "label", "description", ]
    search_fields = ("code", "label", "description",)

    # Change view
    formfield_overrides = FORMFIELD_OVERRIDES
    prepopulated_fields = {"code": ("label",)}

    fieldsets = (
        (_('Details'), {
            'classes': ('grp-collapse', 'grp-open', 'wide', 'extrapretty'),
            'fields': ("label", "description", "code")}
         ),
    )
