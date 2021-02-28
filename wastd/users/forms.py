import logging
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Fieldset, Row, Field, ButtonHolder, Submit, LayoutObject, HTML

from .models import User
from .utils import transfer_user
from .widgets import UserWidget

logger = logging.getLogger(__name__)

class MergeForm(forms.Form):
    old = forms.ModelChoiceField(
        label="User profile to be transferred and closed",
        queryset = User.objects.all(),
        widget=UserWidget()
    )
    new = forms.ModelChoiceField(
        label="User profile to be retained and to receive all records linked against the duplicate profile",
        queryset = User.objects.all(),
        widget=UserWidget()
    )
    save_button = Submit('save', 'Merge User Profiles', css_class='btn-lg')
    cancel_button = Submit('cancel', 'Cancel', css_class='btn-secondary')

    def __init__(self, *args, **kwargs):
        """Initialize the form with a custom layout and a crispy_forms helper."""
        super(MergeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Fieldset(
                    'Merge Duplicate User Profiles',
                    Field('old'),
                    Field('new'),
                    ),
                Div(
                    self.save_button,
                    self.cancel_button,
                    # css_class='offset-sm-4 offset-md-3 offset-lg-2',
                )
            ),
        )
