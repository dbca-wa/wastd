from django_filters.rest_framework import BooleanFilter
from rest_framework_filters import FilterSet, RelatedFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.routers import DefaultRouter

from shared.api import (
    BatchUpsertViewSet,
    NameIDBatchUpsertViewSet,
    OgcFidBatchUpsertViewSet,
)
from taxonomy.models import (
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
    Crossreference,
    Community,
)
from taxonomy import serializers

router = DefaultRouter()


class HbvNameFilter(FilterSet):
    """HbvName filter."""

    class Meta:
        model = HbvName
        fields = {
            "rank_name": "__all__",
            "is_current": "__all__",
            "naturalised_status": "__all__",
            "naturalised_certainty": "__all__",
            "is_eradicated": "__all__",
            "informal": "__all__",
            "name": "__all__",
            "name_id": "__all__",
            "full_name": "__all__",
            "vernacular": "__all__",
            "all_vernaculars": "__all__",
            "author": "__all__",
            "ogc_fid": "__all__",
            "name_id": "__all__",
            "kingdom_id": "__all__",
            "rank_id": "__all__",
            "rank_name": "__all__",
            "name1": "__all__",
            "name2": "__all__",
            "rank3": "__all__",
            "name3": "__all__",
            "rank4": "__all__",
            "name4": "__all__",
            "pub_id": "__all__",
            "vol_info": "__all__",
            "pub_year": "__all__",
            "is_current": "__all__",
            "origin": "__all__",
            "naturalised_status": "__all__",
            "naturalised_certainty": "__all__",
            "is_eradicated": "__all__",
            "naturalised_comments": "__all__",
            "informal": "__all__",
            "form_desc_yr": "__all__",
            "form_desc_mn": "__all__",
            "form_desc_dy": "__all__",
            "comments": "__all__",
            "added_by": "__all__",
            "added_on": "__all__",
            "updated_by": "__all__",
            "updated_on": "__all__",
            "family_code": "__all__",
            "family_nid": "__all__",
            "name": "__all__",
            "full_name": "__all__",
            "author": "__all__",
            "reference": "__all__",
            "editor": "__all__",
            "vernacular": "__all__",
            "all_vernaculars": "__all__",
            "linear_sequence": "__all__",
            "md5_rowhash": "__all__",
        }


class HbvSupraFilter(FilterSet):
    """HbvSupra filter."""

    class Meta:
        model = HbvSupra
        fields = {
            "ogc_fid": "__all__",
            "supra_code": "__all__",
            "supra_name": "__all__",
            "updated_on": "__all__",
            "md5_rowhash": "__all__",
        }


class HbvGroupFilter(FilterSet):
    """HbvGroup filter."""

    class Meta:
        model = HbvGroup
        fields = {
            "ogc_fid": "__all__",
            "class_id": "__all__",
            "name_id": "__all__",
            "updated_by": "__all__",
            "updated_on": "__all__",
            "rank_name": "__all__",
            "name": "__all__",
            "md5_rowhash": "__all__",
        }


class HbvFamilyFilter(FilterSet):
    """HbvFamily filter."""

    class Meta:
        model = HbvFamily
        fields = {
            "ogc_fid": "__all__",
            "name_id": "__all__",
            "kingdom_id": "__all__",
            "rank_id": "__all__",
            "rank_name": "__all__",
            "family_name": "__all__",
            "is_current": "__all__",
            "informal": "__all__",
            "comments": "__all__",
            "family_code": "__all__",
            "linear_sequence": "__all__",
            "order_nid": "__all__",
            "order_name": "__all__",
            "class_nid": "__all__",
            "class_name": "__all__",
            "division_nid": "__all__",
            "division_name": "__all__",
            "kingdom_name": "__all__",
            "author": "__all__",
            "editor": "__all__",
            "reference": "__all__",
            "supra_code": "__all__",
            "added_on": "__all__",
            "updated_on": "__all__",
            "md5_rowhash": "__all__",
        }


class HbvGenusFilter(FilterSet):
    """HbvGenus filter."""

    class Meta:
        model = HbvGenus
        fields = {
            "ogc_fid": "__all__",
            "name_id": "__all__",
            "kingdom_id": "__all__",
            "rank_id": "__all__",
            "rank_name": "__all__",
            "genus": "__all__",
            "is_current": "__all__",
            "informal": "__all__",
            "comments": "__all__",
            "family_code": "__all__",
            "family_nid": "__all__",
            "author": "__all__",
            "editor": "__all__",
            "reference": "__all__",
            "genusid": "__all__",
            "added_on": "__all__",
            "updated_on": "__all__",
            "md5_rowhash": "__all__",
        }


class HbvSpeciesFilter(FilterSet):
    """HbvSpecies filter."""

    class Meta:
        model = HbvSpecies
        fields = {
            "ogc_fid": "__all__",
            "name_id": "__all__",
            "kingdom_id": "__all__",
            "rank_id": "__all__",
            "rank_name": "__all__",
            "family_code": "__all__",
            "family_nid": "__all__",
            "genus": "__all__",
            "species": "__all__",
            "infra_rank": "__all__",
            "infra_name": "__all__",
            "infra_rank2": "__all__",
            "infra_name2": "__all__",
            "author": "__all__",
            "editor": "__all__",
            "reference": "__all__",
            "comments": "__all__",
            "vernacular": "__all__",
            "all_vernaculars": "__all__",
            "species_name": "__all__",
            "species_code": "__all__",
            "is_current": "__all__",
            "naturalised": "__all__",
            "naturalised_status": "__all__",
            "naturalised_certainty": "__all__",
            "is_eradicated": "__all__",
            "naturalised_comments": "__all__",
            "informal": "__all__",
            "added_on": "__all__",
            "updated_on": "__all__",
            "consv_code": "__all__",
            "md5_rowhash": "__all__",
        }


class HbvVernacularFilter(FilterSet):
    """HbvVernacular filter."""

    class Meta:
        model = HbvVernacular
        fields = {
            "ogc_fid": "__all__",
            "name_id": "__all__",
            "name": "__all__",
            "vernacular": "__all__",
            "language": "__all__",
            "lang_pref": "__all__",
            "preferred": "__all__",
            "source": "__all__",
            "updated_by": "__all__",
            "updated_on": "__all__",
            "md5_rowhash": "__all__",
        }


class HbvXrefFilter(FilterSet):
    """HbvXref filter."""

    class Meta:
        model = HbvXref
        fields = {
            "ogc_fid": "__all__",
            "xref_id": "__all__",
            "old_name_id": "__all__",
            "new_name_id": "__all__",
            "xref_type": "__all__",
            "active": "__all__",
            "authorised_by": "__all__",
            "authorised_on": "__all__",
            "comments": "__all__",
            "added_on": "__all__",
            "updated_on": "__all__",
            "md5_rowhash": "__all__",
        }


class HbvParentFilter(FilterSet):
    """HbvParent filter."""

    class Meta:
        model = HbvParent
        fields = {
            "ogc_fid": "__all__",
            "name_id": "__all__",
            "class_id": "__all__",
            "parent_nid": "__all__",
            "updated_by": "__all__",
            "updated_on": "__all__",
            "md5_rowhash": "__all__",
        }


class HbvNameViewSet(NameIDBatchUpsertViewSet):
    """View set for HbvName.

    # Custom features
    POST a GeoJSON feature properties dict to create or update the corresponding Taxon.

    # Pagination: LimitOffset
    The results have four top-level keys:

    * `count` Total number of features
    * `next` URL to next batch. `null` in last page.
    * `previous` URL to previous batch. `null` in first page.

    You can subset your own page with GET parameters `limit` and `offset`, e.g.
    [/api/1/taxonomy/?limit=100&offset=100](/api/1/taxonomy/?limit=100&offset=100).

    # Search and filter

    The following fields offer search filters `exact`, `iexact`, `in`, `startswith`,
    `istartswith`, `contains`, `icontains`:

    `rank_name`,  `is_current`, `naturalised_status`, ` naturalised_certainty`,
    `is_eradicated`, `informal`, `name`, `name_id`, `full_name`, `vernacular`, `all_vernaculars`, `author`.

    Learn more about filter usage at
    [django-rest-framework-filters](https://github.com/philipn/django-rest-framework-filters).

    # Search names
    Search `name`, `name_id`, `full_name`, `vernacular`, `all_vernaculars`, `author` as follows:

    * [/api/1/taxonomy/?full_name__icontains=acacia](/api/1/taxonomy/?full_name__icontains=acacia)
      Any taxon with case-insensitive phrase "acacia" in field `full_name`.
    * Substitute `full_name` for any of name, full_name, vernacular, all_vernaculars, author.
    * Substitute icontains for any of `exact`, `iexact`, `in`, `startswith`, `istartswith`, `contains`.

    # Taxonomic rank

    * [/api/1/taxonomy/?rank_name=Kingdom](/api/1/taxonomy/?rank_name=Kingdom)
      Taxa of exact, case-sensitive rank_name "Kingdom".
    * [/api/1/taxonomy/?rank_name__startswith=King](/api/1/taxonomy/?rank_name__startswith=King)
      Taxa of rank_names starting with the exact, case-sensitive phrase "King".
    * Other ranks available: Division, Phylum, Class, Subclass, Order, Family, Subfamily,
      Genus, Species, Subspecies, Variety, Form

    # Current
    Whether the taxon is current or not:

    * [/api/1/taxonomy/?is_current=Y](/api/1/taxonomy/?is_current=Y) Only current names
    * [/api/1/taxonomy/?is_current=N](/api/1/taxonomy/?is_current=N) Only non-current names

    # Name approval status
    Whether the name is a phrase name, manuscript name, or approved:

    * [/api/1/taxonomy/?informal=PN](/api/1/taxonomy/?informal=PN) Phrase Name
    * [/api/1/taxonomy/?informal=MS](/api/1/taxonomy/?informal=MS) Manuscript Name
    * [/api/1/taxonomy/?informal=-](/api/1/taxonomy/?informal=-) Approved Name

    # Naturalised
    Whether the taxon is naturalised in WA:

    * [/api/1/taxonomy/?naturalised_status=A](/api/1/taxonomy/?naturalised_status=A) A
    * [/api/1/taxonomy/?naturalised_status=M](/api/1/taxonomy/?naturalised_status=M) M
    * [/api/1/taxonomy/?naturalised_status=N](/api/1/taxonomy/?naturalised_status=N) N
    * [/api/1/taxonomy/?naturalised_status=-](/api/1/taxonomy/?naturalised_status=-) -

    # Naturalised certainty
    * [/api/1/taxonomy/?naturalised_certainty=N](/api/1/taxonomy/?naturalised_certainty=N) N
    * [/api/1/taxonomy/?naturalised_certainty=Y](/api/1/taxonomy/?naturalised_certainty=Y) Y
    * [/api/1/taxonomy/?naturalised_certainty=-](/api/1/taxonomy/?naturalised_certainty=-) -

    # Eradicated
    * [/api/1/taxonomy/?is_eradicated=Y](/api/1/taxonomy/?is_eradicated=Y) Y
    * [/api/1/taxonomy/?is_eradicated=-](/api/1/taxonomy/?is_eradicated=-) -
    """

    queryset = HbvName.objects.all()
    serializer_class = serializers.HbvNameSerializer
    filterset_class = HbvNameFilter
    model = HbvName
    uid_fields = ("name_id",)


router.register("names", HbvNameViewSet)


class HbvSupraViewSet(BatchUpsertViewSet):
    """View set for HbvSupra. See HBV Names for details and usage examples."""

    queryset = HbvSupra.objects.all()
    serializer_class = serializers.HbvSupraSerializer
    filterset_class = HbvSupraFilter
    model = HbvSupra
    uid_fields = ("supra_code", )

    def fetch_existing_records(self, new_records, model):
        """Fetch pk, (status if QC mixin), and **uid_fields values from a model."""

        qs = model.objects.filter(
            supra_code__in=list(set([x["supra_code"] for x in new_records]))
        )

        # if issubclass(model, QualityControlMixin):
        #     return qs.values("pk", "supra_code", "status")
        # else:
        return qs.values("pk", "supra_code", )


router.register("supra", HbvSupraViewSet)


class HbvGroupViewSet(NameIDBatchUpsertViewSet):
    """View set for HbvGroup.See HBV Names for details and usage examples."""

    queryset = HbvGroup.objects.all()
    serializer_class = serializers.HbvGroupSerializer
    filterset_class = HbvGroupFilter
    model = HbvGroup
    uid_fields = ("name_id",)


router.register("groups", HbvGroupViewSet)


class HbvFamilyViewSet(NameIDBatchUpsertViewSet):
    """View set for HbvFamily. See HBV Names for details and usage examples."""

    queryset = HbvFamily.objects.all()
    serializer_class = serializers.HbvFamilySerializer
    filterset_class = HbvFamilyFilter
    model = HbvFamily
    uid_fields = ("name_id",)


router.register("families", HbvFamilyViewSet)


class HbvGenusViewSet(NameIDBatchUpsertViewSet):
    """View set for HbvGenus. See HBV Names for details and usage examples."""

    queryset = HbvGenus.objects.all()
    serializer_class = serializers.HbvGenusSerializer
    filterset_class = HbvGenusFilter
    model = HbvGenus
    uid_fields = ("name_id",)


