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
    TrtNestingSeason,
    TrtDamageCauseCodes,
    TrtDamageCodes,
    TrtLocations
)
from import_export.admin import ImportExportModelAdmin
from .forms import EnterUserModelForm, TrtObservationsForm, TrtPersonsForm, TrtNestingSeasonForm
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
    fields = ('linked_data_entry_id','saved_observation', 'observation_date', 'turtle', 'recapture_tags', 'new_tags', 'lay', 'enterer', 'needs_review', 'comments')
    readonly_fields = ('linked_data_entry_id','saved_observation', 'observation_date', 'turtle', 'recapture_tags', 'new_tags', 'lay', 'enterer', 'needs_review', 'comments')
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
        return {}

    def has_module_permission(self, request):
        return False

    fields = (
        'entry_batch', 'user_entry_id', 'turtle_id', 'observation_id', 'do_not_process',
        'recapture_left_tag_id', 'recapture_right_tag_id', 'recapture_pittag_id',
        'new_left_tag_id', 'new_right_tag_id', 'new_pittag_id',
        'place_code', 'observation_date', 'observation_time',
        'nesting', 'species_code', 'identification_confidence', 'sex',
        'curved_carapace_length', 'curved_carapace_width',
        'activity_code', 'beach_position_code',
        'damage_carapace', 'damage_lff', 'damage_rff', 'damage_lhf', 'damage_rhf',
        'comments', 'error_number', 'error_message'
    )
    readonly_fields = ('entry_batch', 'user_entry_id')

    list_display = ('data_entry_id', 'entry_batch', 'observation_date', 'turtle_id', 'do_not_process')
    list_filter = ('do_not_process', 'species_code', 'nesting')
    search_fields = ('data_entry_id', 'turtle_id__turtle_id', 'observation_id__observation_id')

    def needs_review(self, obj):
        return 'Yes' if obj.do_not_process else 'No'
    needs_review.short_description = 'Needs Review'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'entry_batch', 'turtle_id', 'observation_id', 'place_code', 'species_code',
            'activity_code'
        )

    def get_object(self, request, object_id, from_field=None):
        try:
            object_id = int(object_id)
            return self.get_queryset(request).get(data_entry_id=object_id)
        except (ValueError, TrtDataEntry.DoesNotExist):
            return None


@admin.register(TrtTurtles)
class TrtTurtlesAdmin(ImportExportModelAdmin, nested_admin.NestedModelAdmin):

    list_display = ("turtle_id", "species_code", "sex", "turtle_status", "date_entered", "comments")
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


class TrtTagsResource(resources.ModelResource):
    class Meta:
        model = TrtTags
        import_id_fields = ("tag_id",)
        fields = (
            "tag_id",
            "tag_order_id",
            "issue_location",
            "custodian_person",
            "turtle",
            "side",
            "tag_status",
            "return_date",
            "return_condition",
            "comments",
            "field_person_id",
        )
        export_order = fields


@admin.register(TrtTags)
class TrtTagsAdmin(ImportExportModelAdmin):
    resource_class = TrtTagsResource
    list_display = ("tag_id", "turtle", "tag_status")
    list_filter = ["tag_status"]
    search_fields = ["tag_id"]


class TrtPitTagsResource(resources.ModelResource):
    class Meta:
        model = TrtPitTags
        import_id_fields = ("pittag_id",)
        fields = (
            "box_number",
            "pittag_id",
            "batch_number",
            "comments",
            "issue_location",
            "field_person_id",
            "tag_order_id",
            "pit_tag_status",
        )
        export_order = (
            "box_number",
            "pittag_id",
            "batch_number",
            "comments",
            "issue_location",
            "field_person_id",
            "tag_order_id",
            "pit_tag_status",
        )


@admin.register(TrtPitTags)
class TrtPitTagsAdmin(ImportExportModelAdmin):
    resource_class = TrtPitTagsResource
    list_display = ("pittag_id", "linked_turtle", "issue_location", "linked_custodian_person", "pit_tag_status", "comments")
    list_filter = ["pit_tag_status"]
    search_fields = ["pittag_id"]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('turtle', 'custodian_person')

    def linked_turtle(self, obj):
        if obj.turtle:
            url = reverse('admin:wamtram2_trtturtles_change', args=[obj.turtle.pk])
            return format_html('<a href="{}">{}</a>', url, obj.turtle)
        return "-"
    linked_turtle.short_description = 'Turtle'
    
    def linked_custodian_person(self, obj):
        if obj.custodian_person:
            url = reverse('admin:wamtram2_trtpersons_change', args=[obj.custodian_person.pk])
            return format_html('<a href="{}">{}</a>', url, obj.custodian_person)
        return "-"
    linked_custodian_person.short_description = 'Custodian Person'


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
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


@admin.register(TrtNestingSeason)
class TrtNestingSeasonAdmin(admin.ModelAdmin):
    form = TrtNestingSeasonForm
    list_display = ['nesting_season', 'startdate', 'enddate']
    search_fields = ['nesting_season']
    list_filter = ['startdate', 'enddate']
    class Media:
        css = {
            'all': ('https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css',)
        }
        js = (
            'https://cdn.jsdelivr.net/npm/flatpickr',
            'js/admin/custom_flatpickr.js',
        )
        

@admin.register(TrtDamageCauseCodes)
class TrtDamageCauseCodesAdmin(admin.ModelAdmin):
    list_display = ('damage_cause_code', 'description')
    search_fields = ('damage_cause_code', 'description')


@admin.register(TrtDamageCodes)
class TrtDamageCodesAdmin(admin.ModelAdmin):
    list_display = ('damage_code', 'description', 'flipper')
    search_fields = ('damage_code', 'description')
    

@admin.register(TrtLocations)
class TrtLocationsAdmin(admin.ModelAdmin):
    list_display = ('location_code', 'location_name')
    search_fields = ('location_code', 'location_name')
    
    
    
