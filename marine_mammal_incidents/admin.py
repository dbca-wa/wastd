#from datetime import datetime
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from marine_mammal_incidents.models import Incident, Species, Uploaded_file
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget
from django.contrib.gis.geos import Point
from django.contrib.gis.db import models
from mapwidgets.widgets import MapboxPointFieldWidget


class UploadedFileAdmin(admin.StackedInline):
    model = Uploaded_file
    verbose_name = "File"  # Singular name for one object
    verbose_name_plural = "Files and photos"  # Plural name for more than one object
    extra = 0

# Define a custom resource class for the Incident model
class IncidentResource(resources.ModelResource):
    species_name = Field(attribute='species', column_name='species',widget=ForeignKeyWidget(Species, field='scientific_name'))
    latitude = Field(attribute='latitude', column_name='latitude')
    longitude = Field(attribute='longitude', column_name='longitude')

    def dehydrate_latitude(self, incident):
        return incident.geo_location.y if incident.geo_location else None

    def dehydrate_longitude(self, incident):
        return incident.geo_location.x if incident.geo_location else None
    
    class Meta:
        model = Incident
        #exclude = ('geo_location',)
        import_id_fields = ['id']
        fields = [field.name for field in model._meta.fields if field.name != 'species']
    
    def before_import_row(self, row, **kwargs):
        # Convert latitude and longitude to Point
        latitude = row.get('latitude')
        longitude = row.get('longitude')
        if latitude and longitude:
            row['geo_location'] = Point(float(longitude), float(latitude))
        
    
    
        
@admin.register(Incident)
class IncidentAdmin(ImportExportModelAdmin):
    
    #list_display = ('id','species','incident_date')
    date_hierarchy = "incident_date"
    inlines = [UploadedFileAdmin]
    resource_class = IncidentResource  # Use the custom resource class
    list_filter = ['species__common_name','species__scientific_name','incident_date','mass_incident','sex','age_class','condition_when_found','outcome','post_mortem']
    #search_fields = ('comments',)
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.list_display = [field.name for field in model._meta.fields] + ['latitude', 'longitude']

    def latitude(self, obj):
        """Make data source readable."""
        return obj.geo_location.y if obj.geo_location else None
    latitude.short_description = "Latitude"

    def longitude(self, obj):
        """Make data source readable."""
        return obj.geo_location.x if obj.geo_location else None
    longitude.short_description = "Longitude"

    formfield_overrides = {
        models.PointField: {"widget": MapboxPointFieldWidget}
    }

@admin.register(Species)
class SpeciesAdmin(ImportExportModelAdmin):
    list_display = ('common_name', 'scientific_name')

@admin.register(Uploaded_file)
class UploadedFileAdmin(admin.ModelAdmin):
    pass