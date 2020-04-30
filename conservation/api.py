import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_filters import FilterSet

from shared.api import BatchUpsertViewSet, MyGeoJsonPagination
from shared.utils import force_as_list
from conservation.models import (
    CommunityConservationListing,
    ConservationCategory,
    ConservationCriterion,
    ConservationList,
    Document,
    TaxonConservationListing,
)
from conservation.serializers import (
    CommunityConservationListingSerializer,
    ConservationCategorySerializer,
    ConservationCriterionSerializer,
    ConservationListSerializer,
    DocumentSerializer,
    TaxonConservationListingSerializer,
)
from taxonomy.models import Community, Taxon

logger = logging.getLogger(__name__)


class ConservationCategoryFilter(FilterSet):
    """ConservationCategory filter."""

    class Meta:
        """Class opts."""

        model = ConservationCategory
        fields = {
            "conservation_list": ["exact", "in"],
            "code": ["exact", "icontains"],
            "label": ["exact", "icontains"],
            "description": ["icontains"],
        }


class ConservationCategoryViewSet(BatchUpsertViewSet):
    """View set for ConservationCategory.

    Not using BatchUpsertViewSet.
    """

    queryset = ConservationCategory.objects.all()
    serializer_class = ConservationCategorySerializer
    filterset_class = ConservationCategoryFilter


class ConservationCriterionFilter(FilterSet):
    """ConservationCriterion filter."""

    class Meta:
        model = ConservationCriterion
        fields = {
            "code": ["exact", "icontains"],
            "label": ["exact", "icontains"],
            "description": ["icontains"],
            "conservation_list": ["exact", "in"],
        }


class ConservationCriterionViewSet(BatchUpsertViewSet):
    """View set for ConservationCriterion."""
    model = ConservationCriterion
    queryset = ConservationCriterion.objects.all()
    serializer_class = ConservationCriterionSerializer
    filterset_class = ConservationCriterionFilter
    uid_fields = ("code", )

    def build_unique_fields(self, data):
        """Custom unique fields."""
        return {"conservation_list": data["conservation_list"],
                "code": data["code"]}

    def fetch_existing_records(self, new_records, model):
        """Fetch pk, (status if QC mixin), and **uid_fields values from a model."""
        return model.objects.filter(
            conservation_list__in=list(set([x["conservation_list"] for x in new_records])),
            code__in=list(set([x["code"] for x in new_records]))
        ).values("pk", "code", "conservation_list")


class ConservationListFilter(FilterSet):

    class Meta:
        model = ConservationList
        fields = {
            "code": ["exact", "icontains"],
            "label": ["exact", "icontains"],
            "description": ["icontains"],
            "active_from": ["exact", "year__gt"],
            "active_to": ["exact", "year__gt"],
            "scope_wa": ["exact", ],
            "scope_cmw": ["exact", ],
            "scope_intl": ["exact", ],
            "scope_species": ["exact", ],
            "scope_communities": ["exact", ],
            "approval_level": ["exact"]
        }


class ConservationListViewSet(ModelViewSet):
    model = ConservationList
    queryset = ConservationList.objects.all()
    serializer_class = ConservationListSerializer
    filterset_class = ConservationListFilter
    pagination_class = MyGeoJsonPagination
    uid_field = "code"
    uid_fields = ("code", )

    def create_one(self, data):
        """POST: Create or update exactly one model instance."""
        if "csrfmiddlewaretoken" in data:
            data.pop("csrfmiddlewaretoken")

        cat_data = data.pop("conservationcategory_set", [])
        crit_data = data.pop("conservationcriterion_set", [])

        if data["active_from"] == {}:
            data["active_from"] = None
        if data["active_to"] == {}:
            data["active_to"] = None

        conservation_list, created = ConservationList.objects.update_or_create(
            code=data["code"], defaults=data)
        for cat in cat_data:
            logger.debug("[ConsList viewset] Found one cons cat: {0}".format(cat))
            cat.pop("conservation_list")
            cat["conservation_list_id"] = conservation_list.pk
            ConservationCategory.objects.update_or_create(code=cat["code"], defaults=cat)
        for crit in crit_data:
            logger.debug("[ConsList viewset] Found one cons crit: {0}".format(crit))
            crit.pop("conservation_list")
            crit["conservation_list_id"] = conservation_list.pk
            ConservationCriterion.objects.update_or_create(code=crit["code"], defaults=crit)

        return Response(data, status=status.HTTP_200_OK)

    def create(self, request):
        """POST: Create or update one or many model instances.

        request.data must be:

        * a GeoJSON feature property dict, or
        * a list of GeoJSON feature property dicts.
        """
        if self.uid_field in request.data:
            logger.info("[create] Found one ConservationList dict.")
            res = self.create_one(request.data)
            return res
        elif isinstance(request.data, list) and self.uid_field in request.data[0]:
            logger.info("[create] Found multiple ConservationList dicts.")
            res = [self.create_one(data) for data in request.data]
            return Response(request.data, status=status.HTTP_200_OK)
        else:
            logger.debug("[BatchUpsertViewSet] data: {0}".format(request.data))
            return Response(request.data, status=status.HTTP_400_BAD_REQUEST)


