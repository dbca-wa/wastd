from rest_framework.serializers import ModelSerializer, ReadOnlyField, ValidationError, IntegerField, FileField
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from wastd.users.api import FastUserSerializer
from wastd.observations import models
import logging


logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------------#
# Areas, Surveys
# ----------------------------------------------------------------------------#
class AreaSerializer(GeoFeatureModelSerializer):

    class Meta:
        model = models.Area
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
        model = models.Area
        geo_field = "geom"
        fields = ("pk", "area_type", "name")


class SurveySerializer(GeoFeatureModelSerializer):
    reporter = FastUserSerializer(many=False)
    area = FastAreaSerializer(many=False)
    site = FastAreaSerializer(many=False)
    status = ReadOnlyField()
    start_photo = FileField(required=False)
    end_photo = FileField(required=False)

    class Meta:
        model = models.Survey
        geo_field = "start_location"
        fields = "__all__"


class FastSurveySerializer(ModelSerializer):
    reporter = FastUserSerializer(many=False, read_only=True)
    area = FastAreaSerializer(many=False, read_only=True)
    site = FastAreaSerializer(many=False, read_only=True)

    class Meta:
        model = models.Survey
        fields = [
            "id",
            "area",
            "site",
            "start_time",
            "end_time",
            "start_comments",
            "end_comments",
            "reporter",
            "absolute_admin_url",
            "production"
        ]


class SurveyMediaAttachmentSerializer(ModelSerializer):
    """A special Serializer for SurveyMediaAttachment to handle file uploads."""

    attachment = FileField(required=True)
    survey = FastSurveySerializer(read_only=True)

    class Meta:
        model = models.SurveyMediaAttachment
        fields = (
            "pk",
            "source",
            "source_id",
            "survey",
            'media_type',
            'title',
            'attachment'
        )

    def validate(self, data):
        """Raise ValidateError on missing Survey.

           Fields sent:
           "source", "source_id", "survey_source_id", "survey_end_source_id",
           "media_type", "title", "attachment"
        """

        has_source = 'survey_source' in self.initial_data and self.initial_data["survey_source"] != 'NA'
        has_source_id = 'survey_source_id' in self.initial_data and self.initial_data["survey_source_id"] != 'NA'
        has_end_source_id = 'survey_end_source_id' in self.initial_data and self.initial_data[
            "survey_end_source_id"] != 'NA'
        if (has_source and has_source_id and
                models.Survey.objects.filter(
                    source=self.initial_data['survey_source'],
                    source_id=self.initial_data['survey_source_id']
                ).exists()):
            data['survey'] = models.Survey.objects.get(
                    source=self.initial_data['survey_source'],
                    source_id=self.initial_data['survey_source_id']
                )

        elif (has_source and has_end_source_id and
                models.Survey.objects.filter(
                    source=self.initial_data['survey_source'],
                    end_source_id=self.initial_data['survey_end_source_id']
                ).exists()):
            data['survey'] = models.Survey.objects.get(
                    source=self.initial_data['survey_source'],
                    end_source_id=self.initial_data['survey_end_source_id']
                )

        else:
            msg = 'Survey does not exist: \nInitial data: {}'.format(self.initial_data)
            logger.info(msg)
            raise ValidationError(msg)

        return data

    def create(self, validated_data):
        """Create one new object, resolve Survey from survey_source and
           either survey_source_id or survey_end_source_id.
        """
        return self.Meta.model.objects.create(**validated_data)

    def save(self):
        """Override the save method in order to prevent 'duplicate' instances being created by
           the API endpoints. We override save in order to avoid duplicate by either create or update.
        """
        duplicates = self.Meta.model.objects.filter(
            source=self.initial_data["source"],
            source_id=self.initial_data["source_id"]
        )
        if duplicates.exists():
            if duplicates.count() == 1:
                return duplicates.first()
            else:
                # Passed-in data matches >1 existing instance, so raise a validation error.
                raise ValidationError("{}: existing duplicate(s) with {} ".format(
                    self.Meta.model._meta.label, str(**self.validated_data)
                ))
        else:
            # Create the new, unique instance.
            return self.Meta.model.objects.create(**self.validated_data)

# ----------------------------------------------------------------------------#
# Encounter
# ----------------------------------------------------------------------------#


