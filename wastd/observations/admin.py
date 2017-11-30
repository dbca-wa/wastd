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
    Area,
    Expedition,
    SiteVisit,
    Survey,
    FieldMediaAttachment,
    Encounter,
    TurtleNestEncounter,
    AnimalEncounter,
    LoggerEncounter,
    LineTransectEncounter,
    MediaAttachment,
    TagObservation,
    NestTagObservation,
    ManagementAction,
    TrackTallyObservation,
    TurtleNestDisturbanceTallyObservation,
    TurtleMorphometricObservation,
    HatchlingMorphometricObservation,
    DugongMorphometricObservation,
    TurtleDamageObservation,
    TurtleNestObservation,
    TurtleNestDisturbanceObservation,
    TemperatureLoggerSettings,
    DispatchRecord,
    TemperatureLoggerDeployment)
from wastd.observations.filters import LocationListFilter
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


class NestTagObservationInline(admin.TabularInline):
    """TabularInlineAdmin for NestTagObservation."""

    extra = 0
    model = NestTagObservation
    classes = ('grp-collapse grp-open',)


class TurtleMorphometricObservationInline(admin.StackedInline):
    """Admin for TurtleMorphometricObservation."""

    extra = 0
    model = TurtleMorphometricObservation
    classes = ('grp-collapse grp-open',)


class HatchlingMorphometricObservationInline(admin.TabularInline):
    """Admin for HatchlingMorphometricObservation."""

    extra = 0
    model = HatchlingMorphometricObservation
    classes = ('grp-collapse grp-open',)


class DugongMorphometricObservationInline(admin.TabularInline):
    """Admin for DugongMorphometricObservation."""

    extra = 0
    model = DugongMorphometricObservation
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


class TurtleNestDisturbanceTallyObservationInline(admin.TabularInline):
    """Admin for TurtleNestDisturbanceTallyObservation."""

    extra = 0
    model = TurtleNestDisturbanceTallyObservation
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


@admin.register(NestTagObservation)
class NestTagObservationAdmin(VersionAdmin, admin.ModelAdmin):
    """Admin for NestTagObservation"""
    save_on_top = True
    date_hierarchy = 'date_nest_laid'
    list_display = ('tag_name', 'flipper_tag_id', 'date_nest_laid', 'tag_label',
                    'status_display', 'encounter_link', 'comments')
    list_filter = ('flipper_tag_id', 'tag_label', 'status')
    search_fields = ('flipper_tag_id', 'date_nest_laid', 'tag_label', 'comments')

    def tag_name(self, obj):
        """Nest tag name."""
        return obj.name
    tag_name.short_description = 'Nest Tag ID'

    def status_display(self, obj):
        """Make health status human readable."""
        return obj.get_status_display()
    status_display.short_description = 'Status'

    def encounter_link(self, obj):
        """A link to the encounter."""
        return '<a href="{0}">{1}</a>'.format(obj.encounter.absolute_admin_url,
                                              obj.encounter.__str__())
    encounter_link.short_description = 'Encounter'
    encounter_link.allow_tags = True


# Select2Widget forms
S2ATTRS = {'width': '350px'}
ExpeditionForm = s2form(Expedition, attrs=S2ATTRS)
SiteVisitForm = s2form(SiteVisit, attrs=S2ATTRS)
EncounterAdminForm = s2form(Encounter, attrs=S2ATTRS)
AnimalEncounterForm = s2form(AnimalEncounter, attrs=S2ATTRS)
TurtleNestEncounterAdminForm = s2form(TurtleNestEncounter, attrs=S2ATTRS)
LineTransectEncounterAdminForm = s2form(LineTransectEncounter, attrs=S2ATTRS)
LoggerEncounterAdminForm = s2form(LoggerEncounter, attrs=S2ATTRS)
leaflet_settings = {
    'widget': LeafletWidget(attrs={
        'map_height': '400px',
        'map_width': '100%',
        'display_raw': 'true',
        'map_srid': 4326, })}


class FieldMediaAttachmentInline(admin.TabularInline):
    """TabularInlineAdmin for FieldMediaAttachment."""

    extra = 0
    model = FieldMediaAttachment
    classes = ('grp-collapse grp-open',)
    widgets = {'attachment': ImageThumbnailFileInput}  # seems inactive


@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    form = ExpeditionForm
    list_display = ('site', 'started_on', 'finished_on', 'comments')
    date_hierarchy = 'started_on'
    inlines = [FieldMediaAttachmentInline, ]
    # Leaflet geolocation widget
    formfield_overrides = {
        geo_models.PointField: leaflet_settings,
        geo_models.LineStringField: leaflet_settings,
        }


@admin.register(SiteVisit)
class SiteVisitAdmin(ExpeditionAdmin):
    form = SiteVisitForm


@admin.register(Survey)
class SurveyAdmin(VersionAdmin, admin.ModelAdmin):
    form = s2form(Survey, attrs=S2ATTRS)
    # model = Survey
    date_hierarchy = 'start_time'
    list_display = (
        'source',
        'source_id',
        'device_id',
        'site',
        'reporter',
        'start_location',
        'start_time',
        'start_comments',
        'end_source_id',
        'end_location',
        'end_time',
        'end_comments'
    )
    exclude = (
        # 'end_location',
        # 'transect',
        # 'start_location'
        )
    formfield_overrides = {
        geo_models.PointField: leaflet_settings,
        geo_models.LineStringField: leaflet_settings,
        }


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("area_type", "name", "northern_extent", "centroid", )
    list_filter = ("area_type", )
    search_fields = ("name", )

    # Leaflet geolocation widget
    formfield_overrides = {
        geo_models.PolygonField: leaflet_settings,
        }


