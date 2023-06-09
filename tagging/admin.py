from django.contrib import messages
from django.contrib.admin import register, TabularInline, SimpleListFilter
from django.db.models import TextField
from django.forms.widgets import TextInput
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.urls import reverse
from django.utils.html import mark_safe
from django.utils.translation import gettext as _
from fsm_admin.mixins import FSMTransitionMixin
from reversion.admin import VersionAdmin
from shared.admin import FORMFIELD_OVERRIDES
from urllib.parse import quote as urlquote

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
    TagOrder,
    Turtle,
    TurtleObservation,
    TurtleTag,
    TurtlePitTag,
    TurtleMeasurement,
    TurtleDamage,
    TurtleSample,
    TurtleIdentification,
    TurtleTagObservation,
    TurtlePitTagObservation,
)


@register(TagOrder)
class TagOrderAdmin(VersionAdmin):
    date_hierarchy = 'order_date'
    list_display = ('order_number', 'order_date', 'tag_prefix', 'start_tag_number', 'end_tag_number', 'total_tags')
    list_filter = ('tag_prefix',)
    search_fields = ('order_number', 'tag_prefix', 'paid_by', 'comments')


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
class TurtleAdmin(VersionAdmin):
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
        # User clicked the 'Save and add observation' button.
        if "_saveaddobservation" in request.POST:
            opts = self.model._meta
            msg_dict = {
                'name': opts.verbose_name,
                'obj': format_html('<a href="{}">{}</a>', urlquote(request.path), obj),
            }
            msg = format_html(
                _('The {name} “{obj}” was added successfully. You may add an observation for it below.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            redirect_url = reverse('admin:tagging_turtleobservation_add') + f'?turtle={obj.pk}'
            return HttpResponseRedirect(redirect_url)
        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        # User clicked the 'Save and add observation' button.
        if "_saveaddobservation" in request.POST:
            opts = self.model._meta
            msg_dict = {
                'name': opts.verbose_name,
                'obj': format_html('<a href="{}">{}</a>', urlquote(request.path), obj),
            }
            msg = format_html(
                _('The {name} “{obj}” was changed successfully. You may add an observation for it below.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            redirect_url = reverse('admin:tagging_turtleobservation_add') + f'?turtle={obj.pk}'
            return HttpResponseRedirect(redirect_url)
        return super().response_change(request, obj)


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


class TurtleTagObservationInline(TabularInline):
    model = TurtleTagObservation
    fields = ('tag', 'status', 'barnacles', 'comments')
    classes = ('grp-collapse', 'grp-open')
    formfield_overrides = {TextField: {'widget': TextInput}}
    extra = 0
    can_delete = True
    readonly_fields = ('tag',)

    def has_add_permission(self, request, obj):
        return False


class TurtlePitTagObservationInline(TabularInline):
    model = TurtlePitTagObservation
    fields = ('tag', 'status', 'position', 'checked', 'comments')
    classes = ('grp-collapse', 'grp-open')
    formfield_overrides = {TextField: {'widget': TextInput}}
    extra = 0
    can_delete = True
    readonly_fields = ('tag',)

    def has_add_permission(self, request, obj):
        return False


@register(TurtleObservation)
class TurtleObservationAdmin(FSMTransitionMixin, VersionAdmin):
    date_hierarchy = 'observed'
    form = TurtleObservationForm
    list_display = ('pk', 'turtle_link', 'observed', 'status', 'alive', 'place', 'curation_status')
    list_filter = ('status', 'alive', 'place', 'condition', 'curation_status')
    search_fields = ('pk', 'turtle__pk', 'turtle__tags__serial', 'turtle__pit_tags__serial')
    raw_id_fields = ('turtle', 'measurer', 'measurer_reporter', 'tagger', 'tagger_reporter')
    readonly_fields = ('created', 'entered_by', 'curation_status')
    fsm_field = ['curation_status']
    fieldsets = (
        (
            'QA',
            {
                'fields': (
                    'created',
                    'entered_by',
                    'curation_status',
                ),
                'classes': ('grp-collapse', 'grp-closed'),
            },
        ),
        (
            'Observation',
            {
                'fields': (
                    'turtle',
                    'observed',
                    'recorded_by',
                    'measurer',
                    'tagger',
                    'status',
                    'place',
                    'data_sheet',
                    'comments',
                ),
                'classes': ('grp-collapse', 'grp-open'),
            },
        ),
        (
            'Nesting',
            {
                'fields': (
                    'nested',
                    'number_of_eggs',
                    'nesting_interrupted',
                    'nesting_interruption_cause',
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
    formfield_overrides = FORMFIELD_OVERRIDES

    def get_inlines(self, request, obj):
        if not obj:  # New instance, use different inline forms.
            return (
                TurtleMeasurementInline,
                TurtleFlipperDamageInline,
                TurtleInjuryInline,
                TurtleTissueSampleInline,
            )
        else:
            return (
                TurtleMeasurementInline,
                TurtleFlipperDamageInline,
                TurtleInjuryInline,
                TurtleTissueSampleInline,
                TurtleTagObservationInline,
                TurtlePitTagObservationInline,
            )

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

        # Record tag observations for attached tags.
        for tag in obj.turtle.tags.all():
            if tag.is_attached():
                TurtleTagObservation.objects.create(
                    tag=tag,
                    observation=obj,
                )
        for pit_tag in obj.turtle.pit_tags.all():
            if pit_tag.is_attached():
                TurtlePitTagObservation.objects.create(
                    tag=pit_tag,
                    observation=obj,
                )

        if '_addanother' in request.POST:
            opts = self.model._meta
            msg_dict = {
                'name': opts.verbose_name,
                'obj': format_html('<a href="{}">{}</a>', urlquote(request.path), obj),
            }
            msg = format_html(
                _('The {name} “{obj}” was added successfully. You may add another {name} below.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            redirect_url = reverse('admin:tagging_turtleobservation_add') + f'?turtle={obj.turtle.pk}'
            return HttpResponseRedirect(redirect_url)

        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        if '_addanother' in request.POST:
            opts = self.model._meta
            msg_dict = {
                'name': opts.verbose_name,
                'obj': format_html('<a href="{}">{}</a>', urlquote(request.path), obj),
            }
            msg = format_html(
                _('The {name} “{obj}” was changed successfully. You may add another {name} below.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            redirect_url = reverse('admin:tagging_turtleobservation_add') + f'?turtle={obj.turtle.pk}'
            return HttpResponseRedirect(redirect_url)

        return super().response_change(request, obj)


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
class TurtleTagAdmin(VersionAdmin):
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
class TurtlePitTagAdmin(VersionAdmin):
    list_display = ('serial', 'turtle_link', 'issue_location', 'custodian', 'field_person', 'status', 'return_date', 'batch_number', 'box_number')
    list_filter = ('status', AssignedTurtleFilter)
    raw_id_fields = ('turtle', 'custodian', 'field_person')
    search_fields = ('serial', 'custodian__name', 'field_person__name', 'batch_number', 'box_number')
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


@register(TurtleSample)
class TurtleSampleAdmin(VersionAdmin):
    date_hierarchy = 'sample_date'
    list_display = ('id', 'observation_link', 'turtle_link', 'tissue_type', 'label', 'sample_date')
    list_filter = ('tissue_type',)
    raw_id_fields = ('observation',)
    search_fields = ('label', 'comments')

    def observation_link(self, obj):
        url = reverse('admin:tagging_turtleobservation_change', kwargs={'object_id': obj.observation.pk})
        link = f'<a href="{url}">{obj.observation}</a>'
        return mark_safe(link)
    observation_link.short_description = 'observation'

    def turtle_link(self, obj):
        url = reverse('admin:tagging_turtle_change', kwargs={'object_id': obj.observation.turtle.pk})
        link = f'<a href="{url}">{obj.observation.turtle}</a>'
        return mark_safe(link)
    turtle_link.short_description = 'turtle'
