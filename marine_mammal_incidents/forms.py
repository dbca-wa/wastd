from django import forms
from .models import Incident, Uploaded_file
from mapwidgets.widgets import MapboxPointFieldWidget

class IncidentForm(forms.ModelForm):
    comments = forms.CharField(
        widget=forms.Textarea(attrs={'cols': '100', 'rows': '10'}),
        required=False
    )

    class Meta:
        model = Incident
        fields = '__all__'
        widgets = {
            'geo_location': MapboxPointFieldWidget(),
        }

class UploadedFileForm(forms.ModelForm):
    class Meta:
        model = Uploaded_file
        fields = ['title', 'file']