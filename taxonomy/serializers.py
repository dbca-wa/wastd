from rest_framework.serializers import ModelSerializer
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from taxonomy.models import (
    Community,
    Crossreference,
    HbvFamily,
    HbvGenus,
    HbvGroup,
    HbvName,
    HbvParent,
    HbvSpecies,
    HbvSupra,
    HbvVernacular,
    HbvXref,
    Taxon,
    Vernacular,
)


class HbvNameSerializer(ModelSerializer):

    class Meta:
        model = HbvName
        fields = "__all__"


class HbvSupraSerializer(ModelSerializer):

    class Meta:
        model = HbvSupra
        fields = "__all__"


class HbvGroupSerializer(ModelSerializer):

    class Meta:
        model = HbvGroup
        fields = "__all__"


class HbvFamilySerializer(ModelSerializer):

    class Meta:
        model = HbvFamily
        fields = "__all__"


class HbvGenusSerializer(ModelSerializer):

    class Meta:
        model = HbvGenus
        fields = "__all__"


class HbvSpeciesSerializer(ModelSerializer):

    class Meta:
        model = HbvSpecies
        fields = "__all__"


class HbvVernacularSerializer(ModelSerializer):

    class Meta:
        model = HbvVernacular
        fields = "__all__"


class HbvXrefSerializer(ModelSerializer):

    class Meta:
        model = HbvXref
        fields = "__all__"


class HbvParentSerializer(ModelSerializer):

    class Meta:
        model = HbvParent
        fields = "__all__"


class TaxonSerializer(ModelSerializer):
    """Serializer for Taxon.

    Includes a summary of conservation status which is ingested into WACensus.

    Example:

    NAME_ID | CONSV_CODE    | LIST_CODE | EPBC  | WA_IUCN   | IUCN_CRITERIA
    228     | 3             | Priority  |       |           |
    297     | T             | WCA_1991  | EN    | VU        | D1+2
    436     | T             | WCA_1991  | EN    | EN        | B1+2c
    """

    class Meta:
        model = Taxon
        fields = (
            "pk",
            "name_id",
            "name",
            "rank",
            "parent",
            "author",
            "current",
            "publication_status",
            "vernacular_name",
            "vernacular_names",
            "canonical_name",
            "taxonomic_name",
            "paraphyletic_groups"
        )


class FastTaxonSerializer(ModelSerializer):
    """Minimal serializer for Taxon to be used in other serializers.
    """

    class Meta:
        model = Taxon
        fields = (
            "pk",
            "name_id",
            "canonical_name",
            "taxonomic_name",
            "vernacular_names",
        )


class VernacularSerializer(ModelSerializer):

    taxon = FastTaxonSerializer(many=False)

    class Meta:
        model = Vernacular
        fields = (
            "ogc_fid",
            "taxon",
            "name",
            "language",
            "preferred",
        )


class CrossreferenceSerializer(ModelSerializer):
    predecessor = FastTaxonSerializer(many=False)
    successor = FastTaxonSerializer(many=False)

    class Meta:
        model = Crossreference
        fields = (
            "xref_id",
            "predecessor",
            "successor",
            "reason",
            "authorised_by",
            "authorised_on",
            "effective_to",
            "comments",
        )


class CommunitySerializer(GeoFeatureModelSerializer):

    class Meta:
        model = Community
        geo_field = "eoo"
        fields = ["code", "name", "description", "eoo"]
