from django.apps import apps
from rest_framework.serializers import SlugRelatedField, ModelSerializer, ValidationError
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_polymorphic.serializers import PolymorphicSerializer

from taxonomy.models import Community, Taxon
from occurrence.models import (
    AreaEncounter,
    TaxonAreaEncounter,
    CommunityAreaEncounter,
    Landform,
    RockType,
    SoilType,
    SoilColour,
    Drainage,
    SurveyMethod,
    SoilCondition,
    CountAccuracy,
    CountMethod,
    CountSubject,
    PlantCondition,
    DetectionMethod,
    Confidence,
    ReproductiveMaturity,
    AnimalHealth,
    AnimalSex,
    CauseOfDeath,
    SecondarySigns,
    SampleType,
    SampleDestination,
    PermitType,
    ObservationGroup,
    FireHistory,
    FileAttachment,
    PlantCount,
    AssociatedSpecies,
    VegetationClassification,
    HabitatComposition,
    HabitatCondition,
    AreaAssessment,
    PhysicalSample,
    AnimalObservation,
)


class OccurrenceAreaEncounterPolySerializer(GeoFeatureModelSerializer):
    """Serializer for Occurrence AreaEncounter.
    """
    class Meta:
        model = AreaEncounter
        fields = (
            "id", "code", "label", "name", "description", "as_html", "source", "source_id", "status",
            "encountered_on", "encountered_by", "area_type", "accuracy", "northern_extent",
        )
        geo_field = "geom"


class OccurrenceAreaEncounterPointSerializer(GeoFeatureModelSerializer):
    """Serializer for Occurrence Area.
    """
    class Meta:
        model = AreaEncounter
        fields = (
            "id", "code", "label", "name", "description", "as_html", "source", "source_id", "status",
            "encountered_on", "encountered_by", "area_type", "accuracy", "northern_extent",
        )
        geo_field = "point"


class OccurrenceTaxonAreaEncounterPolyInlineSerializer(GeoFeatureModelSerializer):
    """Serializer for Occurrence TaxonAreaEncounter to be used inline in TaxonSerializer.
    """
    class Meta:
        exclude = ("taxon", )
        model = TaxonAreaEncounter
        id_field = "id"
        geo_field = "geom"


class OccurrenceTaxonAreaEncounterPolySerializer(GeoFeatureModelSerializer):
    """Serializer for Occurrence TaxonAreaEncounter.
    """
    taxon = SlugRelatedField(
        queryset=Taxon.objects.all(), slug_field="name_id")

    class Meta:
        model = TaxonAreaEncounter
        fields = (
            "taxon",
            "id",
            "code",
            "label",
            "name",
            "description",
            "as_html",
            "source",
            "source_id",
            "status",
            "encounter_type",
            "encountered_on",
            "encountered_by",
            "area_type",
            "geolocation_capture_method",
            "accuracy",
            "northern_extent",
            "point"
        )
        id_field = "id"
        geo_field = "geom"


class OccurrenceTaxonAreaEncounterPointSerializer(OccurrenceTaxonAreaEncounterPolySerializer):
    """Serializer for Occurrence TaxonAreaEncounter.
    """
    class Meta(OccurrenceTaxonAreaEncounterPolySerializer.Meta):
        geo_field = "point"


class OccurrenceCommunityAreaEncounterPolyInlineSerializer(GeoFeatureModelSerializer):
    """Serializer for Occurrence CommunityAreaEncounter to be used inline in CommunitySerializer.
    """
    class Meta:
        model = CommunityAreaEncounter
        exclude = ("community", )
        id_field = "id"
        geo_field = "geom"


class OccurrenceCommunityAreaEncounterPolySerializer(GeoFeatureModelSerializer):

    community = SlugRelatedField(
        queryset=Community.objects.all(), slug_field="code")

    class Meta:
        model = CommunityAreaEncounter
        fields = (
            "community", "id", "code", "label", "name", "description", "as_html", "source", "source_id",
            "status", "encountered_on", "encountered_by", "area_type", "accuracy", "northern_extent",
            "point",
        )
        id_field = "id"
        geo_field = "geom"


class OccurrenceCommunityAreaEncounterPointSerializer(OccurrenceCommunityAreaEncounterPolySerializer):
    community = SlugRelatedField(
        queryset=Community.objects.all(), slug_field="code")

    class Meta(OccurrenceCommunityAreaEncounterPolySerializer.Meta):
        geo_field = "point"


class LandformSerializer(ModelSerializer):

    class Meta:
        model = Landform
        fields = "__all__"


