from import_export.resources import ModelResource
from wastd.observations.models import AnimalEncounter, TurtleNestEncounter


class AnimalEncounterResource(ModelResource):
    class Meta:
        model = AnimalEncounter
        fields = [
            'when',
            'area',
            'site',
            'where',
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
            'when',
            'area',
            'site',
            'where',
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

