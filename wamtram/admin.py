from django.contrib import admin
from .models import TrtTurtles


@admin.register(TrtTurtles)
class TrtTurtlesAdmin(admin.ModelAdmin):
    list_display = (
        'turtle_id', 'species_code', 'sex', 'turtle_status', 'location_code', 'date_entered', 'turtle_name', 'cause_of_death',
    )
    search_fields = (
        'turtle_id', 'species_code__common_name', 'location_code__location_name', 'turtle_name',  # 'comments', 'tag',
        'pit_tags__pit_tag_id', 'tags__tag_id',
    )
    readonly_fields = (
        'turtle_id', 'species_code', 'identification_confidence', 'turtle_status', 'location_code', 'cause_of_death', 're_entered_population',
        'comments', 'entered_by', 'date_entered', 'original_turtle_id', 'entry_batch_id', 'tag', 'mund_id', 'turtle_name',
    )
