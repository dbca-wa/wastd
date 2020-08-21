from import_export.resources import ModelResource
from wastd.observations.models import (
    Encounter,
    AnimalEncounter,
    TurtleNestEncounter,
    LoggerEncounter,
    LineTransectEncounter
)


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
            'name',
            'taxon',
            'species',
            'sex',
            'maturity',
            'health',
            'checked_for_flipper_tags'
        ]


class TurtleNestEncounterResource(ModelResource):
    class Meta:
        model = TurtleNestEncounter
        fields = [
            'source',
            'source_id',
            'where',
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
            'transect',
        ]
