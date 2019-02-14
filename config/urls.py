# -*- coding: utf-8 -*-
"""WAStD URLs."""
from __future__ import unicode_literals

from adminactions import actions
from ajax_select import urls as ajax_select_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.admin import site
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, re_path, path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from djgeojson.views import GeoJSONLayerView, TiledGeoJSONLayerView
from occurrence.models import CommunityAreaEncounter
from occurrence.views import (
    CommunityAreaEncounterCreateView,
    CommunityAreaEncounterDetailView,
    CommunityAreaEncounterUpdateView,
    TaxonAreaEncounterCreateView,
    TaxonAreaEncounterDetailView,
    TaxonAreaEncounterUpdateView,
    AssociatedSpeciesObservationCreateView,
    AssociatedSpeciesObservationUpdateView,
    FireHistoryObservationCreateView,
    FireHistoryObservationUpdateView
)
from rest_framework.authtoken import views as drf_authviews
from rest_framework.documentation import include_docs_urls
from taxonomy.views import (
    CommunityDetailView,
    CommunityListView,
    TaxonDetailView,
    TaxonListView,
    update_taxon)

from wastd.api import router as wastd_router
from wastd.observations.models import AnimalEncounter, Area, Encounter
from wastd.observations.views import (
    AnimalEncounterTableView,
    EncounterTableView,
    HomeView,
    import_odka_view,
    schema_view
)

# from dynamic_rest import routers as dr


# register all adminactions
actions.add_to_site(site)