class RockTypeSerializer(ModelSerializer):

    class Meta:
        model = RockType
        fields = "__all__"


class SoilTypeSerializer(ModelSerializer):

    class Meta:
        model = SoilType
        fields = "__all__"


class SoilColourSerializer(ModelSerializer):

    class Meta:
        model = SoilColour
        fields = "__all__"


class DrainageSerializer(ModelSerializer):

    class Meta:
        model = Drainage
        fields = "__all__"


class SurveyMethodSerializer(ModelSerializer):

    class Meta:
        model = SurveyMethod
        fields = "__all__"


class SoilConditionSerializer(ModelSerializer):

    class Meta:
        model = SoilCondition
        fields = "__all__"


class CountAccuracySerializer(ModelSerializer):

    class Meta:
        model = CountAccuracy
        fields = "__all__"


class CountMethodSerializer(ModelSerializer):

    class Meta:
        model = CountMethod
        fields = "__all__"


class CountSubjectSerializer(ModelSerializer):

    class Meta:
        model = CountSubject
        fields = "__all__"


class PlantConditionSerializer(ModelSerializer):

    class Meta:
        model = PlantCondition
        fields = "__all__"


class DetectionMethodSerializer(ModelSerializer):

    class Meta:
        model = DetectionMethod
        fields = "__all__"


class ConfidenceSerializer(ModelSerializer):

    class Meta:
        model = Confidence
        fields = "__all__"


class ReproductiveMaturitySerializer(ModelSerializer):

    class Meta:
        model = ReproductiveMaturity
        fields = "__all__"


class AnimalHealthSerializer(ModelSerializer):

    class Meta:
        model = AnimalHealth
        fields = "__all__"


class AnimalSexSerializer(ModelSerializer):

    class Meta:
        model = AnimalSex
        fields = "__all__"


class CauseOfDeathSerializer(ModelSerializer):

    class Meta:
        model = CauseOfDeath
        fields = "__all__"


class SecondarySignsSerializer(ModelSerializer):

    class Meta:
        model = SecondarySigns
        fields = "__all__"


class SampleTypeSerializer(ModelSerializer):

    class Meta:
        model = SampleType
        fields = "__all__"


class SampleDestinationSerializer(ModelSerializer):

    class Meta:
        model = SampleDestination
        fields = "__all__"


class PermitTypeSerializer(ModelSerializer):

    class Meta:
        model = PermitType
        fields = "__all__"


class ObservationGroupSerializer(ModelSerializer):
    """The ObservationGroup serializer resolves its polymorphic subclasses.

    ObservationGroups have polymorphic subclasses.
    A plain DRF serializer would simply return the shared ObservationGroup
    fields, but not the individual fields partial to its subclasses.

    Overriding the `to_representation` method, this serializer tests the
    object to display for its real instance, and calls the `to_representation`
    from the subclasses serializer.

    `Credits <http://stackoverflow.com/a/19976203/2813717>`_
    `Author <http://stackoverflow.com/users/1514427/michael-van-de-waeter>`_
    """

    # as_latex = ReadOnlyField()
    encounter = OccurrenceAreaEncounterPointSerializer(read_only=True)

    class Meta:
        model = ObservationGroup
        fields = "__all__"

    def validate(self, data):
        """Raise ValidateError on missing AreaEncounter(source, source_id).
        """
        if not AreaEncounter.objects.filter(source=int(self.initial_data["source"]), source_id=str(self.initial_data["source_id"])).exists():
            raise ValidationError(
                "AreaEncounter with source {0} and source_id {1}"
                " does not exist, skipping.".format(
                    int(self.initial_data["source"]),
                    str(self.initial_data["source_id"])))
        return data

    def create(self, validated_data):
        """Create one new object, resolve AreaEncounter from source and source_id.
        """
        validated_data["encounter"] = AreaEncounter.objects.get(
            source=int(self.initial_data["source"]),
            source_id=str(self.initial_data["source_id"]))
        return self.Meta.model.objects.create(**validated_data)


class FileAttachmentSerializer(ObservationGroupSerializer):

    class Meta:
        model = FileAttachment
        fields = "__all__"


class HabitatCompositionSerializer(ObservationGroupSerializer):

    class Meta:
        model = HabitatComposition
        fields = "__all__"


class HabitatConditionSerializer(ObservationGroupSerializer):

    class Meta:
        model = HabitatCondition
        fields = "__all__"


class AreaAssessmentSerializer(ObservationGroupSerializer):

    class Meta:
        model = AreaAssessment
        fields = "__all__"


class FireHistorySerializer(ObservationGroupSerializer):

    class Meta:
        model = FireHistory
        fields = "__all__"


