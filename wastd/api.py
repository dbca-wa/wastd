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
from rest_framework import serializers, viewsets
# import rest_framework_filters as filters
# from dynamic_rest import serializers as ds, viewsets as dv
from drf_extra_fields.geo_fields import PointField

from wastd.observations.models import (
    Encounter, TurtleNestEncounter,
    AnimalEncounter,  # TurtleEncounter, CetaceanEncounter,
    Observation, MediaAttachment, TagObservation,
    ManagementAction, TurtleMorphometricObservation, TurtleNestObservation,
    TurtleDamageObservation, TrackTallyObservation)
from wastd.users.models import User


# Serializers ----------------------------------------------------------------#
class UserSerializer(serializers.ModelSerializer):
    """User serializer."""

    class Meta:
        """Class options."""

        model = User
        fields = ('username', 'name', 'email', 'first_name', 'last_name')


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
        if isinstance(obj, TrackTallyObservation):
            return TrackTallyObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, TagObservation):
            return TagObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, MediaAttachment):
            return MediaAttachmentSerializer(
                obj, context=self.context).to_representation(obj)

        return super(ObservationSerializer, self).to_representation(obj)


class MediaAttachmentSerializer(serializers.ModelSerializer):
    """MediaAttachment serializer."""

    class Meta:
        """Class options."""

        model = MediaAttachment
        fields = ('observation_name',
                  'media_type', 'title', 'attachment')


class TagObservationSerializer(serializers.ModelSerializer):
    """TagObservation serializer."""

    class Meta:
        """Class options."""

        model = TagObservation
        fields = ('observation_name',
                  'tag_type', 'name', 'tag_location',
                  'status', 'comments')


class TagObservationEncounterSerializer(serializers.ModelSerializer):
    """TagObservation serializer."""

    class Meta:
        """Class options."""

        model = TagObservation
        fields = ('encounter', 'observation_name',
                  'tag_type', 'name', 'tag_location',
                  'status', 'comments')

class TurtleMorphometricObservationSerializer(serializers.ModelSerializer):
    """TurtleMorphometricObservation serializer."""

    class Meta:
        """Class options."""

        model = TurtleMorphometricObservation
        fields = ('observation_name',
                  'curved_carapace_length_mm', 'curved_carapace_length_accuracy',
                  'curved_carapace_notch_mm', 'curved_carapace_notch_accuracy',
                  'curved_carapace_width_mm', 'curved_carapace_width_accuracy',
                  'tail_length_mm', 'tail_length_accuracy',
                  'maximum_head_width_mm', 'maximum_head_width_mm')


class ManagementActionSerializer(serializers.ModelSerializer):
    """DisposalObservation serializer."""

    class Meta:
        """Class options."""

        model = ManagementAction
        fields = ('observation_name',
                  'management_actions', 'comments',)


class TurtleNestObservationSerializer(serializers.ModelSerializer):
    """TurtleNestObservation serializer."""

    class Meta:
        """Class options."""

        model = TurtleNestObservation
        fields = ('observation_name',
                  'nest_position', 'eggs_laid', 'egg_count', 'no_egg_shells',
                  'no_live_hatchlings', 'no_dead_hatchlings', 'no_undeveloped_eggs',
                  'no_dead_embryos', 'no_dead_full_term_embryos', 'no_depredated_eggs',
                  'no_unfertilized', 'no_yolkless_eggs', 'nest_depth_top',
                  'nest_depth_bottom', 'sand_temp', 'air_temp', 'water_temp',
                  'egg_temp')


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
                  'false_crawls_caretta_caretta',
                  'false_crawls_chelonia_mydas',
                  'false_crawls_eretmochelys_imbricata',
                  'false_crawls_natator_depressus',
                  'false_crawls_lepidochelys_olivacea',
                  'false_crawls_na',
                  'fox_predation',
                  'dog_predation',
                  'dingo_predation',
                  'goanna_predation',
                  'bird_predation',
                  )


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
    observer = serializers.StringRelatedField(read_only=True)
    reporter = serializers.StringRelatedField(read_only=True)
    where = PointField(required=True)

    class Meta:
        """Class options.

        The non-standard name `where` is declared as the geo field for the
        GeoJSON serializer's benefit.
        """

        model = Encounter
        name = 'encounter'
        fields = ('where', 'location_accuracy', 'when', 'name',
                  'observer', 'reporter',
                  'status', 'source', 'source_id', 'observation_set', )
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


