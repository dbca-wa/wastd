# -*- coding: utf-8 -*-
"""WAStD URLs."""
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.admin import site
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, re_path, path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from ajax_select import urls as ajax_select_urls
from adminactions import actions
from djgeojson.views import GeoJSONLayerView, TiledGeoJSONLayerView
from rest_framework.authtoken import views as drf_authviews
from rest_framework.documentation import include_docs_urls

from occurrence.models import CommunityAreaEncounter
from wastd.api import router as wastd_router
from wastd.observations import models as wastd_models
from wastd.observations import views as wastd_views

# register all adminactions
actions.add_to_site(site)

urlpatterns = [
    re_path(r'^$', TemplateView.as_view(template_name='pages/index.html'), name='home'),
    re_path(r'^map/$', wastd_views.HomeView.as_view(), name='map'),
    re_path(r'^healthcheck/$', TemplateView.as_view(template_name='pages/healthcheck.html'), name='healthcheck'),

    re_path(settings.ADMIN_URL, admin.site.urls),
    re_path(r'^grappelli/', include('grappelli.urls')),
    re_path(r'^ajax_select/', include(ajax_select_urls)),
    path('users/', include(('wastd.users.urls', 'users'), namespace='users')),
    path('accounts/', include('allauth.urls')),
    re_path(r'^adminactions/', include('adminactions.urls')),
    re_path(r'^select2/', include('django_select2.urls')),

    # TSC tax, cons, occ
    path('', include(('taxonomy.urls'), namespace='taxonomy')),
    path('conservation/', include(('conservation.urls'), namespace='conservation')),
    path('occurrence/', include(('occurrence.urls'), namespace='occurrence')),

    # WAStD Encounters
    path('encounters/', wastd_views.EncounterTableView.as_view(), name="encounter_list"),
    path('animal-encounters/', wastd_views.AnimalEncounterTableView.as_view(), name="animalencounter_list"),

    # API
    re_path(r'^api/1/swagger/$', wastd_views.schema_view, name="api-docs"),
    re_path(r'^api/1/docs/', include_docs_urls(title='API')),
    re_path(r'^api/1/', include((wastd_router.urls, 'api'), namespace="api")),
    re_path(r'^api-auth/', include(('rest_framework.urls', 'api-auth'), namespace='rest_framework')),
    re_path(r'^api-token-auth/', drf_authviews.obtain_auth_token, name="api-auth"),

    # Djgeojson
    re_path(r'^observations.geojson$',
            GeoJSONLayerView.as_view(
                model=wastd_models.Encounter,
                properties=('as_html', ),
                geometry_field="where"),
            name='observation-geojson'),

    re_path(r'^areas.geojson$',
            GeoJSONLayerView.as_view(
                model=wastd_models.Area,
                properties=('leaflet_title', 'as_html')),
            name='areas-geojson'),

    re_path(r'^sites.geojson$',
            GeoJSONLayerView.as_view(
                model=wastd_models.Area,
                queryset=wastd_models.Area.objects.filter(
                    area_type=wastd_models.Area.AREATYPE_SITE),
                properties=('leaflet_title', 'as_html')),
            name='sites-geojson'),

    # Encounter as tiled GeoJSON
    re_path(r'^data/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+).geojson$',
            TiledGeoJSONLayerView.as_view(
                model=wastd_models.AnimalEncounter,
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

    re_path(r'^tasks/import-odka/$', wastd_views.import_odka_view, name="import-odka"),
    re_path(r'^tasks/update-names/$', wastd_views.update_names_view, name="update-names"),
    re_path(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad request')}),
    re_path(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission denied')}),
    re_path(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not found')}),
    # url(r'^500/$', default_views.server_error, kwargs={'exception': Exception('Internal Server Error')}),
    re_path(r'favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico', permanent=True)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) +\
    staticfiles_urlpatterns()

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [re_path(r'^__debug__/', include(debug_toolbar.urls)), ]

if settings.PROFILING:
    urlpatterns += [re_path(r'^performance/', include(('silk.urls', 'silk'), namespace='silk')), ]
