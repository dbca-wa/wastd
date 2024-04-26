from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Fieldset, Field, Submit, HTML

from .models import Survey


class SurveyChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.make_label()


class SurveyMergeForm(forms.Form):
    survey_duplicates = SurveyChoiceField(
        label="Duplicate surveys",
        queryset=Survey.objects.none(),
        required=False,
    )
    save_button = Submit("save", "Merge duplicate survey", css_class="btn-lg")
    cancel_button = Submit("cancel", "Cancel", css_class="btn-secondary")

    def __init__(self, survey, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["survey_duplicates"].queryset = survey.duplicate_surveys

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Fieldset(
                    "Merge duplicate surveys",
                    HTML(f"<h1>{survey.label_short()}</h1>"),
                    Field("survey_duplicates"),
                ),
                Div(
                    self.save_button,
                    self.cancel_button,
                ),
            ),
        )
