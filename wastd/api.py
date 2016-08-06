from rest_framework import serializers, viewsets
from dynamic_rest import serializers as ds

from wastd.observations.models import (
    Encounter, AnimalEncounter, MediaAttachment, Observation,
    FlipperTagObservation, DisposalObservation, TurtleMorphometricObservation,
    DistinguishingFeatureObservation)
from wastd.users.models import User


# Serializers ----------------------------------------------------------------#
class UserSerializer(ds.DynamicModelSerializer):
    """User serializer."""

    class Meta:
        """Class options."""

        model = User
        fields = ('username', 'name', 'email', 'first_name', 'last_name')


class ObservationSerializer(ds.DynamicModelSerializer):
    """Observation serializer."""

    encounter = serializers.StringRelatedField()

    class Meta:
        """Class options."""

        model = Observation
        fields = ('encounter', )

    def to_representation(self, obj):
        """Resolve Observation to child class."""
        if isinstance(obj, FlipperTagObservation):
            return FlipperTagObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, MediaAttachment):
            return MediaAttachmentSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, DistinguishingFeatureObservation):
            return DistinguishingFeatureObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, TurtleMorphometricObservation):
            return TurtleMorphometricObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, DisposalObservation):
            return DisposalObservationSerializer(
                obj, context=self.context).to_representation(obj)

        return super(ObservationSerializer, self).to_representation(obj)


class MediaAttachmentSerializer(ds.DynamicModelSerializer):
    """MediaAttachment serializer."""

    encounter = serializers.StringRelatedField()

    class Meta:
        """Class options."""

        model = MediaAttachment
        fields = ('encounter', 'media_type', 'title', 'attachment')


class DistinguishingFeatureObservationSerializer(ds.DynamicModelSerializer):
    """DistinguishingFeatureObservation serializer."""

    encounter = serializers.StringRelatedField()

    class Meta:
        """Class options."""

        model = DistinguishingFeatureObservation
        fields = ('encounter', 'damage_injury', 'missing_limbs', 'barnacles',
                  'algal_growth', 'tagging_scars', 'propeller_damage',
                  'entanglement', 'see_photo', 'comments')


class TurtleMorphometricObservationSerializer(ds.DynamicModelSerializer):
    """TurtleMorphometricObservation serializer."""

    encounter = serializers.StringRelatedField()

    class Meta:
        """Class options."""

        model = TurtleMorphometricObservation
        fields = ('encounter',
                  'curved_carapace_length_mm', 'curved_carapace_length_accuracy',
                  'curved_carapace_notch_mm', 'curved_carapace_notch_accuracy',
                  'curved_carapace_width_mm', 'curved_carapace_width_accuracy',
                  'tail_length_mm', 'tail_length_accuracy',
                  'maximum_head_width_mm', 'maximum_head_width_mm')


class DisposalObservationSerializer(ds.DynamicModelSerializer):
    """DisposalObservation serializer."""

    encounter = serializers.StringRelatedField()

    class Meta:
        """Class options."""

        model = DisposalObservation
        fields = ('encounter', 'management_actions', 'comments',)


class FlipperTagObservationSerializer(ds.DynamicModelSerializer):
    """FlipperTagObservation serializer."""

    encounter = serializers.StringRelatedField()

    class Meta:
        """Class options."""

        model = FlipperTagObservation
        fields = ('encounter', 'name', 'side', 'position', 'status', 'comments')


class EncounterSerializer(ds.DynamicModelSerializer):
    # serializers.HyperlinkedModelSerializer):
    """Encounter serializer."""

    # observation_set = serializers.HyperlinkedRelatedField(
    #     many=True, view_name='observation-detail', read_only=True)
    # observation_set = serializers.StringRelatedField(many=True, read_only=True)
    observation_set = ds.DynamicRelationField('ObservationSerializer', embed=True, many=True)
    # who = serializers.StringRelatedField(read_only=True)
    who = ds.DynamicRelationField('UserSerializer', embed=True)

    class Meta:
        """Class options."""

        model = Encounter
        name = 'encounter'
        fields = ('where', 'when', 'who', 'observation_set',)
        geo_field = "where"

    def create(self, validated_data):
        """Make EncounterSerializer writeable."""
        obs_data = validated_data.pop('observations')
        encounter = Encounter.objects.create(**validated_data)
        for obs in obs_data:
            Observation.objects.create(encounter=encounter, **obs)
        return encounter


class AnimalEncounterSerializer(EncounterSerializer):
    """AnimalEncounter serializer."""

    class Meta:
        """Class options."""

        model = AnimalEncounter
        fields = ('where', 'when', 'who',
                  'species', 'health', 'sex', 'behaviour',
                  'observation_set',)


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    """User view set."""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class EncounterViewSet(viewsets.ModelViewSet):
    """Encounter view set."""

    queryset = Encounter.objects.all()
    serializer_class = EncounterSerializer


class AnimalEncounterViewSet(viewsets.ModelViewSet):
    """AnimalEncounter view set."""

    queryset = AnimalEncounter.objects.all()
    serializer_class = AnimalEncounterSerializer


class ObservationViewSet(viewsets.ModelViewSet):
    """Observation view set."""

    queryset = Observation.objects.all()
    serializer_class = ObservationSerializer


class MediaAttachmentViewSet(viewsets.ModelViewSet):
    """MediaAttachment view set."""

    queryset = MediaAttachment.objects.all()
    serializer_class = MediaAttachmentSerializer


class FlipperTagObservationViewSet(viewsets.ModelViewSet):
    """TagObservation view set."""

    queryset = FlipperTagObservation.objects.all()
    serializer_class = FlipperTagObservationSerializer
