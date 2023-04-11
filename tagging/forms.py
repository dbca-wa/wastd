from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Div, HTML
from crispy_forms.bootstrap import InlineCheckboxes
from django import forms
from easy_select2 import Select2
from .models import Turtle, TurtleObservation, TurtleTag, TurtlePitTag, TurtleTagObservation, Place


class TurtleSearchForm(forms.Form):
    turtle_id = forms.IntegerField(label=False, required=False)
    tag_id = forms.CharField(label=False, max_length=64, required=False)
    pit_tag_id = forms.CharField(label=False, max_length=64, required=False)
    # sex
    # species
    # location

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Field('turtle_id', placeholder='Turtle ID', css_class='mr-1'),
            Field('tag_id', placeholder='Tag ID', css_class='mx-1'),
            Field('pit_tag_id', placeholder='Pit tag ID', css_class='mx-1'),
            Submit('search', 'Search', css_class='btn ml-1'),
        )


class BaseFormHelper(FormHelper):
    """Base FormHelper class, with common options set.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_class = 'form-horizontal'
        self.form_method = 'POST'
        self.label_class = 'col-xs-12 col-sm-4 col-md-3 col-lg-2'
        self.field_class = 'col-xs-12 col-sm-8 col-md-6 col-lg-4'
        self.help_text_inline = True
        self.attrs = {'novalidate': ''}


class BaseForm(forms.ModelForm):
    """Base ModelForm class for referral models.
    """
    save_button = Submit('save', 'Save', css_class='btn-lg')
    cancel_button = Submit('cancel', 'Cancel', css_class='btn-secondary')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = BaseFormHelper()


class TurtleCreateForm(BaseForm):
    FLIPPER_CHOICES = (
        ('l1', 'Left flipper scale closest to body'),
        ('l2', 'Left flipper scale 2nd from body'),
        ('l3', 'Left flipper scale 3rd from body'),
        ('r1', 'Right flipper scale closest to body'),
        ('r2', 'Right flipper scale 2nd from body'),
        ('r3', 'Right flipper scale 3rd from body'),
    )
    comments = forms.CharField(required=False)
    prev_tags_lost = forms.BooleanField(required=False, label='All previous tags and IDs lost')
    scars_not_checked = forms.BooleanField(required=False, label='Tag scars were not checked')
    flipper_tag_scars = forms.MultipleChoiceField(choices=FLIPPER_CHOICES, required=False)

    class Meta:
        model = Turtle
        fields = (
            'species', 'sex', 'location', 'name', 'comments', 'prev_tags_lost', 'scars_not_checked',
            'flipper_tag_scars',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define the form layout.
        self.helper.layout = Layout(
            'species',
            'sex',
            'name',
            'location',
            'comments',
            'prev_tags_lost',
            'scars_not_checked',
            Div(
                HTML('Tick the scale(s) that have tag scars:'),
            ),
            InlineCheckboxes('flipper_tag_scars'),
            Div(
                self.save_button,
                self.cancel_button,
                css_class='offset-sm-4 offset-md-3 offset-lg-2 col-xs-12 col-sm-8 col-md-6 col-lg-4')
        )


class TurtleObservationCreateForm(BaseForm):

    class Meta:
        model = TurtleObservation
        exclude = ('turtle', 'observation_date_old')


class TurtleObservationAdminForm(forms.ModelForm):
    place = forms.ModelChoiceField(queryset=Place.objects.all(), widget=Select2())

    class Meta:
        fields = '__all__'
        model = TurtleObservation


class TurtleTagUpdateForm(forms.ModelForm):
    """A basic placeholder ModelForm, used for the 'tags update' view.
    """
    class Meta:
        model = Turtle
        fields = ('comments',)


class TurtleTagForm(forms.ModelForm):
    comments = forms.CharField(required=False)

    class Meta:
        model = TurtleTag
        fields = ('serial', 'status', 'comments')


# Define a formset class to contain TurtleTagForm instances.
# Reference: https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/#model-formsets
TurtleTagFormSet = forms.inlineformset_factory(
    parent_model=Turtle,
    model=TurtleTag,
    form=TurtleTagForm,
    extra=1,
    can_delete=False,
    max_num=6,
)


class TurtleTagFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_class = 'form-inline'
        # Override the table inline formset template (required to properly hide the "hidden" form).
        self.template = 'tagging/table_inline_formset.html'
        self.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.add_input(Submit('cancel', 'Cancel', css_class='btn-secondary'))


class TurtlePitTagForm(forms.ModelForm):
    POSITION_CHOICES = (
        (None, '----'),
        ('LF', 'Left front'),
        ('RF', 'Right front'),
        ('LR', 'Left rear'),
        ('RR', 'Right rear'),
    )
    position = forms.ChoiceField(required=False, choices=POSITION_CHOICES)

    class Meta:
        model = TurtlePitTag
        fields = ('serial', 'position')


PitTagFormSet = forms.inlineformset_factory(
    parent_model=Turtle,
    model=TurtlePitTag,
    form=TurtlePitTagForm,
    extra=1,
    can_delete=False,
    max_num=4,
)


class TurtleTagObservationForm(forms.ModelForm):
    comments = forms.CharField(required=False)

    class Meta:
        model = TurtleTagObservation
        fields = ('tag', 'status', 'position', 'barnacles', 'comments')


TurtleTagObservationFormSet = forms.inlineformset_factory(
    parent_model=TurtleObservation,
    model=TurtleTagObservation,
    form=TurtleTagObservationForm,
    can_delete=False,
)
