from django.contrib.admin import register, ModelAdmin, TabularInline
from django.db.models import TextField
from django.forms.widgets import TextInput
from .models import Turtle, TurtleObservation, TurtleTag, TurtlePitTag


class TurtleTagInline(TabularInline):
    model = TurtleTag
    extra = 0
    fields = ('serial', 'side', 'status', 'return_date', 'return_condition', 'comments')
    formfield_overrides = {TextField: {'widget': TextInput}}
    can_delete = False


class TurtlePitTagInline(TabularInline):
    model = TurtlePitTag
    extra = 0
    fields = ('serial', 'status', 'return_date', 'return_condition', 'comments')
    formfield_overrides = {TextField: {'widget': TextInput}}
    can_delete = False


class TurtleObservationInline(TabularInline):
    model = TurtleObservation
    extra = 0
    fields = ('observation_datetime', 'observation_status', 'alive', 'place', 'activity')
    can_delete = False


@register(Turtle)
class TurtleAdmin(ModelAdmin):
    date_hierarchy = 'date_entered'
    list_display = ('id', 'species', 'sex', 'status', 'location', 'date_entered', 'name', 'cause_of_death')
    list_filters = ('species', 'sex', 'status', 'location', 'cause_of_death')
    search_fields = ('id', 'name', 'pit_tags__serial', 'tags__serial')
    readonly_fields = ('id', 'date_entered')
    fields = (
        'id',
        'date_entered',
        'species',
        'sex',
        'status',
        'location',
        'name',
        'cause_of_death',
        'comments',
    )
    inlines = (
        TurtleTagInline,
        TurtlePitTagInline,
        TurtleObservationInline,
    )


@register(TurtleObservation)
class TurtleObservationAdmin(ModelAdmin):
    date_hierarchy = 'observation_datetime'
    list_display = ('pk', 'turtle', 'observation_datetime', 'alive', 'place', 'activity', 'tagger_person')
    search_fields = ('pk', 'tagger_person__name', 'turtle__pk', 'turtle__tags__serial', 'turtle__pit_tags__serial')
