from django.contrib.admin import register, ModelAdmin, TabularInline, SimpleListFilter
from django.db.models import TextField
from django.forms.widgets import TextInput
from django.urls import reverse
from django.utils.html import mark_safe
from shared.admin import FORMFIELD_OVERRIDES

from .forms import (
    TurtleAddForm,
    TurtleChangeForm,
    TurtleObservationForm,
    TurtleFlipperDamageForm,
    TurtleInjuryForm,
    TurtleSampleForm,
    TurtleTagForm,
    TurtleTagAddForm,
    TurtlePitTagForm,
    TurtlePitTagAddForm,
)
from .models import (
    Turtle,
    TurtleObservation,
    TurtleTag,
    TurtlePitTag,
    TurtleMeasurement,
    TurtleDamage,
    TurtleSample,
    TurtleIdentification,
)


class TurtleTagInline(TabularInline):
    """Tabular inline ModelFormset used during update of an existing Turtle instance.
    """
    model = TurtleTag
    form = TurtleTagForm
    formfield_overrides = {TextField: {'widget': TextInput}}
    extra = 0
    can_delete = True


class TurtleTagAddInline(TabularInline):
    """Tabular inline ModelFormset used during creation of a new Turtle instance.
    """
    model = TurtleTag
    form = TurtleTagAddForm
    formfield_overrides = {TextField: {'widget': TextInput}}
    extra = 0
    can_delete = False


class TurtlePitTagInline(TabularInline):
    """Tabular inline ModelFormset used during update of an existing Turtle instance.
    """
    model = TurtlePitTag
    form = TurtlePitTagForm
    formfield_overrides = {TextField: {'widget': TextInput}}
    extra = 0
    can_delete = True


class TurtlePitTagAddInline(TabularInline):
    """Tabular inline ModelFormset used during creation of a new Turtle instance.
    """
    model = TurtlePitTag
    form = TurtlePitTagAddForm
    formfield_overrides = {TextField: {'widget': TextInput}}
    extra = 0
    can_delete = False


class TurtleIdentificationInline(TabularInline):
    model = TurtleIdentification
    fields = ('identification_type', 'identifier', 'comments')
    formfield_overrides = {TextField: {'widget': TextInput(attrs={'class': 'vTextField'})}}
    extra = 0
    can_delete = False
    verbose_name = 'other identification record'
    verbose_name_plural = 'other identification records'


@register(Turtle)
class TurtleAdmin(ModelAdmin):
    date_hierarchy = 'created'
    list_display = ('id', 'species', 'sex', 'status', 'location', 'created', 'name', 'cause_of_death')
    list_filter = ('species', 'sex', 'status', 'location', 'cause_of_death')
    search_fields = ('id', 'name', 'pit_tags__serial', 'tags__serial')

    def get_form(self, request, obj=None, **kwargs):
        if not obj:  # Add new instance.
            kwargs['form'] = TurtleAddForm
        else:
            kwargs['form'] = TurtleChangeForm
        return super().get_form(request, obj, **kwargs)

    def get_inlines(self, request, obj):
        if not obj:  # New instance, use different inline forms.
            return (TurtleTagAddInline, TurtlePitTagAddInline, TurtleIdentificationInline)
        else:
            return (TurtleTagInline, TurtlePitTagInline, TurtleIdentificationInline)

    def response_add(self, request, obj, post_url_continue=None):
        """Set the request user as the person who entered the record.
        """
        obj.entered_by = request.user
        obj.save()
        return super().response_add(request, obj, post_url_continue)


class TurtleMeasurementInline(TabularInline):
    model = TurtleMeasurement
    classes = ('grp-collapse', 'grp-open')
    fields = ('measurement_type', 'value', 'comments')
    extra = 0
    formfield_overrides = {TextField: {'widget': TextInput}}
    can_delete = False


class TurtleFlipperDamageInline(TabularInline):
    model = TurtleDamage
    form = TurtleFlipperDamageForm
    classes = ('grp-collapse', 'grp-open')
    formfield_overrides = {TextField: {'widget': TextInput}}
    extra = 0
    can_delete = False
    verbose_name = 'flipper damage record'
    verbose_name_plural = 'flipper damage'


