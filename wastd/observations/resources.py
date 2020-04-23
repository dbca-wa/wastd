from import_export.resources import ModelResource
from wastd.observations.models import AnimalEncounter


class AnimalEncounterResource(ModelResource):
    class Meta:
        model = AnimalEncounter
        fields = [
            'when', 'area', 'site', 'where', 'name', 'taxon', 'species', 'sex', 'maturity',
            'health', 'checked_for_flipper_tags']