class EncounterSerializer(GeoFeatureModelSerializer):
    """Encounter serializer.
    """
    area = FastAreaSerializer(required=False)
    site = FastAreaSerializer(required=False)
    survey = FastSurveySerializer(required=False)
    observer_id = IntegerField(write_only=True)
    observer = FastUserSerializer(read_only=True)
    reporter_id = IntegerField(write_only=True)
    reporter = FastUserSerializer(read_only=True)

    class Meta:
        """The non-standard name `where` is declared as the geo field for the
        GeoJSON serializer's benefit.
        """
        model = models.Encounter
        fields = (
            "pk",
            "area",
            "site",
            "survey",
            "where",
            "name",
            "observer_id",
            "observer",
            "reporter_id",
            "reporter",
            "comments",
            "status",
            "source",
            "source_id",
            "encounter_type",
            "when",
            "leaflet_title",
            "location_accuracy",
            "location_accuracy_m",
            "latitude",
            "longitude",
            "crs",
            "absolute_admin_url",
            # "photographs",
            # "tx_logs"
        )
        geo_field = "where"


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
        model = models.Encounter
        name = "encounter"
        fields = (
            "pk",
            "where",
            "location_accuracy_m",
            "when",
            "status",
            "source",
            "source_id",
            "observer",
            "reporter"
        )
        geo_field = "where"
        id_field = "pk"


class FastEncounterSerializer(EncounterSerializer):
    """Faster encounter serializer.
    """
    # area = FastAreaSerializer(required=False)
    # site = FastAreaSerializer(required=False)
    # survey = FastSurveySerializer(required=False)

    class Meta(EncounterSerializer.Meta):
        fields = (
            "pk",
            "source",
            "source_id",
            "encounter_type",
            "status",
            "when",
            "latitude",
            "longitude",
            "crs",
            "location_accuracy",
            "location_accuracy_m",
            "name",
            "leaflet_title",
            "observer",
            "reporter",
            "comments",
            "area",
            "site",
            "survey",
        )


class AnimalEncounterSerializer(EncounterSerializer):
    """AnimalEncounter Serializer.

    Omitted are performace bombs: photographs, observation_set, tx_logs.

    * photographs = MediaAttachments
    * Observations = specific observation seralizers
    """
    # photographs = MediaAttachmentSerializer(many=True, read_only=False)
    # tx_logs = ReadOnlyField()

    class Meta:
        model = models.AnimalEncounter
        fields = (
            "pk",
            "source",
            "source_id",
            "encounter_type",
            "status",
            "when",
            "latitude",
            "longitude",
            "crs",
            "location_accuracy",
            "location_accuracy_m",
            "name",
            "leaflet_title",
            "observer",
            "reporter",
            "comments",
            "area",
            "site",
            "survey",

            "taxon",
            "species",
            "health",
            "sex",
            "maturity",
            "behaviour",
            "habitat",
            "activity",
            "nesting_event",
            "laparoscopy",
            "checked_for_injuries",
            "scanned_for_pit_tags",
            "checked_for_flipper_tags",
            "cause_of_death",
            "cause_of_death_confidence",
            "absolute_admin_url",  # "photographs", "tx_logs",
            # "observation_set",
        )
        geo_field = "where"
        id_field = "source_id"


class TurtleNestEncounterSerializer(EncounterSerializer):
    # photographs = MediaAttachmentSerializer(many=True, read_only=False)
    # tx_logs = ReadOnlyField()

    class Meta:
        model = models.TurtleNestEncounter
        fields = (
            "pk",
            "source",
            "source_id",
            "encounter_type",
            "status",
            "when",
            "latitude",
            "longitude",
            "crs",
            "location_accuracy",
            "location_accuracy_m",
            "name",
            "leaflet_title",
            "observer",
            "reporter",
            "comments",
            "area",
            "site",
            "survey",

            "nest_age",
            "nest_type",
            "species",
            "habitat",
            "disturbance",
            'nest_tagged',
            'logger_found',
            'eggs_counted',
            'hatchlings_measured',
            'fan_angles_measured',
            "comments",
            "absolute_admin_url",
            # "photographs", "tx_logs",
            # "observation_set",
        )
        geo_field = "where"


