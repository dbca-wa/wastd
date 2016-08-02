# -*- coding: utf-8 -*-
"""Custom Widgets for WAStD
"""

from django.contrib.gis import forms


class MapWidget(forms.BaseGeometryWidget):
    """
    An OpenLayers/OpenStreetMap-based widget with additional inputs.

    In development.

    Goal:

    * Lat/Lon/Datum input in addition to map
    * Geocoder?
    """

    template_name = 'gis/mapwidget.html'
    default_lon = 125
    default_lat = -23
    map_srid = 4326
    display_raw = 'false'
    mouse_position = 'true'

    class Media:
        """JS resources for the MapWidget."""
        js = ('http://static.dpaw.wa.gov.au/static/libs/openlayers/2.13.1/OpenLayers.js',
              'http://www.openstreetmap.org/openlayers/OpenStreetMap.js',
              'js/MapWidget.js',)

    def __init__(self, attrs=None):
        """Allow overriding default_lat, default_lon, map_srid, display_raw."""
        super(MapWidget, self).__init__()
        for key in ('default_lon', 'default_lat', 'map_srid',
                    'display_raw', 'mouse_position'):
            self.attrs[key] = getattr(self, key)
        if attrs:
            self.attrs.update(attrs)
