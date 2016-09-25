# -*- coding: utf-8 -*-
"""Forms for WAStD Observations."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout, ButtonHolder, Submit, Div, Field)  # Fieldset, MultiField

from wastd.observations.models import Encounter, AnimalEncounter

class EncounterListFormHelper(FormHelper):
    """django-crispy-forms FormHelper for Encounter."""

    model = Encounter
    # form_class = 'form-horizontal'    # Adding a Filter Button
    form_show_labels = True             # form field labels
    layout = Layout(
        'name',
        'source_id',
        'when',
        ButtonHolder(Submit('submit', 'Filter', css_class='button white right')),
        )




class AnimalEncounterListFormHelper(EncounterListFormHelper):
    """django-crispy-forms FormHelper for AnimalEncounter."""

    model = AnimalEncounter
