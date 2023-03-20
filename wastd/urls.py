#from ajax_select import urls as ajax_select_urls
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path
from django.views.generic import TemplateView
from django.views import defaults
from djgeojson.views import GeoJSONLayerView, TiledGeoJSONLayerView
from rest_framework.authtoken import views as drf_authviews

from wastd.router import router
from observations import models as wastd_models
from observations import views as wastd_views


urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path("map/", wastd_views.MapView.as_view(), name="map"),
    path("admin/", admin.site.urls),
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(template_name="logged_out.html"), name="logout"),
    path("grappelli/", include("grappelli.urls")),
    path("ajax_select/", include("ajax_select.urls")),
    path("select2/", include("django_select2.urls")),
    path("users/", include(("users.urls", "users"), namespace="users")),
    path("tagging/", include("turtle_tag.urls")),
    path("encounters/", wastd_views.EncounterTableView.as_view(), name="encounter_list"),
    path("observations/", include(("observations.urls"), namespace="observations")),
    # API
    path("api/1/", include((router.urls, "api"), namespace="api")),
    path("api-auth/", include(("rest_framework.urls", "api-auth"), namespace="rest_framework")),
    path("api-token-auth/", drf_authviews.obtain_auth_token, name="api-auth"),
    # Djgeojson
    path(
        "observations.geojson",
        GeoJSONLayerView.as_view(
            model=wastd_models.Encounter,
            properties=("as_html",),
            geometry_field="where",
        ),
        name="observation-geojson",
    ),
    path(
        "areas.geojson",
        GeoJSONLayerView.as_view(
            model=wastd_models.Area, properties=("leaflet_title", "as_html")
        ),
        name="areas-geojson",
    ),
    path(
        "localities.geojson",
        GeoJSONLayerView.as_view(
            model=wastd_models.Area,
            queryset=wastd_models.Area.objects.filter(
                area_type=wastd_models.Area.AREATYPE_LOCALITY
            ),
            properties=("leaflet_title", "as_html"),
        ),
        name="localities-geojson",
    ),
    path(
        "sites.geojson",
        GeoJSONLayerView.as_view(
            model=wastd_models.Area,
            queryset=wastd_models.Area.objects.filter(
                area_type=wastd_models.Area.AREATYPE_SITE
            ),
            properties=("leaflet_title", "as_html"),
        ),
        name="sites-geojson",
    ),
    # Encounter as tiled GeoJSON
    path(
        "data/<int:z>/<int:x>/<int:y>.geojson",
        TiledGeoJSONLayerView.as_view(
            model=wastd_models.AnimalEncounter,
            properties=(
                "as_html",
                "leaflet_title",
                "leaflet_icon",
                "leaflet_colour",
            ),
            geometry_field="where",
        ),
        name="encounter-tiled-geojson",
    ),
    # CommunityAreaEncounter as tiled GeoJSON
    # path('community-encounters-poly/<int:z>/<int:x>/<int:y>.geojson', TiledGeoJSONLayerView.as_view(
    #     model=CommunityAreaEncounter,
    #     properties=('as_html', 'label'),
    #     geometry_field="geom"
    # ), name='community-area-encounter-tiled-geojson'),
    # path('areas/<int:z>/<int:x>/<int:y>.geojson', TiledGeoJSONLayerView.as_view(
    #     model=Area, properties=('name',), geometry_field="geom"
    # ), name='area-tiled-geojson'),
    path("tasks/import-odka/", wastd_views.import_odka_view, name="import-odka"),
    path("tasks/update-names/", wastd_views.update_names_view, name="update-names"),
    path("tasks/resave-surveys/", wastd_views.resave_surveys_view, name="resave-surveys"),
    path("tasks/reconstruct-surveys/", wastd_views.reconstruct_surveys_view, name="reconstruct-surveys"),
    path("400/", defaults.bad_request, kwargs={"exception": Exception("Bad request")}),
    path("403/", defaults.permission_denied, kwargs={"exception": Exception("Permission denied")}),
    path("404/", defaults.page_not_found, kwargs={"exception": Exception("Page not found")}),
    path("500/", defaults.server_error),
]
