from rest_framework.serializers import ModelSerializer, ReadOnlyField, FileField, ValidationError
from rest_framework_gis.fields import GeometryField
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from wastd.users.api import FastUserSerializer
from wastd.observations.models import (
    Observation,
    Survey,
    AnimalEncounter,
    Area,
    DispatchRecord,
    DugongMorphometricObservation,
    Encounter,
    HatchlingMorphometricObservation,
    LoggerEncounter,
    ManagementAction,
    MediaAttachment,
    NestTagObservation,
    TagObservation,
    TemperatureLoggerDeployment,
    TemperatureLoggerSettings,
    TrackTallyObservation,
    TurtleDamageObservation,
    TurtleMorphometricObservation,
    TurtleNestDisturbanceObservation,
    TurtleNestDisturbanceTallyObservation,
    TurtleNestEncounter,
    TurtleNestObservation,
    TurtleHatchlingEmergenceObservation,
    TurtleHatchlingEmergenceOutlierObservation,
    LightSourceObservation
)


class AreaSerializer(GeoFeatureModelSerializer):

    class Meta:
        model = Area
        geo_field = "geom"
        fields = (
            "pk",
            "area_type",
            "name",
            "geom",
            "northern_extent",
            "centroid",
            "length_surveyed_m",
            "length_survey_roundtrip_m"
        )


class FastAreaSerializer(ModelSerializer):
    """Minimal Area serializer.
    """
    class Meta:
        model = Area
        geo_field = "geom"
        fields = ("pk", "area_type", "name")


class SurveySerializer(GeoFeatureModelSerializer):
    reporter = FastUserSerializer(many=False)
    site = FastAreaSerializer(many=False)
    status = ReadOnlyField()

    class Meta:
        model = Survey
        geo_field = "start_location"
        fields = "__all__"


class FastSurveySerializer(ModelSerializer):
    reporter = FastUserSerializer(many=False, read_only=True)
    site = FastAreaSerializer(many=False, read_only=True)

    class Meta:
        model = Survey
        fields = [
            "id",
            "site",
            "start_time",
            "end_time",
            "start_comments",
            "end_comments",
            "reporter",
            "absolute_admin_url",
            "production"
        ]


class EncounterSerializer(GeoFeatureModelSerializer):
    """Encounter serializer.
    """

    class Meta:
        """The non-standard name `where` is declared as the geo field for the
        GeoJSON serializer's benefit.
        """
        model = Encounter
        fields = (
            "pk", "area", "site", "survey", "where", "location_accuracy", "when",
            "name", "observer", "reporter", "comments", "status", "source", "source_id",
            "encounter_type", "leaflet_title", "latitude", "longitude", "crs", "absolute_admin_url",
            "photographs", "tx_logs"
        )
        geo_field = "where"


class FastEncounterSerializer(EncounterSerializer):
    """Faster encounter serializer.
    """

    class Meta(EncounterSerializer.Meta):
        fields = (
            "pk", "area", "site", "survey", "location_accuracy", "when",
            "name", "observer", "reporter", "comments", "status", "source", "source_id",
            "encounter_type", "leaflet_title", "latitude", "longitude", "crs"
        )


class ObservationSerializer(ModelSerializer):
    """A serializer class for an Observation model associated with an Encounter.
    Should also be resuable for serializing other model classes that inherit from
    Observation.
    """
    encounter = FastEncounterSerializer(read_only=True)

    class Meta:
        model = Observation
        fields = ['pk', 'encounter']

    def validate(self, data):
        """Raise ValidateError on missing Encounter (encounter PK or source & source_id value).
        """
        if 'encounter' not in self.initial_data and (
            'source' not in self.initial_data and 'source_id' not in self.initial_data
        ):
            raise ValidationError('Encounter reference is required')
        if 'encounter' in self.initial_data:
            if not Encounter.objects.filter(pk=self.initial_data['encounter']).exists():
                raise ValidationError(
                    'Encounter {} does not exist.'.format(self.initial_data['encounter'])
                )
        if 'source' in self.initial_data and 'source_id' in self.initial_data:
            if not Encounter.objects.filter(source=self.initial_data['source'], source_id=self.initial_data['source_id']).exists():
                raise ValidationError(
                    'Encounter with source {} and source_id {} does not exist.'.format(
                        self.initial_data['source'],
                        self.initial_data['source_id'])
                )
        return data

    def create(self, validated_data):
        """Create one new object, resolve Encounter from either PK or source & source_id.
        """
        if 'encounter' in self.initial_data:
            validated_data['encounter'] = Encounter.objects.get(pk=self.initial_data['encounter'])
        else:
            validated_data['encounter'] = Encounter.objects.get(
                source=self.initial_data['source'], source_id=self.initial_data['source_id'])
        return self.Meta.model.objects.create(**validated_data)


