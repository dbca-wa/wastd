from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from .models import Incident, Uploaded_file
from .forms import IncidentForm, UploadedFileForm

def create_incident(request):
    UploadedFileFormSet = inlineformset_factory(Incident, Uploaded_file, form=UploadedFileForm, extra=1)
    
    if request.method == 'POST':
        form = IncidentForm(request.POST)
        formset = UploadedFileFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            incident = form.save()
            formset.instance = incident
            formset.save()
            return redirect('incident_list')  # 假设您有一个名为'incident_list'的URL模式
    else:
        form = IncidentForm()
        formset = UploadedFileFormSet()
    
    return render(request, 'marine_mammal_incidents/create_incident.html', {
        'form': form,
        'formset': formset,
    })