# -*- coding: utf-8 -*-
"""Admin module for wastd.observations."""
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
# from django.utils.translation import ugettext_lazy as _
from easy_select2 import select2_modelform as s2form
# from easy_select2.widgets import Select2
from fsm_admin.mixins import FSMTransitionMixin
from reversion.admin import VersionAdmin
from import_export.admin import ImportExportModelAdmin

from conservation import resources as cons_resources
from conservation import models as cons_models
from shared.admin import S2ATTRS, FORMFIELD_OVERRIDES, CustomStateLogInline


class FileAttachmentInline(GenericTabularInline):
    """Inline for FileAttachment."""

    model = cons_models.FileAttachment
    form = s2form(cons_models.FileAttachment, attrs=S2ATTRS)
    extra = 1
    classes = ("grp-collapse grp-closed wide extrapretty",)


@admin.register(cons_models.ConservationThreatCategory)
class ConservationThreatCategoryAdmin(VersionAdmin):
    """Admin for Conservation Management Threats."""

    model = cons_models.ConservationThreatCategory
    form = s2form(cons_models.ConservationThreatCategory, attrs=S2ATTRS)
    prepopulated_fields = {"code": ("label",)}
    list_display = ("code", "label", "description", )
    search_fields = ("code", "label", "description")
    save_on_top = True


@admin.register(cons_models.ConservationThreat)
class ConservationThreatAdmin(ImportExportModelAdmin, VersionAdmin):
    """Admin for Conservation Management Threats."""

    model = cons_models.ConservationThreat
    form = s2form(cons_models.ConservationThreat, attrs=S2ATTRS)
    resource_class = cons_resources.ConservationThreatResource
    autocomplete_fields = ['taxa', 'communities', "category", ]

    list_display = (
        "pk",
        "taxon_list",
        "com_list",
        "document",
        "occurrence_area_code",
        "category",
        "cause",
        "encountered_on",
        "encountered_by",
        "current_impact",
        "potential_impact",
        "potential_onset",
    )
    list_filter = (
        "category",
        "document",
        ("encountered_on", admin.DateFieldListFilter),
        "current_impact",
        "potential_impact",
        "potential_onset",
    )
    search_fields = (
        "occurrence_area_code",
        "cause",
    )

    save_on_top = True
    formfield_overrides = FORMFIELD_OVERRIDES
    fieldsets = (
        ("Affiliation", {
            "classes": ("grp-collapse", "grp-open", "wide", "extrapretty"),
            "fields": ("taxa", "communities", "document",
                       "target_area", "occurrence_area_code")
        }),
        ("Threat", {
            "classes": ("grp-collapse", "grp-open", "wide", "extrapretty"),
            "fields": ("encountered_by", "encountered_on", "category", "cause",
                       "area_affected_percent", "current_impact",
                       "potential_impact", "potential_onset")
        }),
    )
    inlines = [
        FileAttachmentInline,
    ]

    def taxon_list(self, obj):
        """Make M2M taxa readable."""
        return ", ".join([taxon.__str__() for taxon in obj.taxa.all()])
    taxon_list.short_description = 'Species'

    def com_list(self, obj):
        """Make M2M taxa readable."""
        return ", ".join([com.__str__() for com in obj.communities.all()])
    com_list.short_description = 'Communities'


@admin.register(cons_models.ConservationActionCategory)
class ConservationActionCategoryAdmin(VersionAdmin):
    """Admin for Conservation Management Actions."""

    model = cons_models.ConservationActionCategory
    form = s2form(cons_models.ConservationActionCategory, attrs=S2ATTRS)
    prepopulated_fields = {"code": ("label",)}
    list_display = ("code", "label", "description", )
    search_fields = ("code", "label", "description")
    save_on_top = True


class ConservationActivityInline(admin.TabularInline):
    """Inline admin for ConservationActivity."""

    extra = 1
    model = cons_models.ConservationActivity
    form = s2form(cons_models.ConservationActivity, attrs=S2ATTRS)
    formfield_overrides = FORMFIELD_OVERRIDES
    classes = ("grp-collapse grp-open wide extrapretty",)


