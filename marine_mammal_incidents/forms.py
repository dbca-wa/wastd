from django import forms
from .models import Incident, Uploaded_file
from mapwidgets.widgets import MapboxPointFieldWidget

class IncidentForm(forms.ModelForm):

    class Meta:
        model = Incident
        fields = [
            'incident_date',
            'incident_time',
            'species',
            'species_confirmed_genetically',
            'location_name',
            'geo_location',
            'number_of_animals',
            'mass_incident',
            'incident_type',
            'sex',
            'age_class',
            'length',
            'weight',
            'weight_is_estimated',
            'carcass_location_fate',
            'entanglement_gear',
            'DBCA_staff_attended',
            'condition_when_found',
            'outcome',
            'cause_of_death',
            'photos_taken',
            'samples_taken',
            'post_mortem',
            'comments'
        ]
        widgets = {
            'geo_location': MapboxPointFieldWidget(),
            'comments': forms.Textarea(attrs={'cols': '100', 'rows': '10'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        required_fields = [
            'incident_date', 'species', 'location_name', 'number_of_animals',
            'incident_type', 'sex', 'age_class', 'condition_when_found', 'outcome'
        ]
        
        for field in required_fields:
            self.fields[field].required = True

class UploadedFileForm(forms.ModelForm):
    class Meta:
        model = Uploaded_file
        fields = ['title', 'file']
        labels = {
            'title': 'Attachment name',
            'file': 'File'
        }

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        file = cleaned_data.get('file')

        if file and not title:
            raise forms.ValidationError("The attachment name is required when a file is uploaded.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance