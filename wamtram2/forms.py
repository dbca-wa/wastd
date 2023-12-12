from django import forms
from django.forms import DateInput, DateTimeInput
from easy_select2 import apply_select2
from .models import TrtPersons,TrtDataEntry,TrtTags, TrtTurtles
from django_select2.forms import ModelSelect2Widget
from .models import TrtTags, TrtPitTags
from django.core.exceptions import ValidationError
from datetime import datetime


tagWidget =  ModelSelect2Widget(
    queryset = TrtTags.objects.all() ,
    model = TrtTags,
    search_fields = [ "tag_id__icontains", ]
    
)

pitTagWidget =  ModelSelect2Widget(
    queryset = TrtPitTags.objects.all() ,
    model = TrtPitTags,
    search_fields = [ "pit_tag_id__icontains", ]
    
)

class CustomModelSelect2Widget(ModelSelect2Widget):
    model = TrtTags  # Default model

    def filter_queryset(self, request, term, queryset=None, **dependent_fields):
        trt_tags = TrtTags.objects.filter(tag_id__icontains=term)
        trt_pit_tags = TrtPitTags.objects.filter(pit_tag_id__icontains=term)
        return list(trt_pit_tags) + list(trt_tags)

    def get_queryset(self):
        return self.model.objects.all()
    
class SearchForm(forms.Form):
    batch_id = forms.IntegerField(disabled=True)
    tag_id = forms.CharField(widget=CustomModelSelect2Widget)
    

class TrtDataEntryForm(forms.ModelForm):

    class Meta:
        model = TrtDataEntry
        fields = ['entry_batch',
                  'do_not_process',
                  'turtle_id',
                  'observation_date',
                  'user_entry_id',
                  'recapture_left_tag_id',
                  'recapture_left_tag_id_2',
                  'recapture_left_tag_id_3',
                  'recapture_right_tag_id',
                  'recapture_right_tag_id_2',
                  'recapture_right_tag_id_3',
                  'new_left_tag_id',
                  'new_left_tag_id_2',
                  'new_pit_tag_id',
                  'new_pit_tag_id_2',
                  'recapture_pit_tag_id',
                  'recapture_pit_tag_id_2',
                  'scars_left',
                  'scars_right',
                  'scars_left_scale_1',
                  'scars_left_scale_2',
                  'scars_left_scale_3',
                  'scars_right_scale_1',
                  'scars_right_scale_2',
                  'scars_right_scale_3',
                  'cc_length_not_measured',
                  'cc_notch_length_not_measured',
                  'cc_width_not_measured',
                  'tagscarnotchecked',
                  'didnotcheckforinjury',] #"__all__"
        widgets = {
            'observation_date': DateTimeInput(attrs={'type': 'datetime-local'}),
            "new_left_tag_id": tagWidget,
            "new_left_tag_id_2": tagWidget,
            "new_right_tag_id": tagWidget,
            "new_right_tag_id_2": tagWidget,
            "new_pit_tag_id": pitTagWidget,
            "new_pit_tag_id_2": pitTagWidget,
        }
  

    def __init__(self, *args, **kwargs):
        self.batch_id = kwargs.pop('batch_id', None)
        super().__init__(*args, **kwargs)
        self.fields['entry_batch'].disabled = True
        self.fields['turtle_id'].disabled = True
    
    def save(self, commit=True):
        # Call the parent class's save method to get the instance
        instance = super().save(commit=False)

        # Set the observation_time to the same value as the observation_date
        instance.observation_time = instance.observation_date
        print(instance.observation_time)
        # Save the instance to the database
        if commit:
            instance.save()

        return instance


class DataEntryUserModelForm(forms.ModelForm):
    qs=TrtPersons.objects.all()
    user_entry_id = forms.ModelChoiceField(queryset=qs, widget=apply_select2(forms.Select))

    def clean(self):
        cleaned_data = super().clean()
        ch = cleaned_data.get('user_entry_id')
        try:
            cleaned_data['user_entry_id'] = int(ch.person_id)
        except ValueError:
            raise forms.ValidationError("Choice must be an integer.")

        return cleaned_data


    
class EnterUserModelForm(forms.ModelForm):
    qs=TrtPersons.objects.all()
    entered_person_id = forms.ModelChoiceField(queryset=qs,widget=apply_select2(forms.Select))
   
    def clean(self):
        cleaned_data = super().clean()
        ch = cleaned_data.get('entered_person_id')
        try:
            cleaned_data['entered_person_id'] = int(ch.person_id)
        except ValueError:
            raise forms.ValidationError("Choice must be an integer.")

        return cleaned_data
