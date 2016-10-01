# -*- coding: utf-8 -*-
"""Filters for WAStD Observations."""
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _

import django_filters
from django_filters import filters, widgets
# from leaflet.forms.widgets import LeafletWidget

from wastd.observations.models import Encounter, AnimalEncounter


# class ObservationTypeListFilter(SimpleListFilter):
#     """A custom ListFilter to filter Encounters by observation type."""
#
#     # Human-readable title which will be displayed in the
#     # right admin sidebar just above the filter options.
#     title = _('observation type')
#
#     # Parameter for the filter that will be used in the URL query.
#     parameter_name = 'observation_type'
#
#     def lookups(self, request, model_admin):
#         """
#         Returns a list of tuples. The first element in each
#         tuple is the coded value for the option that will
#         appear in the URL query. The second element is the
#         human-readable name for the option that will appear
#         in the right sidebar.
#         """
#         return (
#             ('stranding', _('stranding')),
#             ('nesting', _('nesting')),
#             ('in water', _('in water')),
#             )
#
#     def queryset(self, request, queryset):
#         """
#         Returns the filtered queryset based on the value
#         provided in the query string and retrievable via
#         `self.value()`.
#         """
#         # Compare the requested value (either '80s' or '90s')
#         # to decide how to filter the queryset.
#         if self.value() == 'stranding':
#             return queryset.exclude(health__exact='alive')
#         if self.value() == 'nesting':
#             return queryset.filter(health__exact='alive')
#         if self.value() == 'in water':
#             return queryset.filter(habitat__in=AnimalEncounter.HABITAT_WATER)


class EncounterFilter(django_filters.FilterSet):
    """Encounter Filter.

    https://django-filter.readthedocs.io/en/latest/usage.html

    TODO https://django-filter.readthedocs.io/en/latest/ref/filters.html#method
         is_tagging / is_stranding / is_open_water
    """
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        help_text=_("Name supports partial match, e.g. searching for "
                    "WA12 will return encounters with WA123 and WA124."))
    source_id = django_filters.CharFilter(
        lookup_expr='icontains',
        help_text=_("Source ID supports partial match.")
        )
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


class AnimalEncounterFilter(EncounterFilter):
    """AnimalEncounter Filter."""

    class Meta:
        """Options for AnimalEncounterFilter."""
        model = AnimalEncounter
