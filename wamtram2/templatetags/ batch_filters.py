from django import template

register = template.Library()

@register.filter
def getattribute(obj, field):
    """Get object attribute, supports dot notation"""
    try:
        for part in field.split('.'):
            obj = getattr(obj, part)
        return obj
    except (AttributeError, TypeError):
        return ''