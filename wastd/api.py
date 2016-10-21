# -*- coding: utf-8 -*-
"""The WAStD API moduleprovides command-line access to:

* Encouter and subclasses: AnimalEncounter, TurtleNestEncounter
* Encounter Inlines: Observation subclasses
* Separate TagObservation serializer to retrieve a Tag history.

This API outputs:

* Interactive HTML API
* CSV
* JSONP
* Latex (coming soon)

This API is built using:

* djangorestframework
* `djangorestframework-gis <https://github.com/djangonauts/django-rest-framework-gis>`_
* djangorestframework-csv
* `djangorestframework-yaml <http://www.django-rest-framework.org/api-guide/renderers/#yaml>`_ (TODO support geo field)
* djangorestframework-jsonp
* djangorestframework-filters
* django-url-filter
* dynamic-rest (not used)
* rest-framework-latex
* markdown
* django-filter
* django-rest-swagger
* coreapi
* coreapi-cli (complementary CLI for coreapi)
"""
import os
from json import loads, dumps
from subprocess import Popen, PIPE

from rest_framework import serializers, viewsets, routers
# from rest_framework.renderers import BrowsableAPIRenderer
# from rest_framework_latex import renderers
# import rest_framework_filters as filters
# from dynamic_rest import serializers as ds, viewsets as dv
from drf_extra_fields.geo_fields import PointField

from rest_framework.authentication import (
    SessionAuthentication, BasicAuthentication, TokenAuthentication)

from wastd.observations.models import (
    Area,
    Encounter, AnimalEncounter, TurtleNestEncounter, LoggerEncounter,
    Observation, MediaAttachment, TagObservation,
    TurtleMorphometricObservation, TurtleDamageObservation, ManagementAction,
    TurtleNestObservation, TurtleNestDisturbanceObservation,
    TrackTallyObservation, TurtleNestDisturbanceTallyObservation,
    TemperatureLoggerSettings, DispatchRecord,
    TemperatureLoggerDeployment)
from wastd.users.models import User

from django.conf import settings
# from synctool.routing import Route as SynctoolRoute

# # Synctools
# # http://django-synctool.readthedocs.io/
# sync_route = SynctoolRoute()
#
#
# @sync_route.app("users", "users")
# @sync_route.app("observations", "observations")


# Serializers ----------------------------------------------------------------#
class UserSerializer(serializers.ModelSerializer):
    """User serializer."""

    class Meta:
        """Class options."""

        model = User
        fields = ('username', 'name', 'email', 'phone', )


class ObservationSerializer(serializers.ModelSerializer):
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

    class Meta:
        """Class options."""

        model = Observation
        fields = ('observation_name', )

    def to_representation(self, obj):
        """Resolve the Observation instance to the child class's serializer."""
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

        return super(ObservationSerializer, self).to_representation(obj)


class MediaAttachmentSerializer(serializers.ModelSerializer):
    """MediaAttachment serializer."""
    attachment = serializers.FileField(use_url=False) # TODO absolute local path
    filepath = serializers.ReadOnlyField()

    class Meta:
        """Class options."""

        model = MediaAttachment
        fields = ('observation_name',
                  'media_type', 'title', 'attachment', 'filepath')
        # fields = '__all__'


class TagObservationSerializer(serializers.ModelSerializer):
    """TagObservation serializer."""

    class Meta:
        """Class options."""

        model = TagObservation
        fields = ('observation_name',
                  'tag_type', 'name', 'tag_location',
                  'status', 'comments', )


class TagObservationEncounterSerializer(serializers.ModelSerializer):
    """TagObservation serializer including encounter for standalone viewset."""

    class Meta:
        """Class options."""

        model = TagObservation
        fields = ('encounter', 'observation_name',
                  'tag_type', 'name', 'tag_location',
                  'status', 'comments', )


