# -*- coding: utf-8 -*-
"""Admin module for wastd.observations."""
from __future__ import absolute_import, unicode_literals

# from leaflet.admin import LeafletGeoAdmin
from leaflet.forms.widgets import LeafletWidget

# from django import forms as django_forms
import floppyforms as ff
from django.contrib import admin
# from django.contrib.gis import forms
from django.contrib.gis.db import models as geo_models

from django.utils.translation import ugettext_lazy as _
from easy_select2 import select2_modelform as s2form
# from easy_select2.widgets import Select2
from fsm_admin.mixins import FSMTransitionMixin
from reversion.admin import VersionAdmin

from wastd.observations.models import (
    Encounter, TurtleNestEncounter, AnimalEncounter, LoggerEncounter,
    MediaAttachment, TagObservation, ManagementAction, TrackTallyObservation,
    TurtleMorphometricObservation, TurtleDamageObservation,
    TurtleNestObservation, TurtleNestDisturbanceObservation,
    TemperatureLoggerSettings, DispatchRecord, TemperatureLoggerDeployment)

from rest_framework.authtoken.admin import TokenAdmin

TokenAdmin.raw_id_fields = ('user',)


class ImageThumbnailFileInput(ff.ClearableFileInput):
    template_name = 'floppyforms/image_thumbnail.html'


class MediaAttachmentInline(admin.TabularInline):
    """TabularInlineAdmin for MediaAttachment."""

    extra = 0
    model = MediaAttachment
    classes = ('grp-collapse grp-open',)
    widgets = {'attachment': ImageThumbnailFileInput}  # seems inactive


class TagObservationInline(admin.TabularInline):
    """TabularInlineAdmin for TagObservation."""

    extra = 0
    model = TagObservation
    classes = ('grp-collapse grp-open',)


class TurtleMorphometricObservationInline(admin.StackedInline):
    """Admin for TurtleMorphometricObservation."""

    extra = 0
    model = TurtleMorphometricObservation
    classes = ('grp-collapse grp-open',)


class ManagementActionInline(admin.TabularInline):
    """TabularInlineAdmin for ManagementAction."""

    extra = 0
    model = ManagementAction
    classes = ('grp-collapse grp-open',)


class TurtleDamageObservationInline(admin.TabularInline):
    """Admin for TurtleDamageObservation."""

    extra = 0
    model = TurtleDamageObservation
    classes = ('grp-collapse grp-open',)


class TrackTallyObservationInline(admin.TabularInline):
    """Admin for TrackTallyObservation."""

    extra = 0
    model = TrackTallyObservation
    classes = ('grp-collapse grp-open',)


class TurtleNestObservationInline(admin.StackedInline):
    """Admin for TurtleNestObservation."""

    extra = 0
    model = TurtleNestObservation
    classes = ('grp-collapse grp-open',)


class TurtleNestDisturbanceObservationInline(admin.TabularInline):
    """Admin for TurtleNestDisturbanceObservation."""

    extra = 0
    model = TurtleNestDisturbanceObservation
    classes = ('grp-collapse grp-open',)


class TemperatureLoggerSettingsInline(admin.TabularInline):
    """Admin for TemperatureLoggerSettings."""

    extra = 0
    model = TemperatureLoggerSettings
    classes = ('grp-collapse grp-open',)


class DispatchRecordInline(admin.TabularInline):
    """Admin for DispatchRecord."""

    extra = 0
    model = DispatchRecord
    classes = ('grp-collapse grp-open',)


class TemperatureLoggerDeploymentInline(admin.TabularInline):
    """Admin for TemperatureLoggerDeployment."""

    extra = 0
    model = TemperatureLoggerDeployment
    classes = ('grp-collapse grp-open',)


