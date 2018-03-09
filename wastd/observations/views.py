"""Views for WAStD."""
# from django.shortcuts import render
# from rest_framework.decorators import api_view, renderer_classes, permission_classes
# from rest_framework import response, schemas, permissions
from itertools import chain

from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer
from rest_framework.renderers import CoreJSONRenderer


# Tables
from django_tables2 import RequestConfig, SingleTableView, tables

# from django.contrib import messages
# from django.views.decorators.csrf import csrf_exempt
# from django.views.generic import ListView, TemplateView
# from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic.list import ListView
from django.utils import timezone

from wastd.observations.models import Encounter, AnimalEncounter
from wastd.observations.filters import EncounterFilter, AnimalEncounterFilter
from wastd.observations.forms import (
    EncounterListFormHelper, AnimalEncounterListFormHelper)
from taxonomy.models import Taxon


class HomeView(ListView):

    model = AnimalEncounter
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

    def get_queryset(self, **kwargs):
        return AnimalEncounter.objects.filter(taxon="Cheloniidae")


class TaxonListView(ListView):
    """A ListView for Taxon."""

    model = Taxon
    template_name = "pages/dashboard.html"
    paginate_by = 12

    def get_context_data(self, **kwargs):
        """Add extra items to context."""
        context = super(TaxonListView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        # context['nodes'] = Taxon.objects.all()
        return context

    def get_queryset(self):
        queryset = Taxon.objects.all()
        if self.request.GET.get('name_id'):
            t = Taxon.objects.filter(name_id=self.request.GET.get('name_id'))
            queryset = list(chain(t.first().get_ancestors(), t, t.first().get_children()))
        return queryset


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


# Django-Rest-Swagger View ---------------------------------------------------#
# http://www.django-rest-framework.org/topics/3.5-announcement/#improved-schema-generation
schema_view = get_schema_view(
    title='WAStD API',
    renderer_classes=[OpenAPIRenderer, CoreJSONRenderer, SwaggerUIRenderer])
