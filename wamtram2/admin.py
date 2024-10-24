from django.contrib import admin
from import_export import resources
from import_export.fields import Field
import nested_admin
from .models import (
    TrtPersons,
    TrtTurtles,
    TrtObservations,
    TrtTags,
    TrtPitTags,
    TrtMeasurements,
    TrtDamage,
    TrtDataEntry,
    TrtEntryBatches,
    TrtTagOrders,
)
from import_export.admin import ImportExportModelAdmin
from .forms import DataEntryUserModelForm, EnterUserModelForm, TrtObservationsForm, TrtPersonsForm
from django.urls import reverse
from django.utils.html import format_html


class TrtMeasurementsInline(nested_admin.NestedTabularInline):
    model = TrtMeasurements
    # form = TrtMeasurementsForm
    verbose_name = "Measurement"
    extra = 0


class TrtObservationsInline(nested_admin.NestedStackedInline):
    model = TrtObservations
    inlines = [TrtMeasurementsInline]
    verbose_name = "Observation"  # Singular name for one object
    extra = 0


class TrtTagsInline(nested_admin.NestedStackedInline):
    model = TrtTags
    verbose_name = "Flipper Tag"  # Singular name for one object
    extra = 0


class TrtPitTagsInline(nested_admin.NestedStackedInline):
    model = TrtPitTags
    verbose_name = "Pit Tag"  # Singular name for one object
    extra = 0


class TrtDamageInline(nested_admin.NestedStackedInline):
    model = TrtDamage
    verbose_name = "Damage"  # Singular name for one object
    extra = 0


class TrtDataEntryInline(admin.TabularInline):
    model = TrtDataEntry
    extra = 0
    fields = ('linked_data_entry_id','saved_observation', 'observation_date', 'turtle', 'recapture_tags', 'new_tags', 'lay', 'system_message', 'enterer', 'needs_review', 'comments')
    readonly_fields = ('linked_data_entry_id','saved_observation', 'observation_date', 'turtle', 'recapture_tags', 'new_tags', 'lay', 'system_message', 'enterer', 'needs_review', 'comments')
    can_delete = False
    max_num = 0

    def has_add_permission(self, request, obj=None):
        return False
    
    def linked_data_entry_id(self, obj):
        url = reverse('admin:wamtram2_trtdataentry_change', args=[obj.data_entry_id])
        return format_html('<a href="{}">{}</a>', url, obj.data_entry_id)
    linked_data_entry_id.short_description = 'Data Entry ID'

    def saved_observation(self, obj):
        return obj.observation_id

    def turtle(self, obj):
        return obj.turtle_id

    def recapture_tags(self, obj):
        tags = []
        for field in ['recapture_left_tag_id', 'recapture_right_tag_id', 'recapture_pittag_id']:
            tag = getattr(obj, field)
            if tag:
                tags.append(str(tag))
        return ', '.join(tags)

    def new_tags(self, obj):
        tags = []
        for field in ['new_left_tag_id', 'new_right_tag_id', 'new_pittag_id']:
            tag = getattr(obj, field)
            if tag:
                tags.append(str(tag))
        return ', '.join(tags)

    def lay(self, obj):
        return 'Yes' if obj.nesting and obj.nesting.code == 'Y' else 'No'

    def enterer(self, obj):
        return obj.entered_by_id

    def needs_review(self, obj):
        return 'Yes' if obj.do_not_process else 'No'

@admin.register(TrtEntryBatches)
class TrtEntryBatchesAdmin(admin.ModelAdmin):
    list_display = ("linked_entry_batch_id", "entry_date", "entered_person_id", "comments")
    ordering = ["-entry_batch_id"]
    inlines = [TrtDataEntryInline]
    form = EnterUserModelForm

    def linked_entry_batch_id(self, obj):
        url = reverse('admin:wamtram2_trtentrybatches_change', args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.entry_batch_id)
    linked_entry_batch_id.short_description = 'Entry batch id'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('trtdataentry_set')

