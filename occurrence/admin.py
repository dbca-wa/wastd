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
from fsm_admin.mixins import FSMTransitionMixin
from reversion.admin import VersionAdmin

from occurrence.models import (
    AreaEncounter,
    CommunityAreaEncounter,
    TaxonAreaEncounter,
    # ObservationGroup,
    AssociatedSpeciesObservation,
    FireHistoryObservation
)

from shared.admin import CustomStateLogInline, S2ATTRS, FORMFIELD_OVERRIDES
from taxonomy.models import Community, Taxon  # noqa
from occurrence.forms import (  # noqa
    TaxonAreaEncounterForm,
    AssociatedSpeciesObservationForm,
    FireHistoryObservationForm
)


class AssociatedSpeciesObservationInline(admin.TabularInline):
    """Associated Species Observation Inline."""

    extra = 0
    # max_num = 1  # limit max number
    model = AssociatedSpeciesObservation
    form = AssociatedSpeciesObservationForm
    classes = ('grp-collapse grp-open',)


class FireHistoryObservationInline(admin.TabularInline):
    """FireHistoryObservation Inline."""

    extra = 0
    # max_num = 1  # limit max number
    model = FireHistoryObservation
    form = FireHistoryObservationForm
    classes = ('grp-collapse grp-open',)


# @admin.register(AreaEncounter)
class AreaEncounterAdmin(FSMTransitionMixin, VersionAdmin):
    """Admin for Area."""

    # Change list
    list_display = ["area_type", "code", "name", "source", "source_id", ]
    list_filter = ["area_type", "source", ]
    search_fields = ("code", "name", )
    date_hierarchy = 'encountered_on'

    # Change view
    form = s2form(AreaEncounter, attrs=S2ATTRS)
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


@admin.register(TaxonAreaEncounter)
class TaxonAreaAdmin(AreaEncounterAdmin):
    """Admin for TaxonArea."""

    # # Change list
    list_display = AreaEncounterAdmin.list_display + ["taxon"]
    list_filter = AreaEncounterAdmin.list_filter + ["taxon"]
    list_select_related = ["taxon", ]
    show_full_result_count = False

    # # Change view
    # form = TaxonAreaEncounterForm
    form = s2form(TaxonAreaEncounter, attrs=S2ATTRS)
    formfield_overrides = FORMFIELD_OVERRIDES
    autocomplete_fields = AreaEncounterAdmin.autocomplete_fields + ["taxon"]
    inlines = [
        # AssociatedSpeciesObservationInline,
        FireHistoryObservationInline
    ]


@admin.register(CommunityAreaEncounter)
class CommunityAreaAdmin(AreaEncounterAdmin):
    """Admin for CommunityArea."""

    # Change list
    list_display = AreaEncounterAdmin.list_display + ["community"]
    list_filter = AreaEncounterAdmin.list_filter + ["community"]
    list_select_related = ["community"]

    # Change view
    form = s2form(CommunityAreaEncounter, attrs=S2ATTRS)
    formfield_overrides = FORMFIELD_OVERRIDES
    fieldsets = ((_('Community'), {
        'classes': ('grp-collapse', 'grp-open', 'wide', 'extrapretty'),
        'fields': ("community", )}
    ),) + AreaEncounterAdmin.fieldsets
    inlines = [
        AssociatedSpeciesObservationInline,
        FireHistoryObservationInline
    ]


@admin.register(AssociatedSpeciesObservation)
class AssociatedSpeciesObservationAdmin(FSMTransitionMixin, VersionAdmin):
    """Associated Species Observation Admin."""

    list_display = ["encounter", "taxon", ]
    form = AssociatedSpeciesObservationForm
    fsm_field = ['status', ]
    autocomplete_fields = ['taxon', ]


@admin.register(FireHistoryObservation)
class FireHistoryObservationAdmin(FSMTransitionMixin, VersionAdmin):
    """FireHistoryObservation Admin."""

    list_display = ["encounter", "last_fire_date", "fire_intensity"]
    form = FireHistoryObservationForm
    fsm_field = ['status', ]
