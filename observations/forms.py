from django import forms
from django.conf import settings
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Fieldset, Field, Submit, HTML

from .models import Survey, Encounter


class SurveyChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.make_label()


class SurveyMergeForm(forms.Form):
    survey_duplicates = SurveyChoiceField(
        label="Duplicate surveys",
        queryset=Survey.objects.none(),
        required=False,
    )
    save_button = Submit("save", "Merge duplicate", css_class="btn-lg")
    cancel_button = Submit("cancel", "Cancel", css_class="btn-secondary")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs["instance"]
        self.fields["survey_duplicates"].queryset = instance.duplicate_surveys
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Fieldset(
                    f"{instance.label_short()} - merge duplicate survey",
                    HTML("<div>Merge the selected survey below into this one and adopt any encounters from the duplicate.</div>"),
                    Field("survey_duplicates"),
                ),
                Div(
                    self.save_button,
                    self.cancel_button,
                    css_class='pb-2',
                ),
            ),
        )


class SurveyCloseDuplicatesForm(forms.ModelForm):

    confirm_button = Submit("confirm", "Confirm", css_class="btn-lg")
    cancel_button = Submit("cancel", "Cancel", css_class="btn-secondary")

    class Meta:
        model = Survey
        exclude = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs["instance"]
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Fieldset(
                    f"Survey {instance.pk} - close {instance.no_duplicates} duplicates",
                    HTML(f"<div>Mark {instance.label_short()} as production, {instance.no_duplicates} duplicates as merged, and adopt all their encounters?</div>"),
                ),
                Div(
                    self.confirm_button,
                    self.cancel_button,
                    css_class='py-2',
                ),
            ),
        )

    def is_valid(self):
        # Bypass all form validation.
        return True


class SurveyMakeProductionForm(SurveyCloseDuplicatesForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs["instance"]
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Fieldset(
                    f"Survey {instance.pk} - make production",
                    HTML(f"<div>Mark {instance.label_short()} as production?</div>"),
                ),
                Div(
                    self.confirm_button,
                    self.cancel_button,
                    css_class='py-2',
                ),
            ),
        )


class EncounterUpdateSurveyForm(forms.ModelForm):
    survey = SurveyChoiceField(
        label="Survey candidates",
        queryset=Survey.objects.none(),
        required=False,
    )
    save_button = Submit("save", "Save", css_class="btn-lg")
    cancel_button = Submit("cancel", "Cancel", css_class="btn-secondary")

    class Meta:
        model = Encounter
        exclude = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs["instance"]
        self.fields["survey"].queryset = instance.get_survey_candidates()
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Fieldset(
                    f"Encounter {instance.pk} - update survey",
                    HTML(f"<div>{ instance } at { instance.when.astimezone(settings.TZ).strftime('%d-%b-%Y %H:%M %Z') }</div>"),
                    Field("survey"),
                ),
                Div(
                    self.save_button,
                    self.cancel_button,
                    css_class='pb-2',
                ),
            ),
        )

    def is_valid(self):
        # Bypass all form validation.
        return True
