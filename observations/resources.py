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

    is_production = Field()
    geometry = Field()

    class Meta:
        model = Survey
        fields = [
            "id",
            "area__name",
            "site__name",
            "reporter__name",
            "start_location",
            "start_time",
            "start_comments",
            "end_location",
            "end_time",
            "is_production",
            "geometry",
            "label",
            "source",
            "source_id",
        ]

    def get_export_order(self):
        return self._meta.fields

    def dehydrate_is_production(self, obj):
        return obj.production

    def dehydrate_source(self, obj):
        return obj.get_source_display()

    def dehydrate_geometry(self, obj):
        if obj.site:
            return obj.site.geom.ewkt
        else:
            return ''

    def dehydrate_label(self, obj):
        return obj.make_label


class EncounterResource(ModelResource):

    locality = Field(column_name='locality')
    site = Field(column_name='site')
    observer = Field(column_name='observer')
    reporter = Field(column_name='reporter')
    survey_id = Field()

    class Meta:
        model = Encounter
        fields = [
            "id",
            "status",
            "when",
            "where",
            "locality",
            "site",
            "survey_id",
            "survey",
            "observer",
            "reporter",
            "encounter_type",
        ]

    def get_export_order(self):
        return self._meta.fields

    def dehydrate_status(self, obj):
        return obj.get_status_display()

    def dehydrate_locality(self, obj):
        return obj.area.name if obj.area else ''

    def dehydrate_site(self, obj):
        return obj.site.name if obj.site else ''

    def dehydrate_survey_id(self, obj):
        return obj.survey_id if obj.survey else ''

    def dehydrate_survey(self, obj):
        return obj.survey.make_label if obj.survey else ''

    def dehydrate_observer(self, obj):
        return obj.observer.name

    def dehydrate_reporter(self, obj):
        return obj.reporter.name

    def dehydrate_encounter_type(self, obj):
        return obj.get_encounter_type_display()


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

    # Construct fields that belong to child TurtleNestObservation objects.
    eggs_laid = Field(column_name='Eggs laid?')
    egg_count = Field(column_name='Eggs count')
    no_egg_shells = Field(column_name='Egg shells count')
    no_live_hatchlings = Field(column_name='Live hatchlings count')
    no_dead_hatchlings = Field(column_name='Dead hatchlings count')
    no_undeveloped_eggs = Field(column_name='Undeveloped eggs count')
    no_unhatched_eggs = Field(column_name='Unhatched eggs (undeveloped) count')
    no_unhatched_term = Field(column_name='Unhatched eggs (full term) count')
    no_depredated_eggs = Field(column_name='Depredated eggs count')
    hatching_success = Field(column_name='Hatching success %')
    emergence_success = Field(column_name='Emergence success %')
    nest_depth_top = Field()
    nest_depth_bottom = Field()
    sand_temp = Field()
    air_temp = Field()
    water_temp = Field()
    egg_temp = Field()
    nest_tag = Field()
    logger = Field()

    # Construct fields that belong to child TurtleHatchlingEmergenceObservation objects.
    bearing_to_water_degrees = Field()
    bearing_leftmost_track_degrees = Field()
    bearing_rightmost_track_degrees = Field()
    no_tracks_main_group = Field()
    no_tracks_main_group_min = Field()
    no_tracks_main_group_max = Field()
    outlier_tracks_present = Field()
    path_to_sea_comments = Field()
    hatchling_emergence_time_known = Field()
    light_sources_present = Field()
    hatchling_emergence_time = Field()
    hatchling_emergence_time_accuracy = Field()
    cloud_cover_at_emergence_known = Field()
    cloud_cover_at_emergence = Field()

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
            "eggs_laid",
            "egg_count",
            "no_egg_shells",
            "no_live_hatchlings",
            "no_dead_hatchlings",
            "no_undeveloped_eggs",
            "no_unhatched_eggs",
            "no_unhatched_term",
            "no_depredated_eggs",
            "hatching_success",
            "emergence_success",
            "nest_depth_top",
            "nest_depth_bottom",
            "sand_temp",
            "air_temp",
            "water_temp",
            "egg_temp",
            "nest_tag",
            "logger",
            "bearing_to_water_degrees",
            "bearing_leftmost_track_degrees",
            "bearing_rightmost_track_degrees",
            "no_tracks_main_group",
            "no_tracks_main_group_min",
            "no_tracks_main_group_max",
            "outlier_tracks_present",
            "path_to_sea_comments",
            "hatchling_emergence_time_known",
            "light_sources_present",
            "hatchling_emergence_time",
            "hatchling_emergence_time_accuracy",
            "cloud_cover_at_emergence_known",
            "cloud_cover_at_emergence",
        ]

    def get_export_order(self):
        return self._meta.fields

    def get_child_observation_output(self, obs, attr):
        if obs is None:
            return ''
        if hasattr(obs, f"get_{attr}_display"):
            return getattr(obs, f"get_{attr}_display")()
        return getattr(obs, attr) or ''

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
            return encounter.disturbance == 'present'

    def dehydrate_nest_tagged(self, encounter):
        if encounter.nest_tagged == NA_VALUE:
            return ''
        else:
            return encounter.nest_tagged == 'present'

    def dehydrate_logger_found(self, encounter):
        if encounter.logger_found == NA_VALUE:
            return ''
        else:
            return encounter.logger_found == 'present'

    def dehydrate_eggs_counted(self, encounter):
        if encounter.eggs_counted == NA_VALUE:
            return ''
        else:
            return encounter.eggs_counted == 'present'

    def dehydrate_hatchlings_measured(self, encounter):
        if encounter.hatchlings_measured == NA_VALUE:
            return ''
        else:
            return encounter.hatchlings_measured == 'present'

    def dehydrate_fan_angles_measured(self, encounter):
        if encounter.fan_angles_measured == NA_VALUE:
            return ''
        else:
            return encounter.fan_angles_measured == 'present'

    def dehydrate_eggs_laid(self, encounter):
        obs = encounter.get_nest_observation()
        return self.get_child_observation_output(obs, 'eggs_laid')

    def dehydrate_egg_count(self, encounter):
        obs = encounter.get_nest_observation()
        return self.get_child_observation_output(obs, 'egg_count')

    def dehydrate_no_egg_shells(self, encounter):
        obs = encounter.get_nest_observation()
        return self.get_child_observation_output(obs, 'no_egg_shells')

    def dehydrate_no_live_hatchlings(self, encounter):
        obs = encounter.get_nest_observation()
        return self.get_child_observation_output(obs, 'no_live_hatchlings')

    def dehydrate_no_dead_hatchlings(self, encounter):
        obs = encounter.get_nest_observation()
        return self.get_child_observation_output(obs, 'no_live_hatchlings')

    def dehydrate_no_undeveloped_eggs(self, encounter):
        obs = encounter.get_nest_observation()
        return self.get_child_observation_output(obs, 'no_undeveloped_eggs')

    def dehydrate_no_unhatched_eggs(self, encounter):
        obs = encounter.get_nest_observation()
        return self.get_child_observation_output(obs, 'no_unhatched_eggs')

    def dehydrate_no_unhatched_term(self, encounter):
        obs = encounter.get_nest_observation()
        return self.get_child_observation_output(obs, 'no_unhatched_term')

    def dehydrate_no_depredated_eggs(self, encounter):
        obs = encounter.get_nest_observation()
        return self.get_child_observation_output(obs, 'no_depredated_eggs')

    def dehydrate_hatching_success(self, encounter):
        obs = encounter.get_nest_observation()
        return self.get_child_observation_output(obs, 'hatching_success')

    def dehydrate_emergence_success(self, encounter):
        obs = encounter.get_nest_observation()
        return self.get_child_observation_output(obs, 'emergence_success')

    def dehydrate_no_nest_depth_top(self, encounter):
        obs = encounter.get_nest_observation()
        return self.get_child_observation_output(obs, 'nest_depth_top')

    def dehydrate_no_nest_depth_bottom(self, encounter):
        obs = encounter.get_nest_observation()
        return self.get_child_observation_output(obs, 'nest_depth_bottom')

    def dehydrate_sand_temp(self, encounter):
        obs = encounter.get_nest_observation()
        return self.get_child_observation_output(obs, 'sand_temp')

    def dehydrate_air_temp(self, encounter):
        obs = encounter.get_nest_observation()
        return self.get_child_observation_output(obs, 'air_temp')

    def dehydrate_water_temp(self, encounter):
        obs = encounter.get_nest_observation()
        return self.get_child_observation_output(obs, 'water_temp')

    def dehydrate_egg_temp(self, encounter):
        obs = encounter.get_nest_observation()
        return self.get_child_observation_output(obs, 'egg_temp')

    def dehydrate_nest_tag(self, encounter):
        obs = encounter.get_nesttag_observation()
        if obs:
            return obs.name
        else:
            return ''

    def dehydrate_logger(self, encounter):
        obs = encounter.get_logger_observation()
        if obs:
            return str(obs)
        else:
            return ''

    def dehydrate_bearing_to_water_degrees(self, encounter):
        obs = encounter.get_hatchling_emergence_observation()
        if obs:
            return self.get_child_observation_output(obs, 'bearing_to_water_degrees')
        else:
            return ''

    def dehydrate_bearing_leftmost_track_degrees(self, encounter):
        obs = encounter.get_hatchling_emergence_observation()
        if obs:
            return self.get_child_observation_output(obs, 'bearing_leftmost_track_degrees')
        else:
            return ''

    def dehydrate_bearing_rightmost_track_degrees(self, encounter):
        obs = encounter.get_hatchling_emergence_observation()
        if obs:
            return self.get_child_observation_output(obs, 'bearing_rightmost_track_degrees')
        else:
            return ''

    def dehydrate_no_tracks_main_group(self, encounter):
        obs = encounter.get_hatchling_emergence_observation()
        if obs:
            return self.get_child_observation_output(obs, 'no_tracks_main_group')
        else:
            return ''

    def dehydrate_no_tracks_main_group_min(self, encounter):
        obs = encounter.get_hatchling_emergence_observation()
        if obs:
            return self.get_child_observation_output(obs, 'no_tracks_main_group_min')
        else:
            return ''

    def dehydrate_no_tracks_main_group_max(self, encounter):
        obs = encounter.get_hatchling_emergence_observation()
        if obs:
            return self.get_child_observation_output(obs, 'no_tracks_main_group_max')
        else:
            return ''

    def dehydrate_outlier_tracks_present(self, encounter):
        obs = encounter.get_hatchling_emergence_observation()
        if obs:
            return self.get_child_observation_output(obs, 'outlier_tracks_present')
        else:
            return ''

    def dehydrate_path_to_sea_comments(self, encounter):
        obs = encounter.get_hatchling_emergence_observation()
        if obs:
            return self.get_child_observation_output(obs, 'path_to_sea_comments')
        else:
            return ''

    def dehydrate_hatchling_emergence_time_known(self, encounter):
        obs = encounter.get_hatchling_emergence_observation()
        if obs:
            return self.get_child_observation_output(obs, 'hatchling_emergence_time_known')
        else:
            return ''

    def dehydrate_light_sources_present(self, encounter):
        obs = encounter.get_hatchling_emergence_observation()
        if obs:
            return self.get_child_observation_output(obs, 'light_sources_present')
        else:
            return ''

    def dehydrate_hatchling_emergence_time(self, encounter):
        obs = encounter.get_hatchling_emergence_observation()
        if obs:
            return self.get_child_observation_output(obs, 'hatchling_emergence_time')
        else:
            return ''

    def dehydrate_hatchling_emergence_time_accuracy(self, encounter):
        obs = encounter.get_hatchling_emergence_observation()
        if obs:
            return self.get_child_observation_output(obs, 'hatchling_emergence_time_accuracy')
        else:
            return ''

    def dehydrate_cloud_cover_at_emergence_known(self, encounter):
        obs = encounter.get_hatchling_emergence_observation()
        if obs:
            return self.get_child_observation_output(obs, 'cloud_cover_at_emergence_known')
        else:
            return ''

    def dehydrate_cloud_cover_at_emergence(self, encounter):
        obs = encounter.get_hatchling_emergence_observation()
        if obs:
            return self.get_child_observation_output(obs, 'cloud_cover_at_emergence')
        else:
            return ''


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
