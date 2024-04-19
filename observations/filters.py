from django.conf import settings
from django_filters import FilterSet
from django_filters.filters import (
    DateFilter,
    ChoiceFilter,
    ModelChoiceFilter,
)
from users.models import User
from wastd.utils import FILTER_OVERRIDES
from .models import (
    Area,
    Survey,
    Encounter,
    AnimalEncounter,
    TurtleNestEncounter,
    LineTransectEncounter,
    TurtleNestDisturbanceObservation,
)
from .lookups import (
    HEALTH_CHOICES,
    SOURCE_CHOICES,
    SPECIES_CHOICES,
    TURTLE_SPECIES_CHOICES,
)


class SurveyFilter(FilterSet):
    date_from = DateFilter(
        field_name="start_time",
        lookup_expr="date__gte",
        label="Date from",
        input_formats=settings.DATE_INPUT_FORMATS,
    )
    date_to = DateFilter(
        field_name="end_time",
        lookup_expr="date__lte",
        label="Date to",
        input_formats=settings.DATE_INPUT_FORMATS,
    )
    user_reporter = ModelChoiceFilter(
        field_name="reporter",
        label="Reported by",
        queryset=User.objects.filter(is_active=True).order_by("name"),
        # NOTE: we can't filter the queryset here due to a circular dependency that breaks Django migrations.
        #queryset = User.objects.filter(pk__in=set(Survey.objects.values_list("reporter", flat=True))).order_by("name")
    )
    area = ModelChoiceFilter(
        label="Locality",
        queryset=Area.objects.filter(area_type__in=[Area.AREATYPE_LOCALITY]).order_by("name"),
    )
    site = ModelChoiceFilter(
        label="Site",
        queryset=Area.objects.filter(area_type__in=[Area.AREATYPE_SITE]).order_by("name"),
        null_label="<No site>",
    )

    class Meta:
        model = Survey
        fields = [
            "date_from",
            "date_to",
            "user_reporter",
            "area",
            "site",
            "production",
        ]


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
        field_name="when",
        lookup_expr="date",
        label="Exact encounter date",
        input_formats=settings.DATE_INPUT_FORMATS,
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


class AnimalEncounterFilter(FilterSet):
    date_from = DateFilter(
        field_name="when",
        lookup_expr="date__gte",
        label="Date from",
        input_formats=settings.DATE_INPUT_FORMATS,
    )
    date_to = DateFilter(
        field_name="when",
        lookup_expr="date__lte",
        label="Date to",
        input_formats=settings.DATE_INPUT_FORMATS,
    )
    user_reporter = ModelChoiceFilter(
        field_name="reporter",
        label="Reported by",
        queryset=User.objects.filter(is_active=True).order_by("name"),
    )
    user_observer = ModelChoiceFilter(
        field_name="observer",
        label="Observed by",
        queryset=User.objects.filter(is_active=True).order_by("name"),
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
        null_label="<No site>",
    )
    status = ChoiceFilter(
        field_name="status",
        choices=(
            (Encounter.STATUS_IMPORTED, "Imported"),
            (Encounter.STATUS_MANUAL_INPUT, "Manual input"),
            (Encounter.STATUS_CURATED, "Curated"),
            (Encounter.STATUS_FLAGGED, "Flagged"),
            (Encounter.STATUS_REJECTED, "Rejected"),
        ),
        label="QA status",
    )

    class Meta:
        model = AnimalEncounter
        fields = [
            "status",
            "date_from",
            "date_to",
            "user_reporter",
            "user_observer",
            "encounter_type",
            "area",  # Locality
            "site",
            "species",
            "health",
        ]