class LoggerEncounterSerializer(EncounterSerializer):

    class Meta:
        model = models.LoggerEncounter
        fields = (
            "pk",
            "source",
            "source_id",
            "encounter_type",
            "status",
            "when",
            "latitude",
            "longitude",
            "crs",
            "location_accuracy",
            "location_accuracy_m",
            "name",
            "leaflet_title",
            "observer",
            "reporter",
            "comments",
            "area",
            "site",
            "survey",

            "logger_type",
            "logger_id",
            "deployment_status",
            "absolute_admin_url",
            # "observation_set",
        )
        geo_field = "where"


class LineTransectEncounterSerializer(EncounterSerializer):
    """Serializer for LineTransectEncounter, geofield: transect.."""

    class Meta:
        model = models.LineTransectEncounter
        fields = (
            "pk",
            "source",
            "source_id",
            "encounter_type",
            "status",
            "when",
            "latitude",
            "longitude",
            "crs",
            "location_accuracy",
            "location_accuracy_m",
            "name",
            "leaflet_title",
            "observer",
            "reporter",
            "comments",
            "area",
            "site",
            "survey",

            "transect",
            "absolute_admin_url",
        )
        geo_field = "where"


# ----------------------------------------------------------------------------#
# Observations
# ----------------------------------------------------------------------------#
class ObservationSerializer(ModelSerializer):
    """
    A serializer class for an Observation model associated with an Encounter.
    Should also be resuable for serializing other model classes that inherit from
    Observation.

    TODO Make writeable, avoid duplicates, avoid losing QA edits:
    https://github.com/dbca-wa/wastd/issues/297
    """
    encounter = EncounterSerializer(read_only=True)

    class Meta:
        model = models.Observation
        fields = ['pk', 'encounter', 'source', 'source_id']

    def validate(self, data):
        """Raise ValidateError on missing Encounter (encounter PK or source & source_id value).
        """
        if 'encounter_id' not in self.initial_data and (
            'encounter_source' not in self.initial_data and
            'encounter_source_id' not in self.initial_data
        ):
            raise ValidationError(
                'Encounter reference is required, either as encounter_id or as '
                'encounter_source and encounter_source_id.'
            )
        if 'encounter_id' in self.initial_data:
            if not models.Encounter.objects.filter(pk=self.initial_data['encounter_id']).exists():
                raise ValidationError(
                    'Encounter {} does not exist.'.format(self.initial_data['encounter_id'])
                )
        if 'encounter_source' in self.initial_data and 'encounter_source_id' in self.initial_data:
            if not models.Encounter.objects.filter(
                source=self.initial_data['encounter_source'],
                source_id=self.initial_data['encounter_source_id']
            ).exists():
                raise ValidationError(
                    'Encounter with source {} and source_id {} does not exist.'.format(
                        self.initial_data['encounter_source'],
                        self.initial_data['encounter_source_id'])
                )
        return data

    def create(self, validated_data):
        """Create one new object, resolve Encounter from either PK or source & source_id.
        """

        if 'encounter_id' in self.initial_data:
            validated_data['encounter'] = models.Encounter.objects.get(
                pk=self.initial_data['encounter_id'])
        else:
            validated_data['encounter'] = models.Encounter.objects.get(
                source=self.initial_data['encounter_source'],
                source_id=self.initial_data['encounter_source_id'])
        return self.Meta.model.objects.create(**validated_data)

    def save(self):
        """Override the save method in order to prevent 'duplicate' instances being created by
        the API endpoints. We override save in order to avoid duplicate by either create or update.
        """
        # logger.info(str(self.validated_data))
        # unique_data = {
        #     source: self.validated_data["source"],
        #     source_id: self.validated_data["source_id"]
        # }

        if 'encounter' in self.initial_data:
            self.validated_data['encounter'] = models.Encounter.objects.get(
                pk=self.initial_data['encounter']
            )
        else:
            self.validated_data['encounter'] = models.Encounter.objects.get(
                source=self.initial_data["encounter_source"],
                source_id=self.initial_data["encounter_source_id"]
            )
        # import ipdb; ipdb.set_trace()
        # Gate check: we want to ensure that duplicate objects are not created.
        duplicates = self.Meta.model.objects.filter(
            source=self.initial_data["source"],
            source_id=self.initial_data["source_id"]
        )
        if duplicates.exists():
            if duplicates.count() == 1:
                # TODO: work out how we might return HTTP status 200 instead of 201.
                # Update existing record: breaks file upload paths! bad!
                # logger.info(f"Updating existing record {str(self.validated_data)}")
                # duplicates.update(**self.validated_data)
                # duplicates.first().save()

                # return self.Meta.model.objects.get(
                #     source = self.initial_data["source"],
                #     source_id = self.initial_data["source_id"])
                # simpler:
                return duplicates.first()
            else:
                # Passed-in data matches >1 existing instance, so raise a validation error.
                raise ValidationError("{}: existing duplicate(s) with {} ".format(
                    self.Meta.model._meta.label, str(**self.validated_data)
                ))
        else:
            # Create the new, unique instance.
            return self.Meta.model.objects.create(**self.validated_data)


