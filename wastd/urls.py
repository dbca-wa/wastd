from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path
from django.views.generic import TemplateView
from django.views import defaults
from djgeojson.views import GeoJSONLayerView

from wastd.router import urlpatterns as api_urlpatterns
from observations import views as observations_views
from observations.models import Area, AnimalEncounter
from django.conf import settings


urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(template_name="logged_out.html"), name="logout"),
    path("grappelli/", include("grappelli.urls")),
    #path("grappelli-docs/", include('grappelli.urls_docs')),
    path('_nested_admin/', include('nested_admin.urls')), 
    path("admin/", admin.site.urls),
    #path("ajax_select/", include("ajax_select.urls")),
    path("select2/", include("django_select2.urls")),
    path("users/", include(("users.urls", "users"), namespace="users")),
    path("observations/", include(("observations.urls"), namespace="observations")),
    path("wamtram2/", include(("wamtram2.urls"), namespace="wamtram2")),
    path("map/", observations_views.MapView.as_view(), name="map"),
    # API
    path('api/1/', include((api_urlpatterns, "wastd"), namespace="api")),
    # Spatial data layers
    path(
        "areas.geojson",
        GeoJSONLayerView.as_view(model=Area, properties=["leaflet_title"]),
        name="areas_geojson",
    ),
    path(
        "localities.geojson",
        GeoJSONLayerView.as_view(
            model=Area,
            queryset=Area.objects.filter(area_type=Area.AREATYPE_LOCALITY),
            properties=["leaflet_title"],
        ),
        name="localities_geojson",
    ),
    path(
        "sites.geojson",
        GeoJSONLayerView.as_view(
            model=Area,
            queryset=Area.objects.filter(area_type=Area.AREATYPE_SITE),
            properties=["leaflet_title"],
        ),
        name="sites_geojson",
    ),
    path(
        "strandings.geojson",
        GeoJSONLayerView.as_view(
            model=AnimalEncounter,
            queryset=AnimalEncounter.objects.filter(encounter_type='stranding'),
            geometry_field="where",
            properties=["as_html", "leaflet_title", "leaflet_icon", "leaflet_colour"],
        ),
        name="strandings_geojson",
    ),
    # Error pages
    path("400/", defaults.bad_request, kwargs={"exception": Exception("Bad request")}),
    path("403/", defaults.permission_denied, kwargs={"exception": Exception("Permission denied")}),
    path("404/", defaults.page_not_found, kwargs={"exception": Exception("Page not found")}),
    path("500/", defaults.server_error),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