urlpatterns = [
    re_path(r'^$',
            TemplateView.as_view(template_name='index.html'),
            name='home'),

    re_path(r'^map/$',
            HomeView.as_view(),
            name='map'),

    # Species
    re_path(r'^species/$',
            TaxonListView.as_view(),
            name='taxon-list'),

    re_path(r'^species/(?P<name_id>[-+]?[0-9]+)/$',
            TaxonDetailView.as_view(),
            name='taxon-detail'),

    re_path(r'^species/(?P<name_id>[-+]?[0-9]+)/occurrences/report/$',
            TaxonAreaEncounterCreateView.as_view(),
            name='taxon-occurrence-create'),

    re_path(r'^species/(?P<name_id>[-+]?[0-9]+)/occurrences/area/(?P<area_code>[\w-]+)/report/$',
            TaxonAreaEncounterCreateView.as_view(),
            name='taxon-occurrence-area-create'),

    re_path(r'^species/occurrences/report/$',
            TaxonAreaEncounterCreateView.as_view(),
            name='taxonareaencounter-create'),

    re_path(r'^species/(?P<name_id>[-+]?[0-9]+)/occurrences/(?P<occ_pk>\d+)/$',
            TaxonAreaEncounterDetailView.as_view(),
            name='taxon-occurrence-detail'),

    re_path(r'species/(?P<name_id>[-+]?[0-9]+)/occurrences/(?P<occ_pk>\d+)/update/$',
            TaxonAreaEncounterUpdateView.as_view(),
            name='taxon-occurrence-update'),

    # Communities
    re_path(r'^communities/$',
            CommunityListView.as_view(),
            name='community-list'),

    re_path(r'^communities/(?P<pk>\d+)/$',
            CommunityDetailView.as_view(),
            name='community-detail'),

    re_path(r'^communities/(?P<pk>\d+)/occurrences/report$',
            CommunityAreaEncounterCreateView.as_view(),
            name='community-occurrence-create'),

    re_path(r'^communities/(?P<pk>\d+)/occurrences/area/(?P<area_code>[\w_-]+)/report$',
            CommunityAreaEncounterCreateView.as_view(),
            name='community-occurrence-area-create'),

    re_path(r'^communities/occurrences/report/$',
            CommunityAreaEncounterCreateView.as_view(),
            name='communityareaencounter-create'),

    re_path(r'^communities/(?P<pk>\d+)/occurrences/(?P<occ_pk>\d+)$',
            CommunityAreaEncounterDetailView.as_view(),
            name='community-occurrence-detail'),

    re_path(r'^communities/(?P<pk>\d+)/occurrences/(?P<occ_pk>\d+)/update$',
            CommunityAreaEncounterUpdateView.as_view(),
            name='community-occurrence-update'),

    re_path(r'^occurrences/(?P<occ_pk>\d+)/associated-species/report$',
            AssociatedSpeciesObservationCreateView.as_view(),
            name='occurrence-associatedspecies-create'),

    re_path(r'^occurrences/(?P<occ_pk>\d+)/associated-species/(?P<obs_pk>\d+)/$',
            AssociatedSpeciesObservationUpdateView.as_view(),
            name='occurrence-associatedspecies-update'),

    re_path(r'^occurrences/(?P<occ_pk>\d+)/fire-history/report$',
            FireHistoryObservationCreateView.as_view(),
            name='occurrence-firehistory-create'),

    re_path(r'^occurrences/(?P<occ_pk>\d+)/fire-history/(?P<obs_pk>\d+)/$',
            FireHistoryObservationUpdateView.as_view(),
            name='occurrence-firehistory-update'),


    re_path(r'^grappelli/',
            include('grappelli.urls')),  # grappelli URLs

    re_path(r'^ajax_select/',
            include(ajax_select_urls)),  # ajax select URLs

    # Django Admin, use {% url 'admin:index' %}
    re_path(settings.ADMIN_URL,
            admin.site.urls),

    # User management
    path('users/',
         include(('wastd.users.urls', 'users'), namespace='users')),

    path('accounts/',
         include('allauth.urls')),

    # Encounters
    path('encounters/',
         EncounterTableView.as_view(),
         name="encounter_list"),

    path('animal-encounters/',
         AnimalEncounterTableView.as_view(),
         name="animalencounter_list"),

    # API
    re_path(r'^api/1/swagger/$',
            schema_view,
            name="api-docs"),

    re_path(r'^api/1/docs/',
            include_docs_urls(title='API')),

    re_path(r'^api/1/',
            include((wastd_router.urls, 'api'), namespace="api")),

    re_path(r'^api-auth/',
            include(('rest_framework.urls', 'api-auth'), namespace='rest_framework')),

    re_path(r'^api-token-auth/',
            drf_authviews.obtain_auth_token, name="api-auth"),

    # GraphQL
    # url(r'^graphql', GraphQLView.as_view(graphiql=True, schema=schema)),

    # Synctools
    # url("^sync/", include(sync_route.urlpatterns)),
    re_path(r'^healthcheck/$',
            TemplateView.as_view(template_name='pages/healthcheck.html'),
            name='healthcheck'),

    re_path(r'^adminactions/',
            include('adminactions.urls')),

    re_path(r'^select2/',
            include('django_select2.urls')),

    # Djgeojson
    re_path(r'^observations.geojson$',
            GeoJSONLayerView.as_view(model=Encounter,
                                     properties=('as_html', ),
                                     geometry_field="where"),
            name='observation-geojson'),

    re_path(r'^areas.geojson$',
            GeoJSONLayerView.as_view(model=Area,
                                     properties=('leaflet_title', 'as_html')),
            name='areas-geojson'),

    # Encounter as tiled GeoJSON
    re_path(r'^data/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+).geojson$',
            TiledGeoJSONLayerView.as_view(
                model=AnimalEncounter,
                properties=('as_html', 'leaflet_title', 'leaflet_icon', 'leaflet_colour'),
                geometry_field="where"),
            name='encounter-tiled-geojson'),

    # CommunityAreaEncounter as tiled GeoJSON
    re_path(r'^community-encounters-poly/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+).geojson$',
            TiledGeoJSONLayerView.as_view(
                model=CommunityAreaEncounter,
                properties=('as_html', 'label',),
                geometry_field="geom"),
            name='community-area-encounter-tiled-geojson'),

    # url(r'^areas/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+).geojson$',
    #     TiledGeoJSONLayerView.as_view(
    #         model=Area,
    #         properties=('name',),
    #         geometry_field="geom"),
    #     name='area-tiled-geojson'),

    re_path(r'^action/update-taxon/$',
            update_taxon,
            name="update-taxon"),

    re_path(r'^action/import-odka/$',
            import_odka_view,
            name="import-odka"),

    re_path(r'^400/$',
            default_views.bad_request,
            kwargs={'exception': Exception('Bad Request!')}),

    re_path(r'^403/$',
            default_views.permission_denied,
            kwargs={'exception': Exception('Permission Denied')}),

    re_path(r'^404/$',
            default_views.page_not_found,
            kwargs={'exception': Exception('Page not Found')}),

    # url(r'^500/$', default_views.server_error,
    #     kwargs={'exception': Exception('Internal Server Error')}),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) +\
    staticfiles_urlpatterns()

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        re_path(r'^__debug__/',
                include(debug_toolbar.urls)),
        re_path(r'^performance/',
                include(('silk.urls', 'silk'), namespace='silk')),
    ]