class DocumentFilter(FilterSet):

    class Meta:
        model = Document
        fields = {
            "source": ["exact", "in"],
            "document_type": ["exact", "in"],
            "title": ["icontains"],
            "status": ["exact", "in"],
            "effective_from": ["exact", "year__gt"],
            "effective_to": ["exact", "year__gt"],
            "effective_from_commonwealth": ["exact", "year__gt"],
            "effective_to_commonwealth": ["exact", "year__gt"],
            "review_due": ["exact", "year__gt"],
            "last_reviewed_on": ["exact", "year__gt"],
        }


class DocumentViewSet(BatchUpsertViewSet):
    model = Document
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    filterset_class = DocumentFilter
    uid_fields = ("source", "source_id")


# ----------------------------------------------------------------------------#
# TaxonConservationListing
#
class TaxonConservationListingFilter(FilterSet):
    """TaxonConservationListing filter.

    Performance: Excluding taxon from filter speeds up
    loading an empty TaxonConservationListing List
    from 14 sec (with) to 5 sec (without).
    """

    class Meta:
        """Class opts."""

        model = TaxonConservationListing
        fields = {
            # "taxon": "__all__",
            # "taxon": ["exact", ],
            "scope": ["exact", "in"],
            "status": ["exact", "in"],
            "category": ["exact", "in"],
            "criteria": ["exact", "in"],
            "proposed_on": ["exact", "year__gt"],
            "effective_from": ["exact", "year__gt"],
            "effective_to": ["exact", "year__gt"],
            "last_reviewed_on": ["exact", "year__gt"],
            "review_due": ["exact", "year__gt"],
            "comments": ["exact", "icontains"],
        }


class TaxonConservationListingViewSet(BatchUpsertViewSet):
    """View set for TaxonConservationListing."""

    queryset = TaxonConservationListing.objects.all().select_related("taxon")
    serializer_class = TaxonConservationListingSerializer
    filterset_class = TaxonConservationListingFilter
    uid_fields = ("source", "source_id")
    model = TaxonConservationListing

    def resolve_fks(self, data):
        """Resolve FKs from PK to object."""

        try:
            data["taxon"] = Taxon.objects.get(name_id=data["taxon"])
        except Exception as e:
            logger.error("Exception {0}: taxon {1} not known,".format(e, data["taxon"]))
        return data

    def create_one(self, data):
        """POST: Create or update exactly one model instance.

        The ViewSet must have a method ``split_data`` returning a dict
        of the unique, mandatory fields to get_or_create,
        and a dict of the other optional values to update.

        Return Response(content, status)
        """
        unique_data, update_data = self.split_data(data)

        # Pop category and criterion out update_data
        if 'category' in update_data:
            cat_ids = force_as_list(update_data.pop("category"))
            logger.debug("[API][create_one] Found categories {}".format(cat_ids))
            categories = [ConservationCategory.objects.get(id=x) for x in cat_ids if x != 'NA']
        else:
            categories = []

        if 'criteria' in update_data:
            crit_ids = force_as_list(update_data.pop("criteria"))
            logger.debug("[API][create_one] Found criteria {}".format(crit_ids))
            criteria = [ConservationCriterion.objects.get(id=x) for x in crit_ids if x != 'NA']
        else:
            criteria = []

        # Early exit 1: None value in unique data
        if None in unique_data.values():
            msg = "[API][create_one] Skipping invalid data: {0} {1}".format(
                str(update_data), str(unique_data))
            logger.warning(msg)
            content = {"msg": msg}
            return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)

        logger.debug("[API][create_one] Received "
                     "{0} with unique fields {1}".format(
                         self.model._meta.verbose_name, str(unique_data)))

        # Without the QA status deciding whether to update existing data:
        obj, created = self.model.objects.update_or_create(defaults=update_data, **unique_data)
        if categories:
            obj.category.set(categories)  # TODO: must do individually or can do as list?
        if criteria:
            obj.criteria.set(criteria)
        obj.save()  # better save() than sorry
        obj.refresh_from_db()
        obj.save()  # to update cached fields

        verb = "Created" if created else "Updated"
        st = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        msg = "[API][create_one] {0} {1}".format(verb, obj.__str__())
        logger.info(msg)
        return {"id": obj.pk, "msg": msg, "status": st}

    def create(self, request):
        """POST: Create or update one or many model instances.

        request.data must be a dict or a list of dicts.

        Return Response(result, status)

        result:

        * Warning message plus data if invalid data (status 406 not acceptable)
        * Dict of object_id, message, and status if one record
        * List of one-record dicts if several records
        """
        # Create one ---------------------------------------------------------#
        if self.uid_fields[0] in request.data:
            logger.info('[API][create] found one record, creating/updating...')
            res = self.create_one(request.data)
            return Response(res, status=res["status"])

        # Create many --------------------------------------------------------#
        elif (isinstance(request.data, list) and
              len(request.data) > 0 and
              self.uid_fields[0] in request.data[0]):
            logger.info('[API][create] found batch of {0} records,'
                        ' creating/updating...'.format(len(request.data)))

            # The slow way:
            res = [self.create_one(data) for data in request.data]
            return Response(res, status=status.HTTP_201_CREATED)

        else:
            logger.error("[API][tcl create] failed with data {}".format(request.data))
            return Response(
                request.data,
                status=status.HTTP_406_NOT_ACCEPTABLE
            )


