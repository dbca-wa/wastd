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


from shared.admin import CustomStateLogInline, S2ATTRS, FORMFIELD_OVERRIDES
from taxonomy.models import Community, Taxon  # noqa
from occurrence import models as occ_models
from occurrence import forms as occ_forms
from occurrence import resources as occ_resources


class FileAttachmentInline(admin.TabularInline):
    """FileAttachment Inline."""

    extra = 0
    # max_num = 1  # limit max number
    model = occ_models.FileAttachment
    form = occ_forms.FileAttachmentForm
    classes = ('grp-collapse grp-open',)


class AssociatedSpeciesInline(admin.TabularInline):
    """Associated Species  Inline."""

    extra = 0
    # max_num = 1  # limit max number
    model = occ_models.AssociatedSpecies
    form = occ_forms.AssociatedSpeciesForm
    classes = ('grp-collapse grp-open',)


class FireHistoryInline(admin.TabularInline):
    """FireHistoryObservation Inline."""

    extra = 0
    # max_num = 1  # limit max number
    model = occ_models.FireHistory
    form = occ_forms.FireHistoryForm
    classes = ('grp-collapse grp-open',)


class AreaAssessmentInline(admin.TabularInline):
    """AreaAssessmentObservation Inline."""

    extra = 0
    # max_num = 1  # limit max number
    model = occ_models.AreaAssessment
    form = occ_forms.AreaAssessmentForm
    classes = ('grp-collapse grp-open',)

# @admin.register(AreaEncounter)


class AreaEncounterAdmin(FSMTransitionMixin, ImportExportModelAdmin, VersionAdmin):
    """Admin for Area."""

    # Change list
    list_display = ["area_type", "code", "name", "source", "source_id", "status", ]
    list_filter = ["area_type", "source", "status", ]
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
            'fields': ("point", "geom", "accuracy",)}
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

    # # Change list
    list_display = AreaEncounterAdmin.list_display + ["taxon"]
    list_filter = AreaEncounterAdmin.list_filter + ["taxon"]
    list_select_related = ["taxon", ]
    show_full_result_count = False
    resource_class = occ_resources.TaxonAreaEncounterResource

    # # Change view
    # form = TaxonAreaEncounterForm
    form = s2form(occ_models.TaxonAreaEncounter, attrs=S2ATTRS)
    formfield_overrides = FORMFIELD_OVERRIDES
    autocomplete_fields = AreaEncounterAdmin.autocomplete_fields + ["taxon"]
    inlines = [
        CustomStateLogInline,
        FileAttachmentInline,
        AreaAssessmentInline,
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
    fieldsets = ((_('Community'), {
        'classes': ('grp-collapse', 'grp-open', 'wide', 'extrapretty'),
        'fields': ("community", )}
    ),) + AreaEncounterAdmin.fieldsets
    inlines = [
        CustomStateLogInline,
        FileAttachmentInline,
        AreaAssessmentInline,
        FireHistoryInline,
        AssociatedSpeciesInline,
    ]


@admin.register(occ_models.AssociatedSpecies)
class AssociatedSpeciesAdmin(FSMTransitionMixin, VersionAdmin):
    """Associated Species Admin."""

    list_display = ["encounter", "taxon", ]
    form = occ_forms.AssociatedSpeciesForm
    fsm_field = ['status', ]
    autocomplete_fields = ['taxon', ]


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
