# -*- coding: utf-8 -*-
"""Admin module for occurrence."""
from __future__ import absolute_import, unicode_literals

from django import forms
# import floppyforms as ff
from django.contrib import admin
from django.contrib.gis.db import models as geo_models
from django.utils.translation import ugettext_lazy as _
from easy_select2 import select2_modelform as s2form
# from django_select2.forms import HeavySelect2MultipleWidget
from django_select2.forms import ModelSelect2Widget

# from ajax_select.fields import (
# AutoCompleteSelectField, AutoCompleteSelectMultipleField)
# from easy_select2.widgets import Select2
from fsm_admin.mixins import FSMTransitionMixin
from reversion.admin import VersionAdmin
from leaflet.forms.widgets import LeafletWidget

from occurrence.models import (
    AreaEncounter,
    CommunityAreaEncounter,
    TaxonAreaEncounter,
    # ObservationGroup,
    AssociatedSpeciesObservation,
    FireHistoryObservation
)

from shared.admin import CustomStateLogInline
from taxonomy.models import Community, Taxon  # noqa
from occurrence.forms import (
    TaxonAreaEncounterForm,
    AssociatedSpeciesObservationForm,
    FireHistoryObservationForm
)


# Select2Widget forms
S2ATTRS = {'width': '350px'}
AreaForm = s2form(AreaEncounter, attrs=S2ATTRS)
TaxonAreaForm = s2form(TaxonAreaEncounter, attrs=S2ATTRS)
CommunityAreaForm = s2form(CommunityAreaEncounter, attrs=S2ATTRS)

LEAFLET_SETTINGS = {
    'widget': LeafletWidget(attrs={
        'map_height': '400px',
        'map_width': '100%',
        'display_raw': 'true',
        'map_srid': 4326, })}

TAXON_SETTINGS = {
    'widget': ModelSelect2Widget(
        model=Taxon,
        search_fields=["taxonomic_name__icontains", "vernacular_names__icontains", ]
    ),
}

FORMFIELD_OVERRIDES = {
    geo_models.PointField: LEAFLET_SETTINGS,
    geo_models.LineStringField: LEAFLET_SETTINGS,
    geo_models.PolygonField: LEAFLET_SETTINGS,
}


class AssociatedSpeciesObservationInline(admin.TabularInline):
    """Associated Species Observation Inline."""

    extra = 1
    # max_num = 1  # limit max number
    model = AssociatedSpeciesObservation
    form = AssociatedSpeciesObservationForm
    classes = ('grp-collapse grp-open',)


class FireHistoryObservationInline(admin.TabularInline):
    """FireHistoryObservation Inline."""

    extra = 1
    # max_num = 1  # limit max number
    model = FireHistoryObservation
    form = FireHistoryObservationForm
    classes = ('grp-collapse grp-open',)


# @admin.register(AreaEncounter)
class AreaEncounterAdmin(FSMTransitionMixin, VersionAdmin):
    """Admin for Area."""

    date_hierarchy = 'encountered_on'
    form = AreaForm
    inlines = [CustomStateLogInline, ]
    list_display = ["area_type", "code", "name", "source", "source_id", ]
    list_filter = ["area_type", "source", ]
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
    formfield_overrides = FORMFIELD_OVERRIDES


@admin.register(TaxonAreaEncounter)
class TaxonAreaAdmin(AreaEncounterAdmin):
    """Admin for TaxonArea."""

    form = TaxonAreaEncounterForm
    list_display = AreaEncounterAdmin.list_display + ["taxon"]
    list_filter = AreaEncounterAdmin.list_filter + ["taxon"]
    list_select_related = ["taxon"]
    # fieldsets = ((_('Taxon'), {
    #     'classes': ('grp-collapse', 'grp-open', 'wide', 'extrapretty'),
    #     'fields': ("taxon", )}
    # ),) + AreaEncounterAdmin.fieldsets
    inlines = [
        # AssociatedSpeciesObservationInline,
        FireHistoryObservationInline
    ]


@admin.register(CommunityAreaEncounter)
class CommunityAreaAdmin(AreaEncounterAdmin):
    """Admin for CommunityArea."""

    form = CommunityAreaForm
    list_display = AreaEncounterAdmin.list_display + ["community"]
    list_filter = AreaEncounterAdmin.list_filter + ["community"]
    list_select_related = ["community"]
    fieldsets = ((_('Community'), {
        'classes': ('grp-collapse', 'grp-open', 'wide', 'extrapretty'),
        'fields': ("community", )}
    ),) + AreaEncounterAdmin.fieldsets
    inlines = [
        AssociatedSpeciesObservationInline,
        FireHistoryObservationInline
    ]


@admin.register(AssociatedSpeciesObservation)
class AssociatedSpeciesObservationAdmin(FSMTransitionMixin, VersionAdmin):
    """Associated Species Observation Admin."""

    list_display = ["encounter", "taxon", ]
    # list_select_related = ObservationGroupAdmin.list_select_related + ["taxon", ]
    form = AssociatedSpeciesObservationForm
    fsm_field = ['status', ]
    taxon = forms.ChoiceField(
        widget=ModelSelect2Widget(
            model=Taxon,
            search_fields=["taxonomic_name__icontains", "vernacular_names__icontains", ]
        )
    )


@admin.register(FireHistoryObservation)
class FireHistoryObservationAdmin(FSMTransitionMixin, VersionAdmin):
    """FireHistoryObservation Admin."""

    list_display = ["encounter", "last_fire_date", "fire_intensity"]
    # list_select_related = ObservationGroupAdmin.list_select_related + ["taxon", ]
    form = FireHistoryObservationForm
    fsm_field = ['status', ]
