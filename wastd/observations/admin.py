# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# from django import forms
from django.contrib import admin
from .models import (Observation, StrandingObservation, TurtleStrandingObservation,
                     DistinguishingFeature, MediaAttachment)


@admin.register(DistinguishingFeature)
class DistinguishingFeaturesAdmin(admin.ModelAdmin):
    """Admin for DistinguishingFeatures."""

    list_display = ('name', 'description')


class MediaAttachmentInline(admin.TabularInline):
    """TabularInlineAdmin for MediaAttachment."""

    model = MediaAttachment


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    """Admin for Observation with inline for MediaAttachment."""
    date_hierarchy = 'when'
    list_filter = ('who', )
    # form = MyUserChangeForm
    # add_form = MyUserCreationForm
    fieldsets = (
        ('Observation', {'fields': ('when', 'where', 'who')}),)
    inlines = [MediaAttachmentInline, ]


@admin.register(StrandingObservation)
class StrandingObservationAdmin(admin.ModelAdmin):
    """Admin for StrandingObservation with inline for TurtleMorphometrics."""

    date_hierarchy = 'when'
    list_filter = ('who', 'species', 'health', )
    filter_horizontal = ['features', ]
    fieldsets = ObservationAdmin.fieldsets + (
        ('Animal', {'fields': ('species', 'health', 'behaviour', 'features')}),
        ('Actions', {'fields': ('management_actions', 'comments',)}),
        )
    list_display = ('when', 'wkt', 'species', 'health_display')
    inlines = [MediaAttachmentInline, ]

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
    inlines = [MediaAttachmentInline, ]
