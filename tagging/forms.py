from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Submit, Div, HTML
from crispy_forms.bootstrap import FormActions
from datetime import datetime
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django_select2.forms import Select2Widget
from easy_select2 import Select2

from users.models import User
from .models import (
    TurtleSpecies,
    Place,
    Turtle,
    TurtleObservation,
    TurtleTag,
    TurtlePitTag,
    TurtleDamage,
    TurtleSample,
)


BODY_PART_CHOICES = (
    (None, ''),
    ('A', 'Carapace - entire'),
    ('B', 'Left front flipper'),
    ('C', 'Right front flipper'),
    ('D', 'Left rear flipper'),
    ('E', 'Right rear flipper'),
    ('H', 'Head'),
    ('I', 'Center mid-carapace'),
    ('J', 'Right front carapace'),
    ('K', 'Left front carapace'),
    ('L', 'Left rear carapace'),
    ('M', 'Right rear carapace'),
    ('N', 'Front mid-carapace'),
    ('O', 'Rear mid-carapace'),
    ('P', 'Plastron - entire'),
    ('T', 'Tail'),
    ('W', 'Whole animal'),
)
DAMAGE_CHOICES = (
    (None, ''),
    ('1', 'Tip off - flipper'),
    ('2', 'Lost from nail - flipper'),
    ('3', 'Lost half - flipper'),
    ('4', 'Lost whole - flipper'),
    ('5', 'Minor Wounds or cuts'),
    ('6', 'Major Wounds or cuts'),
    ('7', 'Deformity'),
)


