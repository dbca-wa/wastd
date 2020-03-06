from rest_framework.serializers import ModelSerializer, ReadOnlyField, FileField
from rest_framework_gis.fields import GeometryField
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from wastd.api import FastUserSerializer
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


class ObservationSerializer(ModelSerializer):
    """The Observation serializer resolves its polymorphic subclasses.

    Observations have polymorphic subclasses (TagObservation, MediaAttachment
    etc.).
    A plain DRF serializer would simply return the shared Observation fields,
    but not the individual fields partial to its subclasses.

    Overriding the `to_representation` method, this serializer tests the
    object to display for its real instance, and calls the `to_representation`
    from the subclasses serializer.

    `Credits <http://stackoverflow.com/a/19976203/2813717>`_
    `Author <http://stackoverflow.com/users/1514427/michael-van-de-waeter>`_
    """
    # as_latex = ReadOnlyField()

    class Meta:
        model = Observation
        fields = ("observation_name",)

    def to_representation(self, obj):
        """Resolve the Observation instance to the child class"s serializer.
        """
        if isinstance(obj, TurtleMorphometricObservation):
            return TurtleMorphometricObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, TurtleDamageObservation):
            return TurtleDamageObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, TurtleNestObservation):
            return TurtleNestObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, ManagementAction):
            return ManagementActionSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, TurtleNestObservation):
            return TurtleNestObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, TurtleNestDisturbanceObservation):
            return TurtleNestDisturbanceObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, TrackTallyObservation):
            return TrackTallyObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, TurtleNestDisturbanceTallyObservation):
            return TurtleNestDisturbanceTallyObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, TagObservation):
            return TagObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, MediaAttachment):
            return MediaAttachmentSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, TemperatureLoggerSettings):
            return TemperatureLoggerSettingsSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, DispatchRecord):
            return DispatchRecordSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, TemperatureLoggerDeployment):
            return TemperatureLoggerDeploymentSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, NestTagObservation):
            return NestTagObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, HatchlingMorphometricObservation):
            return HatchlingMorphometricObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, DugongMorphometricObservation):
            return DugongMorphometricObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, TurtleHatchlingEmergenceObservation):
            return TurtleHatchlingEmergenceObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, TurtleHatchlingEmergenceOutlierObservation):
            return TurtleHatchlingEmergenceOutlierObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, LightSourceObservation):
            return LightSourceObservationSerializer(
                obj, context=self.context).to_representation(obj)

        return super(ObservationSerializer, self).to_representation(obj)


class MediaAttachmentSerializer(ModelSerializer):
    attachment = FileField(use_url=False)
    filepath = ReadOnlyField()
    # as_latex = ReadOnlyField()

    class Meta:
        model = MediaAttachment
        fields = ("observation_name", "media_type", "title", "attachment", "filepath")


class ManagementActionSerializer(ModelSerializer):
    # as_latex = ReadOnlyField()

    class Meta:
        model = ManagementAction
        fields = ("observation_name", "management_actions", "comments")


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