router.register("genera", HbvGenusViewSet)


class HbvSpeciesViewSet(NameIDBatchUpsertViewSet):
    """View set for HbvSpecies. See HBV Names for details and usage examples."""

    queryset = HbvSpecies.objects.all()
    serializer_class = serializers.HbvSpeciesSerializer
    filterset_class = HbvSpeciesFilter
    model = HbvSpecies
    uid_fields = ("name_id",)


router.register("species", HbvSpeciesViewSet)


class HbvVernacularViewSet(OgcFidBatchUpsertViewSet):
    """View set for HbvVernacular. See HBV Names for details and usage examples."""

    queryset = HbvVernacular.objects.all()
    serializer_class = serializers.HbvVernacularSerializer
    filterset_class = HbvVernacularFilter
    model = HbvVernacular
    uid_fields = ("ogc_fid", )


router.register("vernaculars", HbvVernacularViewSet)


class HbvXrefViewSet(BatchUpsertViewSet):
    """View set for HbvXref. See HBV Names for details and usage examples."""

    queryset = HbvXref.objects.all()
    serializer_class = serializers.HbvXrefSerializer
    filterset_class = HbvXrefFilter
    model = HbvXref
    uid_fields = ("xref_id",)

    def fetch_existing_records(self, new_records, model):
        """Fetch pk, (status if QC mixin), and **uid_fields values from a model."""
        return model.objects.filter(
            xref_id__in=list(set([x["xref_id"] for x in new_records]))
        ).values("pk", "xref_id")


router.register("xrefs", HbvXrefViewSet)


class HbvParentViewSet(OgcFidBatchUpsertViewSet):
    """View set for HbvParent. See HBV Names for details and usage examples."""

    queryset = HbvParent.objects.all()
    serializer_class = serializers.HbvParentSerializer
    filterset_class = HbvParentFilter
    model = HbvParent
    uid_fields = ("ogc_fid", )


router.register("parents", HbvParentViewSet)


class TaxonFilter(FilterSet):
    """Taxon filter."""

    current = BooleanFilter(field_name="current")

    class Meta:
        """Class opts."""

        model = Taxon
        fields = {
            "name_id": ["exact", ],
            "name": ["icontains", ],
            "rank": ["icontains", "in", "gt", "gte", "lt", "lte"],
            # "parent": ["exact", ],  # performance bomb
            "publication_status": ["isnull", ],
            # current: provided through field
            "author": ["icontains", ],
            "canonical_name": ["icontains", ],
            "taxonomic_name": ["icontains", ],
            "paraphyletic_groups": ["exact", ],
            # "vernacular_name": ["icontains", ],
            "vernacular_names": ["icontains", ],
            # "eoo" requires polygon filter,

        }


class TaxonViewSet(NameIDBatchUpsertViewSet):
    """View set for Taxon.

    Examples:

    * [Animals](/api/1/taxon/?paraphyletic_groups=20)
    * [Plants sensu latu](/api/1/taxon/?paraphyletic_groups=21)
    * [Only current taxa](/api/1/taxon/?current=true)
    * [Only non-current taxa](/api/1/taxon/?current=false)
    * [Vernacular names contains "woylie" (case insensitive)](/api/1/taxon/?vernacular_names__icontains=woylie) - same works with name, author, can/tax name
    * [NameID exact match](/api/1/taxon/?name_id=25452)
    * [Taxonomic rank Species or lower](/api/1/taxon/?rank__gt=190) - see [Ranks](https://github.com/dbca-wa/wastd/blob/master/taxonomy/models.py#L1613)
    """

    queryset = Taxon.objects.prefetch_related(
        # "paraphyletic_groups",
        # Prefetch("conservation_listings",
        #     queryset=TaxonConservationListing.objects.select_related("taxon")),
        "conservationthreat_set",
        "conservationaction_set",
        "document_set",
    )
    serializer_class = serializers.TaxonSerializer
    filterset_class = TaxonFilter
    model = Taxon
    uid_fields = ("name_id", )


router.register("taxon", TaxonViewSet, basename="taxon_full")


class FastTaxonViewSet(TaxonViewSet):
    """Fast View set for Taxon."""

    serializer_class = serializers.FastTaxonSerializer


router.register("taxon-fast", FastTaxonViewSet, basename="taxon_fast")


class VernacularFilter(FilterSet):
    """Vernacular filter."""

    class Meta:
        """Class opts."""

        model = Vernacular
        fields = {
            "ogc_fid": "__all__",
            # "taxon": "__all__",
            "name": "__all__",
            "language": "__all__",
            "preferred": ["exact", ],
        }