class MediaAttachmentSerializer(ObservationSerializer):
    """A special Serializer for MediaAttachment to handle file uploads."""

    attachment = FileField(required=True)

    class Meta:
        model = models.MediaAttachment
        fields = (
            "pk",
            "source",
            "source_id",
            "encounter",
            'media_type',
            'title',
            'attachment'
        )


class TagObservationSerializer(ObservationSerializer):

    handler_id = IntegerField(write_only=True)
    handler = FastUserSerializer(read_only=True)
    recorder_id = IntegerField(write_only=True)
    recorder = FastUserSerializer(read_only=True)

    class Meta:
        model = models.TagObservation
        fields = (
            "pk",
            "source",
            "source_id",
            "encounter",
            'handler',
            'handler_id',
            'recorder',
            'recorder_id',
            'tag_type',
            'name',
            'tag_location',
            'status',
            'comments'
        )


class NestTagObservationSerializer(ObservationSerializer):

    # encounter = TurtleNestEncounterSerializer(read_only=True)

    class Meta:
        model = models.NestTagObservation
        fields = (
            "pk",
            "source",
            "source_id",
            "encounter",
            "status",
            "flipper_tag_id",
            "date_nest_laid",
            "tag_label",
            "comments",
        )


class ManagementActionSerializer(ObservationSerializer):

    class Meta:
        model = models.ManagementAction
        fields = (
            "pk",
            "source",
            "source_id",
            "encounter",
            'management_actions',
            'comments'
        )


class TurtleMorphometricObservationSerializer(ObservationSerializer):

    handler_id = IntegerField(write_only=True)
    handler = FastUserSerializer(read_only=True)
    recorder_id = IntegerField(write_only=True)
    recorder = FastUserSerializer(read_only=True)

    class Meta:
        model = models.TurtleMorphometricObservation
        fields = (
            "pk",
            "source",
            "source_id",
            "encounter",
            "latitude",
            "longitude",
            "curved_carapace_length_mm",
            "curved_carapace_length_accuracy",
            "curved_carapace_length_min_mm",
            "curved_carapace_length_min_accuracy",
            "straight_carapace_length_mm",
            "straight_carapace_length_accuracy",
            "curved_carapace_width_mm",
            "curved_carapace_width_accuracy",
            "tail_length_carapace_mm",
            "tail_length_carapace_accuracy",
            "tail_length_vent_mm",
            "tail_length_vent_accuracy",
            "tail_length_plastron_mm",
            "tail_length_plastron_accuracy",
            "maximum_head_width_mm",
            "maximum_head_width_accuracy",
            "maximum_head_length_mm",
            "maximum_head_length_accuracy",
            "body_depth_mm",
            "body_depth_accuracy",
            "body_weight_g",
            "body_weight_accuracy",
            'handler',
            'handler_id',
            'recorder',
            'recorder_id',
        )


class HatchlingMorphometricObservationSerializer(ObservationSerializer):

    # encounter = TurtleNestEncounterSerializer(read_only=True)

    class Meta:
        model = models.HatchlingMorphometricObservation
        fields = (
            "pk",
            "source",
            "source_id",
            "encounter",
            'straight_carapace_length_mm',
            'straight_carapace_width_mm',
            'body_weight_g',
        )


class TurtleNestDisturbanceObservationSerializer(ObservationSerializer):

    class Meta:
        model = models.TurtleNestDisturbanceObservation
        fields = (
            "pk",
            "source",
            "source_id",
            "encounter",
            'disturbance_cause',
            'disturbance_cause_confidence',
            'disturbance_severity',
            'comments',
        )


