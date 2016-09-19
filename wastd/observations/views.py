# from django.shortcuts import render
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework import response, schemas, permissions

from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect

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
