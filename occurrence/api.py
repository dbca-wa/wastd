from django.apps import apps
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.viewsets import ModelViewSet
from rest_framework_filters import FilterSet

from shared.api import BatchUpsertViewSet, MyGeoJsonPagination
from wastd.users.models import User

from taxonomy.models import Community, Taxon
from occurrence import serializers
from occurrence.models import (
    AreaEncounter,
    TaxonAreaEncounter,
    EncounterType,
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
    PhysicalSample,
    AnimalObservation,
    VegetationClassification,
    HabitatComposition,
)


class OccurrenceAreaEncounterFilter(FilterSet):
    """Occurrence AreaEncounter filter.
    """
    class Meta:
        model = AreaEncounter
        fields = {
            "area_type": ["exact", "in"],
            "accuracy": ["exact", "gt", "lt"],
            "code": ["exact", "icontains", "in"],
            "label": ["exact", "icontains", "in"],
            "name": ["exact", "icontains", "in"],
            "description": ["exact", "icontains", "in"],
            "northern_extent": ["exact", "gt", "lt"],
            "source": ["exact", "in"],
            "source_id": ["exact", "in"],
        }


class OccurrenceAreaPolyViewSet(BatchUpsertViewSet):
    """Occurrence Area viewset.
    """
    model = AreaEncounter
    queryset = AreaEncounter.objects.all()
    serializer_class = serializers.OccurrenceAreaEncounterPolySerializer
    filter_class = OccurrenceAreaEncounterFilter
    pagination_class = MyGeoJsonPagination
    uid_fields = ("source", "source_id")


class OccurrenceAreaPointViewSet(OccurrenceAreaPolyViewSet):
    """Occurrence Area Point view set."""
    serializer_class = serializers.OccurrenceAreaEncounterPointSerializer


class OccurrenceTaxonAreaEncounterFilter(FilterSet):
    """Occurrence TaxonAreaEncounter filter.
    """
    class Meta:
        model = TaxonAreaEncounter
        fields = {
            "area_type": ["exact", "in"],
            "accuracy": ["exact", "gt", "lt"],
            "code": ["exact", "icontains", "in"],
            "label": ["exact", "icontains", "in"],
            "name": ["exact", "icontains", "in"],
            "description": ["exact", "icontains", "in"],
            "northern_extent": ["exact", "gt", "lt"],
            "source": ["exact", "in"],
            "source_id": ["exact", "in"],
            "encounter_type": ["exact", "in"],
        }


class OccurrenceTaxonAreaEncounterPolyViewSet(BatchUpsertViewSet):
    """TaxonEncounter polygon view set.
    """
    model = TaxonAreaEncounter
    queryset = TaxonAreaEncounter.objects.all().prefetch_related("taxon")
    serializer_class = serializers.OccurrenceTaxonAreaEncounterPolySerializer
    filter_class = OccurrenceTaxonAreaEncounterFilter
    pagination_class = MyGeoJsonPagination
    uid_fields = ("source", "source_id")

    def resolve_fks(self, data):
        """Resolve FKs from PK to object.
        """
        # Undertake validation for required request params.
        if 'taxon' not in data:
            raise ValidationError('taxon is required')
        elif not Taxon.objects.filter(name_id=data['taxon']).exists():
            raise ValidationError('Unknown taxon {}'.format(data['taxon']))
        data['taxon'] = Taxon.objects.get(name_id=data['taxon'])
        if 'encountered_by' not in data:
            raise ValidationError('encountered_by is required')
        elif not User.objects.filter(pk=data['encountered_by']).exists():
            raise ValidationError('Unknown user {}'.format(data['encountered_by']))
        data["encountered_by"] = User.objects.get(pk=data["encountered_by"])
        if 'encounter_type' not in data:
            raise ValidationError('encounter_type is required')
        elif not EncounterType.objects.filter(pk=data['encounter_type']).exists():
            raise ValidationError('Unknown encounter type {}'.format(data['encounter_type']))
        data["encounter_type"] = EncounterType.objects.get(pk=data["encounter_type"])
        return data


