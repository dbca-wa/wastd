import logging
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Fieldset, Field, Submit, HTML

from observations.models import Area
from .models import User
from .widgets import UserWidget

logger = logging.getLogger(__name__)


class MergeForm(forms.Form):
    old = forms.ModelChoiceField(
        label="User profile to be transferred and closed",
        queryset=User.objects.all(),
        widget=UserWidget(),
    )
    new = forms.ModelChoiceField(
        label="User profile to be retained and to receive all records linked against the duplicate profile",
        queryset=User.objects.all(),
        widget=UserWidget(),
    )
    save_button = Submit("save", "Merge User Profiles", css_class="btn-lg")
    cancel_button = HTML('<a class="btn btn-secondary" href="/">Cancel</a>')

    def __init__(self, *args, **kwargs):
        """Initialize the form with a custom layout and a crispy_forms helper."""
        super(MergeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Fieldset(
                    "Merge Duplicate User Profiles",
                    Field("old"),
                    Field("new"),
                ),
                Div(
                    self.save_button,
                    self.cancel_button,
                ),
            ),
        )


class TransferForm(forms.Form):
    old = forms.ModelChoiceField(
        label="Transfer data incorrectly linked to User",
        queryset=User.objects.all(),
        widget=UserWidget(),
    )
    area = forms.ModelChoiceField(
        label="Restrict data transfer to Area",
        queryset=Area.objects.filter(area_type=Area.AREATYPE_LOCALITY),
    )
    new = forms.ModelChoiceField(
        label="Transfer data to User", queryset=User.objects.all(), widget=UserWidget()
    )
    save_button = Submit("save", "Transfer data", css_class="btn-lg")
    cancel_button = HTML('<a class="btn btn-secondary" href="/">Cancel</a>')

    def __init__(self, *args, **kwargs):
        """Initialize the form with a custom layout and a crispy_forms helper."""
        super(TransferForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Fieldset(
                    "Transfer data to another user",
                    Field("old"),
                    Field("area"),
                    Field("new"),
                ),
                Div(
                    self.save_button,
                    self.cancel_button,
                ),
            ),
        )