class EncounterSerializer(GeoFeatureModelSerializer):
    """Encounter serializer.

    Alternative: serializers.HyperlinkedModelSerializer

    TODO: a writable version of the serializer will provide `create` and
    `update` methods, which also create/update the inline Observations.

    Since nested Observations are polymorphic, two steps have to be taken above
    the plain nested writeable API:

    * :mod:`wastd.observations.models.Observation.observation_name` is a property
      method to return the child model"s name
    * :mod:`wastd.api.ObservationSerializer` includes the `observation_name` in
      the API dict
    * :mod:`wastd.api.EncounterSerializer.create` and `update` (coming) handle
      both the Encounter and the nested Observations separately. Observations
      use their included `observation_name` to figure out the actual model that
      we want to `create` or `update`.

      TODO http://stackoverflow.com/q/32123148/2813717
      NOTE this API is not writeable, as related models (User and Observation)
      require customisations to handle data thrown at them.
    """

    observation_set = ObservationSerializer(many=True, read_only=False)
    observer = FastUserSerializer(many=False, read_only=True)
    reporter = FastUserSerializer(many=False, read_only=True)
    area = FastAreaSerializer(many=False, read_only=True)
    site = FastAreaSerializer(many=False, read_only=True)
    survey = FastSurveySerializer(many=False, read_only=True)
    # observer = StringRelatedField(read_only=True)
    # reporter = StringRelatedField(read_only=True)
    # where = PointField(required=True)   ## THIS BREAKS GEOJSON OUTPUT
    leaflet_title = ReadOnlyField()
    latitude = ReadOnlyField()
    longitude = ReadOnlyField()
    crs = ReadOnlyField()
    absolute_admin_url = ReadOnlyField()
    photographs = MediaAttachmentSerializer(many=True, read_only=False)
    tx_logs = ReadOnlyField()

    class Meta:
        """The non-standard name `where` is declared as the geo field for the
        GeoJSON serializer's benefit.
        """
        model = Encounter
        name = "encounter"
        fields = ("pk", "area", "site", "survey",
                  "where", "location_accuracy", "when",
                  "name", "observer", "reporter", "comments",
                  "status", "source", "source_id", "encounter_type",
                  "leaflet_title", "latitude", "longitude", "crs",
                  "absolute_admin_url", "photographs", "tx_logs",
                  #  "as_html", "as_latex",
                  "observation_set", )
        geo_field = "where"
        id_field = "source_id"

    # def create(self, validated_data):
    #     """Make EncounterSerializer writeable: create
    #
    #     POST a set of records, or PUT one record
    #
    #     behaviour:
    #
    #     * If Encounter exists as NEW, update
    #     * If Encounter exists as PROOFREAD, CURATED or PUBLISHED, skip and warn
    #     * If Encounter does not exists, create
    #
    #     The actual child model is looked up by "observation_name".
    #     """
    #     print("EncounterSerializer.save() called".format())
    #     # Keep observation_set in the fridge, make Encounter first
    #     obs_data = validated_data.pop("observation_set")

        # Extract Users from encounter: observer, reporter
        # o = validated_data.pop("observer")
        # observer, observer_created = User.objects.get_or_create(
        #     username=o["username"], email=o["email"])
        # print("observer {0} created {1}".format(observer, observer_created))
        #
        # o = validated_data.pop("reporter")
        # reporter, reporter_created = User.objects.get_or_create(
        #     username=o["username"], email=o["email"])

        # src = validated_data["source"]
        # srcid = validated_data["source_id"]
        #
        # if Encounter.objects.filter(source=src, source_id=srcid).exists():
        #     print("Encounter exists: {0}-{1}".format(src, srcid))
        #     encounter = Encounter.objects.get(source=src, source_id=srcid)
        #     if encounter.status == Encounter.STATUS_NEW:
        #         print("Encounter not proofread/curated, updating...")
        #         encounter.update(**validated_data)
        #         encounter.save()
        #     else:
        #         print("Encounter already changed, skipping.")
        # else:
        #     print("No Encounter with source/source_id found, creating new...")
        #     encounter = Encounter.objects.create(**validated_data)
        #     # encounter.reporter = reporter
        #     # encounter.observer = observer
        #     encounter.save()
        #
        #     for obs in obs_data:
        #         childmodel_name = obs.pop("observation_name")
        #         childmodel = getattr(Observation,
        #                              childmodel_name).related.related_model
        #         childmodel.objects.create(encounter=encounter, **obs)
        #
        # return encounter


