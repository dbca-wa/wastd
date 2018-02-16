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
    """Admin for Taxon.

"name_id": 20887,
        "kingdom_id": 3,
        "rank_id": 180,
        "rank_name": "Genus",
        "name1": "Paraceterach",
        "name2": null,
        "rank3": null,
        "name3": null,
        "rank4": null,
        "name4": null,
        "pub_id": 582,
        "vol_info": "75",
        "pub_year": 1947,
        "is_current": "Y",
        "origin": null,
        "naturalised_status": null,
        "naturalised_certainty": null,
        "is_eradicated": null,
        "naturalised_comments": null,
        "informal": null,
        "form_desc_yr": null,
        "form_desc_mn": null,
        "form_desc_dy": null,
        "comments": null,
        "added_by": "HERBIE",
        "added_on": "2004-12-09Z",
        "updated_by": "SUEC",
        "updated_on": "2010-02-03Z",
        "family_code": "008",
        "family_nid": 22721,
        "name": "Paraceterach",
        "author": "Copel.",
        "reference": "Gen.Fil.\n75\n(1947)",
        "editor": null,
        "vernacular": null,
        "all_vernaculars": null,
        "full_name": "Paraceterach\nCopel.",
    """

    save_on_top = True
    # date_hierarchy = 'datetime'
    list_display = ('name_id', 'name', 'full_name',
                    'vernacular', 'kingdom_id', 'rank_id', 'rank_name',
                    'family_code', 'family_nid', 'author', 'reference')
    list_filter = ('kingdom_id', 'rank_id', 'rank_name',
                   'family_code', 'family_nid', 'author',)
    search_fields = ('name_id', 'name', 'full_name',)
    # autocomplete_lookup_fields = {'fk': ['handler', 'recorder', ], }

    # def type_display(self, obj):
    #     """Make tag type human readable."""
    #     return obj.get_tag_type_display()
    # type_display.short_description = 'Tag Type'
