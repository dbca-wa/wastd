from import_export.fields import Field
from import_export.resources import ModelResource

from .lookups import NA_VALUE
from .models import (
    Encounter,
    AnimalEncounter,
    TurtleNestEncounter,
    LineTransectEncounter,
    Survey,
)


class SurveyResource(ModelResource):

    class Meta:
        model = Survey
        fields = [
            "source",
            "source_id",
            "device_id",
            "site",
            "transect",
            "reporter",
            "reporter__name",
            "start_location",
            "start_location_accuracy_m",
            "start_time",
            "start_photo",
            "start_comments",
            "end_source_id",
            "end_device_id",
            "end_location",
            "end_location_accuracy_m",
            "end_time",
            "end_photo",
            "end_comments",
            "production",
            "team",
            "label",
        ]


class EncounterResource(ModelResource):

    locality = Field(column_name='locality')
    site = Field(column_name='site')
    observer = Field(column_name='observer')
    reporter = Field(column_name='reporter')

    def dehydrate_status(self, encounter):
        return encounter.get_status_display()

    def dehydrate_locality(self, encounter):
        return encounter.area.name if encounter.area else ''

    def dehydrate_site(self, encounter):
        return encounter.site.name if encounter.site else ''

    def dehydrate_observer(self, encounter):
        return encounter.observer.name

    def dehydrate_reporter(self, encounter):
        return encounter.reporter.name

    def dehydrate_encounter_type(self, encounter):
        return encounter.get_encounter_type_display()

    class Meta:
        model = Encounter
        fields = [
            "id",
            "status",
            "when",
            "where",
            "locality",
            "site",
            "observer",
            "reporter",
            "encounter_type",
        ]
        export_order = [
            "id",
            "status",
            "when",
            "where",
            "locality",
            "site",
            "observer",
            "reporter",
            "encounter_type",
        ]


class AnimalEncounterResource(ModelResource):

    class Meta:
        model = AnimalEncounter
        fields = [
            "source",
            "source_id",
            "where",
            "wkt" "longitude",
            "latitude",
            "location_accuracy_m",
            "when",
            "area",
            "area__name",
            "site",
            "site__name",
            "observer",
            "observer__name",
            "reporter",
            "reporter__name",
            "encounter_type",
            "name",
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


class TurtleNestEncounterResource(EncounterResource):

    def dehydrate_nest_type(self, encounter):
        return encounter.get_nest_type_display()

    def dehydrate_nest_age(self, encounter):
        return encounter.get_nest_age_display()

    def dehydrate_species(self, encounter):
        return encounter.get_species_display()

    def dehydrate_disturbance(self, encounter):
        if encounter.disturbance == NA_VALUE:
            return ''
        else:
            return encounter.get_disturbance_display()

    def dehydrate_nest_tagged(self, encounter):
        if encounter.nest_tagged == NA_VALUE:
            return ''
        else:
            return encounter.get_nest_tagged_display()

    def dehydrate_logger_found(self, encounter):
        if encounter.logger_found == NA_VALUE:
            return ''
        else:
            return encounter.get_logger_found_display()

    def dehydrate_eggs_counted(self, encounter):
        if encounter.eggs_counted == NA_VALUE:
            return ''
        else:
            return encounter.get_eggs_counted_display()

    def dehydrate_hatchlings_measured(self, encounter):
        if encounter.hatchlings_measured == NA_VALUE:
            return ''
        else:
            return encounter.get_hatchlings_measured_display()

    def dehydrate_fan_angles_measured(self, encounter):
        if encounter.fan_angles_measured == NA_VALUE:
            return ''
        else:
            return encounter.get_fan_angles_measured_display()

    class Meta:
        model = TurtleNestEncounter
        fields = EncounterResource.Meta.fields + [
            "nest_type",
            "nest_age",
            "species",
            "disturbance",
            "nest_tagged",
            "logger_found",
            "eggs_counted",
            "hatchlings_measured",
            "fan_angles_measured",
        ]


class LineTransectEncounterResource(ModelResource):

    class Meta:
        model = LineTransectEncounter
        fields = [
            "source",
            "source_id",
            "where",
            "wkt" "longitude",
            "latitude",
            "location_accuracy_m",
            "when",
            "area",
            "area__name",
            "site",
            "site__name",
            "observer",
            "observer__name",
            "reporter",
            "reporter__name",
            "encounter_type",
            "transect",
        ]