class VernacularViewSet(OgcFidBatchUpsertViewSet):
    """View set for Vernacular.

    See HBV Names for details and usage examples.
    All filters are available on all fields.
    """

    queryset = Vernacular.objects.all()
    serializer_class = serializers.VernacularSerializer
    filterset_class = VernacularFilter
    model = Vernacular
    uid_fields = ("ogc_fid", )


router.register("vernacular", VernacularViewSet)


class CrossreferenceFilter(FilterSet):
    """Crossreference filter."""

    predecessor = RelatedFilter(TaxonFilter, field_name="predecessor", queryset=Taxon.objects.all())
    successor = RelatedFilter(TaxonFilter, field_name="successor", queryset=Taxon.objects.all())
    # filter_overrides = {
    #     models.DateTimeField: {
    #         'filter_class': filters.IsoDateTimeFilter
    #     },
    # }
    # authorised_on_gte = filters.DateTimeFilter(name="authorised_on", lookup_expr='gte')

    class Meta:
        """Class opts."""

        model = Crossreference
        fields = {
            "xref_id": ["exact", ],
            "reason": ["exact", ],
            "authorised_by": ["exact", ],
            "authorised_on": ["exact", "year__gte", "gt", "gte", "lt", "lte"],
            # "authorised_on_gte": "__all__",
            "effective_to": ["exact", "year__gte", "gt", "gte", "lt", "lte"],
            "comments": ["icontains", ],
        }


class CrossreferenceViewSet(BatchUpsertViewSet):
    """View set for Crossreference.

    See HBV Names for details and usage examples.

    ### Tracing newer names for a Name ID
    See also https://github.com/dbca-wa/wastd/issues/227

    The data shown here are sufficient for the use case, but a convenience method would be faster and, well,  more convenient.

    * [Newer names for Name ID 43353](/api/1/crossreference/?predecessor__name_id=43353) > successor is 43360
    * [Newer names for Name ID 43360](/api/1/crossreference/?predecessor__name_id=43360) > results are [], reached newest name

    ### Tracing older names for a Name ID

    * [Older names for Name ID 43360](/api/1/crossreference/?successor__name_id=43360) > predecessor is 43353
    * [Older names for Name ID 43353](/api/1/crossreference/?successor__name_id=43353) > results are [], reached oldest name

    ### Crossreferences with reason for taxonomic name change:

    * [Reason 0: Misapplied name](/?reason=0)
    * [Reason 1: Taxonomic synonym](/?reason=1)
    * [Reason 2: Nomenclatural synonym](/?reason=2)
    * [Reason 3: Excluded name](/?reason=3)
    * [Reason 4: Concept change](/?reason=4)
    * [Reason 5: Formal description](/?reason=5)
    * [Reason 6: Orthographic variant](/?reason=6)
    * [Reason 7: Name in error](/?reason=7)
    * [Reason 8: Informal Synonym](/?reason=8)

    """

    queryset = Crossreference.objects.all()
    serializer_class = serializers.CrossreferenceSerializer
    filterset_class = CrossreferenceFilter
    pagination_class = LimitOffsetPagination
    model = Crossreference
    uid_fields = ("xref_id", )

    def fetch_existing_records(self, new_records, model):
        """Fetch pk, (status if QC mixin), and **uid_fields values from a model."""
        return model.objects.filter(
            xref_id__in=list(set([x["xref_id"] for x in new_records]))
        ).values("pk", "xref_id")


router.register("crossreference", CrossreferenceViewSet)


class CommunityFilter(FilterSet):
    """Community filter."""

    class Meta:
        """Class opts."""

        model = Community
        fields = {
            "code": "__all__",
            "name": "__all__",
            "description": "__all__",
        }


class CommunityViewSet(BatchUpsertViewSet):
    """View set for Community.

    See HBV Names for details and usage examples.
    All filters are available on all fields.
    """

    queryset = Community.objects.all().prefetch_related(
        "conservation_listings",
        # "conservationthreat_set",
        # "conservationaction_set",
        # "document_set",
    )
    serializer_class = serializers.CommunitySerializer
    filterset_class = CommunityFilter
    model = Community
    uid_fields = ("code",)

    def fetch_existing_records(self, new_records, model):
        """Fetch pk, (status if QC mixin), and **uid_fields values from a model."""
        return model.objects.filter(
            code__in=list(set([x["code"] for x in new_records]))
        ).values("pk", "code")


router.register("community", CommunityViewSet)