class TurtleMorphometricObservationSerializer(serializers.ModelSerializer):
    """TurtleMorphometricObservation serializer."""

    class Meta:
        """Class options."""

        model = TurtleMorphometricObservation
        fields = ('observation_name',
                  'curved_carapace_length_mm', 'curved_carapace_length_accuracy',
                  'straight_carapace_length_mm', 'straight_carapace_length_accuracy',
                  'curved_carapace_width_mm', 'curved_carapace_width_accuracy',
                  'tail_length_carapace_mm', 'tail_length_carapace_accuracy',
                  'tail_length_vent_mm', 'tail_length_vent_accuracy',
                  'tail_length_plastron_mm', 'tail_length_plastron_accuracy',
                  'maximum_head_width_mm', 'maximum_head_width_accuracy',
                  'maximum_head_length_mm', 'maximum_head_length_accuracy',
                  'body_depth_mm', 'body_depth_accuracy',
                  'body_weight_mm', 'body_weight_accuracy',
                  'handler', 'recorder', )


class ManagementActionSerializer(serializers.ModelSerializer):
    """DisposalObservation serializer."""

    class Meta:
        """Class options."""

        model = ManagementAction
        fields = ('observation_name',
                  'management_actions', 'comments', )


class TurtleNestObservationSerializer(serializers.ModelSerializer):
    """TurtleNestObservation serializer."""

    class Meta:
        """Class options."""

        model = TurtleNestObservation
        fields = ('observation_name',
                  'nest_position', 'eggs_laid', 'egg_count',
                  'no_emerged', 'no_egg_shells',
                  'no_live_hatchlings', 'no_dead_hatchlings',
                  'no_undeveloped_eggs', 'no_unhatched_eggs',
                  'no_unhatched_term', 'no_depredated_eggs',
                  'nest_depth_top', 'nest_depth_bottom',
                  'sand_temp', 'air_temp', 'water_temp', 'egg_temp',
                  'hatching_success', 'emergence_success', )


class TurtleNestDisturbanceObservationSerializer(serializers.ModelSerializer):
    """TurtleNestDisturbanceObservation serializer."""

    class Meta:
        """Class options."""

        model = TurtleNestDisturbanceObservation
        fields = ('observation_name',
                  'disturbance_cause', 'disturbance_cause_confidence',
                  'disturbance_severity', 'comments', )


class TurtleDamageObservationSerializer(serializers.ModelSerializer):
    """TurtleDamageObservation serializer."""

    class Meta:
        """Class options."""

        model = TurtleDamageObservation
        fields = ('observation_name',
                  'body_part', 'damage_type', 'damage_age', 'description', )


class TrackTallyObservationSerializer(serializers.ModelSerializer):
    """TrackTallyObservation serializer."""

    class Meta:
        """Class options."""

        model = TrackTallyObservation
        fields = ('observation_name',
                  'species',
                  'track_type',
                  'tally',)


class TurtleNestDisturbanceTallyObservationSerializer(serializers.ModelSerializer):
    """TurtleNestDisturbanceTallyObservation serializer."""

    class Meta:
        """Class options."""

        model = TurtleNestDisturbanceTallyObservation
        fields = ('observation_name',
                  'species',
                  'disturbance_cause',
                  'tally',)



class TemperatureLoggerSettingsSerializer(serializers.ModelSerializer):
    """TemperatureLoggerSettings serializer."""

    class Meta:
        """Class options."""

        model = TemperatureLoggerSettings
        fields = ('logging_interval', 'recording_start', 'tested', )


class DispatchRecordSerializer(serializers.ModelSerializer):
    """DispatchRecord serializer."""

    class Meta:
        """Class options."""

        model = DispatchRecord
        fields = ('sent_to',)


class TemperatureLoggerDeploymentSerializer(serializers.ModelSerializer):
    """TemperatureLoggerDeployment serializer."""

    class Meta:
        """Class options."""

        model = TemperatureLoggerDeployment
        fields = ('depth_mm',
                  'marker1_present',
                  'distance_to_marker1_mm',
                  'marker2_present',
                  'distance_to_marker2_mm',
                  'habitat',
                  'distance_to_vegetation_mm',
                  )


