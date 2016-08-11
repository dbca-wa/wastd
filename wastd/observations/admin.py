# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# from django import forms as django_forms
from django.contrib import admin
# from django.contrib.gis import forms
from django.contrib.gis.db import models as geo_models
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _
from easy_select2 import select2_modelform  # select2_modelform_meta
# from easy_select2.widgets import Select2
from fsm_admin.mixins import FSMTransitionMixin

from wastd.widgets import MapWidget
from .models import (Encounter, TurtleNestEncounter,
                     AnimalEncounter,  # TurtleEncounter, CetaceanEncounter,
                     MediaAttachment, TagObservation, ManagementAction,
                     TurtleMorphometricObservation, DistinguishingFeatureObservation,
                     TurtleNestObservation, TurtleDamageObservation)


class ObservationTypeListFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('observation type')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'observation_type'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('stranding', _('stranding')),
            ('nesting', _('nesting')),
            )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'stranding':
            return queryset.exclude(health='alive')
        if self.value() == 'nesting':
            return queryset.filter(health='alive')


class MediaAttachmentInline(admin.TabularInline):
    """TabularInlineAdmin for MediaAttachment."""

    extra = 0
    model = MediaAttachment
    classes = ('grp-collapse grp-open',)


class DistinguishingFeaturesInline(admin.TabularInline):
    """Admin for DistinguishingFeatures."""

    extra = 0
    model = DistinguishingFeatureObservation
    classes = ('grp-collapse grp-open',)


class TurtleMorphometricObservationInline(admin.TabularInline):
    """Admin for TurtleMorphometricObservation."""

    extra = 0
    model = TurtleMorphometricObservation
    classes = ('grp-collapse grp-open',)


class ManagementActionInline(admin.TabularInline):
    """TabularInlineAdmin for ManagementAction."""

    extra = 0
    model = ManagementAction
    classes = ('grp-collapse grp-open',)


class TurtleNestObservationInline(admin.TabularInline):
    """Admin for TurtleNestObservation."""

    extra = 0
    model = TurtleNestObservation
    classes = ('grp-collapse grp-open',)


class TurtleDamageObservationInline(admin.TabularInline):
    """Admin for TurtleDamageObservation."""

    extra = 0
    model = TurtleDamageObservation
    classes = ('grp-collapse grp-open',)


class TagObservationInline(admin.TabularInline):
    """TabularInlineAdmin for TagObservation."""

    extra = 0
    model = TagObservation
    classes = ('grp-collapse grp-open',)


@admin.register(TagObservation)
class TagObservationAdmin(admin.ModelAdmin):
    """Admin for TagObservation"""

    save_on_top = True
    list_display = ('type_display', 'name', 'side_display', 'position_display',
                    'status_display', 'encounter', 'comments')
    list_filter = ('side', 'position', 'status')
    search_fields = ('name', 'comments')

    def type_display(self, obj):
        """Make tag type human readable."""
        return obj.get_tag_type_display()
    type_display.short_description = 'Tag Type'

    def side_display(self, obj):
        """Make tag side human readable."""
        return obj.get_side_display()
    side_display.short_description = 'Tag Side'

    def position_display(self, obj):
        """Make tag position human readable."""
        return obj.get_position_display()
    position_display.short_description = 'Tag Position'

    def status_display(self, obj):
        """Make health status human readable."""
        return obj.get_status_display()
    status_display.short_description = 'Status'


EncounterAdminForm = select2_modelform(Encounter, attrs={'width': '350px'})