class VegetationClassificationSerializer(ObservationGroupSerializer):

    class Meta:
        model = VegetationClassification
        fields = "__all__"


class PlantCountSerializer(ObservationGroupSerializer):

    count_method = SlugRelatedField(
        queryset=CountMethod.objects.all(), slug_field='code', required=False)
    count_accuracy = SlugRelatedField(
        queryset=CountAccuracy.objects.all(), slug_field='code', required=False)

    class Meta:
        model = PlantCount
        fields = "__all__"


class AssociatedSpeciesSerializer(ObservationGroupSerializer):

    class Meta:
        model = AssociatedSpecies
        fields = "__all__"


class AnimalObservationSerializer(ObservationGroupSerializer):

    class Meta:
        model = AnimalObservation
        fields = "__all__"

    def to_internal_value(self, data):
        """Override to_internal_value and check the value of the optional `secondary_signs` key.
        This key value might be present in a couple of different ways, which all need to be handled:
            - /api/path/?secondary_signs=eggs
            - /api/path/?secondary_signs=eggs,fur
            - /api/path/?secondary_signs=eggs&secondary_signs=fur

        We also need to convert comma-separated strings into a list of PKs for the equivalent
        SecondarySign objects, for the purposes of setting M2M relationships.

        References:
            - https://www.django-rest-framework.org/api-guide/serializers/#read-write-baseserializer-classes
            - https://stackoverflow.com/questions/31281938/overriding-django-rest-framework-serializer-is-valid-method
        """
        data_update = dict(data)
        if 'secondary_signs' in data_update:
            # I.e. ['eggs,fur'] instead of ['eggs', 'fur']
            if len(data_update['secondary_signs']) == 1:
                data_update['secondary_signs'] = data_update[
                    'secondary_signs'][0].split(',')
            # Change secondary_signs from a comma-separated list of strings
            # into a list of PKs.
            data_update['secondary_signs'] = [
                SecondarySigns.objects.get(
                    code=i).pk for i in data_update['secondary_signs']]
            return super(AnimalObservationSerializer, self).to_internal_value(data_update)
        return super(AnimalObservationSerializer, self).to_internal_value(data)

    def create(self, validated_data):
        """Create new object, resolve AreaEncounter from source and source_id.
        """
        validated_data["encounter"] = AreaEncounter.objects.get(
            source=int(self.initial_data["source"]),
            source_id=str(self.initial_data["source_id"]))
        # Pop the secondary_signs list out of validated data so that we can use set() after creating the new object
        # because we can't make the M2M link before the object exists.
        # At this point, it should be a list of PKs.
        secondary_signs = validated_data.pop(
            'secondary_signs') if 'secondary_signs' in validated_data else []
        obj = self.Meta.model.objects.create(**validated_data)
        if secondary_signs:
            obj.secondary_signs.add(*secondary_signs)
        return obj


class PhysicalSampleSerializer(ObservationGroupSerializer):
    sample_type = SlugRelatedField(
        queryset=SampleType.objects.all(), slug_field="code", required=False, allow_null=True)
    sample_destination = SlugRelatedField(
        queryset=SampleDestination.objects.all(), slug_field="code", required=False, allow_null=True)
    permit_type = SlugRelatedField(
        queryset=PermitType.objects.all(), slug_field='code', required=False, allow_null=True)

    class Meta:
        model = PhysicalSample
        fields = "__all__"


class ObservationGroupPolymorphicSerializer(PolymorphicSerializer):
    """Polymorphic seralizer for ObservationGroup.

    https://github.com/apirobot/django-rest-polymorphic
    https://django-polymorphic.readthedocs.io/en/stable/third-party.html#django-rest-framework-support
    """
    model_serializer_mapping = {
        ObservationGroup: ObservationGroupSerializer,
        FireHistory: FireHistorySerializer,
        FileAttachment: FileAttachmentSerializer,
        PlantCount: PlantCountSerializer,
        AssociatedSpecies: AssociatedSpeciesSerializer,
        VegetationClassification: VegetationClassificationSerializer,
        HabitatCondition: HabitatConditionSerializer,
        AreaAssessment: AreaAssessmentSerializer,
        HabitatComposition: HabitatCompositionSerializer,
        PhysicalSample: PhysicalSampleSerializer,
        AnimalObservation: AnimalObservationSerializer
    }
    resource_type_field_name = 'obstype'

    def to_internal_value(self, data):
        """Gate checks for data sanity."""
        return super(ObservationGroupPolymorphicSerializer, self).to_internal_value(data)
