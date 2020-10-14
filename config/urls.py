# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.admin import site
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views import defaults as default_views
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from ajax_select import urls as ajax_select_urls
from adminactions import actions
from djgeojson.views import GeoJSONLayerView, TiledGeoJSONLayerView
from rest_framework.authtoken import views as drf_authviews
from rest_framework.documentation import include_docs_urls
from graphene_django.views import GraphQLView

from occurrence.models import CommunityAreaEncounter
from wastd.router import router
from wastd.observations import models as wastd_models
from wastd.observations import views as wastd_views

from api.schema import schema

# register all adminactions
actions.add_to_site(site)

urlpatterns = [
    path('', TemplateView.as_view(template_name='pages/index.html'), name='home'),
    path('map/', wastd_views.HomeView.as_view(), name='map'),
    path('healthcheck/', TemplateView.as_view(template_name='pages/healthcheck.html'), name='healthcheck'),

    path(settings.ADMIN_URL, admin.site.urls),
    path('grappelli/', include('grappelli.urls')),
    path('ajax_select/', include(ajax_select_urls)),
    path('users/', include(('wastd.users.urls', 'users'), namespace='users')),
    path('accounts/', include('allauth.urls')),
    path('adminactions/', include('adminactions.urls')),
    path('select2/', include('django_select2.urls')),

    # TSC tax, cons, occ
    path('', include(('taxonomy.urls'), namespace='taxonomy')),
    path('conservation/', include(('conservation.urls'), namespace='conservation')),
    path('occurrence/', include(('occurrence.urls'), namespace='occurrence')),

    # WAStD Encounters
    path('encounters/', wastd_views.EncounterTableView.as_view(), name="encounter_list"),
    path('observations/', include(('wastd.observations.urls'), namespace='observations')),

    # API
    path('api/1/swagger/', wastd_views.schema_view, name="api-docs"),
    path('api/1/docs/', include_docs_urls(title='API')),
    path('api/1/', include((router.urls, 'api'), namespace="api")),
    path('api-auth/', include(('rest_framework.urls', 'api-auth'), namespace='rest_framework')),
    path('api-token-auth/', drf_authviews.obtain_auth_token, name="api-auth"),

    path('gql', GraphQLView.as_view(graphiql=True, schema=schema), name="gql-api"),

    # Djgeojson
    path('observations.geojson', GeoJSONLayerView.as_view(
        model=wastd_models.Encounter, properties=('as_html',), geometry_field="where"
    ), name='observation-geojson'),
    path('areas.geojson', GeoJSONLayerView.as_view(
        model=wastd_models.Area, properties=('leaflet_title', 'as_html')
    ), name='areas-geojson'),
    path('sites.geojson', GeoJSONLayerView.as_view(
        model=wastd_models.Area,
        queryset=wastd_models.Area.objects.filter(area_type=wastd_models.Area.AREATYPE_SITE),
        properties=('leaflet_title', 'as_html')
    ), name='sites-geojson'),

    # Encounter as tiled GeoJSON
    path('data/<int:z>/<int:x>/<int:y>.geojson', TiledGeoJSONLayerView.as_view(
        model=wastd_models.AnimalEncounter,
        properties=('as_html', 'leaflet_title', 'leaflet_icon', 'leaflet_colour'),
        geometry_field="where"
    ), name='encounter-tiled-geojson'),

    # CommunityAreaEncounter as tiled GeoJSON
    path('community-encounters-poly/<int:z>/<int:x>/<int:y>.geojson', TiledGeoJSONLayerView.as_view(
        model=CommunityAreaEncounter,
        properties=('as_html', 'label'),
        geometry_field="geom"
    ), name='community-area-encounter-tiled-geojson'),

    # path('areas/<int:z>/<int:x>/<int:y>.geojson', TiledGeoJSONLayerView.as_view(
    #     model=Area, properties=('name',), geometry_field="geom"
    # ), name='area-tiled-geojson'),

    path('tasks/import-odka/', wastd_views.import_odka_view, name="import-odka"),
    path('tasks/update-names/', wastd_views.update_names_view, name="update-names"),
    path('tasks/reconstruct-surveys/', wastd_views.reconstruct_surveys_view, name="reconstruct-surveys"),

    path('400/', default_views.bad_request, kwargs={'exception': Exception('Bad request')}),
    path('403/', default_views.permission_denied, kwargs={'exception': Exception('Permission denied')}),
    path('404/', default_views.page_not_found, kwargs={'exception': Exception('Page not found')}),
    # path('500/', default_views.server_error, kwargs={'exception': Exception('Internal Server Error')}),
    path('favicon.ico', RedirectView.as_view(url='/static/images/favicon.ico', permanent=True)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) +\
    staticfiles_urlpatterns()

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls)), ]

if settings.PROFILING:
    urlpatterns += [path('performance/', include(('silk.urls', 'silk'), namespace='silk')), ]
