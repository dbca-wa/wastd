"""Shared admin."""
from django.contrib.admin.widgets import AdminFileWidget
from django.contrib.gis.db import models as geo_models
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from django_fsm_log.admin import StateLogInline
from leaflet.forms.widgets import LeafletWidget
from reversion.admin import VersionAdmin


# Fix collapsing widget width
# https://github.com/applegrew/django-select2/issues/252
S2ATTRS = {"data-width": "50em"}

LEAFLET_WIDGET_ATTRS = {
    "map_height": "700px",
    "map_width": "100%",
    "display_raw": "true",
    "map_srid": 4326,
}
LEAFLET_SETTINGS = {"widget": LeafletWidget(attrs=LEAFLET_WIDGET_ATTRS)}


class CustomStateLogInline(StateLogInline):
    """Custom StateLogInline."""

    classes = (
        "grp-collapse",
        #"grp-closed",
        "wide",
        "extrapretty",
    )


class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None, renderer=None):
        output = []

        if value and getattr(value, "url", None):
            image_url = value.url
            file_name = str(value)

            output.append(
                f' <a href="{image_url}" target="_blank">'
                f'  <img src="{image_url}" alt="{file_name}" width="150" height="150" '
                f'style="object-fit: cover;"/> </a>'
            )

        output.append(super(AdminFileWidget, self).render(name, value, attrs, renderer))
        return mark_safe("".join(output))


FORMFIELD_OVERRIDES = {
    geo_models.PointField: LEAFLET_SETTINGS,
    geo_models.MultiPointField: LEAFLET_SETTINGS,
    geo_models.LineStringField: LEAFLET_SETTINGS,
    geo_models.MultiLineStringField: LEAFLET_SETTINGS,
    geo_models.PolygonField: LEAFLET_SETTINGS,
    geo_models.MultiPolygonField: LEAFLET_SETTINGS,
    models.ImageField: {"widget": AdminImageWidget},
    models.FileField: {"widget": AdminImageWidget},
}