class MediaAttachmentSerializer(ObservationSerializer):

    class Meta:
        model = MediaAttachment
        fields = ('pk', 'media_type', 'title', 'attachment')


class TagObservationEncounterSerializer(ObservationSerializer):

    class Meta:
        model = TagObservation
        fields = ('pk', 'encounter', 'tag_type', 'name', 'tag_location', 'status', 'comments')


class NestTagObservationEncounterSerializer(ObservationSerializer):

    class Meta:
        model = NestTagObservation
        fields = (
            'pk', 'encounter', 'status', 'flipper_tag_id', 'date_nest_laid', 'tag_label', 'comments')


class ManagementActionSerializer(ObservationSerializer):

    class Meta:
        model = ManagementAction
        fields = ('pk', 'encounter', 'management_actions', 'comments')


class TurtleMorphometricObservationEncounterSerializer(ObservationSerializer):

    class Meta:
        model = TurtleMorphometricObservation
        fields = (
            "encounter", "latitude", "longitude",
            "curved_carapace_length_mm", "curved_carapace_length_accuracy",
            "straight_carapace_length_mm", "straight_carapace_length_accuracy",
            "curved_carapace_width_mm", "curved_carapace_width_accuracy",
            "tail_length_carapace_mm", "tail_length_carapace_accuracy",
            "tail_length_vent_mm", "tail_length_vent_accuracy",
            "tail_length_plastron_mm", "tail_length_plastron_accuracy",
            "maximum_head_width_mm", "maximum_head_width_accuracy",
            "maximum_head_length_mm", "maximum_head_length_accuracy",
            "body_depth_mm", "body_depth_accuracy",
            "body_weight_g", "body_weight_accuracy",
            "handler", "recorder",
        )


class HatchlingMorphometricObservationEncounterSerializer(ObservationSerializer):

    class Meta:
        model = HatchlingMorphometricObservation
        fields = (
            'encounter',
            'latitude',
            'longitude',
            'straight_carapace_length_mm',
            'straight_carapace_width_mm',
            'body_weight_g',
        )


class TurtleNestDisturbanceObservationEncounterSerializer(ObservationSerializer):

    class Meta:
        model = TurtleNestDisturbanceObservation
        fields = (
            'pk', 'encounter', 'disturbance_cause', 'disturbance_cause_confidence',
            'disturbance_severity', 'comments',
        )


class TurtleNestObservationEncounterSerializer(ObservationSerializer):

    class Meta:
        model = TurtleNestObservation
        fields = (
            'pk', 'encounter', 'observation_name', 'latitude', 'longitude',
            'nest_position', 'eggs_laid', 'egg_count',
            'hatching_success', 'emergence_success',
            'no_egg_shells', 'no_live_hatchlings_neck_of_nest', 'no_live_hatchlings',
            'no_dead_hatchlings', 'no_undeveloped_eggs',
            'no_unhatched_eggs', 'no_unhatched_term', 'no_depredated_eggs',
            'nest_depth_top', 'nest_depth_bottom',
            'sand_temp', 'air_temp', 'water_temp', 'egg_temp', 'comments',
        )


class TurtleHatchlingEmergenceObservationEncounterSerializer(ObservationSerializer):

    class Meta:
        model = TurtleHatchlingEmergenceObservation
        fields = (
            'encounter',
            'observation_name',
            'latitude',
            'longitude',
            'bearing_to_water_degrees',
            'bearing_leftmost_track_degrees',
            'bearing_rightmost_track_degrees',
            'no_tracks_main_group',
            'no_tracks_main_group_min',
            'no_tracks_main_group_max',
            'outlier_tracks_present',
            'path_to_sea_comments',
            'hatchling_emergence_time_known',
            'light_sources_present',
            'hatchling_emergence_time',
            'hatchling_emergence_time_accuracy',
            'cloud_cover_at_emergence',
        )


class TurtleHatchlingEmergenceOutlierObservationEncounterSerializer(ObservationSerializer):

    class Meta:
        model = TurtleHatchlingEmergenceOutlierObservation
        fields = (
            "encounter",
            "observation_name",
            "latitude",
            "longitude",
            "bearing_outlier_track_degrees",
            "outlier_group_size",
            "outlier_track_comment",
        )


