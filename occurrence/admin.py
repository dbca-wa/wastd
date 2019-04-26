# -*- coding: utf-8 -*-
"""Admin module for occurrence."""
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from easy_select2 import select2_modelform as s2form
# from django_select2.forms import HeavySelect2MultipleWidget

# from ajax_select.fields import (
# AutoCompleteSelectField, AutoCompleteSelectMultipleField)
# from easy_select2.widgets import Select2
from import_export.admin import ImportExportModelAdmin
from fsm_admin.mixins import FSMTransitionMixin
from reversion.admin import VersionAdmin


from shared.admin import (
    CodeLabelDescriptionAdmin,
    CustomStateLogInline,
    S2ATTRS,
    FORMFIELD_OVERRIDES
)
from taxonomy.models import Community, Taxon  # noqa
from occurrence import models as occ_models
from occurrence import forms as occ_forms
from occurrence import resources as occ_resources


# -----------------------------------------------------------------------------
# HabitatComposition
#
@admin.register(occ_models.Landform)
class LandformAdmin(CodeLabelDescriptionAdmin):
    """Admin for Landform."""

    pass


@admin.register(occ_models.RockType)
class RockTypeAdmin(CodeLabelDescriptionAdmin):
    """Admin for Rock type."""

    pass


@admin.register(occ_models.SoilType)
class SoilTypeAdmin(CodeLabelDescriptionAdmin):
    """Admin for Soil type."""

    pass


@admin.register(occ_models.SoilColour)
class SoilColourAdmin(CodeLabelDescriptionAdmin):
    """Admin for Soil colour."""

    pass


@admin.register(occ_models.HabitatComposition)
class HabitatCompositionAdmin(FSMTransitionMixin, VersionAdmin):
    """HabitatComposition Admin."""

    list_display = [
        "encounter",
        "landform",
        "rock_type",
        "loose_rock_percent",
        "soil_type",
        "soil_colour",
        "drainage",
    ]

    form = occ_forms.HabitatCompositionForm
    fsm_field = ['status', ]


class HabitatCompositionInline(admin.TabularInline):
    """HabitatComposition Inline."""

    extra = 1
    max_num = 1  # limit max number
    model = occ_models.HabitatComposition
    form = occ_forms.HabitatCompositionForm
    classes = ('grp-collapse', 'grp-open', 'wide', 'extrapretty', )


# -----------------------------------------------------------------------------
# AreaAssessment
#
@admin.register(occ_models.AreaAssessment)
class AreaAssessmentAdmin(FSMTransitionMixin, VersionAdmin):
    """AreaAssessment Admin."""

    list_display = [
        "encounter",
        "survey_type",
        "area_surveyed_m2",
        "survey_duration_min",
    ]
    form = occ_forms.AreaAssessmentForm
    fsm_field = ['status', ]


class AreaAssessmentInline(admin.TabularInline):
    """AreaAssessment Inline."""

    extra = 1
    max_num = 1  # limit max number
    model = occ_models.AreaAssessment
    form = occ_forms.AreaAssessmentForm
    classes = ('grp-collapse grp-open',)


# -----------------------------------------------------------------------------
# OccurrenceCondition
#
@admin.register(occ_models.OccurrenceCondition)
class OccurrenceConditionAdmin(FSMTransitionMixin, VersionAdmin):
    """OccurrenceCondition Admin."""

    list_display = [
        "encounter",
        "pristine_percent",
        "excellent_percent",
        "very_good_percent",
        "good_percent",
        "degraded_percent",
        "completely_degraded_percent",
    ]
    form = occ_forms.OccurrenceConditionForm
    fsm_field = ['status', ]


class OccurrenceConditionInline(admin.TabularInline):
    """OccurrenceCondition Inline."""

    extra = 1
    max_num = 1  # limit max number
    model = occ_models.OccurrenceCondition
    form = occ_forms.OccurrenceConditionForm
    classes = ('grp-collapse grp-open',)

# -----------------------------------------------------------------------------
# Associated Species
#


@admin.register(occ_models.AssociatedSpecies)
class AssociatedSpeciesAdmin(FSMTransitionMixin, VersionAdmin):
    """Associated Species Admin."""

    list_display = ["encounter", "taxon", ]
    form = occ_forms.AssociatedSpeciesForm
    fsm_field = ['status', ]
    autocomplete_fields = ['taxon', ]


class AssociatedSpeciesInline(admin.TabularInline):
    """Associated Species  Inline."""

    extra = 1
    # max_num = 1  # limit max number
    model = occ_models.AssociatedSpecies
    form = occ_forms.AssociatedSpeciesForm
    classes = ('grp-collapse', 'grp-open', 'wide', 'extrapretty', )


# -----------------------------------------------------------------------------
# FileAttachment
#
@admin.register(occ_models.FileAttachment)
class FileAttachmentAdmin(FSMTransitionMixin, VersionAdmin):
    """FileAttachment Admin."""

    list_display = [
        "encounter",
        "attachment",
        "title",
        "author",
        "confidential"
    ]
    form = occ_forms.FileAttachmentForm
    fsm_field = ['status', ]


