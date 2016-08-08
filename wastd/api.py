from rest_framework import serializers, viewsets
from dynamic_rest import serializers as ds, viewsets as dv

from wastd.observations.models import (
    Encounter, AnimalEncounter, Observation, MediaAttachment, TagObservation,
    DisposalObservation, TurtleMorphometricObservation,
    DistinguishingFeatureObservation)
from wastd.users.models import User


# Serializers ----------------------------------------------------------------#
class UserSerializer(serializers.ModelSerializer):
    """User serializer."""

    class Meta:
        """Class options."""

        model = User
        fields = ('username', 'name', 'email', 'first_name', 'last_name')


class ObservationSerializer(serializers.ModelSerializer):
    """Observation serializer."""

    # encounter = serializers.StringRelatedField()
    # encounter = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        """Class options."""

        model = Observation
        fields = ('observation_name', )

    def to_representation(self, obj):
        """Resolve Observation to child class."""
        if isinstance(obj, DistinguishingFeatureObservation):
            return DistinguishingFeatureObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, TurtleMorphometricObservation):
            return TurtleMorphometricObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, DisposalObservation):
            return DisposalObservationSerializer(
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
                  'tag_type', 'name', 'side',
                  'position', 'status', 'comments')


class DistinguishingFeatureObservationSerializer(serializers.ModelSerializer):
    """DistinguishingFeatureObservation serializer."""

    class Meta:
        """Class options."""

        model = DistinguishingFeatureObservation
        fields = ('observation_name',
                  'damage_injury', 'missing_limbs', 'barnacles',
                  'algal_growth', 'tagging_scars', 'propeller_damage',
                  'entanglement', 'see_photo', 'comments')


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


class DisposalObservationSerializer(serializers.ModelSerializer):
    """DisposalObservation serializer."""

    class Meta:
        """Class options."""

        model = DisposalObservation
        fields = ('observation_name',
                  'management_actions', 'comments',)


class EncounterSerializer(serializers.ModelSerializer):
    """Encounter serializer."""

    observation_set = ObservationSerializer(many=True, read_only=False)
    who = serializers.StringRelatedField(read_only=True)

    class Meta:
        """Class options."""

        model = Encounter
        name = 'encounter'
        fields = ('where', 'when', 'who', 'observation_set', )
        geo_field = "where"

    def create(self, validated_data):
        """Make EncounterSerializer writeable.

        The actual child model is looked up by "observation_name".
        """
        obs_data = validated_data.pop('observation_set')
        encounter = Encounter.objects.create(**validated_data)
        for obs in obs_data:
            childmodel_name = obs.pop("observation_name")
            childmodel = getattr(Observation, childmodel_name).related.related_model
            childmodel.objects.create(encounter=encounter, **obs)
        return encounter


class AnimalEncounterSerializer(EncounterSerializer):
    """AnimalEncounter serializer."""

    class Meta:
        """Class options."""

        model = AnimalEncounter
        fields = ('where', 'when', 'who',
                  'species', 'health', 'sex', 'behaviour', 'observation_set', )


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


class TagObservationViewSet(viewsets.ModelViewSet):
    """TagObservation view set."""

    queryset = TagObservation.objects.all()
    serializer_class = TagObservationSerializer
