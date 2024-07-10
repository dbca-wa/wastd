from django import forms
from django.forms import DateTimeInput
from easy_select2 import apply_select2
from .models import TrtPersons, TrtDataEntry, TrtTags, TrtEntryBatches, TrtPlaces, TrtPitTags, TrtPitTags, Template
from django_select2.forms import ModelSelect2Widget


tagWidget = ModelSelect2Widget(
    queryset=TrtTags.objects.all(),
    model=TrtTags,
    search_fields=[
        "tag_id__icontains",
    ],
)

unAssignedTagWidget = ModelSelect2Widget(
    queryset=TrtTags.objects.filter(tag_status="U"),
    model=TrtTags,
    search_fields=[
        "tag_id__icontains",
    ],
)

pitTagWidget = ModelSelect2Widget(
    queryset=TrtPitTags.objects.all(),
    model=TrtPitTags,
    search_fields=[
        "pittag_id__icontains",
    ],
)

unassignedPitTagWidget = ModelSelect2Widget(
    queryset=TrtPitTags.objects.filter(pit_tag_status="U"),
    model=TrtPitTags,
    search_fields=[
        "pittag_id__icontains",
    ],
)

personWidget = ModelSelect2Widget(
    queryset=TrtPersons.objects.all(),
    model=TrtPersons,
    search_fields=["first_name__icontains", "surname__icontains"],
)

placeWidget = ModelSelect2Widget(
    queryset=TrtPlaces.objects.all(),
    model=TrtPlaces,
    search_fields=["place_name__icontains", "location_code__location_name__icontains"],
    attrs={'data-required': 'true'} 
)


class CustomModelSelect2Widget(ModelSelect2Widget):
    model = TrtTags  # Default model

    def filter_queryset(self, request, term, queryset=None, **dependent_fields):
        trt_tags = TrtTags.objects.filter(tag_id__icontains=term)
        trt_pit_tags = TrtPitTags.objects.filter(pittag_id__icontains=term)
        return list(trt_pit_tags) + list(trt_tags)

    def get_queryset(self):
        return self.model.objects.all()


class SearchForm(forms.Form):
    batch_id = forms.IntegerField(disabled=True)
    tag_id = forms.CharField(widget=CustomModelSelect2Widget)
    place_code = forms.CharField(widget=forms.HiddenInput(), required=False)
    species_code = forms.CharField(widget=forms.HiddenInput(), required=False)
    sex = forms.CharField(widget=forms.HiddenInput(), required=False)
    default_enterer = forms.CharField(widget=forms.HiddenInput(), required=False)
    selected_template = forms.CharField(required=False, widget=forms.HiddenInput())
    use_default_enterer = forms.BooleanField(required=False, widget=forms.HiddenInput())
    

class TrtEntryBatchesForm(forms.ModelForm):
    class Meta:
        model = TrtEntryBatches
        fields = ["entered_person_id", "comments"]
        widgets = {"entered_person_id": personWidget}


