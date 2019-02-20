# -*- coding: utf-8 -*-
"""Conservation forms."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Fieldset, Layout, Submit
from django import forms
# from django.contrib.auth import get_user_model
from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget
from leaflet.forms.widgets import LeafletWidget
from taxonomy.models import Community, Taxon

from conservation.models import (
    ConservationActionCategory,
    ConservationAction,
    # ConservationActivity,
    Document
)
from shared.admin import LEAFLET_SETTINGS
from shared.forms import DateInput  # DateTimeInput
# from wastd.users.models import User


class ConservationActionForm(forms.ModelForm):
    """Common form for ConservationAction."""

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(ConservationActionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Relations',
                'taxa',
                'communities',
                'document',
                'occurrence_area_code',
            ),
            Fieldset(
                'Task',
                'category',
                'instructions',
            ),
            Fieldset(
                'Implementation',
                'implementation_notes',
                'completion_date',
                'expenditure'
            ),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white')
            )
        )

    class Meta:
        """Class options."""

        model = ConservationAction
        fields = (
            "taxa",
            "communities",
            "document",
            "occurrence_area_code",
            "target_area",
            "category",
            "instructions",
            "implementation_notes",
            "completion_date",
            "expenditure")
        widgets = {
            'taxa': ModelSelect2MultipleWidget(
                model=Taxon,
                search_fields=[
                    "taxonomic_name__icontains",
                    "vernacular_names__icontains",
                ]
            ),
            'communities': ModelSelect2MultipleWidget(
                model=Community,
                search_fields=[
                    "code__icontains",
                    "name__icontains",
                    "description__icontains",
                ]
            ),
            'document': ModelSelect2Widget(
                model=Document,
                search_fields=[
                    "title__icontains",
                    "comments__icontains",
                ]
            ),
            'geom': LeafletWidget(attrs=LEAFLET_SETTINGS),
            'category': ModelSelect2Widget(
                model=ConservationActionCategory,
                search_fields=[
                    "code__icontains",
                    "label__icontains",
                    "description__icontains",
                ]
            ),
            'completion_date': DateInput(),
        }
