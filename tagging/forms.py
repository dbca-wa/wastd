from datetime import datetime
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from easy_select2 import Select2
from .models import (
    Place,
    Turtle,
    TurtleObservation,
    TurtleTag,
    TurtlePitTag,
    TurtleDamage,
    TurtleSample,
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
    BODY_PART_CHOICES = (
        ('A', 'Carapace - entire'),
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
        ('5', 'Minor Wounds or cuts'),
        ('6', 'Major Wounds or cuts'),
        ('7', 'Deformity'),
    )
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


class TurtleTagAddForm(forms.ModelForm):
    TAG_STATUS_CHOICES = (
        ('ATT', 'Tag attached to turtle'),
        ('POOR', 'Poor fix on turtle'),
    )
    status = forms.ChoiceField(required=True, choices=TAG_STATUS_CHOICES)

    class Meta:
        model = TurtleTag
        fields = ('serial', 'side', 'status', 'comments')


class TurtlePitTagAddForm(forms.ModelForm):
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

    class Meta:
        model = TurtlePitTag
        fields = ('serial', 'status', 'position', 'comments')