class TurtleNestObservationSerializer(ObservationSerializer):

    # encounter = TurtleNestEncounterSerializer(read_only=True)

    class Meta:
        model = models.TurtleNestObservation
        fields = (
            "pk",
            "source",
            "source_id",
            "encounter",
            'nest_position',
            'eggs_laid',
            'egg_count',
            'hatching_success',
            'emergence_success',
            'no_egg_shells',
            'no_live_hatchlings_neck_of_nest',
            'no_live_hatchlings',
            'no_dead_hatchlings',
            'no_undeveloped_eggs',
            'no_unhatched_eggs',
            'no_unhatched_term',
            'no_depredated_eggs',
            'nest_depth_top',
            'nest_depth_bottom',
            'sand_temp',
            'air_temp',
            'water_temp',
            'egg_temp',
            'comments',
        )


class TurtleHatchlingEmergenceObservationSerializer(ObservationSerializer):

    # encounter = TurtleNestEncounterSerializer(read_only=True)

    class Meta:
        model = models.TurtleHatchlingEmergenceObservation
        fields = (
            "pk",
            "source",
            "source_id",
            "encounter",
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


class TurtleHatchlingEmergenceOutlierObservationSerializer(ObservationSerializer):

    class Meta:
        model = models.TurtleHatchlingEmergenceOutlierObservation
        fields = (
            "pk",
            "source",
            "source_id",
            "encounter",
            "bearing_outlier_track_degrees",
            "outlier_group_size",
            "outlier_track_comment",
        )


class LightSourceObservationSerializer(ObservationSerializer):

    class Meta:
        model = models.LightSourceObservation
        fields = (
            "pk",
            "source",
            "source_id",
            "encounter",
            "bearing_light_degrees",
            "light_source_type",
            "light_source_description",
        )


class TurtleDamageObservationSerializer(ObservationSerializer):

    class Meta:
        model = models.TurtleDamageObservation
        fields = (
            "pk",
            "source",
            "source_id",
            "encounter",
            "body_part",
            "damage_type",
            "damage_age",
            "description"
        )

class TrackTallyObservationSerializer(ObservationSerializer):

    class Meta:
        model = models.TrackTallyObservation
        fields = (
            "pk",
            "source",
            "source_id",
            "encounter",
            "species",
            "nest_age",
            "nest_type",
            "tally"
        )


class TurtleNestDisturbanceTallyObservationSerializer(ObservationSerializer):

    class Meta:
        model = models.TurtleNestDisturbanceTallyObservation
        fields = (
            "pk",
            "source",
            "source_id",
            "encounter",
            "species",
            "disturbance_cause",
            "no_nests_disturbed",
            "no_tracks_encountered",
            "comments"
        )


class TemperatureLoggerSettingsSerializer(ObservationSerializer):

    class Meta:
        model = models.TemperatureLoggerSettings
        fields = (
            "pk",
            "source",
            "source_id",
            "encounter",
            "logging_interval",
            "recording_start",
            "tested"
        )


class DispatchRecordSerializer(ObservationSerializer):

    class Meta:
        model = models.DispatchRecord
        fields = (
            "pk",
            "source",
            "source_id",
            "encounter",
            "sent_to"
        )


class TemperatureLoggerDeploymentSerializer(ObservationSerializer):

    class Meta:
        model = models.TemperatureLoggerDeployment
        fields = (
            "pk",
            "source",
            "source_id",
            "encounter",
            "depth_mm",
            "marker1_present",
            "distance_to_marker1_mm",
            "marker2_present",
            "distance_to_marker2_mm",
            "habitat",
            "distance_to_vegetation_mm",
        )


class LoggerObservationSerializer(ObservationSerializer):

    class Meta:
        model = models.LoggerObservation
        fields = (
            "pk",
            "source",
            "source_id",
            "encounter",
            "logger_type",
            "deployment_status",
            "logger_id",
            "comments"
        )


class DugongMorphometricObservationSerializer(ObservationSerializer):

    class Meta:
        model = models.DugongMorphometricObservation
        fields = (
            "pk",
            "source",
            "source_id",
            "encounter",
            "body_length_mm",
            "body_girth_mm",
            "tail_fluke_width_mm",
            "tusks_found",
        )