class TurtleNestEncounterFilter(FilterSet):

    date_from = DateFilter(
        field_name="when",
        lookup_expr="date__gte",
        label="Date from",
        input_formats=settings.DATE_INPUT_FORMATS,
    )
    date_to = DateFilter(
        field_name="when",
        lookup_expr="date__lte",
        label="Date to",
        input_formats=settings.DATE_INPUT_FORMATS,
    )
    user_observer = ModelChoiceFilter(
        field_name="observer",
        label="Observed by",
        queryset=User.objects.filter(is_active=True).order_by("name"),
    )
    survey = ChoiceFilter(
        field_name="survey",
        choices=(
            ("null","<No survey>"),
        ),
        label="Survey",
    )
    encounter_type = ChoiceFilter(
        field_name="encounter_type",
        choices=(
            (Encounter.ENCOUNTER_NEST, "Nest"),
            (Encounter.ENCOUNTER_TRACKS, "Tracks"),
        ),
        label="Nest/tracks",
    )
    nest_type = ChoiceFilter(
        field_name="nest_type",
        choices=(
            ("successful-crawl", "Track with nest"),
            ("false-crawl", "Track without nest (false crawl)"),
            ("track-not-assessed", "Track, not checked for nest"),
            ("nest", "Nest, unhatched, no track"),
            ("hatched-nest", "Nest, hatched"),
            ("body-pit", "Body pit, no track"),
        ),
        label="Nest type",
    )
    species = ChoiceFilter(field_name="species", choices=sorted(TURTLE_SPECIES_CHOICES))
    area = ModelChoiceFilter(
        label="Locality",
        queryset=Area.objects.filter(area_type__in=[Area.AREATYPE_LOCALITY]).order_by("name"),
    )
    site = ModelChoiceFilter(
        label="Site",
        queryset=Area.objects.filter(area_type__in=[Area.AREATYPE_SITE]).order_by("name"),
        null_label="<No site>",
    )
    status = ChoiceFilter(
        field_name="status",
        choices=(
            (Encounter.STATUS_IMPORTED, "Imported"),
            (Encounter.STATUS_MANUAL_INPUT, "Manual input"),
            (Encounter.STATUS_CURATED, "Curated"),
            (Encounter.STATUS_FLAGGED, "Flagged"),
            (Encounter.STATUS_REJECTED, "Rejected"),
        ),
        label="QA status",
    )

    class Meta:
        model = TurtleNestEncounter
        fields = [
            "status",
            "date_from",
            "date_to",
            "user_observer",
            #"user_reporter",
            "encounter_type",
            "nest_type",
            "nest_age",
            "area",
            "site",
            "species",
            "disturbance",
            "nest_tagged",
            "logger_found",
            "eggs_counted",
            "hatchlings_measured",
            "fan_angles_measured",
        ]


class LineTransectEncounterFilter(EncounterFilter):

    class Meta(EncounterFilter.Meta):
        model = LineTransectEncounter
        fields = EncounterFilter._meta.fields + [
            "transect",
        ]


class TurtleNestDisturbanceObservationFilter(FilterSet):
    date_from = DateFilter(
        field_name="encounter__when",
        lookup_expr="date__gte",
        label="Date from",
        input_formats=settings.DATE_INPUT_FORMATS,
    )
    date_to = DateFilter(
        field_name="encounter__when",
        lookup_expr="date__lte",
        label="Date to",
        input_formats=settings.DATE_INPUT_FORMATS,
    )
    area = ModelChoiceFilter(
        field_name="encounter__area",
        label="Locality",
        queryset=Area.objects.filter(area_type__in=[Area.AREATYPE_LOCALITY]).order_by("name"),
    )
    site = ModelChoiceFilter(
        field_name="encounter__site",
        label="Site",
        queryset=Area.objects.filter(area_type__in=[Area.AREATYPE_SITE]).order_by("name"),
        null_label="<No site>",
    )
    status = ChoiceFilter(
        field_name="encounter__status",
        choices=(
            (Encounter.STATUS_IMPORTED, "Imported"),
            (Encounter.STATUS_MANUAL_INPUT, "Manual input"),
            (Encounter.STATUS_CURATED, "Curated"),
            (Encounter.STATUS_FLAGGED, "Flagged"),
            (Encounter.STATUS_REJECTED, "Rejected"),
        ),
        label="QA status",
    )

    class Meta:
        model = TurtleNestDisturbanceObservation
        fields = [
            "date_from",
            "date_to",
            "area",
            "site",
            "status",
            "disturbance_severity",
            "disturbance_cause",
            "disturbance_cause_confidence",
        ]
