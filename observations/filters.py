from django_filters import FilterSet
from django_filters.filters import (
    DateFilter,
    BooleanFilter,
    ChoiceFilter,
    MultipleChoiceFilter,
    ModelChoiceFilter,
)
from shared.filters import FILTER_OVERRIDES
from users.models import User
from .models import (
    Area,
    Survey,
    Encounter,
    AnimalEncounter,
    TurtleNestEncounter,
    LineTransectEncounter,
)
from .lookups import (
    HEALTH_CHOICES,
    SOURCE_CHOICES,
    ACTIVITY_CHOICES,
    SPECIES_CHOICES,
    TURTLE_SPECIES_CHOICES,
)


class SurveyFilter(FilterSet):
    no_start = BooleanFilter(label="Start Point reconstructed", field_name="source_id", lookup_expr="isnull")
    no_end = BooleanFilter(label="End Point reconstructed", field_name="end_source_id", lookup_expr="isnull")
    area = ModelChoiceFilter(
        label="Locality",
        queryset=Area.objects.filter(area_type__in=[Area.AREATYPE_LOCALITY]).order_by("name"),
    )
    site = ModelChoiceFilter(
        label="Site",
        queryset=Area.objects.filter(area_type__in=[Area.AREATYPE_SITE]).order_by("name"),
    )
    survey_date = DateFilter(field_name="start_time", lookup_expr="date", label="Exact survey date (YYYY-mm-dd)")

    class Meta:
        model = Survey
        filter_overrides = FILTER_OVERRIDES
        fields = [
            "campaign__owner",
            "area",
            "site",
            "no_start",
            "no_end",
            "production",
            "source",
            "source_id",
            "device_id",
            "reporter",
            "start_location",
            "start_location_accuracy_m",
            "start_time",
            "start_comments",
            "end_source_id",
            "end_device_id",
            "end_location",
            "end_location_accuracy_m",
            "end_time",
            "end_comments",
            "transect",
        ]


class SurveyBasicFilter(FilterSet):
    date_from = DateFilter(
        field_name="start_time",
        lookup_expr="date__gte",
        label="Date from",
    )
    date_to = DateFilter(
        field_name="end_time",
        lookup_expr="date__lte",
        label="Date to",
    )
    user_reporter = ModelChoiceFilter(
        field_name="reporter",
        label="Reported by",
        queryset=User.objects.filter(pk__in=set(Survey.objects.values_list("reporter", flat=True))).order_by("name"),
    )
    area = ModelChoiceFilter(
        label="Locality",
        queryset=Area.objects.filter(area_type__in=[Area.AREATYPE_LOCALITY]).order_by("name"),
    )
    site = ModelChoiceFilter(
        label="Site",
        queryset=Area.objects.filter(area_type__in=[Area.AREATYPE_SITE]).order_by("name"),
    )


class EncounterFilter(FilterSet):
    area = ModelChoiceFilter(
        label="Locality",
        queryset=Area.objects.filter(area_type__in=[Area.AREATYPE_LOCALITY]).order_by("name"),
    )
    site = ModelChoiceFilter(
        label="Site",
        queryset=Area.objects.filter(area_type__in=[Area.AREATYPE_SITE]).order_by("name"),
    )
    encounter_date = DateFilter(
        field_name="when", lookup_expr="date", label="Exact encounter date (YYYY-mm-dd)"
    )
    source = ChoiceFilter(field_name="source", choices=sorted(SOURCE_CHOICES), label="Data Source")

    class Meta:
        model = Encounter
        filter_overrides = FILTER_OVERRIDES
        fields = [
            "campaign__owner",
            "area",
            "site",
            "when",
            "where",
            "reporter",
            "observer",
            "encounter_type",
            "source",
        ]


class AnimalEncounterFilter(EncounterFilter):
    health = MultipleChoiceFilter(choices=sorted(HEALTH_CHOICES))
    activity = ChoiceFilter(field_name="activity", choices=sorted(ACTIVITY_CHOICES))
    species = ChoiceFilter(field_name="species", choices=sorted(SPECIES_CHOICES))

    class Meta(EncounterFilter.Meta):

        model = AnimalEncounter
        fields = EncounterFilter._meta.fields + [
            "identifiers",
            "taxon",
            "species",
            "sex",
            "maturity",
            "health",
            "activity",
            "habitat",
            "sighting_status",
            "sighting_status_reason",
            "datetime_of_last_sighting",
            "site_of_first_sighting",
            "site_of_last_sighting",
            "nesting_event",
            "nesting_disturbed",
            "laparoscopy",
            "checked_for_injuries",
            "scanned_for_pit_tags",
            "checked_for_flipper_tags",
            "cause_of_death",
        ]


