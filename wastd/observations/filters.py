# -*- coding: utf-8 -*-
"""Filters for WAStD Observations."""
# from leaflet.forms.widgets import LeafletWidget
import rest_framework_filters as filters
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _
from django_filters import widgets, FilterSet
from rest_framework_gis import filters as gis_filters
from rest_framework_gis.filterset import GeoFilterSet

from wastd.observations.models import AnimalEncounter, Area, Encounter


class AreaFilter(GeoFilterSet):
    """AreaFilter."""

    name = filters.CharFilter(name='name', lookup_type='istartswith')
    contains_geom = gis_filters.GeometryFilter(name='geom', lookup_type='contains')

    class Meta:
        """Class opts."""

        model = Area
        fields = ['name', ]


class LocationListFilter(SimpleListFilter):
    """A custom ListFilter to filter Encounters by location."""

    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Area')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'where'

    def lookups(self, request, model_admin):
        """Return a list of tuples.

        The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return [(a.pk, a.name) for a in Area.objects.all()]
        # Area.objects.filter(area_type=Area.AREATYPE_MPA)]

    def queryset(self, request, queryset):
        """Return the filtered queryset.

        QS is based on the value provided in the query string
        and retrievable via `self.value()`.
        """
        if self.value():
            a = Area.objects.get(pk=self.value())
            return queryset.filter(where__within=a.geom)
        return queryset

    class Meta:
        """Class opts."""

        model = Area
        fields = ['name', ]


class EncounterFilter(filters.FilterSet):
    """Encounter Filter.

    https://django-filter.readthedocs.io/en/latest/usage.html
    """

    # name = filters.CharFilter(
    #     lookup_expr='icontains',
    #     help_text=_("Name supports partial match, e.g. searching for "
    #                 "WA12 will return encounters with WA123 and WA124."))
    # source_id = filters.CharFilter(
    #     lookup_expr='icontains',
    #     help_text=_("Source ID supports partial match.")
    #     )
    when = filters.DateFromToRangeFilter(
        help_text="Date format: YYYY-mm-dd, e.g. 2015-12-31",
        widget=widgets.RangeWidget(attrs={'placeholder': 'YYYY-mm-dd'}))
    # where = django_filters.CharFilter(
    #     widget=LeafletWidget(attrs={
    #         'map_height': '400px',
    #         'map_width': '100%',
    #         'display_raw': 'False',
    #         'map_srid': 4326,
    #         }))

    class Meta:
        """Options for EncounterFilter."""

        model = Encounter
        # fields = ['when', ]
        exclude = ['where', ]


class AnimalEncounterFilter(EncounterFilter):
    """AnimalEncounter Filter."""

    class Meta:
        """Class opts."""

        model = AnimalEncounter
        exclude = ['where', ]


class AnimalEncounterFilter2(FilterSet):
    class Meta:
        model = AnimalEncounter
        fields = ['taxon', 'species']
