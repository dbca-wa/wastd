# -*- coding: utf-8 -*-
"""Admin module for occurrence."""
from __future__ import absolute_import, unicode_literals

# from django import forms as django_forms
# import floppyforms as ff
from django.contrib import admin
from django.contrib.gis.db import models as geo_models
# from django.contrib.contenttypes.admin import GenericTabularInline
# from django.forms import Textarea
# from django.db import models
from django.utils.translation import ugettext_lazy as _


from easy_select2 import select2_modelform as s2form
# from django_select2.forms import HeavySelect2MultipleWidget
# from ajax_select.fields import (
# AutoCompleteSelectField, AutoCompleteSelectMultipleField)
# from easy_select2.widgets import Select2
from fsm_admin.mixins import FSMTransitionMixin
from leaflet.forms.widgets import LeafletWidget
from reversion.admin import VersionAdmin

from shared.admin import CustomStateLogInline
from occurrence.models import Area, TaxonArea, CommunityArea


# Select2Widget forms
S2ATTRS = {'width': '350px'}
AreaForm = s2form(Area, attrs=S2ATTRS)
TaxonAreaForm = s2form(TaxonArea, attrs=S2ATTRS)
CommunityAreaForm = s2form(CommunityArea, attrs=S2ATTRS)
leaflet_settings = {
    'widget': LeafletWidget(attrs={
        'map_height': '400px',
        'map_width': '100%',
        'display_raw': 'true',
        'map_srid': 4326, })}
formfield_overrides = {
    geo_models.PointField: leaflet_settings,
    geo_models.LineStringField: leaflet_settings,
    geo_models.PolygonField: leaflet_settings,
}


@admin.register(Area)
class AreaAdmin(FSMTransitionMixin, VersionAdmin):
    """Admin for Area."""

    date_hierarchy = 'encountered_on'
    form = AreaForm
    inlines = [CustomStateLogInline, ]
    list_display = ["area_type", "code", "name", "source", "source_id", ]
    list_filter = ["area_type", "source"]
    search_fields = ("code", "name", )
    raw_id_fields = ('encountered_by', )
    fsm_field = ['status', ]
    autocomplete_lookup_fields = {'fk': ['encountered_by', ]}
    fieldsets = (
        (_('Details'), {
            'classes': ('grp-collapse', 'grp-open', 'wide', 'extrapretty'),
            'fields': ("area_type", "code", "name", "description",)}
         ),
        (_('Location'), {
            'classes': ('grp-collapse', 'grp-open', 'wide', 'extrapretty'),
            'fields': ("point", "geom", "accuracy",)}
         ),
        (_('Data lineage'), {
            'classes': ('grp-collapse', 'grp-open', 'wide', 'extrapretty'),
            'fields': ("source", "source_id", "encountered_on", "encountered_by")}
         ),
    )
    # Leaflet geolocation widget
    formfield_overrides = formfield_overrides


@admin.register(TaxonArea)
class TaxonAreaAdmin(AreaAdmin):
    """Admin for TaxonArea."""

    form = TaxonAreaForm
    list_display = AreaAdmin.list_display + ["taxon"]
    list_select_related = ["taxon"]
    fieldsets = ((_('Taxon'), {
        'classes': ('grp-collapse', 'grp-open', 'wide', 'extrapretty'),
        'fields': ("taxon", )}
    ),) + AreaAdmin.fieldsets


@admin.register(CommunityArea)
class CommunityAreaAdmin(AreaAdmin):
    """Admin for CommunityArea."""

    form = CommunityAreaForm
    list_display = AreaAdmin.list_display + ["community"]
    list_select_related = ["community"]
    fieldsets = ((_('Community'), {
        'classes': ('grp-collapse', 'grp-open', 'wide', 'extrapretty'),
        'fields': ("community", )}
    ),) + AreaAdmin.fieldsets
