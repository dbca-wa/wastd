# from django.shortcuts import render
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework import response, schemas, permissions
from django_tables2 import RequestConfig, SingleTableMixin, SingleTableView, tables
import django_filters
from crispy_forms.helper import FormHelper

from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, TemplateView
from django.http import HttpResponseRedirect

from wastd.observations.models import Encounter


# Encounters -----------------------------------------------------------------#
# https://kuttler.eu/en/post/using-django-tables2-filters-crispy-forms-together/

class EncounterTable(tables.Table):
    class Meta:
        model = Encounter
        exclude = ["as_html", "polymorphic_ctype", ]


# class EncounterList(SingleTableView):
#     model = Encounter
#     table_class = EncounterTable


class EncounterFilter(django_filters.FilterSet):
    """Encounter Filter.

    https://django-filter.readthedocs.io/en/latest/usage.html
    """
    class Meta:
        model = Encounter
        fields = {
            # 'latitude': ['lt', 'gt'],
            # 'longitude': ['lt', 'gt'],
            'when': ['exact', 'year__gt', 'year__lt'],
            'source_id': ['exact', ],
            }


class EncounterTableView(TemplateView):
    template_name = 'observations/encounter_list.html'

    def get_queryset(self, **kwargs):
        return Encounter.objects.all()

    def get_context_data(self, **kwargs):
        context = super(EncounterTableView, self).get_context_data(**kwargs)
        filter = EncounterFilter(self.request.GET, queryset=self.get_queryset(**kwargs))
        filter.form.helper = FormHelper()
        table = EncounterTable(filter.qs)
        RequestConfig(self.request).configure(table)
        context['filter'] = filter
        context['table'] = table
        return context


# Django-Rest-Swagger View ---------------------------------------------------#
@api_view()
@permission_classes((permissions.AllowAny,))
@renderer_classes([SwaggerUIRenderer, OpenAPIRenderer])
def schema_view(request):

    generator = schemas.SchemaGenerator(title='WAStD API')
    return response.Response(generator.get_schema(request=request))


@csrf_exempt
def update_names(request):
    """Update cached names on Encounters."""
    from wastd.observations.utils import allocate_animal_names
    no_names = allocate_animal_names()
    messages.success(
        request, "Animal names inferred for {0} encounters".format(no_names))

    return HttpResponseRedirect("/")
