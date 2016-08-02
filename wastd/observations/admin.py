# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# from django import forms
from django.contrib import admin
from django.contrib.gis import forms
from wastd.widgets import MapWidget
from django.contrib.gis.db import models as geo_models
from easy_select2 import select2_modelform
from .models import (Observation,
                     StrandingObservation, TurtleStrandingObservation,
                     TagObservation,
                     DistinguishingFeature, MediaAttachment)


@admin.register(DistinguishingFeature)
class DistinguishingFeaturesAdmin(admin.ModelAdmin):
    """Admin for DistinguishingFeatures."""

    list_display = ('name', 'description')


class MediaAttachmentInline(admin.TabularInline):
    """TabularInlineAdmin for MediaAttachment."""

    model = MediaAttachment


class TagObservationInline(admin.TabularInline):
    """TabularInlineAdmin for TagObservation."""

    model = TagObservation


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    """Admin for Observation with inline for MediaAttachment."""

    date_hierarchy = 'when'
    list_filter = ('who', )
    formfield_overrides = {geo_models.PointField: {'widget': forms.OSMWidget}}
    fieldsets = (
        ('Observation', {'fields': ('when', 'where', 'who')}),)
    inlines = [TagObservationInline, MediaAttachmentInline, ]


@admin.register(StrandingObservation)
class StrandingObservationAdmin(admin.ModelAdmin):
    """Admin for StrandingObservation with inline for TurtleMorphometrics."""

    date_hierarchy = 'when'
    list_filter = ('who', 'species', 'health', )
    filter_horizontal = ['features', ]
    formfield_overrides = {geo_models.PointField: {
        'widget': forms.OpenLayersWidget(
            attrs={'display_raw': True, 'mouse_position': True, }
        )}}
    fieldsets = ObservationAdmin.fieldsets + (
        ('Animal', {'fields': ('species', 'health', 'behaviour', 'features')}),
        ('Actions', {'fields': ('management_actions', 'comments',)}),
        )
    list_display = ('when', 'wkt', 'species', 'health_display')
    inlines = [TagObservationInline, MediaAttachmentInline, ]

    def health_display(self, obj):
        """Make health status human readable."""
        return obj.get_health_display()
    health_display.short_description = 'Health status'


@admin.register(TurtleStrandingObservation)
class TurtleStrandingObservationAdmin(admin.ModelAdmin):
    """Admin for TurtleStrandingObservations."""

    date_hierarchy = 'when'
    list_filter = ('who', 'species', 'health', )
    filter_horizontal = ['features', ]
    formfield_overrides = {geo_models.PointField: {'widget': MapWidget}}
    fieldsets = ObservationAdmin.fieldsets + (
        ('Animal', {'fields': (
            'species', 'health', 'behaviour', 'features', 'sex', 'maturity',
            )}),
        ('Morphometrics', {'fields': (
            ('curved_carapace_length_mm', 'curved_carapace_length_accuracy',),
            ('curved_carapace_width_mm', 'curved_carapace_width_accuracy',),
            ('tail_length_mm', 'tail_length_accuracy',),
            ('maximum_head_width_mm', 'maximum_head_width_accuracy',),
            )}),
        ('Actions', {'fields': ('management_actions', 'comments',)}),
        )
    list_display = ('when', 'wkt', 'species', 'get_health_display')
    inlines = [TagObservationInline, MediaAttachmentInline, ]
