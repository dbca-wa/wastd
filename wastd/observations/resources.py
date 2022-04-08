from import_export.resources import ModelResource
from wastd.observations.models import (
    Encounter,
    AnimalEncounter,
    TurtleNestEncounter,
    LoggerEncounter,
    LineTransectEncounter,
    Survey
)


class SurveyResource(ModelResource):
    class Meta:
        model = Survey
        fields = [
            'source',
            'source_id',
            'device_id',
            'site',
            'transect',
            'reporter',
            'reporter__name',
            'start_location',
            'start_location_accuracy_m',
            'start_time',
            'start_photo',
            'start_comments',
            'end_source_id',
            'end_device_id',
            'end_location',
            'end_location_accuracy_m',
            'end_time',
            'end_photo',
            'end_comments',
            'production',
            'team',
            'label',
        ]


class EncounterResource(ModelResource):
    class Meta:
        model = Encounter
        fields = [
            'source',
            'source_id',
            'where',
            'wkt'
            'longitude',
            'latitude',
            'location_accuracy_m',
            'when',
            'area',
            'area__name',
            'site',
            'site__name',
            'observer',
            'observer__name',
            'reporter',
            'reporter__name',
            'encounter_type',
        ]


class AnimalEncounterResource(ModelResource):
    class Meta:
        model = AnimalEncounter
        fields = [
            'source',
            'source_id',
            'where',
            'wkt'
            'longitude',
            'latitude',
            'location_accuracy_m',
            'when',
            'area',
            'area__name',
            'site',
            'site__name',
            'observer',
            'observer__name',
            'reporter',
            'reporter__name',
            'encounter_type',
            'name',
            "taxon",
            "species",
            "health",
            "sex",
            "maturity",
            "behaviour",
            "habitat",
            "activity",
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
            "cause_of_death_confidence",
            "absolute_admin_url",
        ]


class TurtleNestEncounterResource(ModelResource):
    class Meta:
        model = TurtleNestEncounter
        fields = [
            'source',
            'source_id',
            'where',
            'wkt'
            'longitude',
            'latitude',
            'location_accuracy_m',
            'when',
            'area',
            'area__name',
            'site',
            'site__name',
            'observer',
            'observer__name',
            'reporter',
            'reporter__name',
            'encounter_type',
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


class LoggerEncounterResource(ModelResource):
    class Meta:
        model = LoggerEncounter
        fields = [
            'source',
            'source_id',
            'where',
            'wkt'
            'longitude',
            'latitude',
            'location_accuracy_m',
            'when',
            'area',
            'area__name',
            'site',
            'site__name',
            'observer',
            'observer__name',
            'reporter',
            'reporter__name',
            'encounter_type',
            'logger_type',
            'deployment_status',
            'logger_id',
        ]


class LineTransectEncounterResource(ModelResource):
    class Meta:
        model = LineTransectEncounter
        fields = [
            'source',
            'source_id',
            'where',
            'wkt'
            'longitude',
            'latitude',
            'location_accuracy_m',
            'when',
            'area',
            'area__name',
            'site',
            'site__name',
            'observer',
            'observer__name',
            'reporter',
            'reporter__name',
            'encounter_type',
            'transect',
        ]
