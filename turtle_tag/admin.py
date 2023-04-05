from django.contrib.admin import register, ModelAdmin, TabularInline
from django.db.models import TextField
from django.forms.widgets import TextInput
from shared.admin import FORMFIELD_OVERRIDES

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
    fields = ('observation_datetime', 'status', 'alive', 'place', 'activity')
    can_delete = False


@register(Turtle)
class TurtleAdmin(ModelAdmin):
    date_hierarchy = 'date_entered'
    list_display = ('id', 'species', 'sex', 'status', 'location', 'date_entered', 'name', 'cause_of_death')
    list_filter = ('species', 'sex', 'status', 'location', 'cause_of_death')
    search_fields = ('id', 'name', 'pit_tags__serial', 'tags__serial')
    readonly_fields = ('date_entered', 'entered_by_person')
    fields = (
        'date_entered',
        'entered_by_person',
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

    def response_add(self, request, obj, post_url_continue=None):
        """Set the request user as the person who entered the record.
        """
        obj.entered_by_person = request.user
        obj.save()
        return super().response_add(request, obj, post_url_continue)


@register(TurtleObservation)
class TurtleObservationAdmin(ModelAdmin):
    date_hierarchy = 'observation_datetime'
    list_display = ('pk', 'turtle', 'observation_datetime', 'status', 'alive', 'place', 'activity')
    list_filter = ('status', 'alive', 'place', 'condition')
    search_fields = ('pk', 'tagger_person__name', 'turtle__pk', 'turtle__tags__serial', 'turtle__pit_tags__serial')
    raw_id_fields = ('turtle', 'measurer_person', 'measurer_reporter_person', 'tagger_person', 'reporter_person')
    readonly_fields = ('date_entered', 'entered_by_person')
    fieldsets = (
        (
            'Observation',
            {
                'fields': (
                    'date_entered',
                    'entered_by_person',
                    'turtle',
                    'observation_datetime',
                    'date_convention',
                    'status',
                    'alive',
                    'activity',
                    'nesting',
                    'clutch_completed',
                    'number_of_eggs',
                    'egg_count_method',
                ),
            },
        ),
        (
            'People',
            {
                'fields': (
                    'measurer_person',
                    'measurer_reporter_person',
                    'tagger_person',
                    'reporter_person',
                ),
            },
        ),
        (
            'Place',
            {
                'fields': (
                    'place',
                    'place_description',
                    'point',
                ),
            },
        ),
    )
    formfield_overrides = FORMFIELD_OVERRIDES

    def response_add(self, request, obj, post_url_continue=None):
        """Set the request user as the person who entered the record.
        """
        obj.entered_by_person = request.user
        obj.save()
        return super().response_add(request, obj, post_url_continue)
