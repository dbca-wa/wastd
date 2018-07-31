# -*- coding: utf-8 -*-
"""WAStD URLs."""
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include  # , url
from django.urls import path, re_path
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.admin import site
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView
from django.views import defaults as default_views

from adminactions import actions
from djgeojson.views import GeoJSONLayerView, TiledGeoJSONLayerView
from rest_framework.authtoken import views as drf_authviews
from rest_framework.documentation import include_docs_urls

from ajax_select import urls as ajax_select_urls

# from dynamic_rest import routers as dr

# from graphene_django.views import GraphQLView
# from wastd.schema import schema
from wastd.api import router as wastd_router
from wastd.observations.models import Area, Encounter, AnimalEncounter
from wastd.observations.views import (
    schema_view, HomeView, EncounterTableView, AnimalEncounterTableView)
from taxonomy.views import (
    update_taxon, TaxonListView, CommunityListView, TaxonDetailView, CommunityDetailView)

# register all adminactions
actions.add_to_site(site)

urlpatterns = [
    re_path(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),
    re_path(r'^map/$', HomeView.as_view(), name='map'),

    re_path(r'^species/(?P<name_id>[0-9]+)/$', TaxonDetailView.as_view(), name='taxon-detail'),
    re_path(r'^communities/(?P<pk>[0-9]+)/$', CommunityDetailView.as_view(), name='community-detail'),
    re_path(r'^species/$', TaxonListView.as_view(), name='taxon-list'),
    re_path(r'^communities/$', CommunityListView.as_view(), name='community-list'),


    re_path(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),

    re_path(r'^grappelli/', include('grappelli.urls')),  # grappelli URLs
    re_path(r'^ajax_select/', include(ajax_select_urls)),  # ajax select URLs
    # Django Admin, use {% url 'admin:index' %}
    re_path(settings.ADMIN_URL, admin.site.urls),

    # User management
    re_path(r'^users/', include('wastd.users.urls')),  # namespace='users'
    re_path(r'^accounts/', include('allauth.urls')),

    # Encounters
    re_path(r'^encounters/$', EncounterTableView.as_view(), name="encounter_list"),
    re_path(r'^animal-encounters/$', AnimalEncounterTableView.as_view(), name="animalencounter_list"),

    # API
    re_path(r'^api/1/swagger/$', schema_view, name="api-docs"),
    re_path(r'^api/1/docs/', include_docs_urls(title='API')),
    re_path(r'^api/1/', include(wastd_router.urls)),  # , namespace="api"
    re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    re_path(r'^api-token-auth/', drf_authviews.obtain_auth_token, name="api-auth"),

    re_path(r'^performance/', include('silk.urls', namespace='silk')),

    # GraphQL
    # url(r'^graphql', GraphQLView.as_view(graphiql=True, schema=schema)),

    # Synctools
    # url("^sync/", include(sync_route.urlpatterns)),

    re_path(r'^adminactions/', include('adminactions.urls')),
    re_path(r'^select2/', include('django_select2.urls')),

    # Djgeojson
    re_path(r'^observations.geojson$',
            GeoJSONLayerView.as_view(model=Encounter,
                                     properties=('as_html', ),
                                     geometry_field="where"),
            name='observation-geojson'),

    re_path(r'^areas.geojson$',
            GeoJSONLayerView.as_view(
                model=Area,
                properties=('leaflet_title', 'as_html')),
            name='areas-geojson'),

    # Encounter as tiled GeoJSON
    re_path(r'^data/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+).geojson$',
            TiledGeoJSONLayerView.as_view(
                model=AnimalEncounter,
                properties=(
                    'as_html',
                    'leaflet_title',
                    'leaflet_icon',
                    'leaflet_colour'),
                geometry_field="where"),
            name='encounter-tiled-geojson'),

    # url(r'^areas/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+).geojson$',
    #     TiledGeoJSONLayerView.as_view(
    #         model=Area,
    #         properties=('name',),
    #         geometry_field="geom"),
    #     name='area-tiled-geojson'),

    re_path(r'^action/update-taxon/$', update_taxon, name="update-taxon"),

    re_path(r'^400/$', default_views.bad_request,
            kwargs={'exception': Exception('Bad Request!')}),

    re_path(r'^403/$', default_views.permission_denied,
            kwargs={'exception': Exception('Permission Denied')}),

    re_path(r'^404/$', default_views.page_not_found,
            kwargs={'exception': Exception('Page not Found')}),

    # url(r'^500/$', default_views.server_error,
    #     kwargs={'exception': Exception('Infernal Server Error')}),

] + staticfiles_urlpatterns() + \
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path(r'^__debug__/', include(debug_toolbar.urls)), ]
