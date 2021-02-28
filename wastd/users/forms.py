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
        label="User profile to be retained",
        queryset = User.objects.all(),
        widget=UserWidget()
    )
    save_button = Submit('save', 'Merge User Profiles', css_class='btn-lg')
    cancel_button = Submit('cancel', 'Cancel', css_class='btn-secondary')

    def __init__(self, *args, **kwargs):
        super(MergeForm, self).__init__(*args, **kwargs)
        # self.fields["old_pk"] = kwargs.get("old_pk") # TODO URL include old_pk
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

    # def transfer_user(self):
    #     logger.info(
    #         "wastd.users.forms.MergeForm.transfer_user "
    #         "with old user {0}, new user {1}".format(self.old, self.new))
    #     transfer_user(self.old, self.new)
