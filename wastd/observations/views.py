# -*- coding: utf-8 -*-
"""Views for WAStD."""
# from django.shortcuts import render
# from rest_framework.decorators import api_view, renderer_classes, permission_classes
# from rest_framework import response, schemas, permissions

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, DetailView
# Tables
from django_tables2 import RequestConfig, SingleTableView, tables
from rest_framework.renderers import CoreJSONRenderer
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer
from sentry_sdk import capture_message

from wastd.observations.filters import AnimalEncounterFilter, EncounterFilter
from wastd.observations.forms import AnimalEncounterListFormHelper, EncounterListFormHelper, AnimalEncounterForm, FlipperTagObservationFormSet
from wastd.observations.models import AnimalEncounter, Encounter, TagObservation
from wastd.observations.tasks import import_odka, update_names


@csrf_exempt
def import_odka_view(request):
    """Import all available ODK-Aggregate forms."""
    capture_message("[wastd.observations.views.import_odka_view] Starting ODKA import.", level="error")
    msg = import_odka.now()
    messages.success(request, msg)
    capture_message(msg, level="error")
    return HttpResponseRedirect("/")


@csrf_exempt
def update_names_view(request):
    """Import all available ODK-Aggregate forms."""
    capture_message("[wastd.observations.views.update_names] Rebuilding names.", level="error")
    msg = update_names.now()
    messages.success(request, msg)
    capture_message(msg, level="error")
    return HttpResponseRedirect("/")


class HomeView(ListView):
    """HomeView."""

    model = AnimalEncounter
    template_name = "pages/map.html"

    def get_context_data(self, **kwargs):
        """Context data."""
        context = super(HomeView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

    def get_queryset(self, **kwargs):
        """Queryset."""
        return AnimalEncounter.objects.filter(encounter_type="stranding")


# Encounters -----------------------------------------------------------------#
# https://kuttler.eu/en/post/using-django-tables2-filters-crispy-forms-together/
# http://stackoverflow.com/questions/25256239/
class EncounterTable(tables.Table):
    """A data table for Encounters."""

    class Meta:
        """Model opts."""

        model = Encounter
        exclude = ["as_html", "as_latex", "polymorphic_ctype", "encounter_ptr"]
        attrs = {'class': 'table table-hover table-inverse table-sm'}


class AnimalEncounterTable(tables.Table):
    """A data table for AnimalEncounters."""

    class Meta:
        """Model opts."""

        model = AnimalEncounter
        exclude = ["as_html", "as_latex", "polymorphic_ctype", "encounter_ptr"]
        attrs = {'class': 'table table-hover table-inverse table-sm'}


class PagedFilteredTableView(SingleTableView):
    """Generic class for paged, filtered SingleTableView.

    Inherit from this class and set the class level attributes (``model`` etc.).

    Source:
    http://kuttler.eu/post/using-django-tables2-filters-crispy-forms-together/
    """

    # Set these in instantiated classes:
    model = None
    table_class = None
    paginate_by = 10
    filter_class = None
    formhelper_class = None
    context_filter_name = 'filter'

    def get_queryset(self, **kwargs):
        """Run the queryset through the specified filter class."""
        qs = super(PagedFilteredTableView, self).get_queryset()
        self.filter = self.filter_class(self.request.GET, queryset=qs)
        self.filter.form.helper = self.formhelper_class()
        return self.filter.qs

    def get_table(self, **kwargs):
        """Paginate the table as per paginate_by and request parameters."""
        table = super(PagedFilteredTableView, self).get_table()
        RequestConfig(
            self.request,
            paginate={'page': self.kwargs['page'] if 'page' in self.kwargs else 1,
                      "per_page": self.paginate_by}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        """Add the specified filter class to context."""
        context = super(PagedFilteredTableView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        return context


class EncounterTableView(PagedFilteredTableView):
    """Filtered paginated TableView for Encounter."""

    model = Encounter
    table_class = EncounterTable
    paginate_by = 5
    filter_class = EncounterFilter
    formhelper_class = EncounterListFormHelper


class AnimalEncounterTableView(EncounterTableView):
    """Filtered paginated TableView for AninmalEncounter."""

    model = AnimalEncounter
    table_class = AnimalEncounterTable
    paginate_by = 5
    filter_class = AnimalEncounterFilter
    formhelper_class = AnimalEncounterListFormHelper
    template = "observations/encounter.html"


class AnimalEncounterList(ListView):
    paginate_by = 20

    def get_queryset(self):
        return AnimalEncounter.objects.order_by('-pk')


class AnimalEncounterCreate(CreateView):
    model = AnimalEncounter
    form_class = AnimalEncounterForm

    def get_context_data(self, **kwargs):
        data = super(AnimalEncounterCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['flipper_tags'] = FlipperTagObservationFormSet(self.request.POST)
        else:
            data['flipper_tags'] = FlipperTagObservationFormSet()
        data['formset_prefix'] = 'encounter'  # We set this in order to give the JavaScript something to match.
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        flipper_tags = context['flipper_tags']
        with transaction.atomic():
            # Set observer and reporter to the request user.
            form.instance.observer = self.request.user
            form.instance.reporter = self.request.user
            self.object = form.save()
            if flipper_tags.is_valid():
                flipper_tags.instance = self.object
                flipper_tags.tag_type = 'flipper-tag'
                flipper_tags.save()
        return super(AnimalEncounterCreate, self).form_valid(form)


class AnimalEncounterDetail(DetailView):
    model = AnimalEncounter

    def get_context_data(self, **kwargs):
        data = super(AnimalEncounterDetail, self).get_context_data(**kwargs)
        data['tags'] = TagObservation.objects.filter(encounter__in=[self.get_object()])
        return data


# Django-Rest-Swagger View ---------------------------------------------------#
# http://www.django-rest-framework.org/topics/3.5-announcement/#improved-schema-generation
schema_view = get_schema_view(
    title='WAStD API',
    renderer_classes=[OpenAPIRenderer, CoreJSONRenderer, SwaggerUIRenderer])
