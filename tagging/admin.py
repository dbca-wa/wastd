from django.contrib.admin import register, ModelAdmin, TabularInline
from django.db.models import TextField
from django.forms.widgets import TextInput
from django.urls import reverse
from django.utils.html import mark_safe
from shared.admin import FORMFIELD_OVERRIDES

from .models import Turtle, TurtleObservation, TurtleTag, TurtlePitTag, TurtleMeasurement, TurtleDamage
from .forms import TurtleObservationAdminForm


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
    fields = ('observed', 'status', 'alive', 'place', 'activity')
    can_delete = False


class TurtleMeasurementInline(TabularInline):
    model = TurtleMeasurement
    classes = ('grp-collapse', 'grp-open')
    extra = 0
    fields = ('measurement_type', 'value', 'comments')
    formfield_overrides = {TextField: {'widget': TextInput}}
    can_delete = False


class TurtleDamageInline(TabularInline):
    model = TurtleDamage
    classes = ('grp-collapse', 'grp-open')
    extra = 0
    fields = ('body_part', 'damage', 'cause', 'comments')
    formfield_overrides = {TextField: {'widget': TextInput}}
    can_delete = False


@register(Turtle)
class TurtleAdmin(ModelAdmin):
    date_hierarchy = 'created'
    list_display = ('id', 'species', 'sex', 'status', 'location', 'created', 'name', 'cause_of_death')
    list_filter = ('species', 'sex', 'status', 'location', 'cause_of_death')
    search_fields = ('id', 'name', 'pit_tags__serial', 'tags__serial')
    readonly_fields = ('created', 'entered_by')
    fields = (
        'created',
        'entered_by',
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
    )

    def response_add(self, request, obj, post_url_continue=None):
        """Set the request user as the person who entered the record.
        """
        obj.entered_by = request.user
        obj.save()
        return super().response_add(request, obj, post_url_continue)


@register(TurtleObservation)
class TurtleObservationAdmin(ModelAdmin):
    date_hierarchy = 'observed'
    form = TurtleObservationAdminForm
    list_display = ('pk', 'turtle', 'observed', 'status', 'alive', 'place', 'activity')
    list_filter = ('status', 'alive', 'place', 'condition')
    search_fields = ('pk', 'turtle__pk', 'turtle__tags__serial', 'turtle__pit_tags__serial')
    raw_id_fields = ('turtle', 'measurer', 'measurer_reporter', 'tagger', 'reporter')
    readonly_fields = ('created', 'entered_by')
    fieldsets = (
        (
            'Observation',
            {
                'fields': (
                    'turtle',
                    'observed',
                    'date_convention',
                    'status',
                    'alive',
                    'activity',
                    'beach_position',
                    'condition',
                    'nesting',
                    'clutch_completed',
                    'number_of_eggs',
                    'egg_count_method',
                ),
                'classes': ('grp-collapse', 'grp-open'),
            },
        ),
        (
            'Tag scars',
            {
                'fields': (
                    'scars_left_scale_1',
                    'scars_left_scale_2',
                    'scars_left_scale_3',
                    'scars_right_scale_1',
                    'scars_right_scale_2',
                    'scars_right_scale_3',
                ),
                'classes': ('grp-collapse', 'grp-open'),
            },
        ),
        (
            'People',
            {
                'fields': (
                    'measurer',
                    'measurer_reporter',
                    'tagger',
                    'reporter',
                ),
                'classes': ('grp-collapse', 'grp-open'),
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
                'classes': ('grp-collapse', 'grp-open'),
            },
        ),
    )
    formfield_overrides = FORMFIELD_OVERRIDES
    inlines = (
        TurtleMeasurementInline,
        TurtleDamageInline,
    )

    def response_add(self, request, obj, post_url_continue=None):
        """Set the request user as the person who entered the record.
        """
        obj.entered_by = request.user
        obj.save()
        post_url_continue = reverse('admin:tagging_turtleobservation_add') + f'?turtle={obj.pk}'
        return super().response_add(request, obj, post_url_continue)


@register(TurtleTag)
class TurtleTagAdmin(ModelAdmin):
    list_display = ('serial', 'turtle_link', 'issue_location', 'custodian', 'field_person', 'status', 'return_date')
    list_filter = ('status',)
    raw_id_fields = ('turtle', 'custodian', 'field_person')
    search_fields = ('serial', 'custodian__name', 'field_person__name')
    fields = (
        'serial',
        'turtle',
        'issue_location',
        'tag_order',
        'custodian',
        'field_person',
        'side',
        'status',
        'return_date',
        'return_condition',
        'comments',
    )

    def turtle_link(self, obj):
        if obj.turtle:
            url = reverse('admin:tagging_turtle_change', kwargs={'object_id': obj.turtle.pk})
            link = f'<a href="{url}">{obj.turtle}</a>'
            return mark_safe(link)
        return ''
    turtle_link.short_description = 'turtle'


@register(TurtlePitTag)
class TurtlePitTagAdmin(ModelAdmin):
    list_display = ('serial', 'turtle', 'issue_location', 'custodian', 'field_person', 'status', 'return_date')
    list_filter = ('status',)
    raw_id_fields = ('turtle', 'custodian', 'field_person')
    search_fields = ('serial', 'custodian__name', 'field_person__name')
    fields = (
        'serial',
        'turtle',
        'issue_location',
        'tag_order',
        'custodian',
        'field_person',
        'status',
        'return_date',
        'return_condition',
        'comments',
        'batch_number',
        'box_number',
    )
