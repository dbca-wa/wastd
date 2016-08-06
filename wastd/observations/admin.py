# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# from django import forms
from django.contrib import admin
from django.contrib.gis import forms
from wastd.widgets import MapWidget
from django.contrib.gis.db import models as geo_models
from easy_select2 import select2_modelform
from .models import (Encounter, AnimalEncounter, MediaAttachment,
                     FlipperTagObservation, DisposalObservation,
                     TurtleMorphometricObservation, DistinguishingFeatureObservation)
from fsm_admin.mixins import FSMTransitionMixin


class MediaAttachmentInline(admin.TabularInline):
    """TabularInlineAdmin for MediaAttachment."""

    extra = 0
    model = MediaAttachment


class DistinguishingFeaturesInline(admin.TabularInline):
    """Admin for DistinguishingFeatures."""

    extra = 0
    model = DistinguishingFeatureObservation


class TurtleMorphometricObservationInline(admin.TabularInline):
    """Admin for TurtleMorphometricObservation."""

    extra = 0
    model = TurtleMorphometricObservation


class DisposalObservationInline(admin.TabularInline):
    """TabularInlineAdmin for DisposalObservation."""

    extra = 0
    model = DisposalObservation


class FlipperTagObservationInline(admin.TabularInline):
    """TabularInlineAdmin for TagObservation."""

    extra = 0
    model = FlipperTagObservation


@admin.register(FlipperTagObservation)
class FlipperTagObservationAdmin(admin.ModelAdmin):
    """Admin for FlipperTagObservation"""

    save_on_top = True
    list_display = ('name', 'side', 'position', 'status_display', 'encounter', 'comments')
    list_filter = ('side', 'position', 'status')
    search_fields = ('name', 'comments')

    def status_display(self, obj):
        """Make health status human readable."""
        return obj.get_status_display()
    status_display.short_description = 'Status'


@admin.register(Encounter)
class EncounterAdmin(FSMTransitionMixin, admin.ModelAdmin):
    """Admin for Encounter with inline for MediaAttachment."""

    date_hierarchy = 'when'
    formfield_overrides = {geo_models.PointField: {'widget': MapWidget}}
    list_filter = ('status', 'who', )
    list_display = ('when', 'wkt', 'who', 'status', )
    list_select_related = True
    save_on_top = True
    search_fields = ('who', )
    fsm_field = ['status', ]
    fieldsets = (('Encounter', {'fields': ('when', 'where', 'who')}),)
    inlines = [DistinguishingFeaturesInline,
               TurtleMorphometricObservationInline,
               FlipperTagObservationInline,
               DisposalObservationInline,
               MediaAttachmentInline, ]


@admin.register(AnimalEncounter)
class AnimalEncounterAdmin(FSMTransitionMixin, admin.ModelAdmin):
    """Admin for AnimalEncounter with inlines for TurtleMorphometrics."""

    date_hierarchy = 'when'
    formfield_overrides = {geo_models.PointField: {'widget': MapWidget}}
    list_display = ('when', 'wkt', 'who', 'species', 'health_display',
                    'maturity_display', 'sex_display', 'behaviour', 'status', )
    list_filter = ('status', 'who', 'species', 'health', 'maturity', 'sex', )
    list_select_related = True
    save_on_top = True
    fsm_field = ['status', ]
    search_fields = ('who__name', 'who__username', 'behaviour')
    fieldsets = EncounterAdmin.fieldsets + (
        ('Animal',
         {'fields': ('species', 'health', 'maturity', 'sex', 'behaviour', )}),
        )
    inlines = [DistinguishingFeaturesInline,
               TurtleMorphometricObservationInline,
               FlipperTagObservationInline,
               DisposalObservationInline,
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
