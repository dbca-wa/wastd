# -*- coding: utf-8 -*-
"""Occurrence forms."""

from django import forms
from django.contrib.auth import get_user_model

from leaflet.forms.widgets import LeafletWidget
from django_select2.forms import ModelSelect2Widget
from bootstrap_datepicker_plus import DateTimePickerInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit

from .models import (AreaEncounter, TaxonAreaEncounter, CommunityAreaEncounter)
from taxonomy.models import (Taxon, Community)
# from wastd.users.models import User


LEAFLET_ATTRS = {'map_height': '400px', 'map_width': '100%', 'display_raw': 'true', 'map_srid': 4326}


class AreaEncounterForm(forms.ModelForm):
    """Common form for AreaEncounter."""

    class Meta:
        """Class options."""

        model = AreaEncounter
        fields = ("area_type", "code", "name", "description", "geom", "accuracy", "encountered_on", "encountered_by")
        widgets = {'geom': LeafletWidget(
            attrs=LEAFLET_ATTRS)}


class TaxonAreaEncounterForm(AreaEncounterForm):
    """Form for TaxonAreaEncounter."""

    class Meta:
        """Class options."""

        model = TaxonAreaEncounter
        fields = ('taxon', "area_type", "code", "name", "description",
                  "geom", "point", "accuracy", "encountered_on", "encountered_by")
        widgets = {
            'taxon': ModelSelect2Widget(
                model=Taxon,
                search_fields=["taxonomic_name__icontains", "vernacular_names__icontains", ]
            ),
            'geom': LeafletWidget(attrs=LEAFLET_ATTRS),
            'point': LeafletWidget(attrs=LEAFLET_ATTRS),
            'encountered_on': DateTimePickerInput(options={"format": "D/MM/YYYY HH:mm"}),
            'encountered_by': ModelSelect2Widget(
                model=get_user_model(),
                search_fields=[
                    "name__icontains",
                    "username__icontains",
                    "role__icontains",
                    "email__icontains"]
            ),
        }

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(TaxonAreaEncounterForm, self).__init__(*args, **kwargs)
        self.fields['area_type'].choices = AreaEncounter.TAXON_AREA_TYPES
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Who',
                'encountered_by',
            ),
            Fieldset(
                'When',
                'encountered_on',
            ),
            Fieldset(
                'What',
                'taxon',
                'description',
            ),
            Fieldset(
                'Where',
                'area_type',
                'code',
                'geom',
                'point',
                'accuracy',
            ),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white')
            )
        )


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
            'geom': LeafletWidget(attrs=LEAFLET_ATTRS),
            'encountered_on': DateTimePickerInput(options={"format": "D/MM/YYYY HH:mm"}),
            'encountered_by': ModelSelect2Widget(
                model=get_user_model(),
                search_fields=[
                    "name__icontains",
                    "username__icontains",
                    "role__icontains",
                    "email__icontains"
                ]
            ),
        }

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(CommunityAreaEncounterForm, self).__init__(*args, **kwargs)
        self.fields['area_type'].choices = AreaEncounter.COMMUNITY_AREA_TYPES
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Who',
                'encountered_by',
            ),
            Fieldset(
                'When',
                'encountered_on',
            ),
            Fieldset(
                'What',
                'community',
                'description',
            ),
            Fieldset(
                'Where',
                'area_type',
                'code',
                'geom',
                'accuracy',
            ),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white')
            )
        )