class TurtleInjuryInline(TabularInline):
    model = TurtleDamage
    form = TurtleInjuryForm
    classes = ('grp-collapse', 'grp-open')
    formfield_overrides = {TextField: {'widget': TextInput}}
    extra = 0
    can_delete = False
    verbose_name = 'injury record'
    verbose_name_plural = 'injury records'


class TurtleTissueSampleInline(TabularInline):
    model = TurtleSample
    form = TurtleSampleForm
    classes = ('grp-collapse', 'grp-open')
    extra = 0
    can_delete = False
    verbose_name = 'tissue sample'
    verbose_name_plural = 'tissue samples'


@register(TurtleObservation)
class TurtleObservationAdmin(ModelAdmin):
    date_hierarchy = 'observed'
    form = TurtleObservationForm
    list_display = ('pk', 'turtle_link', 'observed', 'status', 'alive', 'place', 'activity')
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
                    'measurer',
                    'measurer_reporter',
                    'tagger',
                    'reporter',
                    'alive',
                    'place',
                    'activity',
                    'beach_position',
                    'clutch_completed',
                    'number_of_eggs',
                    'egg_count_method',
                    'comments',
                ),
                'classes': ('grp-collapse', 'grp-open'),
            },
        ),
        (
            'Flipper tag scars',
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
            'Location',
            {
                'fields': (
                    'point',
                ),
                'classes': ('grp-collapse', 'grp-open'),
            },
        ),
    )
    inlines = (
        TurtleMeasurementInline,
        TurtleFlipperDamageInline,
        TurtleInjuryInline,
        TurtleTissueSampleInline,

    )
    formfield_overrides = FORMFIELD_OVERRIDES

    def turtle_link(self, obj):
        if obj.turtle:
            url = reverse('admin:tagging_turtle_change', kwargs={'object_id': obj.turtle.pk})
            link = f'<a href="{url}">{obj.turtle}</a>'
            return mark_safe(link)
        return ''
    turtle_link.short_description = 'turtle'

    def response_add(self, request, obj, post_url_continue=None):
        """Set the request user as the person who entered the record.
        """
        obj.entered_by = request.user
        obj.save()
        post_url_continue = reverse('admin:tagging_turtleobservation_add') + f'?turtle={obj.pk}'
        return super().response_add(request, obj, post_url_continue)


class AssignedTurtleFilter(SimpleListFilter):
    title = 'assigned to turtle'
    parameter_name = 'assigned_turtle'

    def lookups(self, request, model_admin):
        return (
            ('true', 'Assigned to turtle'),
            ('false', 'Not assigned to turtle')
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == "false":
                return queryset.filter(turtle__isnull=True)
            else:
                return queryset.filter(turtle__isnull=False)


@register(TurtleTag)
class TurtleTagAdmin(ModelAdmin):

    list_display = ('serial', 'turtle_link', 'issue_location', 'custodian', 'field_person', 'status', 'return_date')
    list_filter = ('status', AssignedTurtleFilter)
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

    def delete_model(self, request, obj):
        """Objects deleted via the admin site should be deleted properly.
        """
        obj.delete(permanent=True)


@register(TurtlePitTag)
class TurtlePitTagAdmin(ModelAdmin):
    list_display = ('serial', 'turtle_link', 'issue_location', 'custodian', 'field_person', 'status', 'return_date')
    list_filter = ('status', AssignedTurtleFilter)
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

    def turtle_link(self, obj):
        if obj.turtle:
            url = reverse('admin:tagging_turtle_change', kwargs={'object_id': obj.turtle.pk})
            link = f'<a href="{url}">{obj.turtle}</a>'
            return mark_safe(link)
        return ''
    turtle_link.short_description = 'turtle'

    def delete_model(self, request, obj):
        """Objects deleted via the admin site should be deleted properly.
        """
        obj.delete(permanent=True)
