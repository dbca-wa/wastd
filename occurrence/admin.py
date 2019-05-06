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
    # form = occ_forms.FileAttachmentForm
    classes = ('grp-collapse', 'grp-open', 'wide', 'extrapretty', )


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
    # form = occ_forms.HabitatCompositionForm
    classes = ('grp-collapse', 'grp-open', 'wide', 'extrapretty', )


# -----------------------------------------------------------------------------
# AreaAssessment
#
@admin.register(occ_models.SurveyMethod)
class SurveyMethodAdmin(CodeLabelDescriptionAdmin):
    """Admin for SurveyMethod."""

    pass


@admin.register(occ_models.AreaAssessment)
class AreaAssessmentAdmin(FSMTransitionMixin, VersionAdmin):
    """AreaAssessment Admin."""

    list_display = [
        "encounter",
        "survey_type",
        "survey_method",
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
    # form = occ_forms.AreaAssessmentForm
    classes = ('grp-collapse grp-open',)


# -----------------------------------------------------------------------------
# HabitatCondition
#
@admin.register(occ_models.SoilCondition)
class SoilConditionAdmin(CodeLabelDescriptionAdmin):
    """Admin for SoilCondition."""

    pass


@admin.register(occ_models.HabitatCondition)
class HabitatConditionAdmin(FSMTransitionMixin, VersionAdmin):
    """HabitatCondition Admin."""

    list_display = [
        "encounter",
        "pristine_percent",
        "excellent_percent",
        "very_good_percent",
        "good_percent",
        "degraded_percent",
        "completely_degraded_percent",
        "soil_condition",
    ]
    form = occ_forms.HabitatConditionForm
    fsm_field = ['status', ]


class HabitatConditionInline(admin.TabularInline):
    """HabitatCondition Inline."""

    extra = 1
    max_num = 1  # limit max number
    model = occ_models.HabitatCondition
    # form = occ_forms.HabitatConditionForm
    classes = ('grp-collapse grp-open',)


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
    # form = occ_forms.FireHistoryForm
    classes = ('grp-collapse grp-open',)

# -----------------------------------------------------------------------------
# PlantCount
#


@admin.register(occ_models.CountAccuracy)
class CountAccuracyAdmin(CodeLabelDescriptionAdmin):
    """Admin for CountAccuracy."""

    pass


@admin.register(occ_models.CountMethod)
class CountMethodAdmin(CodeLabelDescriptionAdmin):
    """Admin for CountMethod."""

    pass


@admin.register(occ_models.CountSubject)
class CountSubjectAdmin(CodeLabelDescriptionAdmin):
    """Admin for CountSubject."""

    pass


@admin.register(occ_models.PlantCondition)
class PlantConditionAdmin(CodeLabelDescriptionAdmin):
    """Admin for PlantCondition."""

    pass


@admin.register(occ_models.PlantCount)
class PlantCountAdmin(FSMTransitionMixin, VersionAdmin):
    """PlantCount Admin."""

    list_display = [
        "land_manager_present",
        "count_method",
        "count_accuracy",
        "count_subject",
        # Plant Count (Detailed)
        "no_alive_mature",
        "no_alive_juvenile",
        "no_alive_seedlings",
        "no_dead_mature",
        "no_dead_juvenile",
        "no_dead_seedlings",
        # Plant Count (Simple)
        "no_alive_simple",
        "no_dead_simple",
        # Quadrats
        "population_area_estimated_m2",
        "quadrats_present",
        "quadrats_details_attached",
        "no_quadrats_surveyed",
        "quadrat_area_individual_m2",
        "quadrat_area_total_m2",
        # Flowering
        "flowering_plants_percent",
        "clonal_present",
        "vegetative_present",
        "flowerbuds_present",
        "flowers_present",
        "immature_fruit_present",
        "ripe_fruit_present",
        "dehisced_fruit_present",
        "plant_condition",
        "comments",
    ]
    list_filter = [
        "count_method",
        "count_accuracy",
        "quadrats_present",
        "quadrats_details_attached",
        "flowering_plants_percent",
        "clonal_present",
        "vegetative_present",
        "flowerbuds_present",
        "flowers_present",
        "immature_fruit_present",
        "ripe_fruit_present",
        "dehisced_fruit_present",
        "plant_condition",
    ]
    form = occ_forms.PlantCountForm
    fsm_field = ['status', ]

    fieldsets = (
        (_('Plant count survey'), {
            'classes': ('grp-collapse', 'grp-open', 'wide', 'extrapretty'),
            'fields': (("count_method", "count_accuracy", "count_subject"))}
         ),
        (_('Plant Count (Detailed)'), {
            'classes': ('grp-collapse', 'grp-open', 'wide', 'extrapretty'),
            'fields': (
                "no_alive_mature",
                "no_alive_juvenile",
                "no_alive_seedlings",
                "no_dead_mature",
                "no_dead_juvenile",
                "no_dead_seedlings",
            )}
         ),
        (_('Plant Count (Simple)'), {
            'classes': ('grp-collapse', 'grp-open', 'wide', 'extrapretty'),
            'fields': ("no_alive_simple", "no_dead_simple",)}
         ),
        (_('Quadrats'), {
            'classes': ('grp-collapse', 'grp-open', 'wide', 'extrapretty'),
            'fields': (
                "quadrats_present",
                "quadrats_details_attached",
                "no_quadrats_surveyed",
                "quadrat_area_individual_m2",
                "quadrat_area_total_m2",
                "population_area_estimated_m2",
            )}
         ),
        (_('Flowering'), {
            'classes': ('grp-collapse', 'grp-open', 'wide', 'extrapretty'),
            'fields': (
                "flowering_plants_percent",
                "clonal_present",
                "vegetative_present",
                "flowerbuds_present",
                "flowers_present",
                "immature_fruit_present",
                "ripe_fruit_present",
                "dehisced_fruit_present",
                "plant_condition",
                "comments",

            )}
         ),
    )


class PlantCountInline(admin.StackedInline):
    """PlantCount Inline."""

    extra = 1
    max_num = 1  # limit max number
    model = occ_models.PlantCount
    # form = occ_forms.PlantCountForm
    classes = ('grp-collapse grp-open',)


# -----------------------------------------------------------------------------
# VegetationClassification
#
@admin.register(occ_models.VegetationClassification)
class VegetationClassificationAdmin(FSMTransitionMixin, VersionAdmin):
    """VegetationClassification Admin."""

    list_display = [
        "encounter",
        "level1",
        "level2",
        "level3",
        "level4",
    ]
    form = occ_forms.VegetationClassificationForm
    fsm_field = ['status', ]


class VegetationClassificationInline(admin.TabularInline):
    """VegetationClassification Inline."""

    extra = 1
    # max_num = 1  # limit max number
    model = occ_models.VegetationClassification
    form = occ_forms.VegetationClassificationForm
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
    # form = occ_forms.AssociatedSpeciesForm
    classes = ('grp-collapse', 'grp-open', 'wide', 'extrapretty', )


# -----------------------------------------------------------------------------
# AnimalObservation
#
@admin.register(occ_models.DetectionMethod)
class DetectionMethodAdmin(CodeLabelDescriptionAdmin):
    """Admin for DetectionMethod."""

    pass


@admin.register(occ_models.Confidence)
class ConfidenceAdmin(CodeLabelDescriptionAdmin):
    """Admin for Confidence."""

    pass


@admin.register(occ_models.ReproductiveMaturity)
class ReproductiveMaturityAdmin(CodeLabelDescriptionAdmin):
    """Admin for ReproductiveMaturity."""

    pass


@admin.register(occ_models.AnimalHealth)
class AnimalHealthAdmin(CodeLabelDescriptionAdmin):
    """Admin for AnimalHealth."""

    pass


@admin.register(occ_models.CauseOfDeath)
class CauseOfDeathAdmin(CodeLabelDescriptionAdmin):
    """Admin for CauseOfDeath."""

    pass


@admin.register(occ_models.SecondarySigns)
class SecondarySignsAdmin(CodeLabelDescriptionAdmin):
    """Admin for SecondarySigns."""

    pass


@admin.register(occ_models.SampleType)
class SampleTypeAdmin(CodeLabelDescriptionAdmin):
    """Admin for SampleType."""

    pass


@admin.register(occ_models.SampleDestination)
class SampleDestinationAdmin(CodeLabelDescriptionAdmin):
    """Admin for SampleDestination."""

    pass


@admin.register(occ_models.PermitType)
class PermitTypeAdmin(CodeLabelDescriptionAdmin):
    """Admin for PermitType."""

    pass


@admin.register(occ_models.AnimalObservation)
class AnimalObservationAdmin(FSMTransitionMixin, VersionAdmin):
    """Associated AnimalObservation."""

    list_display = [
        "encounter",
        "detection_method",
        "species_id_confidence",
        "maturity",
        "health",
        "cause_of_death",
        "distinctive_features",
        "actions_taken",
        "actions_required",
        "no_adult_male",
        "no_adult_female",
        "no_adult_unknown",
        "no_juvenile_male",
        "no_juvenile_female",
        "no_juvenile_unknown",
        "no_dependent_young_male",
        "no_dependent_young_female",
        "no_dependent_young_unknown",
        "observation_details",
        "secondary_signs_list",
    ]
    list_filter = [
        "detection_method",
        "species_id_confidence",
        "maturity",
        "health",
        "cause_of_death",
        "no_adult_male",
        "no_adult_female",
        "no_adult_unknown",
        "no_juvenile_male",
        "no_juvenile_female",
        "no_juvenile_unknown",
        "no_dependent_young_male",
        "no_dependent_young_female",
        "no_dependent_young_unknown",
        "secondary_signs",
    ]
    search_fields = [
        "encounter",
        "distinctive_features",
        "actions_taken",
        "actions_required",
        "observation_details",
    ]
    form = occ_forms.AnimalObservationForm
    fsm_field = ['status', ]
    # autocomplete_fields = ['taxon', ]

    def secondary_signs_list(self, obj):
        """Make M2M secondary_signs readable."""
        return ", ".join([x.label for x in obj.secondary_signs.all()])
    secondary_signs_list.short_description = "Secondary Signs"


class AnimalObservationInline(admin.StackedInline):
    """AnimalObservation Inline."""

    extra = 1
    max_num = 1  # limit max number
    model = occ_models.AnimalObservation
    # form = occ_forms.AnimalObservationForm
    classes = ('grp-collapse', 'grp-open', 'wide', 'extrapretty', )


@admin.register(occ_models.PhysicalSample)
class PhysicalSampleAdmin(FSMTransitionMixin, VersionAdmin):
    """Associated PhysicalSample."""

    list_display = [
        "encounter",
        "sample_type",
        "sample_label",
        "collector_id",
        "sample_destination",
        "permit_type",
        "permit_id",
    ]
    list_filter = [
        "sample_type",
        "sample_destination",
        "permit_type",
    ]
    search_fields = [
        "encounter",
        "sample_label",
        "collector_id",
        "permit_id",

    ]
    form = occ_forms.PhysicalSampleForm
    fsm_field = ['status', ]
    # autocomplete_fields = ['taxon', ]


class PhysicalSampleInline(admin.StackedInline):
    """PhysicalSample Inline."""

    extra = 1
    # max_num = 1  # limit max number
    model = occ_models.PhysicalSample
    # form = occ_forms.PhysicalSampleForm
    classes = ('grp-collapse', 'grp-open', 'wide', 'extrapretty', )


# -----------------------------------------------------------------------------
# Main models
# -----------------------------------------------------------------------------
# @admin.register(AreaEncounter)
class AreaEncounterAdmin(FSMTransitionMixin, ImportExportModelAdmin, VersionAdmin):
    """Admin for Area."""

    # Change list
    list_display = ["encounter_type", "area_type", "code", "name", "source", "source_id", "status", ]
    list_filter = ["encounter_type", "area_type", "source", "status", "geolocation_capture_method"]
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
            'fields': ("encounter_type", "area_type", "code", "name", "description",)}
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
        HabitatCompositionInline,
        AreaAssessmentInline,
        FireHistoryInline,
        PlantCountInline,
        VegetationClassificationInline,
        AssociatedSpeciesInline,
        AnimalObservationInline,
        PhysicalSampleInline,
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
        HabitatCompositionInline,
        AreaAssessmentInline,
        HabitatConditionInline,
        FireHistoryInline,
        VegetationClassificationInline,
        AssociatedSpeciesInline,
        PhysicalSampleInline,
    ]
