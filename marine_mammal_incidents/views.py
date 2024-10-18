from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from .models import Incident, Uploaded_file
from .forms import IncidentForm, UploadedFileForm
from django.contrib import messages
from django.db import transaction 


# def create_incident(request):
#     UploadedFileFormSet = inlineformset_factory(
#         Incident, 
#         Uploaded_file, 
#         form=UploadedFileForm, 
#         extra=1, 
#         can_delete=False
#     )
    
#     if request.method == 'POST':
#         form = IncidentForm(request.POST)
#         formset = UploadedFileFormSet(request.POST, request.FILES)
#         if form.is_valid() and formset.is_valid():
#             incident = form.save()
#             print(f"Incident created: {incident.id}")
#             formset.instance = incident
#             formset.save()
#             messages.success(request, 'Incident created successfully')
#             return redirect('marine_mammal_incidents:incident_list')
#         else:
#             print(form.errors)
#             print(formset.errors)
#             messages.error(request, 'Error creating incident. Please check the form.')
#     else:
#         form = IncidentForm()
#         formset = UploadedFileFormSet()
    
#     context = {
#         'form': form,
#         'formset': formset,
#     }
#     return render(request, 'marine_mammal_incidents/create_incident.html', context)

import logging

logger = logging.getLogger(__name__)

@transaction.atomic
def create_incident(request):
    if request.method == 'POST':
        form = IncidentForm(request.POST)
        if form.is_valid():
            try:
                incident = form.save()
                logger.info(f"Incident saved with ID: {incident.id}")
                logger.info(f"Incident details: {incident.__dict__}")
                
                saved_incident = Incident.objects.filter(id=incident.id).first()
                if saved_incident:
                    logger.info(f"Incident found in database: {saved_incident.id}")
                else:
                    logger.error("Incident not found in database after save")
                
                messages.success(request, 'Incident created successfully')
                return redirect('marine_mammal_incidents:incident_list')
            except Exception as e:
                logger.exception(f"Error saving incident: {str(e)}")
                messages.error(request, f'Error creating incident: {str(e)}')
        else:
            logger.error(f"Form errors: {form.errors}")
            messages.error(request, 'Error creating incident. Please check the form.')


def incident_list(request):
    incidents = Incident.objects.all().order_by('-incident_date')
    context = {
        'incidents': incidents,
    }
    return render(request, 'marine_mammal_incidents/incident_list.html', context)