@admin.register(TagObservation)
class TagObservationAdmin(VersionAdmin, admin.ModelAdmin):
    """Admin for TagObservation"""

    save_on_top = True
    # date_hierarchy = 'datetime'
    list_display = ('datetime', 'latitude', 'longitude',
                    'type_display', 'name', 'tag_location_display',
                    'status_display', 'encounter_link', 'comments')
    list_filter = ('tag_type', 'tag_location', 'status')
    search_fields = ('name', 'comments')
    autocomplete_lookup_fields = {'fk': ['handler', 'recorder', ], }

    def type_display(self, obj):
        """Make tag type human readable."""
        return obj.get_tag_type_display()
    type_display.short_description = 'Tag Type'

    def tag_location_display(self, obj):
        """Make tag side human readable."""
        return obj.get_tag_location_display()
    tag_location_display.short_description = 'Tag Location'

    def status_display(self, obj):
        """Make health status human readable."""
        return obj.get_status_display()
    status_display.short_description = 'Status'

    def animal_name(self, obj):
        """Animal name."""
        return obj.encounter.name
    animal_name.short_description = 'Animal Name'

    def encounter_link(self, obj):
        """A link to the encounter."""
        return '<a href="{0}">{1}</a>'.format(obj.encounter.absolute_admin_url,
                                              obj.encounter.__str__())
    encounter_link.short_description = 'Encounter'
    encounter_link.allow_tags = True


# Select2Widget forms
S2ATTRS = {'width': '350px'}
EncounterAdminForm = s2form(Encounter, attrs=S2ATTRS)
AnimalEncounterForm = s2form(AnimalEncounter, attrs=S2ATTRS)
TurtleNestEncounterAdminForm = s2form(TurtleNestEncounter, attrs=S2ATTRS)
LoggerEncounterAdminForm = s2form(LoggerEncounter, attrs=S2ATTRS)


@admin.register(Encounter)
class EncounterAdmin(FSMTransitionMixin, VersionAdmin, admin.ModelAdmin):
    """Admin for Encounter with inlines for all Observations.

    This admin can be extended by other Encounter Admin classes.
    """

    # Grappelli User lookup overrides select2 select widget
    raw_id_fields = ('observer', 'reporter', )
    autocomplete_lookup_fields = {'fk': ['observer', 'reporter', ], }
    change_list_filter_template = "admin/filter_listing.html"

    # select2 widgets for searchable dropdowns
    form = EncounterAdminForm

    # Date filter widget
    date_hierarchy = 'when'

    # Leaflet geolocation widget
    formfield_overrides = {
        geo_models.PointField: {'widget': LeafletWidget(attrs={
            'map_height': '400px',
            'map_width': '100%',
            'display_raw': 'true',
            'map_srid': 4326, })},
        }

    # Filters for change_list
    list_filter = ('status', 'observer', 'reporter',
                   'location_accuracy', 'encounter_type')

    # Columns for change_list, allow re-use and inserting fields
    FIRST_COLS = ('when', 'latitude', 'longitude', 'location_accuracy', 'name')
    LAST_COLS = ('observer', 'reporter', 'source_display', 'source_id',
                 'status', 'encounter_type')
    list_display = FIRST_COLS + LAST_COLS

    # Performance
    # https://docs.djangoproject.com/en/1.10/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_select_related
    list_select_related = True

    # Layout: save buttons also on top - overridden by Grapelli admin skin
    # save_on_top = True

    # Change_list fulltext search fields
    search_fields = ('observer__name', 'observer__username', 'name',
                     'reporter__name', 'reporter__username', 'source_id',)

    # Django-fsm transitions config
    fsm_field = ['status', ]

    # Change_view form layout
    fieldsets = (('Encounter', {'fields': (
        'where', 'location_accuracy', 'when',
        'observer', 'reporter', 'source', 'source_id', )}),)

    # Change_view inlines
    inlines = [
        MediaAttachmentInline,
        TagObservationInline,
        TurtleDamageObservationInline,
        TurtleMorphometricObservationInline,
        TrackTallyObservationInline,
        ManagementActionInline,
        TurtleNestObservationInline,
        TurtleNestDisturbanceObservationInline,
        ]

    def source_display(self, obj):
        """Make data source readable."""
        return obj.get_source_display()
    source_display.short_description = 'Data Source'

    def latitude(self, obj):
        """Make data source readable."""
        return obj.where.get_y()
    latitude.short_description = 'Latitude'

    def longitude(self, obj):
        """Make data source readable."""
        return obj.where.get_x()
    longitude.short_description = 'Longitude'

    def encounter_type_display(self, obj):
        """Make encounter type readable."""
        return obj.get_encounter_type_display()
    encounter_type_display.short_description = 'Encounter Type'


