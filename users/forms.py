from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Fieldset, Field, Submit, HTML

from observations.models import Area
from .models import User


class UserMergeForm(forms.Form):
    user_old = forms.ModelChoiceField(
        label="User profile to be transferred and closed",
        queryset=User.objects.all(),
    )
    user_new = forms.ModelChoiceField(
        label="User profile to be retained and to receive all records linked against the duplicate profile",
        queryset=User.objects.all(),
    )
    save_button = Submit("save", "Merge User Profiles", css_class="btn-lg")
    cancel_button = HTML('<a class="btn btn-secondary" href="/">Cancel</a>')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Fieldset(
                    "Merge Duplicate User Profiles",
                    Field("user_old"),
                    Field("user_new"),
                ),
                Div(
                    self.save_button,
                    self.cancel_button,
                ),
            ),
        )


class TransferForm(forms.Form):
    user_old = forms.ModelChoiceField(
        label="Transfer data incorrectly linked to User",
        queryset=User.objects.all(),
    )
    area = forms.ModelChoiceField(
        label="Restrict data transfer to Area",
        queryset=Area.objects.filter(area_type=Area.AREATYPE_LOCALITY),
    )
    user_new = forms.ModelChoiceField(
        label="Transfer data to User",
        queryset=User.objects.all(),
    )
    save_button = Submit("save", "Transfer data", css_class="btn-lg")
    cancel_button = HTML('<a class="btn btn-secondary" href="/">Cancel</a>')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Fieldset(
                    "Transfer data to another user",
                    Field("user_old"),
                    Field("area"),
                    Field("user_new"),
                ),
                Div(
                    self.save_button,
                    self.cancel_button,
                ),
            ),
        )
