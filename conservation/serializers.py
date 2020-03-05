from rest_framework.serializers import ModelSerializer, SlugRelatedField
from taxonomy.models import Community

from conservation.models import (
    CommunityConservationListing,
    ConservationCategory,
    ConservationCriterion,
    ConservationList,
    Document,
    TaxonConservationListing,
)
from taxonomy.models import Taxon


class CommunityConservationListingSerializer(ModelSerializer):
    community = SlugRelatedField(
        queryset=Community.objects.all(),
        slug_field="code",
        style={"base_template": "input.html"}
    )

    class Meta:
        model = CommunityConservationListing
        fields = "__all__"


class ConservationCategorySerializer(ModelSerializer):

    class Meta:
        model = ConservationCategory
        fields = "__all__"


class ConservationCriterionSerializer(ModelSerializer):

    class Meta:
        model = ConservationCriterion
        fields = "__all__"


class ConservationListSerializer(ModelSerializer):
    conservationcategory_set = ConservationCategorySerializer(many=True, write_only=False)
    conservationcriterion_set = ConservationCriterionSerializer(many=True, write_only=False)

    def create(self, validated_data):
        """Custom create with nested ConsCat serializer.
        """
        cat_data = validated_data.pop("conservationcategory_set", [])
        crit_data = validated_data.pop("conservationcriterion_set", [])

        conservation_list = ConservationList.objects.update_or_create(
            code=validated_data["code"], defaults=validated_data)

        for cat in cat_data:
            cat["conservation_list_id"] = conservation_list.pk
            ConservationCategory.objects.update_or_create(code=cat["code"], defaults=cat)
        for crit in crit_data:
            crit["conservation_list_id"] = conservation_list.pk
            ConservationCriterion.objects.update_or_create(code=crit["code"], defaults=crit)

        return conservation_list

    class Meta:
        model = ConservationList
        fields = "__all__"


class FastConservationListSerializer(ModelSerializer):
    """Fast serializer for ConservationList.
    """
    class Meta:
        model = ConservationList
        fields = ["id", "code", "label"]


class DocumentSerializer(ModelSerializer):
    """Serializer for Document.

    TODO: File attachments, current/confidential filters.
    """

    class Meta:
        model = Document
        fields = "__all__"


class TaxonConservationListingSerializer(ModelSerializer):
    taxon = SlugRelatedField(
        queryset=Taxon.objects.all(),
        slug_field="name_id",
        style={"base_template": "input.html"}
    )

    class Meta:
        model = TaxonConservationListing
        fields = "__all__"
