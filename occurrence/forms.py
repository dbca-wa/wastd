# -*- coding: utf-8 -*-
"""Occurrence forms."""

from django import forms
from leaflet.forms.widgets import LeafletWidget
from django_select2.forms import ModelSelect2Widget

from .models import (AreaEncounter, TaxonAreaEncounter, CommunityAreaEncounter)
from taxonomy.models import (Taxon, Community)


class AreaEncounterForm(forms.ModelForm):
    """Common form for AreaEncounter."""

    class Meta:
        """Class options."""

        model = AreaEncounter
        fields = ("area_type", "code", "name", "description", "geom", "accuracy", "encountered_on", "encountered_by")
        widgets = {'geom': LeafletWidget(
            attrs={'map_height': '400px', 'map_width': '100%', 'display_raw': 'true', 'map_srid': 4326})}


class TaxonAreaEncounterForm(AreaEncounterForm):
    """Form for TaxonAreaEncounter."""

    class Meta:
        """Class options."""

        model = TaxonAreaEncounter
        fields = ('taxon', "area_type", "code", "name", "description",
                  "geom", "accuracy", "encountered_on", "encountered_by")
        widgets = {
            'taxon': ModelSelect2Widget(
                model=Taxon,
                search_fields=["taxonomic_name__icontains", "vernacular_names__icontains", ]
            ),
            'geom': LeafletWidget(
                attrs={'map_height': '400px', 'map_width': '100%', 'display_raw': 'true', 'map_srid': 4326})}


class CommunityAreaEncounterForm(AreaEncounterForm):
    """Form for CommunityAreaEncounter."""

    class Meta:
        """Class options."""

        model = CommunityAreaEncounter
        fields = ('community', "area_type", "code", "name", "description",
                  "geom", "accuracy", "encountered_on", "encountered_by")
        widgets = {
            'community': ModelSelect2Widget(
                model=Community,
                search_fields=["name__icontains", "code__icontains", ]
            ),
            'geom': LeafletWidget(
                attrs={'map_height': '400px', 'map_width': '100%', 'display_raw': 'true', 'map_srid': 4326})}
