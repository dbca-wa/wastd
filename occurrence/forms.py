# -*- coding: utf-8 -*-
"""Occurrence forms."""

from bootstrap_datepicker_plus import DateTimePickerInput, DatePickerInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Fieldset, Layout, Submit
from django import forms
from django.contrib.auth import get_user_model
from django_select2.forms import ModelSelect2Widget
from leaflet.forms.widgets import LeafletWidget
from taxonomy.models import Community, Taxon

from .models import (
    AreaEncounter,
    CommunityAreaEncounter,
    TaxonAreaEncounter,
    AssociatedSpeciesObservation,
    FireHistoryObservation
)

# from wastd.users.models import User


LEAFLET_ATTRS = {'map_height': '400px', 'map_width': '100%', 'display_raw': 'true', 'map_srid': 4326}
S2ATTRS = {'width': '350px'}


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


# ----------------------------------------------------------------------------#
# ObservationGroup forms
#
class AssociatedSpeciesObservationForm(forms.ModelForm):
    """Associated Species Observation Form."""

    class Meta:
        """Class options."""

        model = AssociatedSpeciesObservation
        fields = ("encounter", "taxon",)
        widgets = {
            "encounter": ModelSelect2Widget(
                model=AreaEncounter,
                search_fields=["code", "name", "area_type", ],
                attrs={'size': 80}
            ),
            "taxon": ModelSelect2Widget(
                model=Taxon,
                search_fields=["taxonomic_name__icontains", "vernacular_names__icontains", ],
                attrs={'size': 80}
            ),
        }

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(AssociatedSpeciesObservationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Observation made during encounter",
                "encounter"
            ),
            Fieldset(
                'Associated Species',
                'taxon',
            ),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white')
            )
        )


class FireHistoryObservationForm(forms.ModelForm):
    """Fire History Observation Form."""

    class Meta:
        """Class options."""

        model = FireHistoryObservation
        fields = ("encounter", "last_fire_date", "fire_intensity")
        widgets = {
            "encounter": ModelSelect2Widget(
                model=AreaEncounter,
                search_fields=["code", "name", "area_type", ],
                attrs={'size': 80}
            ),
            'last_fire_date': DatePickerInput(),
        }

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(FireHistoryObservationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Observation made during encounter",
                "encounter"
            ),
            Fieldset(
                "Fire History",
                "last_fire_date",
                "fire_intensity"
            ),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white')
            )
        )