class OccurrenceTaxonAreaEncounterPointViewSet(OccurrenceTaxonAreaEncounterPolyViewSet):
    """TaxonEncounter point view set.
    """
    serializer_class = serializers.OccurrenceTaxonAreaEncounterPointSerializer


class OccurrenceCommunityAreaEncounterFilter(FilterSet):
    """Occurrence CommunityAreaEncounter filter.
    """
    class Meta:
        model = CommunityAreaEncounter
        fields = {
            "area_type": ["exact", "in"],
            "accuracy": ["exact", "gt", "lt"],
            "code": ["exact", "icontains", "in"],
            "label": ["exact", "icontains", "in"],
            "name": ["exact", "icontains", "in"],
            "description": ["exact", "icontains", "in"],
            "northern_extent": ["exact", "gt", "lt"],
            "source": ["exact", "in"],
            "source_id": ["exact", "in"],
        }


class OccurrenceCommunityAreaEncounterPolyViewSet(BatchUpsertViewSet):
    """Occurrence CommunityAreaEncounter view set.
    """
    model = CommunityAreaEncounter
    queryset = CommunityAreaEncounter.objects.all().prefetch_related("community")
    serializer_class = serializers.OccurrenceCommunityAreaEncounterPolySerializer
    filter_class = OccurrenceCommunityAreaEncounterFilter
    pagination_class = MyGeoJsonPagination
    uid_fields = ("source", "source_id")

    def resolve_fks(self, data):
        """Resolve FKs from PK to object."""
        # Undertake validation for required request params.
        if 'community' not in data:
            raise ValidationError('community is required')
        elif not Community.objects.filter(code=data["community"]).exists():
            raise ValidationError('Unknown community {}'.format(data['community']))
        data['community'] = Community.objects.get(code=data["community"])
        if 'encountered_by' not in data:
            raise ValidationError('encountered_by is required')
        elif not User.objects.filter(pk=data['encountered_by']).exists():
            raise ValidationError('Unknown user {}'.format(data['encountered_by']))
        data["encountered_by"] = User.objects.get(pk=data["encountered_by"])
        if 'encounter_type' not in data:
            raise ValidationError('encounter_type is required')
        elif not EncounterType.objects.filter(pk=data['encounter_type']).exists():
            raise ValidationError('Unknown encounter type {}'.format(data['encounter_type']))
        data["encounter_type"] = EncounterType.objects.get(pk=data["encounter_type"])
        return data


class OccurrenceCommunityAreaEncounterPointViewSet(OccurrenceCommunityAreaEncounterPolyViewSet):
    """Occurrence CommunityAreaEncounter view set."""

    serializer_class = serializers.OccurrenceCommunityAreaEncounterPointSerializer


class LandformViewSet(BatchUpsertViewSet):
    """View set for Landform.
    """
    model = Landform
    queryset = Landform.objects.all()
    serializer_class = serializers.LandformSerializer
    uid_fields = ("pk",)


class RockTypeViewSet(BatchUpsertViewSet):
    """View set for RockType."""

    queryset = RockType.objects.all()
    serializer_class = serializers.RockTypeSerializer
    uid_fields = ("pk",)
    model = RockType


class SoilTypeViewSet(BatchUpsertViewSet):
    """View set for SoilType."""

    queryset = SoilType.objects.all()
    serializer_class = serializers.SoilTypeSerializer
    uid_fields = ("pk",)
    model = SoilType


class SoilColourViewSet(BatchUpsertViewSet):
    """View set for SoilColour."""

    queryset = SoilColour.objects.all()
    serializer_class = serializers.SoilColourSerializer
    uid_fields = ("pk",)
    model = SoilColour


