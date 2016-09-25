# from django.shortcuts import render
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework import response, schemas, permissions

# Tables
from django_tables2 import RequestConfig, SingleTableMixin, SingleTableView, tables


# Forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Fieldset, MultiField, Div

from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
# from django.views.generic import ListView, TemplateView
from django.http import HttpResponseRedirect

from wastd.observations.models import Encounter, AnimalEncounter
from wastd.observations.filters import (
    ObservationTypeListFilter, EncounterFilter, AnimalEncounterFilter)


# Encounters -----------------------------------------------------------------#
# https://kuttler.eu/en/post/using-django-tables2-filters-crispy-forms-together/
# http://stackoverflow.com/questions/25256239/how-do-i-filter-tables-with-django-generic-views
class EncounterTable(tables.Table):
    class Meta:
        model = Encounter
        exclude = ["as_html", "polymorphic_ctype", ]
        attrs = {'class': 'table table-hover table-inverse table-sm'}


class AnimalEncounterTable(tables.Table):
    class Meta:
        model = AnimalEncounter
        exclude = ["as_html", "polymorphic_ctype", "encounter_ptr"]
        attrs = {'class': 'table table-hover table-inverse table-sm'}


class EncounterListFormHelper(FormHelper):
    model = Encounter
    form_tag = False
    form_class = 'form-horizontal'    # Adding a Filter Button
    form_show_labels = True
    layout = Layout(
        'name',
        'source_id',
        'when',
        'where',
        ButtonHolder(Submit('submit', 'Filter', css_class='button white right')),
        )


class AnimalEncounterListFormHelper(EncounterListFormHelper):
    model = AnimalEncounter


class PagedFilteredTableView(SingleTableView):
    """
    Generic class from http://kuttler.eu/post/using-django-tables2-filters-crispy-forms-together/
    which should probably be in a utility file
    """
    filter_class = None
    formhelper_class = None
    context_filter_name = 'filter'

    def get_queryset(self, **kwargs):
        qs = super(PagedFilteredTableView, self).get_queryset()
        self.filter = self.filter_class(self.request.GET, queryset=qs)
        self.filter.form.helper = self.formhelper_class()
        return self.filter.qs

    def get_table(self, **kwargs):
        table = super(PagedFilteredTableView, self).get_table()
        RequestConfig(
            self.request,
            paginate={'page': self.kwargs['page'] if 'page' in self.kwargs else 1,
                      "per_page": self.paginate_by}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        context = super(PagedFilteredTableView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        return context


class EncounterTableView(PagedFilteredTableView):
    model = Encounter
    table_class = EncounterTable
    paginate_by = 5
    filter_class = EncounterFilter
    formhelper_class = EncounterListFormHelper


class AnimalEncounterTableView(EncounterTableView):
    model = AnimalEncounter
    table_class = AnimalEncounterTable
    paginate_by = 5
    filter_class = AnimalEncounterFilter
    formhelper_class = AnimalEncounterListFormHelper
    template = "observations/encounter.html"


# Django-Rest-Swagger View ---------------------------------------------------#
@api_view()
@permission_classes((permissions.AllowAny,))
@renderer_classes([SwaggerUIRenderer, OpenAPIRenderer])
def schema_view(request):
    """Swagger API docs."""
    generator = schemas.SchemaGenerator(title='WAStD API')
    return response.Response(generator.get_schema(request=request))


@csrf_exempt
def update_names(request):
    """Update cached names on Encounters."""
    from wastd.observations.utils import allocate_animal_names
    no_names = allocate_animal_names()
    messages.success(
        request,
        "{0} animal names reconstructed".format(len(no_names)))

    return HttpResponseRedirect("/")