class TurtleNestEncounterSerializer(EncounterSerializer):
    """TurtleNestEncounter serializer."""
    where = PointField(required=True)

    class Meta:
        """Class options."""

        model = TurtleNestEncounter
        fields = ('where', 'location_accuracy', 'when', 'name',
                  'observer', 'reporter',
                  'nest_age', 'species', 'habitat',
                  'status', 'source', 'source_id', 'observation_set', )


class AnimalEncounterSerializer(EncounterSerializer):
    """AnimalEncounter serializer."""
    where = PointField(required=True)

    class Meta:
        """Class options."""

        model = AnimalEncounter
        fields = ('where', 'location_accuracy', 'when', 'name',
                  'observer', 'reporter',
                  'taxon', 'species', 'health', 'sex', 'behaviour',
                  'habitat', 'activity', 'checked_for_injuries',
                  'scanned_for_pit_tags',
                  'checked_for_flipper_tags',
                  'status', 'source', 'source_id', 'observation_set', )


# class TurtleEncounterSerializer(EncounterSerializer):
#     """TurtleEncounter serializer."""
#
#     class Meta:
#         """Class options."""
#
#         model = TurtleEncounter
#         fields = ('where', 'when', 'who',
#                   'species', 'health', 'sex', 'behaviour', 'habitat', 'activity',
#                   'observation_set', )
#
#
# class CetaceanEncounterSerializer(EncounterSerializer):
#     """CetaceanEncounter serializer."""
#
#     class Meta:
#         """Class options."""
#
#         model = CetaceanEncounter
#         fields = ('where', 'when', 'who',
#                   'species', 'health', 'sex', 'behaviour', 'habitat', 'activity',
#                   'observation_set', )


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    """User view set."""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class EncounterViewSet(viewsets.ModelViewSet):
    """Encounter view set."""

    queryset = Encounter.objects.all()
    serializer_class = EncounterSerializer
    filter_fields = [
        'location_accuracy', 'when', 'name', 'observer', 'reporter', 'status',
        'source', 'source_id', ]


class TurtleNestEncounterViewSet(viewsets.ModelViewSet):
    """TurtleNestEncounter view set."""

    queryset = TurtleNestEncounter.objects.all()
    serializer_class = TurtleNestEncounterSerializer
    filter_fields = [
        'location_accuracy', 'when', 'name', 'observer', 'reporter',  'status',
        'nest_age', 'species', 'habitat', 'source', 'source_id', ]


class AnimalEncounterViewSet(viewsets.ModelViewSet):
    """AnimalEncounter view set."""

    queryset = AnimalEncounter.objects.all()
    serializer_class = AnimalEncounterSerializer
    filter_fields = [
        'location_accuracy', 'when', 'name', 'observer', 'reporter', 'status',
        'species', 'health', 'sex', 'maturity', 'habitat', 'behaviour',
        'checked_for_injuries', 'scanned_for_pit_tags', 'checked_for_flipper_tags',
        'source', 'source_id', ]


# class TurtleEncounterViewSet(viewsets.ModelViewSet):
#     """TurtleEncounter view set."""
#
#     queryset = TurtleEncounter.objects.all()
#     serializer_class = TurtleEncounterSerializer
#
#
# class CetaceanEncounterViewSet(viewsets.ModelViewSet):
#     """CetaceanEncounter view set."""
#
#     queryset = CetaceanEncounter.objects.all()
#     serializer_class = CetaceanEncounterSerializer


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
