from django.contrib import admin
import nested_admin
from .models import TrtTurtles, TrtObservations, TrtTags,TrtPitTags,TrtMeasurements,TrtDamage,TrtDataEntry ,TrtEntryBatches, TrtTagOrders
from import_export.admin import ImportExportModelAdmin
#from easy_select2 import select2_modelform
from .forms import DataEntryUserModelForm, EnterUserModelForm
        
#nested admin forms
class TrtMeasurementsInline(nested_admin.NestedTabularInline):
    model = TrtMeasurements
    #form = TrtMeasurementsForm
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
    #form = select2_modelform(TrtTags, attrs={'width': '250px'})

class TrtPitTagsInline(nested_admin.NestedStackedInline):
    model = TrtPitTags
    verbose_name = "Pit Tag"  # Singular name for one object
    extra = 0

class TrtDamageInline(nested_admin.NestedStackedInline):
    model = TrtDamage
    verbose_name = "Damage"  # Singular name for one object
    extra = 0

class TrtDataEntryInline(admin.StackedInline):
    model = TrtDataEntry
    verbose_name = "Data entry"
    form = DataEntryUserModelForm
    extra = 0

@admin.register(TrtEntryBatches)
class TrtEntryBatchesAdmin(admin.ModelAdmin):
    list_display = ('entry_batch_id','entry_date','entered_person_id','comments')
    ordering = ["-entry_batch_id"]
    inlines = [TrtDataEntryInline]
    form = EnterUserModelForm

@admin.register(TrtDataEntry)
class TrtDataEntryAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}

@admin.register(TrtTurtles)
class TrtTurtlesAdmin(ImportExportModelAdmin,nested_admin.NestedModelAdmin):
    
    list_display = ('turtle_id','species_code','turtle_name')
    date_hierarchy = "date_entered"
    ordering = ["date_entered"]
    list_filter = ['species_code','location_code']
    search_fields = ['turtle_id']
    inlines = [TrtObservationsInline,TrtTagsInline,TrtPitTagsInline]

@admin.register(TrtObservations)
class TrtObservationsAdmin(nested_admin.NestedModelAdmin):
    autocomplete_fields= ['turtle']
    list_display = ('observation_id','turtle','observation_date')
    date_hierarchy = "observation_date"
    list_filter = ['turtle__species_code','place_code']
    inlines = [TrtMeasurementsInline,TrtDamageInline]
    
    

@admin.register(TrtMeasurements)
class TrtMeasurementsdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}


@admin.register(TrtTags)
class TrtTagsAdmin(ImportExportModelAdmin):
    list_display = ('tag_id','turtle','tag_status')
    list_filter = ['tag_status']
    search_fields = ['tag_id']

@admin.register(TrtPitTags)
class TrtTagsAdmin(ImportExportModelAdmin):
    list_display = ('pittag_id','turtle','pit_tag_status')
    list_filter = ['pit_tag_status']
    search_fields = ['pittag_id']

@admin.register(TrtTagOrders)
class TrtTagOrdersAdmin(ImportExportModelAdmin):
    list_display = ('tag_order_id','order_date','order_number')
    list_filter = ['order_date']
    search_fields = ['tag_order_id']
    verbose_name = "Tag Order"  # Singular name for one object
    verbose_name_plural = "Tag Orders"