class AnimalEncounterBasicFilter(FilterSet):
    date_from = DateFilter(
        field_name="when",
        lookup_expr="date__gte",
        label="Date from",
    )
    date_to = DateFilter(
        field_name="when",
        lookup_expr="date__lte",
        label="Date to",
    )
    user_observer = ModelChoiceFilter(
        field_name="observer",
        label="Observed by",
        queryset=User.objects.filter(pk__in=set(AnimalEncounter.objects.values_list("observer", flat=True))).order_by("name"),
    )
    user_reporter = ModelChoiceFilter(
        field_name="reporter",
        label="Reported by",
        queryset=User.objects.filter(pk__in=set(AnimalEncounter.objects.values_list("reporter", flat=True))).order_by("name"),
    )
    encounter_type = ChoiceFilter(
        field_name="encounter_type",
        choices=(
            (Encounter.ENCOUNTER_INWATER, "In water"),
            #(Encounter.ENCOUNTER_LOGGER, "Logger"),
            #(Encounter.ENCOUNTER_OTHER, "Other"),
            (Encounter.ENCOUNTER_STRANDING, "Stranding"),
            (Encounter.ENCOUNTER_TAGGING, "Tagging"),
            #(Encounter.ENCOUNTER_TAG, "Tag Management"),
        ),
    )
    species = ChoiceFilter(field_name="species", choices=sorted(SPECIES_CHOICES))
    health = ChoiceFilter(choices=sorted(HEALTH_CHOICES))
    area = ModelChoiceFilter(
        label="Locality",
        queryset=Area.objects.filter(area_type__in=[Area.AREATYPE_LOCALITY]).order_by("name"),
    )
    site = ModelChoiceFilter(
        label="Site",
        queryset=Area.objects.filter(area_type__in=[Area.AREATYPE_SITE]).order_by("name"),
    )
    status = ChoiceFilter(
        field_name="status",
        choices=(
            (Encounter.STATUS_NEW, "New"),
            (Encounter.STATUS_CURATED, "Curated"),
            (Encounter.STATUS_FLAGGED, "Flagged"),
        ),
        label="QA status",
    )

    class Meta:
        model = AnimalEncounter
        fields = [
            "date_from",
            "date_to",
            "user_observer",
            "user_reporter",
            "encounter_type",
            "area",  # Locality
            "site",
            "species",
            "health",
            "status",
        ]


class TurtleNestEncounterFilter(EncounterFilter):

    class Meta(EncounterFilter.Meta):
        model = TurtleNestEncounter
        fields = EncounterFilter._meta.fields + [
            "species",
            "nest_type",
            "nest_age",
            "habitat",
            "disturbance",
            "nest_tagged",
            "logger_found",
            "eggs_counted",
            "hatchlings_measured",
            "fan_angles_measured",
        ]


class TurtleNestEncounterBasicFilter(FilterSet):
    date_from = DateFilter(
        field_name="when",
        lookup_expr="date__gte",
        label="Date from",
    )
    date_to = DateFilter(
        field_name="when",
        lookup_expr="date__lte",
        label="Date to",
    )
    user_observer = ModelChoiceFilter(
        field_name="observer",
        label="Observed by",
        queryset=User.objects.filter(pk__in=set(TurtleNestEncounter.objects.values_list("observer", flat=True))).order_by("name"),
    )
    user_reporter = ModelChoiceFilter(
        field_name="reporter",
        label="Reported by",
        queryset=User.objects.filter(pk__in=set(TurtleNestEncounter.objects.values_list("reporter", flat=True))).order_by("name"),
    )
    species = ChoiceFilter(field_name="species", choices=sorted(TURTLE_SPECIES_CHOICES))
    area = ModelChoiceFilter(
        label="Locality",
        queryset=Area.objects.filter(area_type__in=[Area.AREATYPE_LOCALITY]).order_by("name"),
    )
    site = ModelChoiceFilter(
        label="Site",
        queryset=Area.objects.filter(area_type__in=[Area.AREATYPE_SITE]).order_by("name"),
    )
    status = ChoiceFilter(
        field_name="status",
        choices=(
            (Encounter.STATUS_NEW, "New"),
            (Encounter.STATUS_CURATED, "Curated"),
            (Encounter.STATUS_FLAGGED, "Flagged"),
        ),
        label="QA status",
    )

    class Meta:
        model = TurtleNestEncounter
        fields = [
            "date_from",
            "date_to",
            "user_observer",
            "user_reporter",
            "nest_type",
            "area",  # Locality
            "site",
            "species",
            "status",
        ]


class LineTransectEncounterFilter(EncounterFilter):

    class Meta(EncounterFilter.Meta):
        model = LineTransectEncounter
        fields = EncounterFilter._meta.fields + [
            "transect",
        ]
