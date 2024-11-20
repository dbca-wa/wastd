from django import template
from django.db.models import Model

register = template.Library()

@register.filter
def get_field_value(obj, field_name):
    """
    Get field value from an object, supporting foreign key relationships and regular fields
    
    Args:
        obj: The data object
        field_name: Name of the field
    
    Returns:
        Field value or None if not found
    """
    try:
        # Handle nested foreign key relationships (e.g., 'species_code.id')
        if '.' in field_name:
            parts = field_name.split('.')
            value = obj
            for part in parts:
                value = getattr(value, part, None)
                if value is None:
                    return None
            return value
            
        # Get regular field value
        value = getattr(obj, field_name)
        
        # If foreign key, return the related object
        if isinstance(value, Model):
            return value
            
        return value
    except (AttributeError, ValueError):
        return None
    

@register.filter
def is_tag_field(field_name, tag_type):
    tag_fields = {
        'new': ['new_left_tag_id', 'new_left_tag_id_2', 'new_right_tag_id', 'new_right_tag_id_2',
                'new_pittag_id', 'new_pittag_id_2', 'new_pittag_id_3', 'new_pittag_id_4'],
        'recapture': ['recapture_left_tag_id', 'recapture_left_tag_id_2', 'recapture_left_tag_id_3',
                    'recapture_right_tag_id', 'recapture_right_tag_id_2', 'recapture_right_tag_id_3',
                    'recapture_pittag_id', 'recapture_pittag_id_2', 'recapture_pittag_id_3',
                    'recapture_pittag_id_4'],
        'other': ['other_left_tag', 'other_right_tag', 'other_tags'],
        'dud': ['dud_flipper_tag', 'dud_flipper_tag_2', 'dud_pit_tag', 'dud_pit_tag_2']
    }
    return field_name in tag_fields.get(tag_type, [])
 