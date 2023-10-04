from import_export.fields import Field
from import_export.resources import ModelResource

from datetime import datetime, timedelta
from dateutil import tz

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
        return obj.make_label()


class EncounterResource(ModelResource):

    locality = Field(column_name='locality')
    site = Field(column_name='site')
    observer = Field(column_name='observer')
    reporter = Field(column_name='reporter')
    survey_id = Field()
    #split out lat long
    latitude = Field(column_name='latitude')
    longitude = Field(column_name='longitude')
    
    #split the date
    day = Field(column_name='day')
    month = Field(column_name='month')
    year = Field(column_name='year')
    time = Field(column_name='time')
    #Turtle time
    turtle_time_day = Field(column_name='turtle_time_day')
    



    class Meta:
        model = Encounter
        fields = [
            "id",
            "source",
            "source_id",
            "status",
            "when",
            "day",
            "turtle_time_day",
            "month",
            "year",
            "time",
            "where",
            "latitude",
            "longitude",
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
        return obj.survey.make_label() if obj.survey else ''

    def dehydrate_observer(self, obj):
        return obj.observer.name

    def dehydrate_reporter(self, obj):
        return obj.reporter.name

    def dehydrate_encounter_type(self, obj):
        return obj.get_encounter_type_display()
    
    #split lat long
    def dehydrate_latitude(self, obj):
         return obj.latitude

    def dehydrate_longitude(self, obj):
        return obj.longitude
    
    #excel can't deal with timezone objects so convert to a string. 
    #Note this is the server local time NOT the local time the encouter happened - this is potetially bad. Really should be storing the timezone of collection
    def dehydrate_when(self, obj):
        return obj.when.astimezone(tz.tzlocal()).strftime("%d-%b-%Y %H:%M:%S")

    
    #split the date
    def dehydrate_day(self, obj):
        if obj.when:
            return obj.when.astimezone(tz.tzlocal()).day
        return ''

    def dehydrate_month(self, obj):
        if obj.when:
            return obj.when.astimezone(tz.tzlocal()).month
        return ''

    def dehydrate_year(self, obj):
        if obj.when:
            return obj.when.astimezone(tz.tzlocal()).year
        return ''
    
    #Note this is the server local time NOT the local time the encouter happened - this is potetially bad. Really should be storing the timezone of collection
    def dehydrate_time(self, obj):
        if obj.when:
            return obj.when.astimezone(tz.tzlocal()).strftime("%H:%M:%S")
        return ''
    
    #from 12pm to 12pm then next day, the date stays the same i.e 11:59am on 3/12/23 is 2/12/23
    ##Note this is the server local time NOT the local time the encouter happened - this is potetially bad. Really should be storing the timezone of collection
    def dehydrate_turtle_time_day(self, obj):
        if obj.when:
            if obj.when.astimezone(tz.tzlocal()).hour < 12:
                adjusted_date =  obj.when.astimezone(tz.tzlocal()) - timedelta(days=1)
                return adjusted_date.strftime("%d-%b-%Y")
            return obj.when.strftime("%d-%b-%Y")
        return ''
        




class AnimalEncounterResource(EncounterResource):

    class Meta:
        model = AnimalEncounter
        fields =  EncounterResource.Meta.fields + [
            "id",
            "source",
            "source_id",
            "location_accuracy_m",
            "area",
            "observer",
            "reporter",
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
            "cause_of_death_confidence"
            #"absolute_admin_url"
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

    # Construct fields that belong to child NestTagObservation objects
    nest_tag_status = Field()
    flipper_tag_id = Field()
    date_nest_laid = Field()
    tag_label = Field()

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
            "nest_tag_status",
            "flipper_tag_id",
            "date_nest_laid",
            "tag_label",
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
            return encounter.disturbance in ['present', 'yes']

    def dehydrate_nest_tagged(self, encounter):
        if encounter.nest_tagged == NA_VALUE:
            return ''
        else:
            return encounter.nest_tagged in ['present', 'yes']

    def dehydrate_logger_found(self, encounter):
        if encounter.logger_found == NA_VALUE:
            return ''
        else:
            return encounter.logger_found in ['present', 'yes']

    def dehydrate_eggs_counted(self, encounter):
        if encounter.eggs_counted == NA_VALUE:
            return ''
        else:
            return encounter.eggs_counted in ['present', 'yes']

    def dehydrate_hatchlings_measured(self, encounter):
        if encounter.hatchlings_measured == NA_VALUE:
            return ''
        else:
            return encounter.hatchlings_measured in ['present', 'yes']

    def dehydrate_fan_angles_measured(self, encounter):
        if encounter.fan_angles_measured == NA_VALUE:
            return ''
        else:
            return encounter.fan_angles_measured in ['present', 'yes']

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
        return self.get_child_observation_output(obs, 'no_dead_hatchlings')

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

    def dehydrate_nest_depth_top(self, encounter):
        obs = encounter.get_nest_observation()
        return self.get_child_observation_output(obs, 'nest_depth_top')

    def dehydrate_nest_depth_bottom(self, encounter):
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
    #assumed recored in AWST then stored in UTC
    def dehydrate_hatchling_emergence_time(self, encounter):
        obs = encounter.get_hatchling_emergence_observation()
        if obs:
            atime =  self.get_child_observation_output(obs, 'hatchling_emergence_time')
            if atime:
                return atime.astimezone(tz.tzlocal()).strftime("%d-%b-%Y %H:%M:%S")
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

    def dehydrate_nest_tag_status(self, encounter):
        obs = encounter.get_nesttag_observation()
        if obs:
            return obs.get_status_display()
        else:
            return ''

    def dehydrate_flipper_tag_id(self, encounter):
        obs = encounter.get_nesttag_observation()
        if obs:
            return obs.flipper_tag_id
        else:
            return ''
    
    
    def dehydrate_date_nest_laid(self, encounter):
        obs = encounter.get_nesttag_observation()
        if obs and obs.date_nest_laid:
            return obs.date_nest_laid.strftime("%Y-%m-%d") #no timezone stored in object - this may be displaying UTC?
        else:
            return ''

    def dehydrate_tag_label(self, encounter):
        obs = encounter.get_nesttag_observation()
        if obs:
            return obs.tag_label or ''
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
