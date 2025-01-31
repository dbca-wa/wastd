from django import template

register = template.Library()

@register.filter
def get_dud_status(current_status, tag_id):
    """
    Get the status description for a DUD tag
    """
    if not current_status or not tag_id:
        return "No Status"
    
    return str(current_status)

@register.filter
def startswith(text, starts):
    """
    Returns True if the value starts with the argument
    """
    if text is None:
        return False
    return str(text).startswith(str(starts))