@admin.register(Encounter)
class EncounterAdmin(FSMTransitionMixin, admin.ModelAdmin):
    """Admin for Encounter with inline for MediaAttachment."""

    # Grappelli User lookup overrides select2 select widget
    raw_id_fields = ('who', )
    autocomplete_lookup_fields = {'fk': ['who'], }

    # select2 widgets for searchable dropdowns
    form = EncounterAdminForm

    date_hierarchy = 'when'
    formfield_overrides = {geo_models.PointField: {'widget': MapWidget}}
    list_filter = ('status', 'who', )
    list_display = ('when', 'wkt', 'who', 'status', )
    list_select_related = True
    save_on_top = True
    search_fields = ('who', )
    fsm_field = ['status', ]
    fieldsets = (('Encounter', {'fields': ('where', 'location_accuracy',
                                           'when', 'who')}),)
    inlines = [DistinguishingFeaturesInline,
               TurtleMorphometricObservationInline,
               TurtleNestObservationInline,
               TurtleDamageObservationInline,
               TagObservationInline,
               ManagementActionInline,
               MediaAttachmentInline, ]


TurtleNestEncounterAdminForm = select2_modelform(TurtleNestEncounter,
                                                 attrs={'width': '350px'})


@admin.register(TurtleNestEncounter)
class TurtleNestEncounterAdmin(FSMTransitionMixin, admin.ModelAdmin):
    """Admin for TurtleNestEncounter."""

    raw_id_fields = ('who', )
    autocomplete_lookup_fields = {'fk': ['who'], }
    form = TurtleNestEncounterAdminForm
    date_hierarchy = 'when'
    formfield_overrides = {geo_models.PointField: {'widget': MapWidget}}
    list_display = ('when', 'wkt', 'who', 'species', 'habitat_display', )
    list_filter = ('status', 'who', 'species', 'habitat', )
    list_select_related = True
    save_on_top = True
    fsm_field = ['status', ]
    search_fields = ('who__name', 'who__username', )
    fieldsets = EncounterAdmin.fieldsets + (
        ('Nest',
         {'fields': ('species', 'habitat', )}),
        )
    inlines = [TurtleNestObservationInline,
               TagObservationInline,
               MediaAttachmentInline, ]

    def habitat_display(self, obj):
        """Make habitat human readable."""
        return obj.get_habitat_display()
    habitat_display.short_description = 'Habitat'

    def age_display(self, obj):
        """Make nest age human readable."""
        return obj.get_nest_age_display()
    age_display.short_description = 'Nest age'


AnimalEncounterForm = select2_modelform(AnimalEncounter,
                                        attrs={'width': '350px'})


@admin.register(AnimalEncounter)
class AnimalEncounterAdmin(FSMTransitionMixin, admin.ModelAdmin):
    """Admin for AnimalEncounter."""

    raw_id_fields = ('who', )
    autocomplete_lookup_fields = {'fk': ['who'], }
    form = AnimalEncounterForm
    date_hierarchy = 'when'
    formfield_overrides = {geo_models.PointField: {'widget': MapWidget}}
    list_display = ('when', 'wkt', 'who', 'species', 'health_display',
                    'maturity_display', 'sex_display', 'behaviour',
                    'habitat_display', 'status_display', )
    list_filter = (ObservationTypeListFilter,
                   'status', 'who', 'taxon', 'species', 'health', 'maturity',
                   'sex', 'habitat')
    list_select_related = True
    save_on_top = True
    fsm_field = ['status', ]
    search_fields = ('who__name', 'who__username', 'behaviour')
    fieldsets = EncounterAdmin.fieldsets + (
        ('Animal',
         {'fields': ('taxon', 'species', 'health', 'maturity', 'sex',
                     'activity', 'behaviour', 'habitat', )}),
        )
    inlines = [DistinguishingFeaturesInline,
               TurtleDamageObservationInline,
               TurtleMorphometricObservationInline,
               TurtleNestObservationInline,
               ManagementActionInline,
               TagObservationInline,
               MediaAttachmentInline, ]

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
        """Make health status human readable."""
        return obj.get_status_display()
    status_display.short_description = 'Status'

    def habitat_display(self, obj):
        """Make habitat human readable."""
        return obj.get_habitat_display()
    habitat_display.short_description = 'Habitat'
