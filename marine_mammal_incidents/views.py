from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from .models import Incident, Uploaded_file
from .forms import IncidentForm, UploadedFileForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



def incident_form(request, pk=None):
    incident = get_object_or_404(Incident, pk=pk) if pk else None
    UploadedFileFormSet = inlineformset_factory(
        Incident, 
        Uploaded_file, 
        form=UploadedFileForm, 
        extra=1, 
        can_delete=True
    )
    
    if request.method == 'POST':
        form = IncidentForm(request.POST, instance=incident)
        formset = UploadedFileFormSet(request.POST, request.FILES, instance=incident)
        if form.is_valid() and formset.is_valid():
            incident = form.save()
            formset.instance = incident
            formset.save()
            messages.success(request, 'Incident saved successfully')
            return redirect('marine_mammal_incidents:incident_list')
        else:
            messages.error(request, 'Error saving incident. Please check the form.')
    else:
        form = IncidentForm(instance=incident)
        formset = UploadedFileFormSet(instance=incident)
    
    context = {
        'form': form,
        'formset': formset,
        'form_title': 'Update Incident' if incident else 'Create New Incident',
        'submit_button_text': 'Update Incident' if incident else 'Create Incident',
    }
    return render(request, 'marine_mammal_incidents/incident_form.html', context)


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


