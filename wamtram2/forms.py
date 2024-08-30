from django import forms
from django.forms import DateTimeInput
from easy_select2 import apply_select2
from .models import TrtPersons, TrtDataEntry, TrtTags, TrtEntryBatches, TrtPlaces, TrtPitTags, TrtPitTags, Template, TrtObservations,TrtTagStates, TrtDamageCodes
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
    queryset=TrtPersons.objects.all().only('person_id', 'first_name', 'surname'),
    model=TrtPersons,
    search_fields=["first_name__icontains"],
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
    
class DateTimeForm(forms.Form):
    observation_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )


class TrtEntryBatchesForm(forms.ModelForm):
    class Meta:
        model = TrtEntryBatches
        fields = ["entered_person_id", "comments", "entry_date"]
        widgets = {
            "entered_person_id": forms.HiddenInput(),
            "comments": forms.Textarea(attrs={"rows": 1, "class": "form-control"}),
            "entry_date": forms.HiddenInput(),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['entered_person_id'].label = "Enterer Name"


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
            "egg_count_method",
            
            # v2.0 added columns
            "recapture_left_tag_state",
            "recapture_left_tag_state_2",
            "recapture_right_tag_state",
            "recapture_right_tag_state_2",
            "new_left_tag_state",
            "new_left_tag_state_2",
            "new_right_tag_state",
            "new_right_tag_state_2",
            "recapture_left_tag_position",
            "recapture_left_tag_position_2",
            "recapture_right_tag_position",
            "recapture_right_tag_position_2",
            "new_left_tag_position",
            "new_left_tag_position_2",
            "new_right_tag_position",
            "new_right_tag_position_2",
            "recapture_left_tag_barnacles",
            "recapture_left_tag_barnacles_2",
            "recapture_right_tag_barnacles",
            "recapture_right_tag_barnacles_2",
            "new_left_tag_barnacles",
            "new_left_tag_barnacles_2",
            "new_right_tag_barnacles",
            "new_right_tag_barnacles_2",
            "identifier",
            "identification_type",
            

            "curved_carapace_length_notch",
            "measurement_type_3",
            "measurement_value_3",
            "measurement_type_4",
            "measurement_value_4",
            "measurement_type_5",
            "measurement_value_5",
            "measurement_type_6",
            "measurement_value_6",
            "cc_notch_length_not_measured",
            
            "flipper_tag_check",
            "pit_tag_check",
            "injury_check",
            "scar_check",
            
            "recapture_pittag_id_3",
            "recapture_pittag_id_4",
            "new_pittag_id_3",
            "new_pittag_id_4",
            
            "new_pit_tag_sticker_present",
            "new_pit_tag_2_sticker_present",
            "new_pit_tag_3_sticker_present",
            "new_pit_tag_4_sticker_present",

            "dud_filpper_tag",
            "dud_filpper_tag_2",
            "dud_pit_tag",
            "dud_pit_tag_2",

        ]  # "__all__"

        widgets = {
            "turtle_id": forms.HiddenInput(),
            "entry_batch": forms.HiddenInput(),
            "observation_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),

            "measured_by_id": forms.HiddenInput(),
            "recorded_by_id": forms.HiddenInput(),
            "tagged_by_id": forms.HiddenInput(),
            "entered_by_id": forms.HiddenInput(),
            # "measured_recorded_by_id": personWidget,
            "place_code": forms.HiddenInput(),
            "comments": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "clutch_completed": forms.Select(attrs={"class": "form-control"}),
            "egg_count": forms.NumberInput(attrs={"class": "form-control"}),
            "egg_count_method": forms.Select(attrs={"class": "form-control"}),
            "identification_type": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.batch_id = kwargs.pop("batch_id", None)
        super().__init__(*args, **kwargs)
        
        # Filter the queryset for new tag fields
        new_tag_states = TrtTagStates.objects.filter(
            tag_state__in=["A1", "AE", "P_ED", "P_OK", "#", "R"]
        )
        self.fields['new_left_tag_state'].queryset = new_tag_states
        self.fields['new_right_tag_state'].queryset = new_tag_states
        self.fields['new_left_tag_state_2'].queryset = new_tag_states
        self.fields['new_right_tag_state_2'].queryset = new_tag_states

        # Filter the queryset for recapture (old) tag fields
        old_tag_states = TrtTagStates.objects.filter(
            tag_state__in=["RQ", "RC", "OO", "OX", "P", "P_ED", "P_OK", "PX"]
        )
        
        self.fields['recapture_left_tag_state'].queryset = old_tag_states
        self.fields['recapture_right_tag_state'].queryset = old_tag_states
        self.fields['recapture_left_tag_state_2'].queryset = old_tag_states
        self.fields['recapture_right_tag_state_2'].queryset = old_tag_states
        
        # Filter the queryset for damage codes
        self.fields["damage_carapace"].queryset = TrtDamageCodes.objects.filter(
            damage_code__in=["0", "5", "6", "7"]
        )

        self.fields["observation_date"].required = True
        self.fields["species_code"].required = True
        self.fields["place_code"].required = True
        self.fields["sex"].required = True
        self.fields["clutch_completed"].required = True
        
        self.fields["latitude"].label = "Latitude (-xx.xxxxxx)"
        self.fields["longitude"].label = "Longitude (xxx.xxxxxx)"
        self.fields["nesting"].label = "Was nesting interrupted by tag team?"
        self.fields["entered_by_id"].label = "Entered by"
        self.fields["place_code"].label = "Location/Beach"
        self.fields["species_code"].label = "Species"
        self.fields["observation_date"].label = "Observation Date & Time"
        self.fields["recorded_by_id"].label = "Data captured by"
        self.fields["recapture_pittag_id"].label = "Old Left PIT Tag"
        self.fields["recapture_pittag_id_2"].label = "Old Right PIT Tag"
        self.fields["recapture_pittag_id_3"].label = "Old Left PIT Tag 2"
        self.fields["recapture_pittag_id_4"].label = "Old Right PIT Tag 2"
        self.fields["new_pittag_id"].label = "New Left PIT Tag"
        self.fields["new_pittag_id_2"].label = "New Right PIT Tag"
        self.fields["new_pittag_id_3"].label = "New Left PIT Tag 2"
        self.fields["new_pittag_id_4"].label = "New Right PIT Tag 2"
        self.fields["recapture_left_tag_id"].label = "Old Left Flipper Tag"
        self.fields["recapture_left_tag_id_2"].label = "Old Left Flipper Tag 2"
        self.fields["recapture_left_tag_id_3"].label = "Old Left Flipper Tag 3"
        self.fields["recapture_right_tag_id"].label = "Old Right Flipper Tag"
        self.fields["recapture_right_tag_id_2"].label = "Old Right Flipper Tag 2"
        self.fields["recapture_right_tag_id_3"].label = "Old Right Flipper Tag 3"
        self.fields["new_left_tag_id"].label = "New Left Flipper Tag"
        self.fields["new_left_tag_id_2"].label = "New Left Flipper Tag 2"
        self.fields["new_right_tag_id"].label = "New Right Flipper Tag"
        self.fields["new_right_tag_id_2"].label = "New Right Flipper Tag 2"
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
        self.fields["cc_length_not_measured"].label = "CCL max not measured"
        self.fields["cc_width_not_measured"].label = "CCW not measured"
        self.fields["curved_carapace_length"].label = "CCL max (mm)"
        self.fields["curved_carapace_width"].label = "CCW (mm)"
        self.fields["curved_carapace_length_notch"].label = "CCL min (mm)"
        self.fields["clutch_completed"].label = "Did the turtle lay?"
        self.fields["damage_carapace"].label = "Carapace"
        self.fields["damage_lff"].label = "Left front flipper"
        self.fields["damage_rff"].label = "Right front flipper"
        self.fields["damage_lhf"].label = "Left hind flipper"
        self.fields["damage_rhf"].label = "Right hind flipper"
        
        # v2.0 added columns
        self.fields["recapture_left_tag_state"].label = "Recapture Left Tag State"
        self.fields["recapture_left_tag_state_2"].label = "Recapture Left Tag Status 2"
        self.fields["recapture_right_tag_state"].label = "Recapture Right Tag Status"
        self.fields["recapture_right_tag_state_2"].label = "Recapture Right Tag Status 2"
        self.fields["new_left_tag_state"].label = "New Left Tag Status"
        self.fields["new_left_tag_state_2"].label = "New Left Tag Status 2"
        self.fields["new_right_tag_state"].label = "New Right Tag Status"
        self.fields["new_right_tag_state_2"].label = "New Right Tag Status 2"
        self.fields["recapture_left_tag_position"].label = "Recapture Left Tag Position"
        self.fields["recapture_left_tag_position_2"].label = "Recapture Left Tag Position 2"
        self.fields["recapture_right_tag_position"].label = "Recapture Right Tag Position"
        self.fields["recapture_right_tag_position_2"].label = "Recapture Right Tag Position 2"
        self.fields["new_left_tag_position"].label = "New Left Tag Position"
        self.fields["new_left_tag_position_2"].label = "New Left Tag Position 2"
        self.fields["new_right_tag_position"].label = "New Right Tag Position"
        self.fields["new_right_tag_position_2"].label = "New Right Tag Position 2"
        self.fields["recapture_left_tag_barnacles"].label = ""
        self.fields["recapture_left_tag_barnacles_2"].label = ""
        self.fields["recapture_right_tag_barnacles"].label = ""
        self.fields["recapture_right_tag_barnacles_2"].label = ""
        # self.fields["new_left_tag_barnacles"].label = ""
        # self.fields["new_left_tag_barnacles_2"].label = ""
        # self.fields["new_right_tag_barnacles"].label = ""
        # self.fields["new_right_tag_barnacles_2"].label = ""
        
        self.fields["cc_notch_length_not_measured"].label = "CCL min not measured"
        
        self.fields["new_pit_tag_sticker_present"].label = "Sticker?"
        self.fields["new_pit_tag_2_sticker_present"].label = "Sticker?"
        self.fields["new_pit_tag_3_sticker_present"].label = "Sticker?"
        self.fields["new_pit_tag_4_sticker_present"].label = "Sticker?"
        
        self.fields["do_not_process"].label = "Needs Review"
        
        self.fields["recapture_left_tag_state"].required = False
        self.fields["recapture_left_tag_state_2"].required = False
        self.fields["recapture_right_tag_state"].required = False
        self.fields["recapture_right_tag_state_2"].required = False
        self.fields["new_left_tag_state"].required = False
        self.fields["new_left_tag_state_2"].required = False
        self.fields["new_right_tag_state"].required = False
        self.fields["new_right_tag_state_2"].required = False
        self.fields["recapture_left_tag_position"].required = False
        self.fields["recapture_left_tag_position_2"].required = False
        self.fields["recapture_right_tag_position"].required = False
        self.fields["recapture_right_tag_position_2"].required = False
        self.fields["new_left_tag_position"].required = False
        self.fields["new_left_tag_position_2"].required = False
        self.fields["new_right_tag_position"].required = False
        self.fields["new_right_tag_position_2"].required = False
        self.fields["recapture_left_tag_barnacles"].required = False
        self.fields["recapture_left_tag_barnacles_2"].required = False
        self.fields["recapture_right_tag_barnacles"].required = False
        self.fields["recapture_right_tag_barnacles_2"].required = False
        self.fields["new_left_tag_barnacles"].required = False
        self.fields["new_left_tag_barnacles_2"].required = False
        self.fields["new_right_tag_barnacles"].required = False
        self.fields["new_right_tag_barnacles_2"].required = False
        self.fields["identifier"].required = False
        self.fields["identification_type"].required = False
        

        self.fields["curved_carapace_length_notch"].required = False
        self.fields["measurement_type_3"].required = False
        self.fields["measurement_type_4"].required = False
        self.fields["measurement_type_5"].required = False
        self.fields["measurement_type_6"].required = False
        self.fields["measurement_value_3"].required = False
        self.fields["measurement_value_4"].required = False
        self.fields["measurement_value_5"].required = False
        self.fields["measurement_value_6"].required = False
        
        self.fields["cc_notch_length_not_measured"].required = False
        
        optional_fields = [
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
            "recapture_pittag_id",
            "recapture_pittag_id_2",
            "new_pittag_id",
            "new_pittag_id_2",
            "recapture_pittag_id_3",
            "recapture_pittag_id_4",
            "new_pittag_id_3",
            "new_pittag_id_4",
            "dud_filpper_tag",
            "dud_filpper_tag_2",
            "dud_pit_tag",
            "dud_pit_tag_2",
        ]

        for field in optional_fields:
            self.fields[field].required = False
            self.fields[field].widget = forms.TextInput(attrs={'class': 'form-control'})

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
        # if instance.measured_recorded_by_id:
        #     person = TrtPersons.objects.get(person_id=instance.measured_recorded_by_id.person_id)
        #     instance.measured_recorded_by = "{} {}".format(person.first_name, person.surname)

        # Set the observation_time to the same value as the observation_date
        instance.observation_time = instance.observation_date

        # Save the instance to the database
        if commit:
            instance.save()

        return instance
                
    def clean(self):
        cleaned_data = super().clean()
        do_not_process = cleaned_data.get("do_not_process")

        if do_not_process:
            return cleaned_data
        
        place_code = cleaned_data.get("place_code")
        if not place_code:
            raise forms.ValidationError("The place code is required.")
        
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
        fields = ['name', 'location_code', 'place_code', 'species_code', 'sex']
        
class TrtObservationsForm(forms.ModelForm):
    class Meta:
        model = TrtObservations
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        if 'observation_status' in cleaned_data:
            cleaned_data.pop('observation_status')
        if 'corrected_date' in cleaned_data:
            cleaned_data.pop('corrected_date')
        return cleaned_data