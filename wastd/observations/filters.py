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
    Survey,
    Encounter,
    AnimalEncounter,
    TurtleNestEncounter,
    LoggerEncounter,
    LineTransectEncounter
)


class SurveyFilter(FilterSet):
    """Survey Filter.

    https://django-filter.readthedocs.io/en/latest/usage.html
    """
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
        model = Survey
        filter_overrides = FILTER_OVERRIDES
        fields = [
            'source',
            'source_id',
            'device_id',
            'site',
            'reporter',
            'start_location',
            'start_location_accuracy_m',
            'start_time',
            'start_comments',
            'end_source_id',
            'end_device_id',
            'end_location',
            'end_location_accuracy_m',
            'end_time',
            'end_comments',
            'production',
            # 'team', # m2m
            # 'label',
            'transect',
        ]



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


class LoggerEncounterFilter(EncounterFilter):

    class Meta(EncounterFilter.Meta):
        model = LoggerEncounter
        fields = EncounterFilter._meta.fields + [
            'logger_type',
            'deployment_status',
            'logger_id',
        ]


class LineTransectEncounterFilter(EncounterFilter):

    class Meta(EncounterFilter.Meta):
        model = LineTransectEncounter
        fields = EncounterFilter._meta.fields + [
            'transect',
        ]
