from django import forms
from easy_select2 import apply_select2
from .models import TrtPersons, TrtDataEntry, TrtTags, TrtEntryBatches, TrtPlaces, TrtPitTags, Template, TrtObservations,TrtTagStates, TrtMeasurementTypes,TrtYesNo
from django_select2.forms import ModelSelect2Widget
from django.core.validators import RegexValidator
from django.db.models import Case, When, IntegerField


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
    # default_enterer = forms.CharField(widget=forms.HiddenInput(), required=False)
    selected_template = forms.CharField(required=False, widget=forms.HiddenInput())
    # use_default_enterer = forms.BooleanField(required=False, widget=forms.HiddenInput())


class TrtEntryBatchesForm(forms.ModelForm):
    curved_carapace_length_notch = forms.IntegerField(
        required=False,
        validators=[RegexValidator(r'^\d+$', 'Enter a valid integer.')],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '0'})
    )
    curved_carapace_width = forms.IntegerField(
        required=False,
        validators=[RegexValidator(r'^\d+$', 'Enter a valid integer.')],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '0'})
    )
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
            "entered_by",
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
            
            "body_part_4",
            "damage_code_4",
            "body_part_5",
            "damage_code_5",
            "body_part_6",
            "damage_code_6",

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
        self.fields['entered_by'].widget = forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter name',
        })
        
        
        nesting_choices = TrtYesNo.objects.filter(code__in=['N', 'P', 'Y'])
        self.fields['nesting'].queryset = nesting_choices

        # Filter the queryset for measurement types
        filtered_measurement_types = TrtMeasurementTypes.objects.exclude(
            measurement_type__in=['CCW', 'CCL NOTCH']
        )
        for i in range(1, 7):
            field_name = f'measurement_type_{i}'
            self.fields[field_name].queryset = filtered_measurement_types

        
        tag_state_order = ["A1", "AE", "#"]
        
        tag_state_order_case = Case(
            *[When(tag_state=state, then=pos) for pos, state in enumerate(tag_state_order)],
            default=len(tag_state_order),
            output_field=IntegerField()
        )
        
        # Filter the queryset for new tag fields
        new_tag_states = TrtTagStates.objects.filter(
            tag_state__in=tag_state_order
        ).order_by(tag_state_order_case)
        
        self.fields['new_left_tag_state'].queryset = new_tag_states
        self.fields['new_right_tag_state'].queryset = new_tag_states
        self.fields['new_left_tag_state_2'].queryset = new_tag_states
        self.fields['new_right_tag_state_2'].queryset = new_tag_states

        # Filter the queryset for recapture (old) tag fields
        old_tag_state_order = ["P_OK","P", "RC", "RN", "OO", "R", "#"]
        
        old_tag_state_order_case = Case(
            *[When(tag_state=state, then=pos) for pos, state in enumerate(old_tag_state_order)],
            default=len(old_tag_state_order),
            output_field=IntegerField()
        )
        
        old_tag_states = TrtTagStates.objects.filter(
            tag_state__in=old_tag_state_order
        ).order_by(old_tag_state_order_case)
        
        self.fields['recapture_left_tag_state'].queryset = old_tag_states
        self.fields['recapture_right_tag_state'].queryset = old_tag_states
        self.fields['recapture_left_tag_state_2'].queryset = old_tag_states
        self.fields['recapture_right_tag_state_2'].queryset = old_tag_states
        

        self.fields["observation_date"].required = True
        self.fields["species_code"].required = True
        self.fields["place_code"].required = True
        self.fields["sex"].required = True
        self.fields["clutch_completed"].required = True
        
        self.fields["latitude"].label = "Latitude - (xx.xxxxxx)"
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
        
        # tag_fields = [
        #     'recapture_left_tag_id', 'recapture_left_tag_id_2', 'recapture_left_tag_id_3',
        #     'recapture_right_tag_id', 'recapture_right_tag_id_2', 'recapture_right_tag_id_3',
        #     'new_left_tag_id', 'new_left_tag_id_2', 'new_right_tag_id', 'new_right_tag_id_2',
        #     'dud_filpper_tag', 'dud_filpper_tag_2'
        # ]
        
        # for field in tag_fields:
        #     if cleaned_data.get(field):
        #         cleaned_data[field] = cleaned_data[field].upper()

        if do_not_process:
            return cleaned_data
        
        place_code = cleaned_data.get("place_code")
        if not place_code:
            raise forms.ValidationError("The place code is required.")
        
        latitude = cleaned_data.get("latitude")
        if latitude is not None:
            latitude_str = str(latitude)
            if not latitude_str.startswith('-') and not latitude_str.startswith('-'):
                cleaned_data['latitude'] = f'-{latitude}'
            else:
                cleaned_data['latitude'] = latitude_str
                
        
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
        
    def clean(self):
        cleaned_data = super().clean()
        species_code = cleaned_data.get('species_code')
        sex = cleaned_data.get('sex')
        location_code = cleaned_data.get('location_code')
        place_code = cleaned_data.get('place_code')

        if not species_code:
            cleaned_data['species_code'] = None
        if not sex:
            cleaned_data['sex'] = None
        if not location_code:
            cleaned_data['location_code'] = None
        if not place_code:
            cleaned_data['place_code'] = None

        return cleaned_data
        
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

class BatchesCodeForm(forms.ModelForm):
    class Meta:
        model = TrtEntryBatches
        fields = ['batches_code', 'comments', 'template', 'entered_person_id']
        labels = {
            'batches_code': 'Batches Code',
            'comments': 'Comments',
            'template': 'Template',
            'entered_person_id': 'Team Leader Name',
        }
        widgets = {
            'batches_code': forms.TextInput(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control'}),
            'template': forms.Select(attrs={'class': 'form-control'}),
            'entered_person_id': forms.HiddenInput(), 
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['entered_person_id'].queryset = TrtPersons.objects.all()
        self.fields['template'].queryset = Template.objects.all()


class BatchesSearchForm(forms.Form):
    batches_code = forms.CharField(
        max_length=255, 
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Batch Code'
    )
    
class TrtPersonsForm(forms.ModelForm):
    class Meta:
        model = TrtPersons
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get("first_name")
        surname = cleaned_data.get("surname")
        email = cleaned_data.get("email")
        recorder = cleaned_data.get("recorder")

        if not first_name:
            self.add_error('first_name', "First name is required.")
        if not surname:
            self.add_error('surname', "Surname is required.")
        if not email:
            self.add_error('email', "Email is required.")
        if recorder is None:
            self.add_error('recorder', "Please specify if this person is a recorder.")

        return cleaned_data

