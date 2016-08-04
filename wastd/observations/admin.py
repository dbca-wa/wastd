# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# from django import forms
from django.contrib import admin
from django.contrib.gis import forms
from wastd.widgets import MapWidget
from django.contrib.gis.db import models as geo_models
from easy_select2 import select2_modelform
from .models import (Encounter, AnimalEncounter, MediaAttachment,
                     TagObservation, DisposalObservation,
                     TurtleMorphometricObservation, DistinguishingFeatureObservation)


class MediaAttachmentInline(admin.TabularInline):
    """TabularInlineAdmin for MediaAttachment."""

    model = MediaAttachment


class DistinguishingFeaturesInline(admin.TabularInline):
    """Admin for DistinguishingFeatures."""

    extra = 1
    model = DistinguishingFeatureObservation


class TurtleMorphometricObservationInline(admin.TabularInline):
    """Admin for TurtleMorphometricObservation."""

    extra = 1
    model = TurtleMorphometricObservation


class DisposalObservationInline(admin.TabularInline):
    """TabularInlineAdmin for DisposalObservation."""

    extra = 1
    model = DisposalObservation


class TagObservationInline(admin.TabularInline):
    """TabularInlineAdmin for TagObservation."""

    extra = 4
    model = TagObservation


@admin.register(Encounter)
class EncounterAdmin(admin.ModelAdmin):
    """Admin for Encounter with inline for MediaAttachment."""

    date_hierarchy = 'when'
    list_filter = ('who', )
    formfield_overrides = {geo_models.PointField: {'widget': forms.OSMWidget}}
    fieldsets = (
        ('Encounter', {'fields': ('when', 'where', 'who')}),)
    inlines = [MediaAttachmentInline, ]


@admin.register(AnimalEncounter)
class AnimalEncounterAdmin(admin.ModelAdmin):
    """Admin for AnimalEncounter with inlines for TurtleMorphometrics."""

    date_hierarchy = 'when'
    list_filter = ('who', 'species', 'health', )
    formfield_overrides = {geo_models.PointField: {'widget': MapWidget}}
    fieldsets = EncounterAdmin.fieldsets + (
        ('Animal', {'fields': ('species', 'health', 'behaviour', 'sex', 'maturity')}),
        )
    list_display = ('when', 'wkt', 'species', 'health_display')
    inlines = [DistinguishingFeaturesInline,
               TurtleMorphometricObservationInline,
               TagObservationInline,
               DisposalObservationInline,
               MediaAttachmentInline, ]

    def health_display(self, obj):
        """Make health status human readable."""
        return obj.get_health_display()
    health_display.short_description = 'Health status'