class AreaSerializer(serializers.ModelSerializer):
    """Area serializer."""

    class Meta:
        """Class options."""

        model = Area
        fields = ("area_type", "name", "geom", "northern_extent", "centroid", )


class EncounterSerializer(serializers.ModelSerializer):
    """Encounter serializer.

    TODO: a writable version of the serializer will provide `create` and
    `update` methods, which also create/update the inline Observations.

    Since nested Observations are polymorphic, two steps have to be taken above
    the plain nested writeable API:

    * :mod:`wastd.observations.models.Observation.observation_name` is a property
      method to return the child model's name
    * :mod:`wastd.api.ObservationSerializer` includes the `observation_name` in
      the API dict
    * :mod:`wastd.api.EncounterSerializer.create` and `update` (coming) handle
      both the Encounter and the nested Observations separately. Observations
      use their included `observation_name` to figure out the actual model that
      we want to `create` or `update`.
    """

    observation_set = ObservationSerializer(many=True, read_only=False)
    observer = UserSerializer(many=False, read_only=False)
    reporter = UserSerializer(many=False, read_only=False)
    # observer = serializers.StringRelatedField(read_only=True)
    # reporter = serializers.StringRelatedField(read_only=True)
    where = PointField(required=True)
    leaflet_title = serializers.ReadOnlyField()
    latitude = serializers.ReadOnlyField()
    longitude = serializers.ReadOnlyField()
    crs = serializers.ReadOnlyField()
    absolute_admin_url = serializers.ReadOnlyField()
    photographs = MediaAttachmentSerializer(many=True, read_only=False)

    class Meta:
        """Class options.

        The non-standard name `where` is declared as the geo field for the
        GeoJSON serializer's benefit.
        """

        model = Encounter
        name = 'encounter'
        fields = ('pk', 'site_visit', 'where', 'location_accuracy', 'when',
                  'name', 'observer', 'reporter',
                  'status', 'source', 'source_id', 'encounter_type',
                  'leaflet_title', 'latitude', 'longitude', 'crs',
                  'absolute_admin_url', 'photographs',
                  'observation_set', )
        geo_field = "where"

    def create(self, validated_data):
        """Make EncounterSerializer writeable.

        The actual child model is looked up by "observation_name".
        """
        obs_data = validated_data.pop('observation_set')
        encounter = Encounter.objects.create(**validated_data)
        for obs in obs_data:
            childmodel_name = obs.pop("observation_name")
            childmodel = getattr(Observation,
                                 childmodel_name).related.related_model
            childmodel.objects.create(encounter=encounter, **obs)
        return encounter


class AnimalEncounterSerializer(EncounterSerializer):
    """AnimalEncounter serializer."""
    where = PointField(required=True)

    class Meta:
        """Class options."""

        model = AnimalEncounter
        fields = ('pk', 'site_visit', 'where', 'location_accuracy', 'when', 'name',
                  'observer', 'reporter',
                  'taxon', 'species', 'health', 'sex', 'behaviour',
                  'habitat', 'activity', 'checked_for_injuries',
                  'scanned_for_pit_tags',
                  'checked_for_flipper_tags',
                  'status', 'source', 'source_id', 'encounter_type',
                  'observation_set', )


class TurtleNestEncounterSerializer(EncounterSerializer):
    """TurtleNestEncounter serializer."""
    where = PointField(required=True)

    class Meta:
        """Class options."""

        model = TurtleNestEncounter
        fields = ('pk', 'site_visit', 'where', 'location_accuracy', 'when', 'name',
                  'observer', 'reporter',
                  'nest_age', 'species', 'habitat', 'disturbance',
                  'status', 'source', 'source_id', 'encounter_type',
                  'observation_set', )


class LoggerEncounterSerializer(EncounterSerializer):
    """LoggerEncounter serializer."""
    where = PointField(required=True)

    class Meta:
        """Class options."""

        model = LoggerEncounter
        fields = ('pk', 'where', 'location_accuracy', 'when', 'name',
                  'observer', 'reporter',
                  'deployment_status', 'comments',
                  'observation_set', )


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    """User view set."""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class AreaViewSet(viewsets.ModelViewSet):
    """Area view set."""

    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    filter_fields = ["area_type", ]