@admin.register(cons_models.ConservationAction)
class ConservationActionAdmin(ImportExportModelAdmin, VersionAdmin):
    """Admin for Conservation Management Actions."""

    model = cons_models.ConservationAction
    form = s2form(cons_models.ConservationAction, attrs=S2ATTRS)
    resource_class = cons_resources.ConservationActionResource
    autocomplete_fields = ['taxa', 'communities', "category", ]

    list_display = (
        "pk",
        "taxon_list",
        "com_list",
        "document",
        "occurrence_area_code",
        "category",
        "instructions",
        "implementation_notes",
        "completion_date",
        "expenditure",
        "status")
    list_filter = (
        "status",
        "category",
        "document",
        ("completion_date", admin.DateFieldListFilter),
    )
    search_fields = (
        "occurrence_area_code",
        "instructions",
        "implementation_notes",
    )

    save_on_top = True
    # filter_horizontal = ("communities", )
    formfield_overrides = FORMFIELD_OVERRIDES
    readonly_fields = ["expenditure", ]

    fieldsets = (
        ("Affiliation", {
            "classes": ("grp-collapse", "grp-open", "wide", "extrapretty"),
            "fields": ("taxa", "communities", "document",
                       "target_area", "occurrence_area_code")
        }),
        ("Intent", {
            "classes": ("grp-collapse", "grp-open", "wide", "extrapretty"),
            "fields": ("category", "instructions",)
        }),
        ("Implementation", {
            "classes": ("grp-collapse", "grp-open", "wide", "extrapretty"),
            "fields": ("implementation_notes", "completion_date", "expenditure")
        }),

    )
    inlines = [
        FileAttachmentInline,
        ConservationActivityInline,
    ]

    def taxon_list(self, obj):
        """Make M2M taxa readable."""
        return ", ".join([taxon.__str__() for taxon in obj.taxa.all()])
    taxon_list.short_description = 'Species'

    def com_list(self, obj):
        """Make M2M taxa readable."""
        return ", ".join([com.__str__() for com in obj.communities.all()])
    com_list.short_description = 'Communities'

    def status(self, obj):
        """Make status readable."""
        return obj.status
    status.short_description = 'Progress'


class ConservationActionInline(admin.TabularInline):
    """Inline admin for Management Action."""

    extra = 1
    model = cons_models.ConservationAction
    form = s2form(cons_models.ConservationAction, attrs=S2ATTRS)
    formfield_overrides = FORMFIELD_OVERRIDES
    classes = ("grp-collapse grp-closed wide extrapretty",)
    # prepopulated_fields = {"taxa": ("taxa",), "communities": ("communities",), }
    # TODO: https://stackoverflow.com/questions/5223048/django-set-initial-data-to-formset-with-manytomany


@admin.register(cons_models.ConservationCategory)
class ConservationCategoryAdmin(FSMTransitionMixin, VersionAdmin):
    """Admin for ConservationCategory."""

    search_fields = [
        'conservation_list__code__icontains',
        'code__icontains',
        'label__icontains',
        'description__icontains'
    ]


@admin.register(cons_models.ConservationCriterion)
class ConservationCriterionAdmin(FSMTransitionMixin, VersionAdmin):
    """Admin for ConservationCriterion."""

    search_fields = [
        'conservation_list__code__icontains',
        'code__icontains',
        'label__icontains',
        'description__icontains'
    ]


class ConservationCategoryInline(admin.TabularInline):
    """Inline admin for ConservationCategory."""

    extra = 1
    model = cons_models.ConservationCategory
    classes = ("grp-collapse grp-closed wide extrapretty",)
    form = s2form(cons_models.ConservationCategory, attrs=S2ATTRS)
    # formfield_overrides = FORMFIELD_OVERRIDES


class ConservationCriterionInline(admin.TabularInline):
    """Inline admin for ConservationCriterion."""

    extra = 1
    model = cons_models.ConservationCriterion
    classes = ("grp-collapse grp-closed wide extrapretty",)
    form = s2form(cons_models.ConservationCriterion, attrs=S2ATTRS)
    # formfield_overrides = FORMFIELD_OVERRIDES