class DrainageViewSet(BatchUpsertViewSet):
    """View set for Drainage."""

    queryset = Drainage.objects.all()
    serializer_class = serializers.DrainageSerializer
    uid_fields = ("pk",)
    model = Drainage


class SurveyMethodViewSet(BatchUpsertViewSet):
    """View set for SurveyMethod."""

    queryset = SurveyMethod.objects.all()
    serializer_class = serializers.SurveyMethodSerializer
    uid_fields = ("pk",)
    model = SurveyMethod


class SoilConditionViewSet(BatchUpsertViewSet):
    """View set for SoilCondition."""

    queryset = SoilCondition.objects.all()
    serializer_class = serializers.SoilConditionSerializer
    uid_fields = ("pk",)
    model = SoilCondition


class CountAccuracyViewSet(BatchUpsertViewSet):
    """View set for CountAccuracy."""

    queryset = CountAccuracy.objects.all()
    serializer_class = serializers.CountAccuracySerializer
    uid_fields = ("pk",)
    model = CountAccuracy


class CountMethodViewSet(BatchUpsertViewSet):
    """View set for CountMethod."""

    queryset = CountMethod.objects.all()
    serializer_class = serializers.CountMethodSerializer
    uid_fields = ("pk",)
    model = CountMethod


class CountSubjectViewSet(BatchUpsertViewSet):
    """View set for CountSubject."""

    queryset = CountSubject.objects.all()
    serializer_class = serializers.CountSubjectSerializer
    uid_fields = ("pk",)
    model = CountSubject


class PlantConditionViewSet(BatchUpsertViewSet):
    """View set for PlantCondition."""

    queryset = PlantCondition.objects.all()
    serializer_class = serializers.PlantConditionSerializer
    uid_fields = ("pk",)
    model = PlantCondition


class DetectionMethodViewSet(BatchUpsertViewSet):
    """View set for DetectionMethod."""

    queryset = DetectionMethod.objects.all()
    serializer_class = serializers.DetectionMethodSerializer
    uid_fields = ("pk",)
    model = DetectionMethod


class ConfidenceViewSet(BatchUpsertViewSet):
    """View set for Confidence."""

    queryset = Confidence.objects.all()
    serializer_class = serializers.ConfidenceSerializer
    uid_fields = ("pk",)
    model = Confidence


class ReproductiveMaturityViewSet(BatchUpsertViewSet):
    """View set for ReproductiveMaturity."""

    queryset = ReproductiveMaturity.objects.all()
    serializer_class = serializers.ReproductiveMaturitySerializer
    uid_fields = ("pk",)
    model = ReproductiveMaturity


class AnimalHealthViewSet(BatchUpsertViewSet):
    """View set for Drainage."""

    queryset = AnimalHealth.objects.all()
    serializer_class = serializers.AnimalHealthSerializer
    uid_fields = ("pk",)
    model = AnimalHealth


class AnimalSexViewSet(BatchUpsertViewSet):
    """View set for Drainage."""

    queryset = AnimalSex.objects.all()
    serializer_class = serializers.AnimalSexSerializer
    uid_fields = ("pk",)
    model = AnimalSex


class CauseOfDeathViewSet(BatchUpsertViewSet):
    """View set for CauseOfDeath."""

    queryset = CauseOfDeath.objects.all()
    serializer_class = serializers.CauseOfDeathSerializer
    uid_fields = ("pk",)
    model = CauseOfDeath


class SecondarySignsViewSet(BatchUpsertViewSet):
    """View set for SecondarySigns."""

    queryset = SecondarySigns.objects.all()
    serializer_class = serializers.SecondarySignsSerializer
    uid_fields = ("pk",)
    model = SecondarySigns


class SampleTypeViewSet(BatchUpsertViewSet):
    """View set for SampleType."""

    queryset = SampleType.objects.all()
    serializer_class = serializers.SampleTypeSerializer
    uid_fields = ("pk",)
    model = SampleType


