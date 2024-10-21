from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from .models import Incident, Uploaded_file
from .forms import IncidentForm, UploadedFileForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



def create_incident(request):
    UploadedFileFormSet = inlineformset_factory(
        Incident, 
        Uploaded_file, 
        form=UploadedFileForm, 
        extra=1, 
        can_delete=False
    )
    
    if request.method == 'POST':
        form = IncidentForm(request.POST)
        formset = UploadedFileFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            incident = form.save()
            formset.instance = incident
            formset.save()
            messages.success(request, 'Incident created successfully')
            return redirect('marine_mammal_incidents:incident_list')
        else:
            messages.error(request, 'Error creating incident. Please check the form.')
    else:
        form = IncidentForm()
        formset = UploadedFileFormSet()
    
    context = {
        'form': form,
        'formset': formset,
        'form_title': 'Create New Incident',
        'submit_button_text': 'Create Incident',
    }
    return render(request, 'marine_mammal_incidents/create_incident.html', context)


def incident_list(request):
    incidents = Incident.objects.all().order_by('-incident_date')
    
    paginator = Paginator(incidents, 30) 
    page = request.GET.get('page')
    
    try:
        incidents = paginator.page(page)
    except PageNotAnInteger:
        incidents = paginator.page(1)
    except EmptyPage:
        incidents = paginator.page(paginator.num_pages)
    
    context = {
        'incidents': incidents,
        'object_count': paginator.count,
        'is_paginated': incidents.has_other_pages(),
    }
    return render(request, 'marine_mammal_incidents/incident_list.html', context)

def update_incident(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    if request.method == 'POST':
        form = IncidentForm(request.POST, instance=incident)
        file_form = UploadedFileForm(request.POST, request.FILES)
        if form.is_valid() and file_form.is_valid():
            form.save()
            if file_form.cleaned_data['file']:
                uploaded_file = file_form.save(commit=False)
                uploaded_file.incident = incident
                uploaded_file.save()
            return redirect('marine_mammal_incidents:incident_list')
    else:
        form = IncidentForm(instance=incident)
        file_form = UploadedFileForm()

    return render(request, 'marine_mammal_incidents/create_incident.html', {
        'form': form,
        'file_form': file_form,
        'form_title': 'Update Incident',
        'submit_button_text': 'Update Incident',
    })