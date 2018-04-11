# -*- coding: utf-8 -*-
"""Admin module for wastd.observations."""
from __future__ import absolute_import, unicode_literals

# from django import forms as django_forms
# import floppyforms as ff
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.forms import Textarea
from django.db import models

# from django.utils.translation import ugettext_lazy as _
from easy_select2 import select2_modelform as s2form
# from easy_select2.widgets import Select2
from fsm_admin.mixins import FSMTransitionMixin
from django_fsm_log.admin import StateLogInline
# from django_fsm_log.models import StateLog
from reversion.admin import VersionAdmin

from conservation.models import (
    FileAttachment,
    ConservationList,
    ConservationCategory,
    ConservationCriterion,
    # Gazettal,
    TaxonGazettal,
    CommunityGazettal
)


S2ATTRS = {'width': 'auto'}
ConservationCategoryForm = s2form(ConservationCategory, attrs=S2ATTRS)
ConservationCriterionForm = s2form(ConservationCriterion, attrs=S2ATTRS)
ConservationListForm = s2form(ConservationList, attrs=S2ATTRS)
TaxonGazettalForm = s2form(TaxonGazettal, attrs=S2ATTRS)
CommunityGazettalForm = s2form(CommunityGazettal, attrs=S2ATTRS)
FileAttachmentForm = s2form(FileAttachment, attrs=S2ATTRS)

FORMFIELD_OVERRIDES = {
    models.TextField: {'widget': Textarea(attrs={'rows': 20, 'cols': 80})},
}


class CustomStateLogInline(StateLogInline):
    """Custom StateLogInline."""
    classes = ('grp-collapse grp-closed wide extrapretty',)


class FileAttachmentInline(GenericTabularInline):
    """Inline for FileAttachment."""

    model = FileAttachment
    form = FileAttachmentForm
    extra = 1
    classes = ('grp-collapse grp-closed wide extrapretty',)


class ConservationCategoryInline(admin.TabularInline):
    """Inline admin for ConservationCategory."""

    extra = 1
    model = ConservationCategory
    classes = ('grp-collapse grp-closed wide extrapretty',)
    form = ConservationCategoryForm
    # formfield_overrides = FORMFIELD_OVERRIDES


class ConservationCriterionInline(admin.TabularInline):
    """Inline admin for ConservationCriterion."""

    extra = 1
    model = ConservationCriterion
    classes = ('grp-collapse grp-closed wide extrapretty',)
    form = ConservationCriterionForm
    # formfield_overrides = FORMFIELD_OVERRIDES


@admin.register(ConservationList)
class ConservationListAdmin(VersionAdmin):
    """Admin for ConservationList."""

    save_on_top = True
    date_hierarchy = 'active_to'

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
    )
    list_filter = ("scope_wa",
                   "scope_cmw",
                   "scope_intl",
                   "scope_species",
                   "scope_communities",)
    search_fields = ("code", "label", "description", )
    fieldsets = (
        ('Details', {'fields': ("code", "label", "description",)}),
        ('Scope', {
            'classes': ('grp-collapse', 'grp-closed', 'wide'),
            'fields': ("active_from", "active_to",
                       "scope_wa", "scope_cmw", "scope_intl",
                       "scope_species", "scope_communities")

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
    date_hierarchy = 'gazetted_on'

    # FSM Transitions
    fsm_field = ['status', ]

    # List View
    list_display = (
        "taxon",
        "status",
        "category_cache",
        "criteria_cache",
        "proposed_on",
        "gazetted_on",
        "deactivated_on",
        "review_due",
        "comments",
    )
    list_filter = (
        "category",
        "status",
        ('proposed_on', admin.DateFieldListFilter),
        ('gazetted_on', admin.DateFieldListFilter),
        ('deactivated_on', admin.DateFieldListFilter),
        ('review_due', admin.DateFieldListFilter),
    )

    search_fields = ("comments", )

    # Detail View layout and widgets
    filter_horizontal = ('category', 'criteria',)
    raw_id_fields = ('taxon', )
    autocomplete_lookup_fields = {'fk': ['taxon', ]}
    form = TaxonGazettalForm
    formfield_overrides = FORMFIELD_OVERRIDES
    inlines = [CustomStateLogInline, FileAttachmentInline]

    fieldsets = (
        ('Conservation Status', {
            'classes': ('grp-collapse', 'grp-open', 'wide', 'extrapretty'),
            'fields': ("taxon", "category", "criteria",)}
         ),
        ('Approval process', {
            'classes': ('grp-collapse', 'grp-closed', 'wide', 'extrapretty'),
            'fields': ("proposed_on", "gazetted_on", "deactivated_on", "review_due", "comments",)}
         ),
    )


@admin.register(CommunityGazettal)
class CommunityGazettalAdmin(FSMTransitionMixin, VersionAdmin):
    """Admin for CommunityGazettal."""

    save_on_top = True
    date_hierarchy = 'gazetted_on'

    # FSM Transitions
    fsm_field = ['status', ]

    # List View
    list_display = (
        "community",
        "status",
        "category_cache",
        "criteria_cache",
        "proposed_on",
        "gazetted_on",
        "deactivated_on",
        "review_due",
        "comments",
    )
    list_filter = (
        "category",
        "status",
        ('proposed_on', admin.DateFieldListFilter),
        ('gazetted_on', admin.DateFieldListFilter),
        ('deactivated_on', admin.DateFieldListFilter),
        ('review_due', admin.DateFieldListFilter),
    )
    search_fields = ("comments", )

    # Detail View
    filter_horizontal = ('category', 'criteria',)
    raw_id_fields = ('community', )
    autocomplete_lookup_fields = {'fk': ['community', ]}
    form = CommunityGazettalForm
    formfield_overrides = FORMFIELD_OVERRIDES
    inlines = [CustomStateLogInline, FileAttachmentInline]

    fieldsets = (
        ('Conservation Status', {
            'classes': ('grp-collapse', 'grp-open', 'wide', 'extrapretty'),
            'fields': ("community", "category", "criteria",)}
         ),
        ('Approval process', {
            'classes': ('grp-collapse', 'grp-closed', 'wide', 'extrapretty'),
            'fields': ("proposed_on", "gazetted_on", "deactivated_on", "review_due", "comments",)}
         ),
    )
