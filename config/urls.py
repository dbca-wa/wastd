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
from djgeojson.views import GeoJSONLayerView, TiledGeoJSONLayerView
from rest_framework.authtoken import views as drf_authviews
# from dynamic_rest import routers as dr

# from graphene_django.views import GraphQLView
# from wastd.schema import schema

from wastd.api import router  # , sync_route
from wastd.observations.models import Area, Encounter, AnimalEncounter
from wastd.observations.views import (
    schema_view, update_names,
    HomeView, EncounterTableView, AnimalEncounterTableView)

# register all adminactions
actions.add_to_site(site)

urlpatterns = [
    url(r'^$',
        # TemplateView.as_view(template_name='pages/home.html'),
        HomeView.as_view(),
        name='home'),

    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'),
        name='about'),

    url(r'^grappelli/', include('grappelli.urls')),  # grappelli URLS
    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, include(admin.site.urls)),

    # User management
    url(r'^users/', include('wastd.users.urls', namespace='users')),
    url(r'^accounts/', include('allauth.urls')),

    # Encounters
    url(r'^encounters/$',
        EncounterTableView.as_view(),
        name="encounter_list"),

    url(r'^animal-encounters/$',
        AnimalEncounterTableView.as_view(),
        name="animalencounter_list"),

    # API
    url(r'^api/docs/$', schema_view, name="api-docs"),
    url(r'^api/1/', include(router.urls, namespace="api")),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', drf_authviews.obtain_auth_token, name="api-auth"),

    # GraphQL
    # url(r'^graphql', GraphQLView.as_view(graphiql=True, schema=schema)),

    # Synctools
    # url("^sync/", include(sync_route.urlpatterns)),

    url(r'^adminactions/', include('adminactions.urls')),
    url(r'^select2/', include('django_select2.urls')),

    # Djgeojson
    url(r'^observations.geojson$',
        GeoJSONLayerView.as_view(model=Encounter,
                                 properties=('as_html', ),
                                 geometry_field="where"),
        name='observation-geojson'),

    url(r'^areas.geojson$',
        GeoJSONLayerView.as_view(
            model=Area,
            properties=('leaflet_title', 'as_html')),
        name='areas-geojson'),

    # Encounter as tiled GeoJSON
    url(r'^data/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+).geojson$',
        TiledGeoJSONLayerView.as_view(
            model=AnimalEncounter,
            properties=('as_html', 'leaflet_title', 'leaflet_icon', 'leaflet_colour'),
            geometry_field="where"),
        name='encounter-tiled-geojson'),

    # url(r'^areas/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+).geojson$',
    #     TiledGeoJSONLayerView.as_view(
    #         model=Area,
    #         properties=('name',),
    #         geometry_field="geom"),
    #     name='area-tiled-geojson'),

    # Update animal names for all Encounters
    url(r'^action/update-names/$', update_names, name="update-names"),

    url(r'^400/$', default_views.bad_request,
        kwargs={'exception': Exception('Bad Request!')}),

    url(r'^403/$', default_views.permission_denied,
        kwargs={'exception': Exception('Permission Denied')}),

    url(r'^404/$', default_views.page_not_found,
        kwargs={'exception': Exception('Page not Found')}),

    # url(r'^500/$', default_views.server_error,
    #     kwargs={'exception': Exception('Infernal Server Error')}),

    ] +\
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) +\
    staticfiles_urlpatterns()

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls)), ]
