import graphene
import graphql_geojson
from graphene_django.types import DjangoObjectType

from taxonomy import models as tax_models

# ----------------------------------------------------------------------------#
# Types
# ----------------------------------------------------------------------------#


class CommunityType(DjangoObjectType):
    class Meta:
        model = tax_models.Community
        geojson_field = 'eoo'


class TaxonType(DjangoObjectType):
    class Meta:
        model = tax_models.Taxon
        geojson_field = 'eoo'


class CrossreferenceType(DjangoObjectType):
    class Meta:
        model = tax_models.Crossreference


# ----------------------------------------------------------------------------#
# Queries
# ----------------------------------------------------------------------------#
class Query(object):
    community = graphene.Field(CommunityType,
                               id=graphene.Int(),
                               code=graphene.String(),
                               name=graphene.String(),
                               description=graphene.String(),
                               )

    all_communities = graphene.List(CommunityType)

    taxon = graphene.Field(TaxonType)

    all_taxa = graphene.List(TaxonType)
    all_crossreferences = graphene.List(CrossreferenceType)

    def resolve_community(self, info, **kwargs):
        id = kwargs.get('id')
        code = kwargs.get('code')

        if id is not None:
            return tax_models.Community.objects.get(pk=id)

        if code is not None:
            return tax_models.Community.objects.get(code=code)

        return None

    def resolve_all_communities(self, info, **kwargs):
        return tax_models.Community.objects.all()

    def resolve_taxon(self, info, **kwargs):
        id = kwargs.get('id')
        name_id = kwargs.get('nameId')

        if id is not None:
            return tax_models.Taxon.objects.get(pk=id)

        if name_id is not None:
            return tax_models.Taxon.objects.get(name_id=name_id)

        return None

    def resolve_all_taxa(self, info, **kwargs):
        return tax_models.Taxon.objects.all()

    def resolve_all_crossreferences(self, info, **kwargs):
        # We can easily optimize query count in the resolve method
        return tax_models.Crossreference.objects.select_related('predecessor', 'successor').all()
