from django import template

from django_fsm_log.models import StateLog

register = template.Library()


@register.inclusion_tag('tx_logs.html', takes_context=False)
def tx_logs(obj):
    """Renders the FSM transition logs for an object."""
    return {'logs': [log for log in StateLog.objects.for_(obj)]}
