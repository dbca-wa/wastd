# -*- coding: utf-8 -*-
"""Admin module for wastd.observations."""
from __future__ import absolute_import, unicode_literals

# from leaflet.admin import LeafletGeoAdmin
from leaflet.forms.widgets import LeafletWidget

# from django import forms as django_forms
import floppyforms as ff
from django.contrib import admin
# from django.contrib.gis import forms
from django.contrib.gis.db import models as geo_models

from django.utils.translation import ugettext_lazy as _
from easy_select2 import select2_modelform as s2form
# from easy_select2.widgets import Select2
from fsm_admin.mixins import FSMTransitionMixin
from reversion.admin import VersionAdmin

from taxonomy.models import Taxon
# from wastd.observations.filters import LocationListFilter
from rest_framework.authtoken.admin import TokenAdmin

TokenAdmin.raw_id_fields = ('user',)


@admin.register(Taxon)
class TaxonAdmin(VersionAdmin, admin.ModelAdmin):
    """Admin for Taxon."""

    save_on_top = True
    # date_hierarchy = 'datetime'
    list_display = (
        'name_id', 'rank_name', 'full_name', 'vernacular', 'all_vernaculars',
        'author', 'reference', 'naturalised_status', 'naturalised_certainty',
        'is_eradicated', 'informal', 'is_current', 'comments',
        'added_by', 'added_on', 'updated_by', 'updated_on',
    )
    list_filter = (
        'rank_name', 'is_current', 'naturalised_status', 'naturalised_certainty',
        'is_eradicated', 'informal',
    )
    search_fields = (
        'name_id', 'name', 'full_name', 'vernacular', 'all_vernaculars', 'author')
    # autocomplete_lookup_fields = {'fk': ['handler', 'recorder', ], }

    # def type_display(self, obj):
    #     """Make tag type human readable."""
    #     return obj.get_tag_type_display()
    # type_display.short_description = 'Tag Type'