class TurtleAddForm(forms.ModelForm):
    """A modified form to allow some additional recordkeeping on creation of new Turtle instances.
    """

    class Meta:
        model = Turtle
        fields = (
            'species',
            'sex',
            'name',
            'comments',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['species'].required = True


class TurtleChangeForm(forms.ModelForm):
    """A form to allow changes to existing Turtle instances.
    """
    class Meta:
        model = Turtle
        fields = (
            'species',
            'sex',
            'name',
            'cause_of_death',
            'comments',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['species'].required = True


class TurtleObservationForm(forms.ModelForm):
    place = forms.ModelChoiceField(queryset=Place.objects.all(), widget=Select2())

    class Meta:
        model = TurtleObservation
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].label = 'Observation type'
        self.fields['alive'].required = True
        self.fields['measurer'].required = True
        self.fields['measurer_reporter'].required = True
        self.fields['place'].required = True
        self.fields['activity'].required = True

    def clean_observed(self):
        observed = self.cleaned_data['observed']
        if observed >= datetime.now().astimezone(settings.AWST):
            raise ValidationError("Observations cannot be recorded in the future")
        return observed


class TurtleFlipperDamageForm(forms.ModelForm):
    FLIPPER_PART_CHOICES = (
        ('B', 'Left front flipper'),
        ('C', 'Right front flipper'),
        ('D', 'Left rear flipper'),
        ('E', 'Right rear flipper'),
    )
    FLIPPER_DAMAGE_CHOICES = (
        ('0', 'None significant'),
        ('1', 'Tip off'),
        ('2', 'Lost from Nail'),
        ('3', 'Lost half'),
        ('4', 'Lost whole'),
        ('7', 'Deformity'),
    )
    body_part = forms.ChoiceField(required=True, label='flipper', choices=FLIPPER_PART_CHOICES)
    damage = forms.ChoiceField(required=True, choices=FLIPPER_DAMAGE_CHOICES)

    class Meta:
        model = TurtleDamage
        fields = ('body_part', 'damage', 'comments')


class TurtleInjuryForm(forms.ModelForm):
    body_part = forms.ChoiceField(required=True, choices=BODY_PART_CHOICES)
    damage = forms.ChoiceField(required=True, choices=DAMAGE_CHOICES)

    class Meta:
        model = TurtleDamage
        fields = ('body_part', 'damage', 'comments')


class TurtleSampleForm(forms.ModelForm):

    class Meta:
        model = TurtleSample
        fields = ('tissue_type', 'label')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['label'].required = True


class TurtleTagForm(forms.ModelForm):

    class Meta:
        model = TurtleTag
        fields = ('serial', 'side', 'status', 'return_date', 'return_condition', 'comments')

    def clean_serial(self):
        """Only validate serial number uniqueness on creation of new tags.
        """
        serial = self.cleaned_data['serial'].strip()
        if not self.instance.pk:
            if TurtleTag.objects.filter(serial__iexact=serial).exists():
                existing_tag = TurtleTag.objects.get(serial__iexact=serial)
                if existing_tag.turtle:
                    raise ValidationError(f"Tag with serial {existing_tag.serial} already exists and is assigned to {existing_tag.turtle}")
                else:
                    raise ValidationError(f"Tag with serial {existing_tag.serial} already exists")
            return serial
        return serial


class TurtleTagAddForm(TurtleTagForm):
    """Override the normal form, to be used when creating a new turtle.
    """
    TAG_STATUS_CHOICES = (
        ('ATT', 'Tag attached to turtle'),
        ('POOR', 'Poor fix on turtle'),
    )
    status = forms.ChoiceField(required=True, choices=TAG_STATUS_CHOICES)

    class Meta(TurtleTagForm.Meta):
        fields = ('serial', 'side', 'status', 'comments')


class TurtlePitTagForm(forms.ModelForm):

    class Meta:
        model = TurtlePitTag
        fields = ('serial', 'status', 'return_date', 'return_condition', 'comments')

    def clean_serial(self):
        """Only validate serial number uniqueness on creation of new tags.
        """
        serial = self.cleaned_data['serial'].strip()
        if not self.instance.pk:
            if TurtlePitTag.objects.filter(serial__iexact=serial).exists():
                existing_tag = TurtlePitTag.objects.get(serial__iexact=serial)
                if existing_tag.turtle:
                    raise ValidationError(f"Pit tag with serial {existing_tag.serial} already exists and is assigned to {existing_tag.turtle}")
                else:
                    raise ValidationError(f"Pit tag with serial {existing_tag.serial} already exists")
        return serial


class TurtlePitTagAddForm(TurtlePitTagForm):
    """Override the normal form, to be used when creating a new turtle.
    """
    POSITION_CHOICES = (
        ('LF', 'Left front'),
        ('RF', 'Right front'),
        ('LR', 'Left rear'),
        ('RR', 'Right rear'),
    )
    PIT_TAG_STATUS_CHOICES = (
        ('ATT', 'Tag attached to turtle - Read OK'),
        ('POOR', 'Applied new - Did not read'),
    )
    status = forms.ChoiceField(required=True, choices=PIT_TAG_STATUS_CHOICES)
    position = forms.ChoiceField(required=False, choices=POSITION_CHOICES)

    class Meta(TurtlePitTagForm.Meta):
        fields = ('serial', 'status', 'position', 'comments')


class Row(Div):
    css_class = 'row'


class UserChoiceField(forms.ModelChoiceField):

    def __init__(self, *args, **kwargs):
        # TODO: determine if there is a better filter for users.
        kwargs['queryset'] = User.objects.filter(is_active=True, alive=True)
        kwargs['widget'] = Select2Widget
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        return obj.name


class AjaxUserChoiceField(forms.ChoiceField):
    """A basic empty ChoiceField intended to be populated via an Ajax call.
    """
    def valid_value(self, value):
        '''Provided value is always a valid choice, even when no choices are defined.
        Reference: https://github.com/django/django/blob/main/django/forms/fields.py
        '''
        return True


class TurtleTagObservationAddForm(forms.Form):

    SEX_CHOICES = (
        (None, ''),
        ('F', 'Female'),
        ('M', 'Male'),
        ('U', 'Unknown'),
    )
    CHECKED_CHOICES = (
        (None, ''),
        ('na', 'Did not check'),
        ('y', 'Yes'),
        ('n', 'No'),
    )
    YES_NO_CHOICES = (
        (None, ''),
        ('y', 'Yes'),
        ('n', 'No'),
    )
    SCALE_CHOICES = (
        (None, ''),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
    )
    SAMPLE_TYPE_CHOICES = [(None, '')] + list(TurtleSample.TISSUE_TYPE_CHOICES)
    NEST_LOCATION_CHOICES = (
        (None, 'No nest'),
        ('C', 'Below high water mark'),
        ('B', 'At high water mark'),
        ('A', 'Above high water mark'),
        ('D', 'Edge of vegetation/slope'),
        ('E', 'In vegetation/dune'),
        ('?', 'Other'),
    )
    NESTED_CHOICES = (
        (None, ''),
        ('yes', 'Yes, saw eggs'),
        ('possible', "Possible, didn't see eggs"),
        ('no-nest', 'No nest'),
        ('uncertain', 'Uncertain'),
        ('dnc', "Didn't check"),
    )

    existing_turtle_id = forms.IntegerField(initial=0, widget=forms.HiddenInput)
    place = forms.ModelChoiceField(Place.objects.all(), label='Location/beach', widget=Select2Widget)
    latitude = forms.FloatField(required=False)
    longitude = forms.FloatField(required=False)
    species = forms.ModelChoiceField(TurtleSpecies.objects.all())
    observed = forms.DateTimeField(label='Observed at', input_formats=settings.DATETIME_INPUT_FORMATS)
    sex = forms.ChoiceField(choices=SEX_CHOICES)
    recorded_by = AjaxUserChoiceField()

    old_flipper_tags = forms.ChoiceField(choices=CHECKED_CHOICES, help_text='Does this turtle have old flipper tags?')
    tag_l1 = forms.CharField(required=False)
    tag_l1_new = forms.ChoiceField(choices=YES_NO_CHOICES, required=False)
    tag_l1_scale = forms.ChoiceField(choices=SCALE_CHOICES, required=False)
    tag_l1_barnacles = forms.ChoiceField(choices=YES_NO_CHOICES, required=False)
    tag_l1_secure = forms.ChoiceField(choices=YES_NO_CHOICES, required=False)
    tag_l1_scars = forms.ChoiceField(choices=YES_NO_CHOICES, required=False)
    tag_l2 = forms.CharField(required=False)
    tag_l2_new = forms.ChoiceField(choices=YES_NO_CHOICES, required=False)
    tag_l2_scale = forms.ChoiceField(choices=SCALE_CHOICES, required=False)
    tag_l2_barnacles = forms.ChoiceField(choices=YES_NO_CHOICES, required=False)
    tag_l2_secure = forms.ChoiceField(choices=YES_NO_CHOICES, required=False)
    tag_l2_scars = forms.ChoiceField(choices=YES_NO_CHOICES, required=False)

    tag_r1 = forms.CharField(required=False)
    tag_r1_new = forms.ChoiceField(choices=YES_NO_CHOICES, required=False)
    tag_r1_scale = forms.ChoiceField(choices=SCALE_CHOICES, required=False)
    tag_r1_barnacles = forms.ChoiceField(choices=YES_NO_CHOICES, required=False)
    tag_r1_secure = forms.ChoiceField(choices=YES_NO_CHOICES, required=False)
    tag_r1_scars = forms.ChoiceField(choices=YES_NO_CHOICES, required=False)
    tag_r2 = forms.CharField(required=False)
    tag_r2_new = forms.ChoiceField(choices=YES_NO_CHOICES, required=False)
    tag_r2_scale = forms.ChoiceField(choices=SCALE_CHOICES, required=False)
    tag_r2_barnacles = forms.ChoiceField(choices=YES_NO_CHOICES, required=False)
    tag_r2_secure = forms.ChoiceField(choices=YES_NO_CHOICES, required=False)
    tag_r2_scars = forms.ChoiceField(choices=YES_NO_CHOICES, required=False)

    pit_tag_present = forms.ChoiceField(choices=CHECKED_CHOICES, help_text='Does this turtle have any pit tags present?')
    pit_tag_l = forms.CharField(required=False)
    pit_tag_l_new = forms.ChoiceField(choices=YES_NO_CHOICES, required=False)
    pit_tag_r = forms.CharField(required=False)
    pit_tag_r_new = forms.ChoiceField(choices=YES_NO_CHOICES, required=False)

    tagged_by = AjaxUserChoiceField(required=False)
    tags_recorded_by = AjaxUserChoiceField(required=False)

    ccl_min = forms.IntegerField(required=False, label='CCL min (mm)')
    ccl_max = forms.IntegerField(required=False, label='CCL max (mm)')
    cc_width = forms.IntegerField(required=False, label='CC width (mm)')
    weight = forms.FloatField(required=False, label='Weight (kg)')
    measured_by = AjaxUserChoiceField(required=False)
    measurements_recorded_by = AjaxUserChoiceField(required=False)

    nest_location = forms.ChoiceField(choices=NEST_LOCATION_CHOICES, required=False)
    nesting_interrupted = forms.ChoiceField(label='Was the nesting process interruped?', choices=YES_NO_CHOICES, required=False)
    nested = forms.ChoiceField(label='Did the turtle lay?', choices=NESTED_CHOICES, required=False)

    damage = forms.ChoiceField(choices=CHECKED_CHOICES, help_text='Does this turtle have damage/distinguishing features?')
    damage_1_part = forms.ChoiceField(choices=BODY_PART_CHOICES, required=False)
    damage_1_type = forms.ChoiceField(choices=DAMAGE_CHOICES, required=False)
    damage_2_part = forms.ChoiceField(choices=BODY_PART_CHOICES, required=False)
    damage_2_type = forms.ChoiceField(choices=DAMAGE_CHOICES, required=False)
    damage_3_part = forms.ChoiceField(choices=BODY_PART_CHOICES, required=False)
    damage_3_type = forms.ChoiceField(choices=DAMAGE_CHOICES, required=False)
    damage_4_part = forms.ChoiceField(choices=BODY_PART_CHOICES, required=False)
    damage_4_type = forms.ChoiceField(choices=DAMAGE_CHOICES, required=False)
    damage_5_part = forms.ChoiceField(choices=BODY_PART_CHOICES, required=False)
    damage_5_type = forms.ChoiceField(choices=DAMAGE_CHOICES, required=False)

    biopsy_no = forms.CharField(required=False)
    satellite_tag_no = forms.CharField(required=False)
    photos = forms.ChoiceField(choices=YES_NO_CHOICES, required=False)
    sample_1_type = forms.ChoiceField(choices=SAMPLE_TYPE_CHOICES, required=False)
    sample_1_label = forms.CharField(required=False)
    sample_2_type = forms.ChoiceField(choices=SAMPLE_TYPE_CHOICES, required=False)
    sample_2_label = forms.CharField(required=False)
    comments = forms.CharField(widget=forms.Textarea, required=False)

    save_button = Submit('save', 'Save', css_class='btn-lg')
    cancel_button = Submit('cancel', 'Cancel', css_class='btn-secondary')

    def __init__(self, *args, **kwargs):
        if "turtle_id" in kwargs:
            turtle_id = kwargs.pop("turtle_id")
        else:
            turtle_id = None
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.attrs = {'novalidate': ''}  # Disable default in-browser form validation.

        self.fields['recorded_by'].widget.attrs['class'] = 'select-user-choice'
        self.fields['tagged_by'].widget.attrs['class'] = 'select-user-choice'
        self.fields['tags_recorded_by'].widget.attrs['class'] = 'select-user-choice'
        self.fields['measured_by'].widget.attrs['class'] = 'select-user-choice'
        self.fields['measurements_recorded_by'].widget.attrs['class'] = 'select-user-choice'
        if turtle_id:
            self.fields['species'].disabled = True
            self.fields['sex'].disabled = True

        # Remove labels from some fields
        self.fields['tag_l1'].label = False
        self.fields['tag_l1_new'].label = False
        self.fields['tag_l1_scale'].label = False
        self.fields['tag_l1_barnacles'].label = False
        self.fields['tag_l1_secure'].label = False
        self.fields['tag_l1_scars'].label = False
        self.fields['tag_l2'].label = False
        self.fields['tag_l2_new'].label = False
        self.fields['tag_l2_scale'].label = False
        self.fields['tag_l2_barnacles'].label = False
        self.fields['tag_l2_secure'].label = False
        self.fields['tag_l2_scars'].label = False
        self.fields['tag_r1'].label = False
        self.fields['tag_r1_new'].label = False
        self.fields['tag_r1_scale'].label = False
        self.fields['tag_r1_barnacles'].label = False
        self.fields['tag_r1_secure'].label = False
        self.fields['tag_r1_scars'].label = False
        self.fields['tag_r2'].label = False
        self.fields['tag_r2_new'].label = False
        self.fields['tag_r2_scale'].label = False
        self.fields['tag_r2_barnacles'].label = False
        self.fields['tag_r2_secure'].label = False
        self.fields['tag_r2_scars'].label = False
        self.fields['pit_tag_l'].label = False
        self.fields['pit_tag_l_new'].label = False
        self.fields['pit_tag_r'].label = False
        self.fields['pit_tag_r_new'].label = False
        self.fields['damage_1_part'].label = False
        self.fields['damage_1_type'].label = False
        self.fields['damage_2_part'].label = False
        self.fields['damage_2_type'].label = False
        self.fields['damage_3_part'].label = False
        self.fields['damage_3_type'].label = False
        self.fields['damage_4_part'].label = False
        self.fields['damage_4_type'].label = False
        self.fields['damage_5_part'].label = False
        self.fields['damage_5_type'].label = False

        self.helper.layout = Layout(
            'existing_turtle_id',

            Fieldset(
                None,
                Row(
                    Field('place', wrapper_class='form-group col-8'),
                    Field('species', wrapper_class='form-group col-4'),
                ),
                Row(
                    Field('longitude', wrapper_class='form-group col-4'),
                    Field('latitude', wrapper_class='form-group col-4'),
                    Field('sex', wrapper_class='form-group col-4'),
                ),
                Row(
                    Field('observed', wrapper_class='form-group col-4'),
                    Field('recorded_by', wrapper_class='form-group col-4'),
                ),
                css_class='border px-2',
            ),

            HTML('<div class="my-3"><h5>Tags</h5></div>'),
            Fieldset(
                None,
                Row(
                    Field('old_flipper_tags', wrapper_class='form-group col-3'),
                ),
                Row(
                    HTML('<div class="col-1"></div>'),
                    HTML('<div class="col-6">Tag number</div>'),
                    HTML('<div class="col">New tag?</div>'),
                    HTML('<div class="col">Scale</div>'),
                    HTML('<div class="col">Barnacles?</div>'),
                    HTML('<div class="col">Secure fix?</div>'),
                    HTML('<div class="col">Tag scars?</div>'),
                    css_class='pb-2',
                ),
                Row(
                    HTML('<div class="col-1">LEFT</div>'),
                    Field('tag_l1', wrapper_class='form-group col-6'),
                    Field('tag_l1_new', wrapper_class='form-group col'),
                    Field('tag_l1_scale', wrapper_class='form-group col'),
                    Field('tag_l1_barnacles', wrapper_class='form-group col'),
                    Field('tag_l1_secure', wrapper_class='form-group col'),
                    Field('tag_l1_scars', wrapper_class='form-group col'),
                ),
                Row(
                    HTML('<div class="col-1"></div>'),
                    Field('tag_l2', wrapper_class='form-group col-6'),
                    Field('tag_l2_new', wrapper_class='form-group col'),
                    Field('tag_l2_scale', wrapper_class='form-group col'),
                    Field('tag_l2_barnacles', wrapper_class='form-group col'),
                    Field('tag_l2_secure', wrapper_class='form-group col'),
                    Field('tag_l2_scars', wrapper_class='form-group col'),
                ),
                Row(
                    HTML('<div class="col-1">RIGHT</div>'),
                    Field('tag_r1', wrapper_class='form-group col-6'),
                    Field('tag_r1_new', wrapper_class='form-group col'),
                    Field('tag_r1_scale', wrapper_class='form-group col'),
                    Field('tag_r1_barnacles', wrapper_class='form-group col'),
                    Field('tag_r1_secure', wrapper_class='form-group col'),
                    Field('tag_r1_scars', wrapper_class='form-group col'),
                ),
                Row(
                    HTML('<div class="col-1"></div>'),
                    Field('tag_r2', wrapper_class='form-group col-6'),
                    Field('tag_r2_new', wrapper_class='form-group col'),
                    Field('tag_r2_scale', wrapper_class='form-group col'),
                    Field('tag_r2_barnacles', wrapper_class='form-group col'),
                    Field('tag_r2_secure', wrapper_class='form-group col'),
                    Field('tag_r2_scars', wrapper_class='form-group col'),
                ),
                Row(
                    Field('pit_tag_present', wrapper_class='form-group col-3'),
                ),
                Row(
                    HTML('<div class="col-1"></div>'),
                    HTML('<div class="col-9">Pit tag number</div>'),
                    HTML('<div class="col-2">New tag?</div>'),
                    css_class='pb-2',
                ),
                Row(
                    HTML('<div class="col-1">LEFT</div>'),
                    Field('pit_tag_l', wrapper_class='form-group col-9'),
                    Field('pit_tag_l_new', wrapper_class='form-group col-2'),
                ),
                Row(
                    HTML('<div class="col-1">RIGHT</div>'),
                    Field('pit_tag_r', wrapper_class='form-group col-9'),
                    Field('pit_tag_r_new', wrapper_class='form-group col-2'),
                ),
                Row(
                    Field('tagged_by', wrapper_class='form-group col-4'),
                    Field('tags_recorded_by', wrapper_class='form-group col-4'),
                ),
                css_class='border px-2',
            ),

            HTML('<div class="my-3"><h5>Measurements</h5></div>'),
            Fieldset(
                None,
                Row(
                    Field('ccl_min', wrapper_class='form-group col-4'),
                    Field('ccl_max', wrapper_class='form-group col-4'),
                    Field('measured_by', wrapper_class='form-group col-4'),
                ),
                Row(
                    Field('cc_width', wrapper_class='form-group col-4'),
                    Field('weight', wrapper_class='form-group col-4'),
                    Field('measurements_recorded_by', wrapper_class='form-group col-4'),
                ),
                css_class='border px-2',
            ),

            HTML('<div class="my-3"><h5>Nesting</h5></div>'),
            Fieldset(
                None,
                Row(
                    Field('nest_location', wrapper_class='form-group col-6'),
                ),
                Row(
                    Field('nesting_interrupted', wrapper_class='form-group col-6'),
                ),
                Row(
                    Field('nested', wrapper_class='form-group col-6'),
                ),
                css_class='border px-2',
            ),

            HTML('<div class="my-3"><h5>Damage</h5></div>'),
            Fieldset(
                None,
                Row(
                    Field('damage', wrapper_class='form-group col-6'),
                ),
                Row(
                    HTML('<div class="col-2"></div>'),
                    HTML('<div class="col-4">Body part</div>'),
                    HTML('<div class="col-4">Damage</div>'),
                    css_class='pb-2',
                ),
                Row(
                    HTML('<div class="col-2">Feature 1</div>'),
                    Field('damage_1_part', wrapper_class='form-group col-4'),
                    Field('damage_1_type', wrapper_class='form-group col-4'),
                ),
                Row(
                    HTML('<div class="col-2">Feature 2</div>'),
                    Field('damage_2_part', wrapper_class='form-group col-4'),
                    Field('damage_2_type', wrapper_class='form-group col-4'),
                ),
                Row(
                    HTML('<div class="col-2">Feature 3</div>'),
                    Field('damage_3_part', wrapper_class='form-group col-4'),
                    Field('damage_3_type', wrapper_class='form-group col-4'),
                ),
                Row(
                    HTML('<div class="col-2">Feature 4</div>'),
                    Field('damage_4_part', wrapper_class='form-group col-4'),
                    Field('damage_4_type', wrapper_class='form-group col-4'),
                ),
                Row(
                    HTML('<div class="col-2">Feature 5</div>'),
                    Field('damage_5_part', wrapper_class='form-group col-4'),
                    Field('damage_5_type', wrapper_class='form-group col-4'),
                ),
                css_class='border px-2',
            ),

            HTML('<div class="my-3"><h5>Samples</h5></div>'),
            Fieldset(
                None,
                Row(
                    Field('biopsy_no', wrapper_class='form-group col-4'),
                    Field('satellite_tag_no', wrapper_class='form-group col-4'),
                    Field('photos', wrapper_class='form-group col-4')
                ),
                Row(
                    Field('sample_1_type', wrapper_class='form-group col-4'),
                    Field('sample_1_label', wrapper_class='form-group col-4'),
                ),
                Row(
                    Field('sample_2_type', wrapper_class='form-group col-4'),
                    Field('sample_2_label', wrapper_class='form-group col-4'),
                ),
                css_class='border px-2',
            ),
            Row(
                Field('comments', wrapper_class='form-group col'),
            ),

            FormActions(
                self.save_button,
                self.cancel_button,
            ),
        )

    def clean_longitude(self):
        longitude = self.cleaned_data['longitude']
        # Western Australia bounds
        if longitude and (longitude > 130.0 or longitude < 108.0):
            raise ValidationError("Invalid longitude value")
        return longitude

    def clean_latitude(self):
        latitude = self.cleaned_data['latitude']
        # Western Australia bounds
        if latitude and (latitude > -10.0 or latitude < -42.0):
            raise ValidationError("Invalid latitude value")
        return latitude

    def clean_observed(self):
        observed = self.cleaned_data['observed']
        if observed >= datetime.now().astimezone(settings.AWST):
            raise ValidationError("Observations cannot be recorded in the future")
        return observed

    def clean_tag_l1_new(self):
        # Note that this works because the tag_l1 field is cleaned prior.
        tag_l1 = self.cleaned_data['tag_l1']
        tag_l1_new = self.cleaned_data['tag_l1_new']
        # If a tag serial is recorded, the "new" Y/N field MUST be filled.
        if tag_l1 and not tag_l1_new:
            raise ValidationError("You must record whether this tag is new")
        return tag_l1_new

    def clean_pit_tag_l_new(self):
        # Note that this works because the pit_tag_l field is cleaned prior.
        pit_tag_l = self.cleaned_data['pit_tag_l']
        pit_tag_l_new = self.cleaned_data['pit_tag_l_new']
        # If a tag serial is recorded, the "new" Y/N field MUST be filled.
        if pit_tag_l and not pit_tag_l_new:
            raise ValidationError("You must record whether this tag is new")
        return pit_tag_l_new

    def clean(self):
        # TODO: validation relating to tags:
        # - New tag on new turtle.
        # - New tag on existing turtle.
        cleaned_data = super().clean()
        if cleaned_data.get('existing_turtle_id'):
            turtle = Turtle.objects.get(pk=cleaned_data.get('existing_turtle_id'))
        else:
            turtle = None

        tag_l1 = cleaned_data.get('tag_l1')
        if tag_l1:
            # Checks: new, serial exists | not new, already assigned | not new, not assigned
            tag_l1_new = cleaned_data.get('tag_l1_new') == 'y'
            tag_l1_exists = TurtleTag.objects.filter(serial=tag_l1).exists()
            # If a tag is recorded as new, the serial number must be unique.
            if tag_l1_new and tag_l1_exists and TurtleTag.objects.filter(serial=tag_l1, turtle__isnull=False).exists():
                self.add_error('tag_l1', f'Tag with serial number {tag_l1} already exists in the database')
            # If tag is recorded as not new but is on a different turtle, return error.
            if not tag_l1_new and tag_l1_exists and TurtleTag.objects.filter(serial=tag_l1).exclude(turtle=turtle).exists():
                self.add_error('tag_l1', f'Tag with serial number {tag_l1} is already assigned to another turtle')
        # Repeat for tag L2, R1, R2

        pit_tag_l = cleaned_data.get('pit_tag_l')
        if pit_tag_l:
            # Checks: new, serial exists | not new, already assigned | not new, not assigned
            pit_tag_l_new = cleaned_data.get('pit_tag_l_new') == 'y'
            pit_tag_l_exists = TurtlePitTag.objects.filter(serial=pit_tag_l).exists()
            # If a pit tag is recorded as new, the serial number must be unique.
            if pit_tag_l_new and pit_tag_l_exists and TurtlePitTag.objects.filter(serial=pit_tag_l, turtle__isnull=False).exists():
                self.add_error('pit_tag_l', f'Pit tag with serial number {pit_tag_l} already exists in the database')
            # If tag is recorded as not new but is on a different turtle, return an error.
            if not pit_tag_l_new and pit_tag_l_exists and TurtlePitTag.objects.filter(serial=pit_tag_l).exclude(turtle=turtle).exists():
                self.add_error('pit_tag_l', f'Pit tag with serial number {pit_tag_l} is already assigned to another turtle')
