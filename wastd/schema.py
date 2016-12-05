# from graphene import relay, ObjectType, AbstractType
# from graphene_django import DjangoObjectType
# from graphene_django.filter import DjangoFilterConnectionField
#
# from wastd.observations.models import *
# 
# class EncounterNode(DjangoObjectType):
#     class Meta:
#         model = Encounter
#         filter_fields = ['source_id', ]
#         interfaces = (relay.Node, )
#
#
# class Query(graphene.ObjectType):
#     encounter = relay.Node.Field(EncounterNode)
#     all_encounters = DjangoFilterConnectionField(EncounterNode)
#
#     # ingredient = relay.Node.Field(IngredientNode)
#     # all_ingredients = DjangoFilterConnectionField(IngredientNode)
#
#     @graphene.resolve_only_args
#     def resolve_encounters(self):
#         return Encounter.objects.all()
#
# schema = graphene.Schema(query=Query)