class LightSourceObservationEncounterSerializer(ObservationSerializer):

    class Meta:
        model = LightSourceObservation
        fields = (
            "encounter",
            "observation_name",
            "latitude",
            "longitude",
            "bearing_light_degrees",
            "light_source_type",
            "light_source_description",
        )


class TurtleDamageObservationSerializer(ModelSerializer):
    # as_latex = ReadOnlyField()

    class Meta:
        model = TurtleDamageObservation
        fields = ("observation_name", "body_part", "damage_type", "damage_age", "description")


class TrackTallyObservationSerializer(ModelSerializer):
    # as_latex = ReadOnlyField()

    class Meta:
        model = TrackTallyObservation
        fields = ("observation_name", "species", "nest_type")


class TurtleNestDisturbanceTallyObservationSerializer(ModelSerializer):
    # as_latex = ReadOnlyField()

    class Meta:
        model = TurtleNestDisturbanceTallyObservation
        fields = ("observation_name", "species", "disturbance_cause")


class TemperatureLoggerSettingsSerializer(ModelSerializer):
    # as_latex = ReadOnlyField()

    class Meta:
        model = TemperatureLoggerSettings
        fields = ("observation_name", "logging_interval", "recording_start", "tested")


class DispatchRecordSerializer(ModelSerializer):
    # as_latex = ReadOnlyField()

    class Meta:
        model = DispatchRecord
        fields = ("observation_name", "sent_to")


class TemperatureLoggerDeploymentSerializer(ModelSerializer):
    # as_latex = ReadOnlyField()

    class Meta:
        model = TemperatureLoggerDeployment
        fields = (
            "observation_name",
            "depth_mm",
            "marker1_present",
            "distance_to_marker1_mm",
            "marker2_present",
            "distance_to_marker2_mm",
            "habitat",
            "distance_to_vegetation_mm",
        )


class DugongMorphometricObservationSerializer(ModelSerializer):
    # as_latex = ReadOnlyField()

    class Meta:
        model = DugongMorphometricObservation
        fields = ("observation_name",
                  "body_length_mm",
                  "body_girth_mm",
                  "tail_fluke_width_mm",
                  "tusks_found",
                  )


class SourceIdEncounterSerializer(GeoFeatureModelSerializer):
    """Encounter serializer with pk, source, source_id, where, when, status.

    Use this serializer to retrieve a filtered set of Encounter ``source_id``
    values to split data imports into create / update / skip.

    @see https://github.com/dbca-wa/wastd/issues/253
    """

    class Meta:
        """The non-standard name `where` is declared as the geo field for the
        GeoJSON serializer's benefit.
        """
        model = Encounter
        name = "encounter"
        fields = ("pk", "where", "when", "status", "source", "source_id", )
        geo_field = "where"
        id_field = "source_id"


class AnimalEncounterSerializer(EncounterSerializer):
    photographs = MediaAttachmentSerializer(many=True, read_only=False)
    tx_logs = ReadOnlyField()

    class Meta:
        model = AnimalEncounter
        fields = ("pk", "area", "site", "survey", "source", "source_id",
                  "encounter_type", "leaflet_title",
                  "status", "observer", "reporter", "comments",
                  "where", "latitude", "longitude", "crs", "location_accuracy",
                  "when", "name",
                  "name", "taxon", "species", "health", "sex", "maturity", "behaviour",
                  "habitat", "activity", "nesting_event",
                  "checked_for_injuries",
                  "scanned_for_pit_tags",
                  "checked_for_flipper_tags",
                  "cause_of_death", "cause_of_death_confidence",
                  "absolute_admin_url", "photographs", "tx_logs",
                  "observation_set", )
        geo_field = "where"
        id_field = "source_id"


class TurtleNestEncounterSerializer(EncounterSerializer):

    class Meta:
        model = TurtleNestEncounter
        fields = ("pk", "area", "site", "survey", "source", "source_id",
                  "encounter_type", "leaflet_title",
                  "status", "observer", "reporter", "comments",
                  "where", "latitude", "longitude", "crs", "location_accuracy",
                  "when", "name",
                  "nest_age", "nest_type", "species", "habitat", "disturbance",
                  "comments",
                  "absolute_admin_url",
                  # "observation_set",
                  )
        geo_field = "where"