@admin.register(Encounter)
class EncounterAdmin(FSMTransitionMixin, VersionAdmin, admin.ModelAdmin):
    """Admin for Encounter with inlines for all Observations.

    This admin can be extended by other Encounter Admin classes.
    """

    # Grappelli User lookup overrides select2 select widget
    raw_id_fields = ('site_visit', 'observer', 'reporter')
    autocomplete_lookup_fields = {'fk': ['site_visit', 'observer', 'reporter']}
    change_list_filter_template = "admin/filter_listing.html"

    # select2 widgets for searchable dropdowns
    form = EncounterAdminForm

    # Date filter widget
    date_hierarchy = 'when'

    # Leaflet geolocation widget
    formfield_overrides = {
        geo_models.PointField: leaflet_settings,
        geo_models.LineStringField: leaflet_settings,
        }

    # Filters for change_list
    list_filter = (LocationListFilter,
                   'site_visit', 'status', 'observer', 'reporter',
                   'location_accuracy', 'encounter_type', 'source')

    # Columns for change_list, allow re-use and inserting fields
    FIRST_COLS = ('when', 'site_visit', 'latitude', 'longitude',
                  'location_accuracy', 'name')
    LAST_COLS = ('observer', 'reporter', 'source_display', 'source_id',
                 'status', 'encounter_type')
    list_display = FIRST_COLS + LAST_COLS

    # Performance
    # https://docs.djangoproject.com/en/1.10/ref/contrib/admin/
    # django.contrib.admin.ModelAdmin.list_select_related
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
        'site_visit', 'where', 'location_accuracy', 'when',
        'observer', 'reporter', 'source', 'source_id', )}),)

    # Change_view inlines
    inlines = [
        MediaAttachmentInline,
        TagObservationInline,
        TurtleDamageObservationInline,
        TurtleMorphometricObservationInline,
        TrackTallyObservationInline,
        TurtleNestDisturbanceTallyObservationInline,
        ManagementActionInline,
        NestTagObservationInline,
        TurtleNestObservationInline,
        TurtleNestDisturbanceObservationInline,
        HatchlingMorphometricObservationInline,
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
        'nesting_event',
        'checked_for_injuries',
        'scanned_for_pit_tags',
        'checked_for_flipper_tags',
        ) + EncounterAdmin.LAST_COLS
    list_filter = EncounterAdmin.list_filter + (
        'taxon', 'species',
        'health', 'cause_of_death', 'cause_of_death_confidence',
        'maturity', 'sex', 'habitat',
        'nesting_event',
        'checked_for_injuries',
        'scanned_for_pit_tags',
        'checked_for_flipper_tags', )
    fieldsets = EncounterAdmin.fieldsets + (
        ('Animal',
         {'fields': ('taxon', 'species', 'maturity', 'sex',
                     'activity', 'behaviour', 'habitat',
                     'health', 'cause_of_death', 'cause_of_death_confidence',
                     'nesting_event',
                     'checked_for_injuries',
                     'scanned_for_pit_tags',
                     'checked_for_flipper_tags',)}), )

    # Custom set of inlines excludes some Encounter inlines
    inlines = [
        MediaAttachmentInline,
        TagObservationInline,
        TurtleDamageObservationInline,
        TurtleMorphometricObservationInline,
        DugongMorphometricObservationInline,
        TurtleNestObservationInline,
        ManagementActionInline,
        NestTagObservationInline,
        ]

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
        'age_display', 'type_display', 'species',
        'habitat_display', 'disturbance', 'comments'
        ) + EncounterAdmin.LAST_COLS
    list_filter = EncounterAdmin.list_filter + (
        'nest_age', 'nest_type', 'species', 'habitat', 'disturbance')
    fieldsets = EncounterAdmin.fieldsets + (
        ('Nest', {'fields': (
            'nest_age', 'nest_type', 'species',
            'habitat', 'disturbance', 'comments')}), )

    # Exclude some EncounterAdmin inlines
    inlines = [
        MediaAttachmentInline,
        NestTagObservationInline,
        TurtleNestObservationInline,
        TurtleNestDisturbanceObservationInline,
        HatchlingMorphometricObservationInline,
        ]

    def habitat_display(self, obj):
        """Make habitat human readable."""
        return obj.get_habitat_display()
    habitat_display.short_description = 'Habitat'

    def age_display(self, obj):
        """Make nest age human readable."""
        return obj.get_nest_age_display()
    age_display.short_description = 'Nest age'

    def type_display(self, obj):
        """Make nest type human readable."""
        return obj.get_nest_type_display()
    type_display.short_description = 'Nest type'


@admin.register(LineTransectEncounter)
class LineTransectEncounterAdmin(EncounterAdmin):
    """Admin for LineTransectEncounter."""

    form = LineTransectEncounterAdminForm
    list_display = EncounterAdmin.FIRST_COLS + (
        'transect',
        ) + EncounterAdmin.LAST_COLS
    # list_filter = EncounterAdmin.list_filter + ()
    fieldsets = EncounterAdmin.fieldsets + (
        ('Location', {'fields': ('transect', )}), )

    inlines = [
        TrackTallyObservationInline,
        TurtleNestDisturbanceTallyObservationInline,
        ]


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
        TagObservationInline,
        NestTagObservationInline,
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