@admin.register(cons_models.ConservationList)
class ConservationListAdmin(VersionAdmin):
    """Admin for ConservationList."""

    save_on_top = True
    date_hierarchy = "active_to"

    # List View
    list_display = (
        "code",
        "label",
        "description",
        "active_from",
        "active_to",
        "scope_wa",
        "scope_cmw",
        "scope_intl",
        "scope_species",
        "scope_communities",
        "approval_level",
    )
    list_filter = ("scope_wa",
                   "scope_cmw",
                   "scope_intl",
                   "scope_species",
                   "scope_communities",
                   "approval_level",)
    search_fields = ("code", "label", "description", )
    fieldsets = (
        ("Details", {"fields": ("code", "label", "description",)}),
        ("Scope", {
            "classes": ("grp-collapse", "grp-closed", "wide"),
            "fields": ("active_from", "active_to",
                       "scope_wa", "scope_cmw", "scope_intl",
                       "scope_species", "scope_communities", "approval_level",)

        }),
    )
    form = s2form(cons_models.ConservationList, attrs=S2ATTRS)
    formfield_overrides = FORMFIELD_OVERRIDES
    inlines = [ConservationCategoryInline,
               ConservationCriterionInline,
               FileAttachmentInline]


@admin.register(cons_models.TaxonGazettal)
class TaxonGazettalAdmin(FSMTransitionMixin, VersionAdmin):
    """Admin for TaxonGazettal."""

    save_on_top = True
    date_hierarchy = "effective_from"

    # FSM Transitions
    fsm_field = ["status", ]

    # List View
    list_display = (
        "source",
        "source_id",
        "taxon",
        "scope",
        "status",
        "category_cache",
        "criteria_cache",
        "proposed_on",
        "effective_from",
        "effective_to",
        "last_reviewed_on",
        "review_due",
        "comments",
    )
    list_filter = (
        "source",
        "category",
        "scope",
        "status",
        ("proposed_on", admin.DateFieldListFilter),
        ("effective_from", admin.DateFieldListFilter),
        ("effective_to", admin.DateFieldListFilter),
        ("last_reviewed_on", admin.DateFieldListFilter),
        ("review_due", admin.DateFieldListFilter),
    )

    search_fields = ("comments", )

    # Detail View layout and widgets
    form = s2form(cons_models.TaxonGazettal, attrs=S2ATTRS)
    formfield_overrides = FORMFIELD_OVERRIDES
    autocomplete_fields = ["taxon", "category", "criteria", ]
    inlines = [CustomStateLogInline, FileAttachmentInline]

    fieldsets = (
        ("Conservation Status", {
            "classes": ("grp-collapse", "grp-open", "wide", "extrapretty"),
            "fields": ("taxon", "scope", "category", "criteria",)}
         ),
        ("Data lineage", {
            "classes": ("grp-collapse", "grp-closed", "wide", "extrapretty"),
            "fields": ("source", "source_id", )}
         ),
        ("Approval milestones and log", {
            "classes": ("grp-collapse", "grp-closed", "wide", "extrapretty"),
            "fields": ("proposed_on", "effective_from", "effective_to",
                       "last_reviewed_on", "review_due", "comments",)}
         ),
    )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Restrict available cat and crit to lists relevant to species."""
        if db_field.name == "category":
            kwargs["queryset"] = cons_models.ConservationCategory.objects.filter(
                conservation_list__scope_species=True
            ).prefetch_related(
                'conservation_list'
            ).order_by(
                "conservation_list__code", "rank"
            )

        if db_field.name == "criteria":
            kwargs["queryset"] = cons_models.ConservationCriterion.objects.filter(
                conservation_list__scope_species=True
            ).prefetch_related(
                'conservation_list'
            ).order_by(
                "conservation_list__code", "rank"
            )
        return super(TaxonGazettalAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(cons_models.CommunityGazettal)
class CommunityGazettalAdmin(FSMTransitionMixin, VersionAdmin):
    """Admin for CommunityGazettal."""

    save_on_top = True
    date_hierarchy = "effective_from"

    # FSM Transitions
    fsm_field = ["status", ]

    # List View
    list_display = (
        "community",
        "scope",
        "status",
        "category_cache",
        "criteria_cache",
        "proposed_on",
        "effective_from",
        "effective_to",
        "review_due",
        "comments",
    )
    list_filter = (
        "category",
        "scope",
        "status",
        ("proposed_on", admin.DateFieldListFilter),
        ("effective_from", admin.DateFieldListFilter),
        ("effective_to", admin.DateFieldListFilter),
        ("review_due", admin.DateFieldListFilter),
    )
    search_fields = ("comments", )

    # Detail View
    form = s2form(cons_models.CommunityGazettal, attrs=S2ATTRS)
    formfield_overrides = FORMFIELD_OVERRIDES
    autocomplete_fields = ["community", "category", "criteria", ]
    inlines = [CustomStateLogInline, FileAttachmentInline]

    fieldsets = (
        ("Conservation Status", {
            "classes": ("grp-collapse", "grp-open", "wide", "extrapretty"),
            "fields": ("community", "scope", "category", "criteria",)}
         ),
        ("Data lineage", {
            "classes": ("grp-collapse", "grp-closed", "wide", "extrapretty"),
            "fields": ("source", "source_id", )}
         ),
        ("Approval milestones and log", {
            "classes": ("grp-collapse", "grp-closed", "wide", "extrapretty"),
            "fields": ("proposed_on", "effective_from", "effective_to", "last_reviewed_on", "review_due", "comments",)}
         ),
    )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Restrict available cat and crit to lists relevant to species."""
        if db_field.name == "category":
            kwargs["queryset"] = cons_models.ConservationCategory.objects.filter(
                conservation_list__scope_communities=True
            ).prefetch_related(
                'conservation_list'
            ).order_by(
                "conservation_list__code", "rank"
            )

        if db_field.name == "criteria":
            kwargs["queryset"] = cons_models.ConservationCriterion.objects.filter(
                conservation_list__scope_communities=True
            ).prefetch_related(
                'conservation_list'
            ).order_by(
                "conservation_list__code", "rank"
            )
        return super(CommunityGazettalAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(cons_models.Document)
class DocumentAdmin(FSMTransitionMixin, VersionAdmin):
    """Admin for Document."""

    save_on_top = True
    date_hierarchy = "effective_from"

    # FSM Transitions
    fsm_field = ["status", ]

    # List View
    list_display = (
        "source",
        "source_id",
        "document_type",
        "title",
        "effective_from",
        "effective_to",
        "effective_from_commonwealth",
        "effective_to_commonwealth",
        "last_reviewed_on",
        "review_due",
    )
    list_filter = (
        # "taxa",
        # "communities",
        "source",
        "document_type",
        "status",
        ("effective_from", admin.DateFieldListFilter),
        ("effective_to", admin.DateFieldListFilter),
        ("last_reviewed_on", admin.DateFieldListFilter),
        ("review_due", admin.DateFieldListFilter),
        ("effective_from_commonwealth", admin.DateFieldListFilter),
        ("effective_to_commonwealth", admin.DateFieldListFilter),
    )
    search_fields = ("title", "source_id", )

    # Detail View
    form = s2form(cons_models.Document, attrs=S2ATTRS)
    formfield_overrides = FORMFIELD_OVERRIDES
    inlines = [
        # ConservationActionInline, # throws admin.E028
        CustomStateLogInline,
        FileAttachmentInline, ]

    fieldsets = (
        ("Scope", {
            "classes": ("grp-collapse", "grp-open", "wide", "extrapretty"),
            "fields": ("document_type", "title", "taxa", "communities", "team",)}
         ),
        ("Approval milestones and log", {
            "classes": ("grp-collapse", "grp-closed", "wide", "extrapretty"),
            "fields": ("effective_from", "effective_to",
                       "effective_from_commonwealth", "effective_to_commonwealth",
                       "last_reviewed_on", "review_due", "comments")}
         ),
    )