class FileAttachmentInline(admin.TabularInline):
    """FileAttachment Inline."""

    extra = 1
    # max_num = 1  # limit max number
    model = occ_models.FileAttachment
    form = occ_forms.FileAttachmentForm
    classes = ('grp-collapse', 'grp-open', 'wide', 'extrapretty', )


# -----------------------------------------------------------------------------
# FireHistory
#
@admin.register(occ_models.FireHistory)
class FireHistoryAdmin(FSMTransitionMixin, VersionAdmin):
    """FireHistory Admin."""

    list_display = [
        "encounter",
        "last_fire_date",
        "fire_intensity"
    ]
    form = occ_forms.FireHistoryForm
    fsm_field = ['status', ]


class FireHistoryInline(admin.TabularInline):
    """FireHistory Inline."""

    extra = 1
    # max_num = 1  # limit max number
    model = occ_models.FireHistory
    form = occ_forms.FireHistoryForm
    classes = ('grp-collapse grp-open',)


# -----------------------------------------------------------------------------
# Main models
# -----------------------------------------------------------------------------
# @admin.register(AreaEncounter)
class AreaEncounterAdmin(FSMTransitionMixin, ImportExportModelAdmin, VersionAdmin):
    """Admin for Area."""

    # Change list
    list_display = ["area_type", "code", "name", "source", "source_id", "status", ]
    list_filter = ["area_type", "source", "status", "geolocation_capture_method"]
    search_fields = ("code", "name", )
    date_hierarchy = 'encountered_on'

    # Change view
    form = s2form(occ_models.AreaEncounter, attrs=S2ATTRS)
    formfield_overrides = FORMFIELD_OVERRIDES
    fsm_field = ['status', ]
    autocomplete_fields = ['encountered_by', ]
    fieldsets = (
        (_('Details'), {
            'classes': ('grp-collapse', 'grp-open', 'wide', 'extrapretty'),
            'fields': ("area_type", "code", "name", "description",)}
         ),
        (_('Location'), {
            'classes': ('grp-collapse', 'grp-open', 'wide', 'extrapretty'),
            'fields': ("point", "geom", "accuracy", "geolocation_capture_method")}
         ),
        (_('Data lineage'), {
            'classes': ('grp-collapse', 'grp-open', 'wide', 'extrapretty'),
            'fields': ("source", "source_id", "encountered_on", "encountered_by")}
         ),
    )
    inlines = [CustomStateLogInline, ]


@admin.register(occ_models.TaxonAreaEncounter)
class TaxonAreaAdmin(AreaEncounterAdmin):
    """Admin for TaxonArea."""

    # Change list
    list_display = AreaEncounterAdmin.list_display + ["taxon"]
    list_filter = AreaEncounterAdmin.list_filter + ["taxon"]
    list_select_related = ["taxon", ]
    show_full_result_count = False
    resource_class = occ_resources.TaxonAreaEncounterResource

    # Change view
    form = s2form(occ_models.TaxonAreaEncounter, attrs=S2ATTRS)
    formfield_overrides = FORMFIELD_OVERRIDES
    autocomplete_fields = AreaEncounterAdmin.autocomplete_fields + ["taxon"]
    fieldsets = (
        (_('Taxon'), {
            'classes': ('grp-collapse', 'grp-open', 'wide', 'extrapretty'),
            'fields': ("taxon",)}
         ),
    ) + AreaEncounterAdmin.fieldsets
    inlines = [
        CustomStateLogInline,
        FileAttachmentInline,
        AreaAssessmentInline,
        HabitatCompositionInline,
        FireHistoryInline,
        AssociatedSpeciesInline,
    ]


@admin.register(occ_models.CommunityAreaEncounter)
class CommunityAreaAdmin(AreaEncounterAdmin):
    """Admin for CommunityArea."""

    # Change list
    list_display = AreaEncounterAdmin.list_display + ["community"]
    list_filter = AreaEncounterAdmin.list_filter + ["community"]
    list_select_related = ["community"]
    show_full_result_count = False
    resource_class = occ_resources.CommunityAreaEncounterResource

    # Change view
    form = s2form(occ_models.CommunityAreaEncounter, attrs=S2ATTRS)
    formfield_overrides = FORMFIELD_OVERRIDES
    autocomplete_fields = AreaEncounterAdmin.autocomplete_fields + ["community"]
    fieldsets = ((_('Community'), {
        'classes': ('grp-collapse', 'grp-open', 'wide', 'extrapretty'),
        'fields': ("community", )}
    ),) + AreaEncounterAdmin.fieldsets
    inlines = [
        CustomStateLogInline,
        FileAttachmentInline,
        AreaAssessmentInline,
        HabitatCompositionInline,
        OccurrenceConditionInline,
        FireHistoryInline,
        AssociatedSpeciesInline,
    ]