class FastEncounterSerializer(GeoFeatureModelSerializer):
    """Encounter serializer.

    Alternative: serializers.HyperlinkedModelSerializer

    TODO: a writable version of the serializer will provide `create` and
    `update` methods, which also create/update the inline Observations.

    Since nested Observations are polymorphic, two steps have to be taken above
    the plain nested writeable API:

    * :mod:`wastd.observations.models.Observation.observation_name` is a property
      method to return the child model"s name
    * :mod:`wastd.api.ObservationSerializer` includes the `observation_name` in
      the API dict
    * :mod:`wastd.api.EncounterSerializer.create` and `update` (coming) handle
      both the Encounter and the nested Observations separately. Observations
      use their included `observation_name` to figure out the actual model that
      we want to `create` or `update`.

      TODO http://stackoverflow.com/q/32123148/2813717
      NOTE this API is not writeable, as related models (User and Observation)
      require customisations to handle data thrown at them.
    """

    # observation_set = ObservationSerializer(many=True, read_only=False)
    observer = FastUserSerializer(many=False, read_only=True)
    reporter = FastUserSerializer(many=False, read_only=True)
    area = FastAreaSerializer(many=False, read_only=True)
    site = FastAreaSerializer(many=False, read_only=True)
    survey = FastSurveySerializer(many=False, read_only=True)
    # observer = StringRelatedField(read_only=True)
    # reporter = StringRelatedField(read_only=True)
    # where = PointField(required=True)   ## THIS BREAKS GEOJSON OUTPUT
    leaflet_title = ReadOnlyField()
    latitude = ReadOnlyField()
    longitude = ReadOnlyField()
    crs = ReadOnlyField()
    absolute_admin_url = ReadOnlyField()
    photographs = MediaAttachmentSerializer(many=True, read_only=False)
    tx_logs = ReadOnlyField()

    class Meta:
        """The non-standard name `where` is declared as the geo field for the
        GeoJSON serializer's benefit.
        """
        model = Encounter
        name = "encounter"
        fields = ("pk", "area", "site", "survey",
                  "where", "location_accuracy", "when",
                  "name", "observer", "reporter", "comments",
                  "status", "source", "source_id", "encounter_type",
                  "leaflet_title", "latitude", "longitude", "crs",
                  "absolute_admin_url", "photographs", "tx_logs",
                  #  "as_html", "as_latex",
                  # "observation_set",
                  )
        geo_field = "where"
        id_field = "source_id"


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
                  "absolute_admin_url", "photographs", "tx_logs",
                  "observation_set",
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
                  "absolute_admin_url", "photographs", "tx_logs",
                  "observation_set", )
        geo_field = "where"


class TagObservationSerializer(ModelSerializer):
    # as_latex = ReadOnlyField()

    class Meta:
        model = TagObservation
        fields = ("observation_name",  # "as_latex",
                  "tag_type", "name", "tag_location",
                  "status", "comments", )


class TagObservationEncounterSerializer(GeoFeatureModelSerializer):
    """TagObservation serializer including encounter for standalone viewset.
    """
    encounter = FastEncounterSerializer(many=False, read_only=True)
    point = GeometryField()

    class Meta:
        model = TagObservation
        geo_field = "point"
        fields = ("encounter", "observation_name", "tag_type", "name",
                  "tag_location", "status", "comments", )


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