# ----------------------------------------------------------------------------#
# CommunityConservationListing
#
class CommunityConservationListingFilter(FilterSet):
    """CommunityConservationListing filter.
    """
    class Meta:
        model = CommunityConservationListing
        fields = {
            "community": ["exact", ],
            "scope": ["exact", "in"],
            "status": ["exact", "in"],
            "category": ["exact", "in"],
            "criteria": ["exact", "in"],
            "proposed_on": ["exact", "year__gt"],
            "effective_from": ["exact", "year__gt"],
            "effective_to": ["exact", "year__gt"],
            "last_reviewed_on": ["exact", "year__gt"],
            "review_due": ["exact", "year__gt"],
            "comments": ["exact", "icontains"],
        }


class CommunityConservationListingViewSet(BatchUpsertViewSet):
    """View set for CommunityConservationListing.
    """
    model = CommunityConservationListing
    queryset = CommunityConservationListing.objects.all().select_related("community")
    serializer_class = CommunityConservationListingSerializer
    filterset_class = CommunityConservationListingFilter
    uid_fields = ("source", "source_id")

    def resolve_fks(self, data):
        """Resolve FKs from PK to object."""
        try:
            data["community"] = Community.objects.get(code=data["community"])
        except Exception as e:
            print("Exception '{0}': community '{1}' not known.".format(e, data["community"]))
        return data

    def create_one(self, data):
        """POST: Create or update exactly one model instance.

        The ViewSet must have a method ``split_data`` returning a dict
        of the unique, mandatory fields to get_or_create,
        and a dict of the other optional values to update.

        Return Response(content, status)
        """
        unique_data, update_data = self.split_data(data)

        # Pop category and criterion out update_data
        if 'category' in update_data:
            cat_ids = force_as_list(update_data.pop("category"))
            logger.debug("[API][create_one] Found categories {}".format(cat_ids))
            categories = [ConservationCategory.objects.get(id=x) for x in cat_ids if x != 'NA']
        else:
            categories = []

        if 'criteria' in update_data:
            crit_ids = force_as_list(update_data.pop("criteria"))
            logger.debug("[API][create_one] Found criteria {}".format(crit_ids))
            criteria = [ConservationCriterion.objects.get(id=x) for x in crit_ids if x != 'NA']
        else:
            criteria = []

        # Early exit 1: None value in unique data
        if None in unique_data.values():
            msg = "[API][create_one] Skipping invalid data: {0} {1}".format(
                str(update_data), str(unique_data))
            logger.warning(msg)
            content = {"msg": msg}
            return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)

        logger.debug("[API][create_one] Received "
                     "{0} with unique fields {1}".format(
                         self.model._meta.verbose_name, str(unique_data)))

        # Without the QA status deciding whether to update existing data:
        obj, created = self.model.objects.update_or_create(defaults=update_data, **unique_data)
        if categories:
            obj.category.set(categories)
        if criteria:
            obj.criteria.set(criteria)
        obj.save()  # better save() than sorry
        obj.refresh_from_db()
        obj.save()  # to update cached fields

        verb = "Created" if created else "Updated"
        st = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        msg = "[API][create_one] {0} {1}".format(verb, obj.__str__())
        logger.info(msg)
        return {"id": obj.pk, "msg": msg, "status": st}

    def create(self, request):
        """POST: Create or update one or many model instances.

        request.data must be a dict or a list of dicts.

        Return Response(result, status)

        result:

        * Warning message if invalid data (status 406 not acceptable)
        * Dict of object_id and message if one record
        * List of one-record dicts if several records
        """

        # Create one ---------------------------------------------------------#
        if self.uid_fields[0] in request.data:
            logger.info('[API][create] found one record, creating/updating...')
            res = self.create_one(request.data)
            return Response(res, status=res["status"])

        # Create many --------------------------------------------------------#
        elif (isinstance(request.data, list) and
              len(request.data) > 0 and
              self.uid_fields[0] in request.data[0]):
            logger.info('[API][create] found batch of {0} records,'
                        ' creating/updating...'.format(len(request.data)))
            res = [self.create_one(data) for data in request.data]
            return Response(res, status=status.HTTP_201_CREATED)

        else:
            return Response(
                request.data,
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