class TrtDataEntryForm(forms.ModelForm):
    
    class Meta:
        model = TrtDataEntry
        fields = [
            "entry_batch",
            "alive",
            "do_not_process",
            "turtle_id",
            "observation_date",
            "observation_id",
            "latitude",
            "longitude",
            "place_code",
            "species_code",
            "sex",
            "user_entry_id",
            "measured_by_id",
            "recorded_by_id",
            "tagged_by_id",
            "entered_by_id",
            "measured_recorded_by_id",
            "recapture_left_tag_id",
            "recapture_left_tag_id_2",
            "recapture_left_tag_id_3",
            "recapture_right_tag_id",
            "recapture_right_tag_id_2",
            "recapture_right_tag_id_3",
            "new_left_tag_id",
            "new_left_tag_id_2",
            "new_right_tag_id",
            "new_right_tag_id_2",
            "new_pittag_id",
            "new_pittag_id_2",
            "recapture_pittag_id",
            "recapture_pittag_id_2",
            "scars_left",
            "scars_right",
            "scars_left_scale_1",
            "scars_left_scale_2",
            "scars_left_scale_3",
            "scars_right_scale_1",
            "scars_right_scale_2",
            "scars_right_scale_3",
            "cc_length_not_measured",
            "curved_carapace_length",
            "cc_notch_length_not_measured",
            "cc_width_not_measured",
            "curved_carapace_width",
            "measurement_value_1",
            "measurement_value_2",
            "measurement_type_1",
            "measurement_type_2",
            "tagscarnotchecked",
            "didnotcheckforinjury",
            "damage_carapace",
            "damage_lff",
            "damage_rff",
            "damage_lhf",
            "damage_rhf",
            "body_part_1",
            "damage_code_1",
            "body_part_2",
            "damage_code_2",
            "body_part_3",
            "damage_code_3",
            "activity_code",
            "nesting",
            "sample_label_1",
            "tissue_type_1",
            "sample_label_2",
            "tissue_type_2",
            "comments",
            "clutch_completed",
            "egg_count",
            "egg_count_method"
        ]  # "__all__"

        widgets = {
            "turtle_id": forms.HiddenInput(),
            "entry_batch": forms.HiddenInput(),
            "observation_date": DateTimeInput(attrs={"type": "datetime-local"}),
            "user_entry_id": personWidget,
            "measured_by_id": personWidget,
            "recorded_by_id": personWidget,
            "tagged_by_id": personWidget,
            "entered_by_id": personWidget,
            "measured_recorded_by_id": personWidget,
            "place_code": placeWidget,
            "comments": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "clutch_completed": forms.Select(attrs={"class": "form-control"}),
            "egg_count": forms.NumberInput(attrs={"class": "form-control"}),
            "egg_count_method": forms.Select(attrs={"class": "form-control"}),
            # "new_left_tag_id": unAssignedTagWidget,
            # "new_left_tag_id_2": unAssignedTagWidget,
            # "new_right_tag_id": unAssignedTagWidget,
            # "new_right_tag_id_2": unAssignedTagWidget,
            # "new_pittag_id": unassignedPitTagWidget,
            # "new_pittag_id_2": unassignedPitTagWidget,
            #"recapture_left_tag_id": tagWidget,
            #"recapture_left_tag_id_2": tagWidget,
            #"recapture_left_tag_id_3": tagWidget,
            #"recapture_right_tag_id": tagWidget,
            #"recapture_right_tag_id_2": tagWidget,
            #"recapture_right_tag_id_3": tagWidget,
            # "recapture_pittag_id": pitTagWidget,
            # "recapture_pittag_id_2": pitTagWidget,
        }

    def __init__(self, *args, **kwargs):
        self.batch_id = kwargs.pop("batch_id", None)
        super().__init__(*args, **kwargs)

        # self.fields["activity_code"].required = True
        # self.fields["alive"].required = True
        # self.fields["nesting"].required = True
        self.fields["observation_date"].required = True
        self.fields["species_code"].required = True
        self.fields["place_code"].required = True
        self.fields["sex"].required = True
        
        self.fields["latitude"].label = "Latitude (-xx.xxxxxx)"
        self.fields["longitude"].label = "Longitude (xxx.xxxxxx)"
        self.fields["nesting"].label = "Did nesting complete?"
        self.fields["entered_by_id"].label = "Entered by"
        self.fields["place_code"].label = "Location/Beach"
        self.fields["species_code"].label = "Species"
        self.fields["observation_date"].label = "Observation Date & Time"
        self.fields["recorded_by_id"].label = "Data captured by"
        self.fields["recapture_pittag_id"].label = "Recapture Left PIT Tag"
        self.fields["recapture_pittag_id_2"].label = "Recapture Right PIT Tag"
        self.fields["new_pittag_id"].label = "New Left PIT Tag"
        self.fields["new_pittag_id_2"].label = "New Right PIT Tag"
        self.fields["recapture_left_tag_id"].label = "Recapture Left Tag"
        self.fields["recapture_left_tag_id_2"].label = "Recapture Left Tag 2"
        self.fields["recapture_left_tag_id_3"].label = "Recapture Left Tag 3"
        self.fields["recapture_right_tag_id"].label = "Recapture Right Tag"
        self.fields["recapture_right_tag_id_2"].label = "Recapture Right Tag 2"
        self.fields["recapture_right_tag_id_3"].label = "Recapture Right Tag 3"
        self.fields["new_left_tag_id"].label = "New Left Tag"
        self.fields["new_left_tag_id_2"].label = "New Left Tag 2"
        self.fields["new_right_tag_id"].label = "New Right Tag"
        self.fields["new_right_tag_id_2"].label = "New Right Tag 2"
        self.fields["scars_left_scale_1"].label = "1"
        self.fields["scars_left_scale_2"].label = "2"
        self.fields["scars_left_scale_3"].label = "3"
        self.fields["scars_right_scale_1"].label = "1"
        self.fields["scars_right_scale_2"].label = "2"
        self.fields["scars_right_scale_3"].label = "3"
        self.fields["tagged_by_id"].label = "Tagged by"
        self.fields["measured_by_id"].label = "Measured by"
        self.fields["tagscarnotchecked"].label = "Didn't check for tag scars"
        self.fields["didnotcheckforinjury"].label = "Didn't check for injury"
        self.fields["cc_length_not_measured"].label = "CCL not measured"
        self.fields["cc_width_not_measured"].label = "CCW not measured"
        self.fields["curved_carapace_length"].label = "Curved carapace length (mm)"
        self.fields["curved_carapace_width"].label = "Curved carapace width (mm)"
        self.fields["clutch_completed"].label = "Did turtle lay?"
        self.fields["damage_carapace"].label = "Carapace"
        self.fields["damage_lff"].label = "Left front flipper"
        self.fields["damage_rff"].label = "Right front flipper"
        self.fields["damage_lhf"].label = "Left hind flipper"
        self.fields["damage_rhf"].label = "Right hind flipper"
        
        
        self.fields['recapture_left_tag_id'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['recapture_left_tag_id_2'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['recapture_left_tag_id_3'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['recapture_right_tag_id'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['recapture_right_tag_id_2'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['recapture_right_tag_id_3'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['new_left_tag_id'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['new_left_tag_id_2'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['new_right_tag_id'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['new_right_tag_id_2'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['recapture_pittag_id'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['recapture_pittag_id_2'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['new_pittag_id'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['new_pittag_id_2'].widget = forms.TextInput(attrs={'class': 'form-control'})

        # Disable all fields if there is an observation_id as it already in the database
        if self.instance.observation_id:
            for field in self.fields:
                self.fields[field].disabled = True
                
        # Set the required fields to have a class of 'required-field'
        for field_name in self.fields:
            field = self.fields[field_name]
            if field.required:
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' required-field'

    # saves the people names as well as the person_id for use in MS Access front end
    def save(self, commit=True):
        # Call the parent class's save method to get the instance
        instance = super().save(commit=False)
        if instance.measured_by_id:
            person = TrtPersons.objects.get(person_id=instance.measured_by_id.person_id)
            instance.measured_by = "{} {}".format(person.first_name, person.surname)
        if instance.recorded_by_id:
            person = TrtPersons.objects.get(person_id=instance.recorded_by_id.person_id)
            instance.recorded_by = "{} {}".format(person.first_name, person.surname)
        if instance.tagged_by_id:
            person = TrtPersons.objects.get(person_id=instance.tagged_by_id.person_id)
            instance.tagged_by = "{} {}".format(person.first_name, person.surname)
        if instance.entered_by_id:
            person = TrtPersons.objects.get(person_id=instance.entered_by_id.person_id)
            instance.entered_by = "{} {}".format(person.first_name, person.surname)
        if instance.measured_recorded_by_id:
            person = TrtPersons.objects.get(person_id=instance.measured_recorded_by_id.person_id)
            instance.measured_recorded_by = "{} {}".format(person.first_name, person.surname)

        # Set the observation_time to the same value as the observation_date
        instance.observation_time = instance.observation_date

        # Save the instance to the database
        if commit:
            instance.save()

        return instance
                
        def clean(self):
            cleaned_data = super().clean()

            # fields_to_check = [
            #     "recapture_left_tag_id",
            #     "recapture_left_tag_id_2",
            #     "recapture_left_tag_id_3",
            #     "recapture_right_tag_id",
            #     "recapture_right_tag_id_2",
            #     "recapture_right_tag_id_3",
            #     "recapture_pittag_id",
            #     "recapture_pittag_id_2",
            # ]
            # if cleaned_data.get("turtle_id"):
            #     if not any(cleaned_data.get(field) for field in fields_to_check):
            #         raise ValidationError(
            #             "No recapture tags have been entered for a recaptured turtle."
            #         )

            # fields_to_check = [
            #     "tagscarnotchecked",
            #     "scars_left",
            #     "scars_right",
            #     "scars_left_scale_1",
            #     "scars_right_scale_1",
            #     "scars_left_scale_2",
            #     "scars_right_scale_2",
            #     "scars_left_scale_3",
            #     "scars_right_scale_3",
            # ]

            # if not any(cleaned_data.get(field) for field in fields_to_check):
            #     raise ValidationError(
            #         "At least one of the tag scar fields must be selected."
            #     )

            # fields_to_check = [
            #     "cc_length_not_measured",
            #     "curved_carapace_length",
            # ]

            # if not any(cleaned_data.get(field) for field in fields_to_check):
            #     raise ValidationError("Did you measure CCL?")

            # fields_to_check = [
            #     "cc_width_not_measured",
            #     "curved_carapace_width",
            # ]

            # if not any(cleaned_data.get(field) for field in fields_to_check):
            #     raise ValidationError("Did you measure CCW?")

            # fields_to_check = [
            #     "didnotcheckforinjury",
            #     "damage_carapace",
            #     "damage_lff",
            #     "damage_rff",
            #     "damage_lhf",
            #     "damage_rhf",
            #     "body_part_1",
            #     "damage_code_1",
            #     "body_part_2",
            #     "damage_code_2",
            # ]

            # if not any(cleaned_data.get(field) for field in fields_to_check):
            #     raise ValidationError("At least one of the injury fields must be selected.")

            return cleaned_data


class DataEntryUserModelForm(forms.ModelForm):
    qs = TrtPersons.objects.all()
    user_entry_id = forms.ModelChoiceField(
        queryset=qs, widget=apply_select2(forms.Select)
    )

    # def clean(self):
    #     cleaned_data = super().clean()
    #     ch = cleaned_data.get("user_entry_id")
    #     try:
    #         cleaned_data["user_entry_id"] = int(ch.person_id)
    #     except ValueError:
    #         raise forms.ValidationError("Choice must be an integer.")

    #     return cleaned_data


class EnterUserModelForm(forms.ModelForm):
    qs = TrtPersons.objects.all()
    entered_person_id = forms.ModelChoiceField(
        queryset=qs, widget=apply_select2(forms.Select)
    )

    # def clean(self):
    #     cleaned_data = super().clean()
    #     ch = cleaned_data.get("entered_person_id")
    #     try:
    #         cleaned_data["entered_person_id"] = int(ch.person_id)
    #     except ValueError:
    #         raise forms.ValidationError("Choice must be an integer.")

    #     return cleaned_data
    
class TemplateForm(forms.ModelForm):
    class Meta:
        model = Template
        fields = ['name', 'place_code', 'species_code', 'sex']