class TurtleMorphometricObservationEncounterSerializer(GeoFeatureModelSerializer):
    """TurtleMorphometricObservation serializer including encounter for standalone viewset."""

    encounter = FastEncounterSerializer(many=False, read_only=True)
    point = GeometryField()

    class Meta:
        model = TurtleMorphometricObservation
        geo_field = "point"
        fields = (
            "encounter", "observation_name", "latitude", "longitude",
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


class TurtleNestObservationEncounterSerializer(GeoFeatureModelSerializer):
    """TurtleNestObservation serializer including encounter for standalone viewset."""
    encounter = FastEncounterSerializer(many=False, read_only=True)
    point = GeometryField()

    class Meta:
        model = TurtleNestObservation
        geo_field = "point"
        fields = (
            "encounter", "observation_name", "latitude", "longitude",
            "nest_position", "eggs_laid", "egg_count",
            "hatching_success", "emergence_success",
            "no_egg_shells", "no_live_hatchlings_neck_of_nest", "no_live_hatchlings",
            "no_dead_hatchlings", "no_undeveloped_eggs",
            "no_unhatched_eggs", "no_unhatched_term", "no_depredated_eggs",
            "nest_depth_top", "nest_depth_bottom",
            "sand_temp", "air_temp", "water_temp", "egg_temp", "comments",
        )


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


class NestTagObservationEncounterSerializer(GeoFeatureModelSerializer):
    """NestTagObservationSerializer with encounter."""
    encounter = FastEncounterSerializer(many=False, read_only=True)
    point = GeometryField()

    class Meta:
        model = NestTagObservation
        geo_field = "point"
        fields = (
            "encounter",
            "observation_name",
            "status",
            "flipper_tag_id",
            "date_nest_laid",
            "tag_label",
            "comments",)


class TurtleNestDisturbanceObservationSerializer(ModelSerializer):
    # as_latex = ReadOnlyField()

    class Meta:
        model = TurtleNestDisturbanceObservation
        fields = ("observation_name",  # "as_latex",
                  "disturbance_cause", "disturbance_cause_confidence",
                  "disturbance_severity", "comments", )


class TurtleNestDisturbanceObservationEncounterSerializer(GeoFeatureModelSerializer):
    """TurtleNestDisturbanceObservation serializer with encounter."""
    encounter = FastEncounterSerializer(many=False, read_only=True)
    point = GeometryField()

    class Meta:
        model = TurtleNestDisturbanceObservation
        geo_field = "point"
        fields = (
            "encounter",
            "observation_name",
            "disturbance_cause",
            "disturbance_cause_confidence",
            "disturbance_severity",
            "comments", )


class HatchlingMorphometricObservationSerializer(ModelSerializer):
    # as_latex = ReadOnlyField()

    class Meta:
        model = HatchlingMorphometricObservation
        fields = ("observation_name",  # "as_latex", #
                  "straight_carapace_length_mm",
                  "straight_carapace_width_mm",
                  "body_weight_g",
                  )


class HatchlingMorphometricObservationEncounterSerializer(GeoFeatureModelSerializer):
    """HatchlingMorphometricObservation serializer including encounter for standalone viewset."""
    encounter = FastEncounterSerializer(many=False, read_only=True)
    point = GeometryField()

    class Meta:
        model = HatchlingMorphometricObservation
        geo_field = "point"
        fields = (
            "encounter",
            "observation_name",
            "latitude",
            "longitude",
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


class TurtleHatchlingEmergenceObservationEncounterSerializer(GeoFeatureModelSerializer):
    """TurtleHatchlingEmergenceObservation serializer including encounter for standalone viewset."""
    encounter = FastEncounterSerializer(many=False, read_only=True)
    point = GeometryField()

    class Meta:
        model = TurtleHatchlingEmergenceObservation
        geo_field = "point"
        fields = (
            "encounter",
            "observation_name",
            "latitude",
            "longitude",
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


class TurtleHatchlingEmergenceOutlierObservationEncounterSerializer(GeoFeatureModelSerializer):
    """TurtleHatchlingEmergenceOutlierObservation serializer including encounter for standalone viewset.
    """
    encounter = FastEncounterSerializer(many=False, read_only=True)
    point = GeometryField()

    class Meta:
        model = TurtleHatchlingEmergenceOutlierObservation
        geo_field = "point"
        fields = (
            "encounter",
            "observation_name",
            "latitude",
            "longitude",
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


class LightSourceObservationEncounterSerializer(GeoFeatureModelSerializer):
    """LightSource serializer including encounter for standalone viewsets.
    """
    encounter = FastEncounterSerializer(many=False, read_only=True)
    point = GeometryField()

    class Meta:
        model = LightSourceObservation
        geo_field = "point"
        fields = (
            "encounter",
            "observation_name",
            "latitude",
            "longitude",
            "bearing_light_degrees",
            "light_source_type",
            "light_source_description",
        )