class EncounterViewSet(viewsets.ModelViewSet):
    """Encounter view set."""

    latex_name = 'latex/encounter.tex'
    queryset = Encounter.objects.all()
    serializer_class = EncounterSerializer
    filter_fields = [
        'location_accuracy', 'when', 'name', 'observer', 'reporter', 'status',
        'source', 'source_id', 'encounter_type', ]

    def pre_latex(view, t_dir, data):
        """Symlink photographs to temp dir for use by latex template."""
        for enc in loads(dumps(data)):
            if len(enc["photographs"]) > 0:

                # Once per encounter, create temp_dir/media_path
                media_path = os.path.split(enc["photographs"][0]["attachment"])[0]
                print(media_path)
                dest_dir = os.path.join(t_dir, "tex", media_path)
                os.makedirs(dest_dir)

                for photo in enc["photographs"]:
                    # Once per photo, symlink file to temp_dir
                    src = photo["filepath"]
                    rel_src = photo["attachment"]
                    dest = os.path.join(t_dir, "tex", rel_src)
                    if os.path.lexists(dest):
                        # emulate ln -sf
                        os.remove(dest)
                    os.symlink(src, dest)

class TurtleNestEncounterViewSet(viewsets.ModelViewSet):
    """TurtleNestEncounter view set."""
    latex_name = 'latex/turtlenestencounter.tex'
    queryset = TurtleNestEncounter.objects.all()
    serializer_class = TurtleNestEncounterSerializer
    filter_fields = [
        'location_accuracy', 'when', 'name', 'observer', 'reporter',  'status',
        'nest_age', 'species', 'habitat', 'disturbance', 'source', 'source_id',
        'encounter_type', ]


class AnimalEncounterViewSet(viewsets.ModelViewSet):
    """AnimalEncounter view set."""
    latex_name = 'latex/animalencounter.tex'
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    queryset = AnimalEncounter.objects.all()
    serializer_class = AnimalEncounterSerializer
    filter_fields = [
        'location_accuracy', 'when', 'name', 'observer', 'reporter', 'status',
        'species', 'health', 'sex', 'maturity', 'habitat', 'behaviour',
        'checked_for_injuries', 'scanned_for_pit_tags', 'checked_for_flipper_tags',
        'source', 'source_id', 'encounter_type', ]


class LoggerEncounterViewSet(viewsets.ModelViewSet):
    """LoggerEncounter view set."""
    latex_name = 'latex/loggerencounter.tex'
    queryset = LoggerEncounter.objects.all()
    serializer_class = LoggerEncounterSerializer
    filter_fields = [
        'location_accuracy', 'when', 'name', 'observer', 'reporter', 'status',
        'deployment_status', 'comments',
        'source', 'source_id', 'encounter_type', ]


class ObservationViewSet(viewsets.ModelViewSet):
    """Observation view set."""

    queryset = Observation.objects.all()
    serializer_class = ObservationSerializer


class MediaAttachmentViewSet(viewsets.ModelViewSet):
    """MediaAttachment view set."""

    queryset = MediaAttachment.objects.all()
    serializer_class = MediaAttachmentSerializer


class TagObservationViewSet(viewsets.ModelViewSet):
    """TagObservation view set."""

    queryset = TagObservation.objects.all()
    serializer_class = TagObservationEncounterSerializer
    filter_fields = ['tag_type', 'tag_location', 'name', 'status', 'comments']

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter(schema_title='WAStD API')
# router.register(r'users', UserViewSet)
router.register(r'areas', AreaViewSet)
router.register(r'encounters', EncounterViewSet)
router.register(r'animal-encounters', AnimalEncounterViewSet)
router.register(r'turtle-nest-encounters', TurtleNestEncounterViewSet)
router.register(r'logger-encounters', LoggerEncounterViewSet)
router.register(r'observations', ObservationViewSet)
router.register(r'media-attachments', MediaAttachmentViewSet)
router.register(r'tag-observations', TagObservationViewSet)
