# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.admin import site
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView
from django.views import defaults as default_views

from adminactions import actions
from rest_framework import routers
# from dynamic_rest import routers as dr
from wastd.observations.models import Encounter
from wastd.observations.views import schema_view
from wastd.api import (
    UserViewSet, EncounterViewSet, TurtleNestEncounterViewSet,
    AnimalEncounterViewSet, ObservationViewSet, MediaAttachmentViewSet,
    TagObservationViewSet)
from djgeojson.views import GeoJSONLayerView, TiledGeoJSONLayerView

# register all adminactions
actions.add_to_site(site)

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter(schema_title='WAStD API')
router.register(r'users', UserViewSet)
router.register(r'encounters', EncounterViewSet)
router.register(r'turtle-nest-encounters', TurtleNestEncounterViewSet)
router.register(r'animal-encounters', AnimalEncounterViewSet)
# router.register(r'turtle-encounters', TurtleEncounterViewSet)
# router.register(r'cetacean-encounters', CetaceanEncounterViewSet)
router.register(r'observations', ObservationViewSet)
router.register(r'media-attachments', MediaAttachmentViewSet)
router.register(r'tag-observations', TagObservationViewSet)

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='pages/home.html'),
        name='home'),

    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'),
        name='about'),

    url(r'^grappelli/', include('grappelli.urls')),  # grappelli URLS
    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, include(admin.site.urls)),

    # User management
    url(r'^users/', include('wastd.users.urls', namespace='users')),
    url(r'^accounts/', include('allauth.urls')),

    # Your stuff: custom urls includes go here
    # API
    url(r'^api/1/', include(router.urls), name='api'),
    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-docs/1/', schema_view, name="api-docs"),
    url(r'^adminactions/', include('adminactions.urls')),
    url(r'^select2/', include('django_select2.urls')),

    # Djgeojson
    url(r'^observations.geojson$',
        GeoJSONLayerView.as_view(model=Encounter,
                                 properties=('as_html', ),
                                 geometry_field="where"),
        name='observation-geojson'),

    # Encounter as tiled GeoJSON
    url(r'^data/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+).geojson$',
        TiledGeoJSONLayerView.as_view(
            model=Encounter,
            properties=('as_html', ),
            geometry_field="where"),
        name='encounter-tiled-geojson'),
    ] +\
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) +\
    staticfiles_urlpatterns()

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request,
            kwargs={'exception': Exception('Bad Request!')}),

        url(r'^403/$', default_views.permission_denied,
            kwargs={'exception': Exception('Permission Denied')}),

        url(r'^404/$', default_views.page_not_found,
            kwargs={'exception': Exception('Page not Found')}),

        url(r'^500/$', default_views.server_error),
        ]
