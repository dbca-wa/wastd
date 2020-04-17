# -*- coding: utf-8 -*-
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Fieldset, Row, Field, ButtonHolder, Submit, LayoutObject, HTML
from django import forms
from django.forms.models import inlineformset_factory
from django.template.loader import render_to_string
import re

from wastd.observations.models import Encounter, AnimalEncounter, TagObservation


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


class Formset(LayoutObject):
    template = 'observations/formset.html'

    def __init__(self, formset_context_name, helper_context_name=None, template=None, label=None):
        self.formset_context_name = formset_context_name
        self.helper_context_name = helper_context_name
        self.fields = []

        # Overrides class variable with an instance level variable
        if template:
            self.template = template

    def render(self, form, form_style, context, **kwargs):
        formset = context.get(self.formset_context_name)
        helper = context.get(self.helper_context_name)
        if helper:
            helper.form_tag = False

        context.update({'formset': formset, 'helper': helper})
        return render_to_string(self.template, context.flatten())


class BaseForm(forms.ModelForm):
    """Base ModelForm class with a crispy_forms FormHelper.
    """
    save_button = Submit('save', 'Save', css_class='btn-lg')
    cancel_button = Submit('cancel', 'Cancel')

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-xs-12 col-sm-4 col-md-3 col-lg-2'
        self.helper.field_class = 'col-xs-12 col-sm-8 col-md-6 col-lg-4'
        self.helper.help_text_inline = True
        super(BaseForm, self).__init__(*args, **kwargs)


class AnimalEncounterForm(BaseForm):

    class Meta:
        model = AnimalEncounter
        fields = ['where', 'when', 'taxon', 'species', 'health', 'sex', 'maturity', 'checked_for_flipper_tags']

    def __init__(self, *args, **kwargs):
        super(AnimalEncounterForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                Fieldset(
                    'Marine animal observation details',
                    Field('where'),
                    Field('when'),
                    Field('taxon'),
                    Field('species'),
                    Field('health'),
                    Field('sex'),
                    Field('maturity'),
                    Field('checked_for_flipper_tags'),
                ),
                Fieldset(
                    'Flipper tags',
                    HTML('<p>The ID of any tag must be unique within the tag type.</p>'),
                    Formset('flipper_tags', template='observations/formset_simple.html')
                ),
                ButtonHolder(
                    self.save_button,
                    self.cancel_button,
                )
            ),
        )


class TagObservationForm(forms.ModelForm):

    class Meta:
        model = TagObservation
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super(TagObservationForm, self).__init__(*args, **kwargs)
        formtag_prefix = re.sub('-[0-9]+$', '', kwargs.get('prefix', ''))
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.fields['name'].help_text = None
        self.helper.layout = Layout(
            Row(
                Field('name'),
                Field('DELETE', type='hidden'),
                css_class='formset_row-{}'.format(formtag_prefix)
            )
        )


FlipperTagObservationFormSet = inlineformset_factory(
    parent_model=AnimalEncounter,
    model=TagObservation,
    form=TagObservationForm,
    can_delete=True,
    extra=1,
)
