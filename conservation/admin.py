# -*- coding: utf-8 -*-
"""Admin module for wastd.observations."""
from __future__ import absolute_import, unicode_literals

from ajax_select.fields import AutoCompleteSelectMultipleField  # AutoCompleteSelectField,
from conservation.models import (  # Gazettal,
    CommunityGazettal,
    ConservationActionCategory,
    ConservationAction,
    ConservationActivity,
    ConservationCategory,
    ConservationCriterion,
    ConservationList,
    Document,
    FileAttachment,
    TaxonGazettal
)
# from django import forms as django_forms
# import floppyforms as ff
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.gis.db import models as geo_models
from django.db import models
from django.forms import Textarea
from django.utils.translation import ugettext_lazy as _
from django_select2.forms import HeavySelect2MultipleWidget
from easy_select2 import select2_modelform as s2form
# from easy_select2.widgets import Select2
from fsm_admin.mixins import FSMTransitionMixin
from leaflet.forms.widgets import LeafletWidget
from reversion.admin import VersionAdmin
from shared.admin import CustomStateLogInline

S2ATTRS = {"width": "auto"}
ConservationActionCategoryForm = s2form(ConservationActionCategory, attrs=S2ATTRS)
ConservationActionForm = s2form(ConservationAction, attrs=S2ATTRS)
ConservationActivityForm = s2form(ConservationActivity, attrs=S2ATTRS)
ConservationCategoryForm = s2form(ConservationCategory, attrs=S2ATTRS)
ConservationCriterionForm = s2form(ConservationCriterion, attrs=S2ATTRS)
ConservationListForm = s2form(ConservationList, attrs=S2ATTRS)
TaxonGazettalForm = s2form(TaxonGazettal, attrs=S2ATTRS)
CommunityGazettalForm = s2form(CommunityGazettal, attrs=S2ATTRS)
FileAttachmentForm = s2form(FileAttachment, attrs=S2ATTRS)
DocumentForm = s2form(Document, attrs=S2ATTRS)


class AjaxDocumentForm(DocumentForm):
    """A document form with a type-ahead widget for Taxa."""

    taxa = AutoCompleteSelectMultipleField(
        "taxon",
        required=False,
        help_text=_("Enter a part of the taxonomic name to search. "
                    "The search is case-insensitive."))
    # taxa = HeavySelect2MultipleWidget()

leaflet_settings = {
    'widget': LeafletWidget(attrs={
        'map_height': '400px',
        'map_width': '100%',
        'display_raw': 'true',
        'map_srid': 4326, })}

FORMFIELD_OVERRIDES = {
    models.TextField: {"widget": Textarea(attrs={"rows": 20, "cols": 80})},
    models.ManyToManyField: {"widget": HeavySelect2MultipleWidget(data_url="/api/1/taxon/?format=json")},
    geo_models.PointField: leaflet_settings,
    geo_models.LineStringField: leaflet_settings,
    geo_models.MultiPolygonField: leaflet_settings,

}


class FileAttachmentInline(GenericTabularInline):
    """Inline for FileAttachment."""

    model = FileAttachment
    form = FileAttachmentForm
    extra = 1
    classes = ("grp-collapse grp-closed wide extrapretty",)


@admin.register(ConservationActionCategory)
class ConservationActionCategoryAdmin(VersionAdmin):
    """Admin for Conservation Management Actions."""

    model = ConservationActionCategory
    form = ConservationActionCategoryForm
    prepopulated_fields = {"code": ("label",)}
    list_display = ("code", "label", "description", )
    save_on_top = True


class ConservationActivityInline(admin.TabularInline):
    """Inline admin for ConservationActivity."""

    extra = 1
    model = ConservationActivity
    form = ConservationActivityForm
    formfield_overrides = FORMFIELD_OVERRIDES
    classes = ("grp-collapse grp-open wide extrapretty",)


@admin.register(ConservationAction)
class ConservationActionAdmin(VersionAdmin):
    """Admin for Conservation Management Actions."""

    model = ConservationAction
    form = ConservationActionForm
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

    taxa = AutoCompleteSelectMultipleField(
        "taxon",
        required=False,
        help_text=_("Enter a part of the taxonomic name to search. "
                    "The search is case-insensitive."))
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
    model = ConservationAction
    form = ConservationActionForm
    formfield_overrides = FORMFIELD_OVERRIDES
    classes = ("grp-collapse grp-closed wide extrapretty",)
    # prepopulated_fields = {"taxa": ("taxa",), "communities": ("communities",), }
    # TODO: https://stackoverflow.com/questions/5223048/django-set-initial-data-to-formset-with-manytomany


class ConservationCategoryInline(admin.TabularInline):
    """Inline admin for ConservationCategory."""

    extra = 1
    model = ConservationCategory
    classes = ("grp-collapse grp-closed wide extrapretty",)
    form = ConservationCategoryForm
    # formfield_overrides = FORMFIELD_OVERRIDES


class ConservationCriterionInline(admin.TabularInline):
    """Inline admin for ConservationCriterion."""

    extra = 1
    model = ConservationCriterion
    classes = ("grp-collapse grp-closed wide extrapretty",)
    form = ConservationCriterionForm
    # formfield_overrides = FORMFIELD_OVERRIDES


@admin.register(ConservationList)
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
    formfield_overrides = FORMFIELD_OVERRIDES
    inlines = [ConservationCategoryInline,
               ConservationCriterionInline,
               FileAttachmentInline]


@admin.register(TaxonGazettal)
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
    filter_horizontal = ("category", "criteria",)
    raw_id_fields = ("taxon", )
    autocomplete_lookup_fields = {"fk": ["taxon", ]}
    form = TaxonGazettalForm
    formfield_overrides = FORMFIELD_OVERRIDES
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
            "fields": ("proposed_on", "effective_from", "effective_to", "last_reviewed_on", "review_due", "comments",)}
         ),
    )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Restrict available cat and crit to lists relevant to species."""
        if db_field.name == "category":
            kwargs["queryset"] = ConservationCategory.objects.filter(
                conservation_list__scope_species=True).order_by("conservation_list__code", "rank")

        if db_field.name == "criteria":
            kwargs["queryset"] = ConservationCriterion.objects.filter(
                conservation_list__scope_species=True).order_by("conservation_list__code", "rank")
        return super(TaxonGazettalAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(CommunityGazettal)
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
    filter_horizontal = ("category", "criteria",)
    raw_id_fields = ("community", )
    autocomplete_lookup_fields = {"fk": ["community", ]}
    form = CommunityGazettalForm
    formfield_overrides = FORMFIELD_OVERRIDES
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
            kwargs["queryset"] = ConservationCategory.objects.filter(
                conservation_list__scope_communities=True).order_by("conservation_list__code", "rank")

        if db_field.name == "criteria":
            kwargs["queryset"] = ConservationCriterion.objects.filter(
                conservation_list__scope_communities=True).order_by("conservation_list__code", "rank")
        return super(CommunityGazettalAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(Document)
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
    filter_horizontal = ("taxa", "communities", "team",)
    # raw_id_fields = ("taxa", "communities", "team")
    # autocomplete_lookup_fields = {"fk": ["taxa", "communities", "team"]}
    form = AjaxDocumentForm
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