@admin.register(TrtDataEntry)
class TrtDataEntryAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}

    def has_module_permission(self, request):
        """
        Return False to hide this model from the admin index page.
        """
        return False

    fields = ('entry_batch', 'observation_date', 'turtle_id', 'recapture_tags', 'new_tags', 'lay', 'enterer', 'needs_review', 'comments')
    readonly_fields = ('entry_batch', 'observation_date', 'turtle_id', 'recapture_tags', 'new_tags', 'lay', 'enterer', 'needs_review', 'comments')

    def recapture_tags(self, obj):
        tags = []
        for field in ['recapture_left_tag_id', 'recapture_right_tag_id', 'recapture_pittag_id']:
            tag = getattr(obj, field)
            if tag:
                tags.append(str(tag))
        return ', '.join(tags)

    def new_tags(self, obj):
        tags = []
        for field in ['new_left_tag_id', 'new_right_tag_id', 'new_pittag_id']:
            tag = getattr(obj, field)
            if tag:
                tags.append(str(tag))
        return ', '.join(tags)

    def lay(self, obj):
        return 'Yes' if obj.nesting and obj.nesting.code == 'Y' else 'No'

    def enterer(self, obj):
        return obj.entered_by_id

    def needs_review(self, obj):
        return 'Yes' if obj.do_not_process else 'No'


@admin.register(TrtTurtles)
class TrtTurtlesAdmin(ImportExportModelAdmin, nested_admin.NestedModelAdmin):

    list_display = ("turtle_id", "species_code", "turtle_name")
    date_hierarchy = "date_entered"
    ordering = ["date_entered"]
    list_filter = ["species_code", "location_code"]
    search_fields = ["turtle_id"]
    inlines = [TrtObservationsInline, TrtTagsInline, TrtPitTagsInline]


@admin.register(TrtObservations)
class TrtObservationsAdmin(nested_admin.NestedModelAdmin):
    form = TrtObservationsForm
    readonly_fields = ('observation_status','corrected_date',)
    
    autocomplete_fields = ["turtle"]
    list_display = ("observation_id", "turtle", "observation_date", "entry_batch")
    date_hierarchy = "observation_date"
    list_filter = ["turtle__species_code", "place_code"]
    search_fields = ["observation_id", "entry_batch__entry_batch_id"]
    inlines = [TrtMeasurementsInline, TrtDamageInline]
    
    def save_model(self, request, obj, form, change):
        if 'observation_status' in form.cleaned_data:
            form.cleaned_data.pop('observation_status')
        if 'corrected_date' in form.cleaned_data:
            form.cleaned_data.pop('corrected_date')
        super().save_model(request, obj, form, change)


@admin.register(TrtMeasurements)
class TrtMeasurementsdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}


@admin.register(TrtTags)
class TrtTagsAdmin(ImportExportModelAdmin):
    list_display = ("tag_id", "turtle", "tag_status")
    list_filter = ["tag_status"]
    search_fields = ["tag_id"]


@admin.register(TrtPitTags)
class TrtPitTagsAdmin(ImportExportModelAdmin):
    list_display = ("pittag_id", "turtle", "pit_tag_status")
    list_filter = ["pit_tag_status"]
    search_fields = ["pittag_id"]


@admin.register(TrtTagOrders)
class TrtTagOrdersAdmin(ImportExportModelAdmin):
    list_display = ("tag_order_id", "order_date", "order_number")
    list_filter = ["order_date"]
    search_fields = ["tag_order_id"]
    verbose_name = "Tag Order"  # Singular name for one object
    verbose_name_plural = "Tag Orders"

class TrtPersonsResource(resources.ModelResource):
    recorder = Field(attribute='recorder', column_name='Recorder')

    def before_import_row(self, row, **kwargs):
        if 'Recorder' not in row or row['Recorder'] == '':
            row['Recorder'] = False

    class Meta:
        model = TrtPersons
        import_id_fields = ('email',)
        fields = ('first_name', 'surname', 'email', 'recorder')
        export_order = fields

@admin.register(TrtPersons)
class TrtPersonsAdmin(ImportExportModelAdmin):
    resource_class = TrtPersonsResource
    form = TrtPersonsForm
    list_display = ('first_name', 'surname', 'email', 'recorder')
    search_fields = ['first_name', 'surname', 'email']
    fieldsets = (
        ('Required Information', {
            'fields': ('first_name', 'surname', 'email', 'recorder'),
            'description': 'These fields are required.'
        }),
        ('Additional Information', {
            'fields': ('middle_name', 'specialty', 'address_line_1', 'address_line_2', 'town', 'state', 'post_code', 'country', 'telephone', 'fax', 'mobile', 'comments', 'transfer'),
        }),
    )
