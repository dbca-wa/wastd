# -*- coding: utf-8 -*-
"""Admin module for wastd.observations."""
from __future__ import absolute_import, unicode_literals

# from django import forms as django_forms
# import floppyforms as ff
from django.contrib import admin

# from django.utils.translation import ugettext_lazy as _
from easy_select2 import select2_modelform as s2form
# from easy_select2.widgets import Select2
from fsm_admin.mixins import FSMTransitionMixin
from reversion.admin import VersionAdmin

from conservation.models import (
    ConservationList,
    ConservationCategory,
    ConservationCriterion,
    TaxonGazettal,
    CommunityGazettal
)


class ConservationCategoryInline(admin.TabularInline):
    """Inline admin for ConservationCategory."""

    extra = 1
    model = ConservationCategory
    classes = ('grp-collapse grp-open',)


class ConservationCriterionInline(admin.TabularInline):
    """Inline admin for ConservationCriterion."""

    extra = 1
    model = ConservationCriterion
    classes = ('grp-collapse grp-open',)


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
        ('Scope', {'fields': ("active_from", "active_to",
                              "scope_wa", "scope_cmw", "scope_intl",
                              "scope_species", "scope_communities",)}),
    )
    inlines = [ConservationCategoryInline,
               ConservationCriterionInline]


S2ATTRS = {'width': '350px'}
TaxonGazettalForm = s2form(TaxonGazettal, attrs=S2ATTRS)
CommunityGazettalForm = s2form(CommunityGazettal, attrs=S2ATTRS)


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
        "category_cache",
        "criteria_cache",
        "proposed_on",
        "gazetted_on",
        "deactivated_on",
        "review_due",
        "comments",
    )
    list_filter = ("category",)

    list_filter = (
        "category",
        ('proposed_on', admin.DateFieldListFilter),
        ('gazetted_on', admin.DateFieldListFilter),
        ('deactivated_on', admin.DateFieldListFilter),
        ('review_due', admin.DateFieldListFilter),
    )

    search_fields = ("taxon", "comments", )

    # Detail View layout and widgets
    filter_horizontal = ('category', 'criteria',)
    raw_id_fields = ('taxon', )
    autocomplete_lookup_fields = {'fk': ['taxon', ]}
    form = TaxonGazettalForm
    fieldsets = (
        ('Conservation Status',
            {'fields': (
                "taxon",
                "category",
                "criteria",
            )}
         ),
        ('Approval process',
            {'fields': (
                "proposed_on",
                "gazetted_on",
                "deactivated_on",
                "review_due",
                "comments",
            )}
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
        "category_cache",
        "criteria_cache",
        "proposed_on",
        "gazetted_on",
        "deactivated_on",
        "review_due",
        "comments",
    )
    list_filter = ("category",)
    search_fields = ("category", "comments", )

    # Detail View
    filter_horizontal = ('category', 'criteria',)
    raw_id_fields = ('community', )
    autocomplete_lookup_fields = {'fk': ['community', ]}
    form = CommunityGazettalForm
    fieldsets = (
        ('Conservation Status',
            {'fields': (
                "community",
                "category",
                "criteria",
            )}
         ),
        ('Approval process',
            {'fields': (
                "proposed_on",
                "gazetted_on",
                "deactivated_on",
                "review_due",
                "comments",
            )}
         ),
    )