class LoggerEncounterSerializer(EncounterSerializer):

    class Meta:
        model = LoggerEncounter
        fields = ("pk", "area", "site", "survey", "source", "source_id",
                  "encounter_type", "leaflet_title",
                  "status", "observer", "reporter", "comments",
                  "where", "latitude", "longitude", "crs", "location_accuracy",
                  "when", "name",
                  "deployment_status", "comments",
                  "comments",
                  "absolute_admin_url",
                  "observation_set", )
        geo_field = "where"


class TagObservationSerializer(ModelSerializer):
    # as_latex = ReadOnlyField()

    class Meta:
        model = TagObservation
        fields = ("observation_name",  # "as_latex",
                  "tag_type", "name", "tag_location",
                  "status", "comments", )


class TurtleMorphometricObservationSerializer(ModelSerializer):
    # as_latex = ReadOnlyField()

    class Meta:
        model = TurtleMorphometricObservation
        fields = ("observation_name",  # "as_latex",
                  "curved_carapace_length_mm", "curved_carapace_length_accuracy",
                  "straight_carapace_length_mm", "straight_carapace_length_accuracy",
                  "curved_carapace_width_mm", "curved_carapace_width_accuracy",
                  "tail_length_carapace_mm", "tail_length_carapace_accuracy",
                  "tail_length_vent_mm", "tail_length_vent_accuracy",
                  "tail_length_plastron_mm", "tail_length_plastron_accuracy",
                  "maximum_head_width_mm", "maximum_head_width_accuracy",
                  "maximum_head_length_mm", "maximum_head_length_accuracy",
                  "body_depth_mm", "body_depth_accuracy",
                  "body_weight_g", "body_weight_accuracy",
                  "handler", "recorder", )


class TurtleNestObservationSerializer(ModelSerializer):
    # as_latex = ReadOnlyField()

    class Meta:
        model = TurtleNestObservation
        fields = ("observation_name",  # "as_latex",
                  "nest_position", "eggs_laid", "egg_count",
                  "egg_count_calculated",
                  "no_emerged", "no_egg_shells",
                  "no_live_hatchlings_neck_of_nest",
                  "no_live_hatchlings", "no_dead_hatchlings",
                  "no_undeveloped_eggs", "no_unhatched_eggs",
                  "no_unhatched_term", "no_depredated_eggs",
                  "nest_depth_top", "nest_depth_bottom",
                  "sand_temp", "air_temp", "water_temp", "egg_temp",
                  "hatching_success", "emergence_success",
                  "comments")


class NestTagObservationSerializer(ModelSerializer):
    # as_latex = ReadOnlyField()

    class Meta:
        model = NestTagObservation
        fields = ("observation_name",  # "as_latex", #
                  "status",
                  "flipper_tag_id",
                  "date_nest_laid",
                  "tag_label",
                  "comments",
                  )


class TurtleNestDisturbanceObservationSerializer(ModelSerializer):
    # as_latex = ReadOnlyField()

    class Meta:
        model = TurtleNestDisturbanceObservation
        fields = (
            "observation_name",
            # "as_latex",
            "disturbance_cause",
            "disturbance_cause_confidence",
            "disturbance_severity",
            "comments",
        )


class HatchlingMorphometricObservationSerializer(ModelSerializer):
    # as_latex = ReadOnlyField()

    class Meta:
        model = HatchlingMorphometricObservation
        fields = ("observation_name",  # "as_latex", #
                  "straight_carapace_length_mm",
                  "straight_carapace_width_mm",
                  "body_weight_g",
                  )


class TurtleHatchlingEmergenceObservationSerializer(ModelSerializer):
    """TurtleHatchlingEmergenceObservation serializer excluding encounter for inlines."""

    class Meta:
        model = TurtleHatchlingEmergenceObservation
        fields = (
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
            "cloud_cover_at_emergence",
        )


class TurtleHatchlingEmergenceOutlierObservationSerializer(ModelSerializer):
    """TurtleHatchlingEmergenceOutlierObservation serializer excluding encounter for inlines."""

    class Meta:
        model = TurtleHatchlingEmergenceOutlierObservation

        fields = (
            "bearing_outlier_track_degrees",
            "outlier_group_size",
            "outlier_track_comment",
        )


class LightSourceObservationSerializer(ModelSerializer):
    """LightSource serializer excluding encounter for inlines.
    """

    class Meta:
        model = LightSourceObservation
        fields = (
            "bearing_light_degrees",
            "light_source_type",
            "light_source_description",
        )
