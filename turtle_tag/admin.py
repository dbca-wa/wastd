from django.contrib.admin import register, ModelAdmin
from .models import Turtle, TurtleObservation


@register(Turtle)
class TurtleAdmin(ModelAdmin):
    date_hierarchy = 'date_entered'
    list_display = ('pk', 'species', 'sex', 'status', 'location', 'date_entered', 'name', 'cause_of_death')
    list_filters = ('species', 'sex', 'status', 'location', 'cause_of_death')
    search_fields = ('pk', 'name', 'pit_tags__pk', 'tags__pk')
    fields = ('pk', 'species', 'sex', 'status', 'location', 'date_entered', 'name', 'cause_of_death')


@register(TurtleObservation)
class TurtleObservationAdmin(ModelAdmin):
    date_hierarchy = 'observation_datetime'
    list_display = ('pk', 'turtle', 'observation_datetime', 'alive', 'place', 'activity', 'tagger_person')
    search_fields = ('pk', 'tagger_person__name', 'turtle__pk', 'turtle__tags__serial', 'turtle__pit_tags__serial')
