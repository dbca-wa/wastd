from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from .models import Incident, Uploaded_file, Species
from .forms import IncidentForm, UploadedFileForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import csv
import xlwt
from openpyxl import Workbook
from django.http import HttpResponse



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

def export_form(request):
    try:
        species_list = Species.objects.all()
    except Exception as e:
        species_list = []
    return render(request, 'marine_mammal_incidents/export_form.html', {'species_list': species_list})


def export_data(request):

    incident_date_from = request.GET.get('incident_date_from')
    incident_date_to = request.GET.get('incident_date_to')
    species_id = request.GET.get('species')
    location_name = request.GET.get('location_name')
    file_format = request.GET.get('format', 'csv')

    incidents = Incident.objects.all()
    if incident_date_from:
        incidents = incidents.filter(incident_date__gte=incident_date_from)
    if incident_date_to:
        incidents = incidents.filter(incident_date__lte=incident_date_to)
    if species_id:
        incidents = incidents.filter(species_id=species_id)
    if location_name:
        incidents = incidents.filter(location_name__icontains=location_name)

    # Prepare data
    data = [['Species', 'Latitude', 'Longitude', 'ID', 'Incident Date', 'Incident Time', 
            'Species Confirmed Genetically', 'Location Name', 'Geo Location', 
            'Number of Animals', 'Mass Incident', 'Incident Type', 'Sex', 'Age Class', 
            'Length', 'Weight', 'Weight Is Estimated', 'Carcass Location Fate', 
            'Entanglement Gear', 'DBCA Staff Attended', 'Condition When Found', 
            'Outcome', 'Cause of Death', 'Photos Taken', 'Samples Taken', 
            'Post Mortem', 'Comments']]

    for incident in incidents:
        data.append([
            str(incident.species) if incident.species is not None else '',
            incident.latitude if incident.latitude is not None else '',
            incident.longitude if incident.longitude is not None else '',
            incident.id if incident.id is not None else '',
            incident.incident_date if incident.incident_date is not None else '',
            incident.incident_time if incident.incident_time is not None else '',
            incident.species_confirmed_genetically if incident.species_confirmed_genetically is not None else '',
            incident.location_name if incident.location_name is not None else '',
            incident.geo_location if incident.geo_location is not None else '',
            incident.number_of_animals if incident.number_of_animals is not None else '',
            incident.mass_incident if incident.mass_incident is not None else '',
            incident.incident_type if incident.incident_type is not None else '',
            incident.sex if incident.sex is not None else '',
            incident.age_class if incident.age_class is not None else '',
            incident.length if incident.length is not None else '',
            incident.weight if incident.weight is not None else '',
            incident.weight_is_estimated if incident.weight_is_estimated is not None else '',
            incident.carcass_location_fate if incident.carcass_location_fate is not None else '',
            incident.entanglement_gear if incident.entanglement_gear is not None else '',
            incident.DBCA_staff_attended if incident.DBCA_staff_attended is not None else '',
            incident.condition_when_found if incident.condition_when_found is not None else '',
            incident.outcome if incident.outcome is not None else '',
            incident.cause_of_death if incident.cause_of_death is not None else '',
            incident.photos_taken if incident.photos_taken is not None else '',
            incident.samples_taken if incident.samples_taken is not None else '',
            incident.post_mortem if incident.post_mortem is not None else '',
            incident.comments if incident.comments is not None else ''
        ])

    if file_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="incidents.csv"'
        writer = csv.writer(response)
        writer.writerows(data)
    elif file_format == 'xls':
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="incidents.xls"'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Incidents')
        for row_num, row_data in enumerate(data):
            for col_num, cell_value in enumerate(row_data):
                ws.write(row_num, col_num, cell_value)
        wb.save(response)
    elif file_format == 'xlsx':
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="incidents.xlsx"'
        wb = Workbook()
        ws = wb.active
        for row in data:
            ws.append(row)
        wb.save(response)
    else:
        return HttpResponse("Invalid file format")

    return response
