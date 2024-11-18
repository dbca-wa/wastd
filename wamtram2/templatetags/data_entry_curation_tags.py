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