class SampleDestinationViewSet(BatchUpsertViewSet):
    """View set for SampleDestination."""

    queryset = SampleDestination.objects.all()
    serializer_class = serializers.SampleDestinationSerializer
    uid_fields = ("pk",)
    model = SampleDestination


class PermitTypeViewSet(BatchUpsertViewSet):
    """View set for PermitType."""

    queryset = PermitType.objects.all()
    serializer_class = serializers.PermitTypeSerializer
    uid_fields = ("pk",)
    model = PermitType


class ObservationGroupViewSet(ModelViewSet):
    """ObservationGroup models.

    Filter the Observations to a specific type with the parameter `obstype`:

    * [FileAttachment](/api/1/occ-observation/?obstype=FileAttachment)
    * [AreaAssessment](/api/1/occ-observation/?obstype=AreaAssessment)
    * [HabitatComposition](/api/1/occ-observation/?obstype=HabitatComposition)
    * [HabitatCondition](/api/1/occ-observation/?obstype=HabitatCondition)
    * [VegetationClassification](/api/1/occ-observation/?obstype=VegetationClassification)
    * [FireHistory](/api/1/occ-observation/?obstype=FireHistory)
    * [PlantCount](/api/1/occ-observation/?obstype=PlantCount)
    * [AssociatedSpecies](/api/1/occ-observation/?obstype=AssociatedSpecies)
    * [PhysicalSample](/api/1/occ-observation/?obstype=PhysicalSample)
    * [AnimalObservation](/api/1/occ-observation/?obstype=AnimalObservation)
    """
    serializer_class = serializers.ObservationGroupPolymorphicSerializer

    class Meta:
        model = ObservationGroup

    def get_queryset(self):
        """Filter queryset to the model specified by request parameter "obstype"."""
        model_name = self.request.query_params.get('obstype', None)
        if model_name is not None:
            return apps.get_model("occurrence", model_name).objects.all()
        else:
            return ObservationGroup.objects.all()

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """A custom method to serve as an extra action of this viewset to bulk-create objects.
        Expects a JSON payload of a list of dicts, each being a valid object.
        In order to be as fast as possible, the save method is bespoke for each different model type.
        Unfortunately, we can't call bulk_create so this still needs to save each object individually.
        TODO: this method could probably be refactored to be more general in nature.
        """
        model_name = self.request.query_params.get('obstype', None)
        if model_name is not None:
            model_type = apps.get_model('occurrence', model_name)
        else:
            model_type = ObservationGroup
        created_count = 0
        errors = []
        encounter_cache = {}
        sampletype_cache = {}
        sampledest_cache = {}
        permittype_cache = {}
        detectmethod_cache = {}
        confidence_cache = {}
        maturity_cache = {}
        sex_cache = {}
        health_cache = {}
        causedeath_cache = {}
        secsigns_cache = {}
        landform_cache = {}
        rocktype_cache = {}
        soiltype_cache = {}
        soilcolour_cache = {}
        drainage_cache = {}

        if model_type == PhysicalSample:
            for obj in request.data:
                source = obj['source']
                source_id = obj['source_id']
                # Do some caching to reduce DB queries.
                if '{}|{}'.format(source, source_id) not in encounter_cache:
                    encounter_cache['{}|{}'.format(source, source_id)] = AreaEncounter.objects.get(source=source, source_id=source_id)
                if 'sample_type' in obj and obj['sample_type'] not in sampletype_cache:
                    sampletype_cache[obj['sample_type']] = SampleType.objects.get(code=obj['sample_type'])
                if 'sample_destination' in obj and obj['sample_destination'] not in sampledest_cache:
                    sampledest_cache[obj['sample_destination']] = SampleDestination.objects.get(code=obj['sample_destination'])
                if 'permit_type' in obj and obj['permit_type'] not in permittype_cache:
                    permittype_cache[obj['permit_type']] = PermitType.objects.get(code=obj['permit_type'])
                try:
                    PhysicalSample.objects.create(
                        encounter=encounter_cache['{}|{}'.format(source, source_id)],
                        sample_type=sampletype_cache[obj['sample_type']] if 'sample_type' in obj else None,
                        sample_label=obj['sample_label'] if 'sample_label' in obj else '',
                        collector_id=obj['collector_id'] if 'collector_id' in obj else '',
                        sample_destination=sampledest_cache[obj['sample_destination']] if 'sample_destination' in obj else None,
                        permit_type=permittype_cache[obj['permit_type']] if 'permit_type' in obj else None,
                        permit_id=obj['permit_id'] if 'permit_id' in obj else '',
                    )
                    created_count += 1
                except:
                    errors.append(obj)
        elif model_type == AnimalObservation:
            for obj in request.data:
                source = obj['source']
                source_id = obj['source_id']
                # Do some caching to reduce DB queries.
                if '{}|{}'.format(source, source_id) not in encounter_cache:
                    encounter_cache['{}|{}'.format(source, source_id)] = AreaEncounter.objects.get(source=source, source_id=source_id)
                if 'detection_method' in obj and obj['detection_method'] not in detectmethod_cache:
                    detectmethod_cache[obj['detection_method']] = DetectionMethod.objects.get(code=obj['detection_method'])
                if 'species_id_confidence' in obj and obj['species_id_confidence'] not in confidence_cache:
                    confidence_cache[obj['species_id_confidence']] = Confidence.objects.get(code=obj['species_id_confidence'])
                if 'maturity' in obj and obj['maturity'] not in maturity_cache:
                    maturity_cache[obj['maturity']] = ReproductiveMaturity.objects.get(code=obj['maturity'])
                if 'sex' in obj and obj['sex'] not in sex_cache:
                    sex_cache[obj['sex']] = AnimalSex.objects.get(code=obj['sex'])
                if 'health' in obj and obj['health'] not in health_cache:
                    health_cache[obj['health']] = AnimalHealth.objects.get(code=obj['health'])
                if 'cause_of_death' in obj and obj['cause_of_death'] not in causedeath_cache:
                    causedeath_cache[obj['cause_of_death']] = CauseOfDeath.objects.get(code=obj['cause_of_death'])
                if 'secondary_signs' in obj:
                    for ss in obj['secondary_signs']:
                        if ss not in secsigns_cache:
                            secsigns_cache[ss] = SecondarySigns.objects.get(code=ss)
                try:
                    ae = AnimalObservation.objects.create(
                        encounter=encounter_cache['{}|{}'.format(source, source_id)],
                        detection_method=detectmethod_cache[obj['detection_method']] if 'detection_method' in obj else None,
                        species_id_confidence=confidence_cache[obj['species_id_confidence']] if 'species_id_confidence' in obj else None,
                        maturity=maturity_cache[obj['maturity']] if 'maturity' in obj else None,
                        sex=sex_cache[obj['sex']] if 'sex' in obj else None,
                        health=health_cache[obj['health']] if 'health' in obj else None,
                        cause_of_death=causedeath_cache[obj['cause_of_death']] if 'cause_of_death' in obj else None,
                        distinctive_features=obj['distinctive_features'] if 'distinctive_features' in obj else '',
                        actions_taken=obj['actions_taken'] if 'actions_taken' in obj else '',
                        actions_required=obj['actions_required'] if 'actions_required' in obj else '',
                        no_adult_male=obj['no_adult_male'] if 'no_adult_male' in obj else None,
                        no_adult_female=obj['no_adult_female'] if 'no_adult_female' in obj else None,
                        no_adult_unknown=obj['no_adult_unknown'] if 'no_adult_unknown' in obj else None,
                        no_juvenile_male=obj['no_juvenile_male'] if 'no_juvenile_male' in obj else None,
                        no_juvenile_female=obj['no_juvenile_female'] if 'no_juvenile_female' in obj else None,
                        no_juvenile_unknown=obj['no_juvenile_unknown'] if 'no_juvenile_unknown' in obj else None,
                        no_dependent_young_male=obj['no_dependent_young_male'] if 'no_dependent_young_male' in obj else None,
                        no_dependent_young_female=obj['no_dependent_young_female'] if 'no_dependent_young_female' in obj else None,
                        no_dependent_young_unknown=obj['no_dependent_young_unknown'] if 'no_dependent_young_unknown' in obj else None,
                        observation_details=obj['observation_details'] if 'observation_details' in obj else '',
                    )
                    if 'secondary_signs' in obj:
                        for ss in obj['secondary_signs']:
                            ae.secondary_signs.add(secsigns_cache[ss])
                    created_count += 1
                except:
                    errors.append(obj)
        elif model_type == VegetationClassification:
            for obj in request.data:
                source = obj['source']
                source_id = obj['source_id']
                # Do some caching to reduce DB queries.
                if '{}|{}'.format(source, source_id) not in encounter_cache:
                    encounter_cache['{}|{}'.format(source, source_id)] = AreaEncounter.objects.get(source=source, source_id=source_id)
                try:
                    VegetationClassification.objects.create(
                        encounter=encounter_cache['{}|{}'.format(source, source_id)],
                        level1=obj['level1'] if 'level1' in obj else '',
                        level2=obj['level2'] if 'level2' in obj else '',
                        level3=obj['level3'] if 'level3' in obj else '',
                        level4=obj['level4'] if 'level4' in obj else '',
                    )
                    created_count += 1
                except:
                    errors.append(obj)
        elif model_type == HabitatComposition:
            for obj in request.data:
                source = obj['source']
                source_id = obj['source_id']
                # Do some caching to reduce DB queries.
                if '{}|{}'.format(source, source_id) not in encounter_cache:
                    encounter_cache['{}|{}'.format(source, source_id)] = AreaEncounter.objects.get(source=source, source_id=source_id)
                if 'landform' in obj and obj['landform'] not in landform_cache:
                    landform_cache[obj['landform']] = Landform.objects.get(code=obj['landform'])
                if 'rock_type' in obj and obj['rock_type'] not in rocktype_cache:
                    rocktype_cache[obj['rock_type']] = RockType.objects.get(code=obj['rock_type'])
                if 'soil_type' in obj and obj['soil_type'] not in soiltype_cache:
                    soiltype_cache[obj['soil_type']] = SoilType.objects.get(code=obj['soil_type'])
                if 'soil_colour' in obj and obj['soil_colour'] not in soilcolour_cache:
                    soilcolour_cache[obj['soil_colour']] = SoilColour.objects.get(code=obj['soil_colour'])
                if 'drainage' in obj and obj['drainage'] not in drainage_cache:
                    drainage_cache[obj['drainage']] = Drainage.objects.get(code=obj['drainage'])
                try:
                    HabitatComposition.objects.create(
                        encounter=encounter_cache['{}|{}'.format(source, source_id)],
                        landform=landform_cache[obj['landform']] if 'landform' in obj else None,
                        rock_type=rocktype_cache[obj['rock_type']] if 'rock_type' in obj else None,
                        loose_rock_percent=obj['loose_rock_percent'] if 'loose_rock_percent' in obj else None,
                        soil_type=soiltype_cache[obj['soil_type']] if 'soil_type' in obj else None,
                        soil_colour=soilcolour_cache[obj['soil_colour']] if 'soil_colour' in obj else None,
                        drainage=drainage_cache[obj['drainage']] if 'drainage' in obj else None,
                    )
                    created_count += 1
                except:
                    errors.append(obj)

        return Response({'model_name': model_name, 'created_count': created_count, 'errors': errors})
