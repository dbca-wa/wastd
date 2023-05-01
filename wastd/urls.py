from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path
from django.views.generic import TemplateView
from django.views import defaults
from djgeojson.views import GeoJSONLayerView, TiledGeoJSONLayerView
from rest_framework.authtoken import views as drf_authviews

from wastd.router import router
from wastd.router import urlpatterns as api_v2_urlpatterns
from observations import views as wastd_views
from observations.models import Area, AnimalEncounter


urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(template_name="logged_out.html"), name="logout"),
    path("grappelli/", include("grappelli.urls")),
    #path("grappelli-docs/", include('grappelli.urls_docs')),
    path("admin/", admin.site.urls),
    path("ajax_select/", include("ajax_select.urls")),
    path("select2/", include("django_select2.urls")),
    path("users/", include(("users.urls", "users"), namespace="users")),
    path("tagging/", include("tagging.urls")),
    path("observations/", include(("observations.urls"), namespace="observations")),
    # API
    path("api/1/", include((router.urls, "api"), namespace="api")),
    path('api/2/', include((api_v2_urlpatterns, "wastd"), namespace="api_v2")),
    path("api-auth/", include(("rest_framework.urls", "api-auth"), namespace="rest_framework")),
    path("api-token-auth/", drf_authviews.obtain_auth_token, name="api-auth"),
    # Djgeojson
    #path("observations.geojson", GeoJSONLayerView.as_view(model=Encounter, properties=("as_html",), geometry_field="where"), name="observation-geojson"),
    path("areas.geojson", GeoJSONLayerView.as_view(model=Area, properties=("leaflet_title", "as_html")), name="areas-geojson"),
    path("localities.geojson", GeoJSONLayerView.as_view(model=Area, queryset=Area.objects.filter(area_type=Area.AREATYPE_LOCALITY), properties=("leaflet_title", "as_html")), name="localities-geojson"),
    path("sites.geojson", GeoJSONLayerView.as_view(model=Area, queryset=Area.objects.filter(area_type=Area.AREATYPE_SITE), properties=("leaflet_title", "as_html")), name="sites-geojson"),
    # Encounter as tiled GeoJSON
    path("data/<int:z>/<int:x>/<int:y>.geojson", TiledGeoJSONLayerView.as_view(model=AnimalEncounter, properties=("as_html", "leaflet_title", "leaflet_icon", "leaflet_colour"), geometry_field="where"), name="encounter-tiled-geojson"),
    path("map/", wastd_views.MapView.as_view(), name="map"),
    path("tasks/import-odka/", wastd_views.import_odka_view, name="import-odka"),
    path("tasks/update-names/", wastd_views.update_names_view, name="update-names"),
    path("tasks/resave-surveys/", wastd_views.resave_surveys_view, name="resave-surveys"),
    path("tasks/reconstruct-surveys/", wastd_views.reconstruct_surveys_view, name="reconstruct-surveys"),
    path("400/", defaults.bad_request, kwargs={"exception": Exception("Bad request")}),
    path("403/", defaults.permission_denied, kwargs={"exception": Exception("Permission denied")}),
    path("404/", defaults.page_not_found, kwargs={"exception": Exception("Page not found")}),
    path("500/", defaults.server_error),
]