@admin.register(AnimalEncounter)
class AnimalEncounterAdmin(EncounterAdmin):
    """Admin for AnimalEncounter."""

    form = AnimalEncounterForm
    list_display = EncounterAdmin.FIRST_COLS + (
        'species', 'health_display',
        'cause_of_death', 'cause_of_death_confidence',
        'maturity_display', 'sex_display', 'behaviour',
        'habitat_display',
        'checked_for_injuries',
        'scanned_for_pit_tags',
        'checked_for_flipper_tags',
        ) + EncounterAdmin.LAST_COLS
    list_filter = EncounterAdmin.list_filter + (
        'taxon', 'species',
        'health', 'cause_of_death', 'cause_of_death_confidence',
        'maturity', 'sex', 'habitat',
        'checked_for_injuries',
        'scanned_for_pit_tags',
        'checked_for_flipper_tags', )
    fieldsets = EncounterAdmin.fieldsets + (
        ('Animal',
         {'fields': ('taxon', 'species', 'maturity', 'sex',
                     'activity', 'behaviour', 'habitat',
                     'health', 'cause_of_death', 'cause_of_death_confidence',
                     'checked_for_injuries',
                     'scanned_for_pit_tags',
                     'checked_for_flipper_tags',)}), )

    # Custom set of inlines excludes some Encounter inlines
    inlines = [
        MediaAttachmentInline,
        TagObservationInline,
        TurtleDamageObservationInline,
        TurtleMorphometricObservationInline,
        TurtleNestObservationInline,
        ManagementActionInline, ]

    def health_display(self, obj):
        """Make health status human readable."""
        return obj.get_health_display()
    health_display.short_description = 'Health'

    def maturity_display(self, obj):
        """Make maturity human readable."""
        return obj.get_maturity_display()
    maturity_display.short_description = 'Maturity'

    def sex_display(self, obj):
        """Make sex human readable."""
        return obj.get_sex_display()
    sex_display.short_description = 'Sex'

    def status_display(self, obj):
        """Make QA status human readable."""
        return obj.get_status_display()
    status_display.short_description = 'QA Status'

    def habitat_display(self, obj):
        """Make habitat human readable."""
        return obj.get_habitat_display()
    habitat_display.short_description = 'Habitat'


@admin.register(TurtleNestEncounter)
class TurtleNestEncounterAdmin(EncounterAdmin):
    """Admin for TurtleNestEncounter."""

    form = TurtleNestEncounterAdminForm
    list_display = EncounterAdmin.FIRST_COLS + (
        'species', 'age_display', 'habitat_display', 'disturbance'
        ) + EncounterAdmin.LAST_COLS
    list_filter = EncounterAdmin.list_filter + (
        'nest_age', 'species', 'habitat', 'disturbance')
    fieldsets = EncounterAdmin.fieldsets + (
        ('Nest', {'fields': ('nest_age', 'species', 'habitat', 'disturbance')}), )

    # Exclude some EncounterAdmin inlines
    inlines = [
        MediaAttachmentInline,
        TagObservationInline,
        TurtleNestObservationInline,
        TurtleNestDisturbanceObservationInline, ]

    def habitat_display(self, obj):
        """Make habitat human readable."""
        return obj.get_habitat_display()
    habitat_display.short_description = 'Habitat'

    def age_display(self, obj):
        """Make nest age human readable."""
        return obj.get_nest_age_display()
    age_display.short_description = 'Nest age'


@admin.register(LoggerEncounter)
class LoggerEncounterAdmin(EncounterAdmin):
    """Admin for LoggerEncounter."""

    form = LoggerEncounterAdminForm
    list_display = EncounterAdmin.FIRST_COLS + (
        'logger_type_display', 'deployment_status_display',
        'logger_id', 'comments',
        ) + EncounterAdmin.LAST_COLS
    list_filter = EncounterAdmin.list_filter + ('logger_type', 'deployment_status',)
    search_fields = ('logger_id', 'source_id')
    fieldsets = EncounterAdmin.fieldsets + (
        ('Logger', {'fields': (
            'logger_type', 'deployment_status', 'logger_id', 'comments',)}), )

    # Exclude some EncounterAdmin inlines
    inlines = [
        MediaAttachmentInline,
        TemperatureLoggerSettingsInline,
        DispatchRecordInline,
        TemperatureLoggerDeploymentInline, ]

    def logger_type_display(self, obj):
        """Make habitat human readable."""
        return obj.get_logger_type_display()
    logger_type_display.short_description = 'Logger Type'

    def deployment_status_display(self, obj):
        """Make habitat human readable."""
        return obj.get_deployment_status_display()
    deployment_status_display.short_description = 'Deployment Status'
