from rest_framework import routers, serializers, viewsets

from wastd.observations.models import (
    Encounter, AnimalEncounter, MediaAttachment, Observation,
    FlipperTagObservation, DisposalObservation, TurtleMorphometricObservation,
    DistinguishingFeatureObservation)
from wastd.users.models import User


# Serializers ----------------------------------------------------------------#
class UserSerializer(serializers.HyperlinkedModelSerializer):
    """User serializer."""

    class Meta:
        """Class options."""

        model = User
        fields = ('username', 'name', 'email', 'first_name', 'last_name')


class ObservationSerializer(serializers.HyperlinkedModelSerializer):
    """Observation serializer."""

    encounter = serializers.HyperlinkedRelatedField(
        source='encounter.pk', view_name='encounter-detail', read_only=True)

    class Meta:
        """Class options."""

        model = Observation
        fields = ('encounter', )

    def to_representation(self, obj):
        """
        Because GalleryItem is Polymorphic
        """
        if isinstance(obj, FlipperTagObservation):
            return FlipperTagObservationSerializer(obj, context=self.context).to_native(obj)

        return super(ObservationSerializer, self).to_representation(obj)


class MediaAttachmentSerializer(ObservationSerializer):
    """MediaAttachment serializer."""

    class Meta:
        """Class options."""

        model = MediaAttachment
        fields = ('encounter', 'media_type', 'title', 'attachment')


class DistinguishingFeatureObservationSerializer(ObservationSerializer):
    """DistinguishingFeatureObservation serializer."""

    class Meta:
        """Class options."""

        model = DistinguishingFeatureObservation
        fields = ('encounter', 'damage_injury', 'missing_limbs', 'barnacles',
                  'algal_growth', 'tagging_scars', 'propeller_damage',
                  'entanglement', 'see_photo', 'comments')


class TurtleMorphometricObservationSerializer(ObservationSerializer):
    """TurtleMorphometricObservation serializer."""

    class Meta:
        """Class options."""

        model = TurtleMorphometricObservation
        fields = ('encounter',
                  'curved_carapace_length_mm', 'curved_carapace_length_accuracy',
                  'curved_carapace_notch_mm', 'curved_carapace_notch_accuracy',
                  'curved_carapace_width_mm', 'curved_carapace_width_accuracy',
                  'tail_length_mm', 'tail_length_accuracy',
                  'maximum_head_width_mm', 'maximum_head_width_mm')


class DisposalObservationSerializer(ObservationSerializer):
    """DisposalObservation serializer."""

    class Meta:
        """Class options."""

        model = DisposalObservation
        fields = ('encounter', 'management_actions', 'comments',)


class FlipperTagObservationSerializer(ObservationSerializer):
    """FlipperTagObservation serializer."""

    class Meta:
        """Class options."""

        model = FlipperTagObservation
        fields = ('encounter', 'type', 'status', 'name', 'comments')


class EncounterSerializer(serializers.HyperlinkedModelSerializer):
    """Encounter serializer."""

    observation_set = serializers.HyperlinkedRelatedField(
        many=True, view_name='observation-detail', read_only=True)

    class Meta:
        """Class options."""

        model = Encounter
        fields = ('where', 'when', 'who', 'observation_set',)
        geo_field = "where"


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
    serializer_class = FlipperTagObservation
