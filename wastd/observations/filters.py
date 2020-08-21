# -*- coding: utf-8 -*-
"""Filters for WAStD Observations."""
# from leaflet.forms.widgets import LeafletWidget
import rest_framework_filters as filters
from django.contrib.admin import SimpleListFilter
from django.contrib.gis.db import models as geo_models
from django.utils.translation import ugettext_lazy as _
from django_filters import FilterSet
from django_filters.filters import (  # noqa
    BooleanFilter, CharFilter,
    ChoiceFilter, MultipleChoiceFilter,
    ModelChoiceFilter, ModelMultipleChoiceFilter)
from shared.filters import FILTER_OVERRIDES
from wastd.observations.models import (
    Area,
    Encounter,
    AnimalEncounter,
    TurtleNestEncounter,
    LoggerEncounter,
    LineTransectEncounter
)

class EncounterFilter(FilterSet):
    """Encounter Filter.

    https://django-filter.readthedocs.io/en/latest/usage.html
    """
    area = ModelChoiceFilter(
        label="Locality",
        queryset=Area.objects.filter(
            area_type__in=[Area.AREATYPE_LOCALITY,]
        ).order_by(
            "-northern_extent",
            "name"
        ),
        # method='taxa_occurring_in_area'
    )
    site = ModelChoiceFilter(
        label="Site",
        queryset=Area.objects.filter(
            area_type__in=[Area.AREATYPE_SITE,]
        ).order_by(
            "-northern_extent",
            "name"
        ),
        # method='taxa_occurring_in_area'
    )
    class Meta:
        """Options for EncounterFilter."""
        model = Encounter
        filter_overrides = FILTER_OVERRIDES
        fields = [
            'area',
            'site',
            'when',
            'where',
            'encounter_type',
            'source',
        ]


class AnimalEncounterFilter(EncounterFilter):

    class Meta(EncounterFilter.Meta):
        model = AnimalEncounter
        fields = EncounterFilter._meta.fields + [
            'taxon',
            'species',
            'sex',
            'maturity',
            'health',
            'activity',
            'habitat',
            'nesting_event',
            'laparoscopy',
            'checked_for_injuries',
            'scanned_for_pit_tags',
            'checked_for_flipper_tags',
            'cause_of_death',
        ]


class TurtleNestEncounterFilter(EncounterFilter):

    class Meta(EncounterFilter.Meta):
        model = TurtleNestEncounter
        fields = EncounterFilter._meta.fields + [
            'species',
            'nest_type',
            'nest_age',
            'habitat',
            'disturbance',
            'nest_tagged',
            'logger_found',
            'eggs_counted',
            'hatchlings_measured',
            'fan_angles_measured',
        ]
