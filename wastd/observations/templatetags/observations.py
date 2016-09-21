from django import template

from django_fsm_log.models import StateLog
from django.template.defaultfilters import stringfilter, register
from wastd.observations.models import (
    Encounter, ACCURACY_ICONS, OBSERVATION_ICONS)

register = template.Library()

@register.inclusion_tag('tx_logs.html', takes_context=False)
def tx_logs(obj):
    """Render the FSM transition logs for an object."""
    return {'logs': [log for log in StateLog.objects.for_(obj)]}


@register.filter
@stringfilter
def tb_status_icon(status_value):
    """Turn a given status value into a complete twitter-boootstrap v4 CSS class.

    Uses ``Encounter.STATUS_LABELS`` to resolve values for:

    * new
    * proofread
    * curated
    * published
    """
    return "tag tag-{0}".format(Encounter.STATUS_LABELS[status_value])


@register.filter
@stringfilter
def fa_accuracy_icon(accuracy_value):
    """Turn a given accuracy value into a complete fontawesome icon class.

    Uses ``wastd.observations.ACCURACY_ICONS`` to resolve values for:

    * measured
    * estimated
    * unknown
    """
    return ACCURACY_ICONS[accuracy_value]


@register.filter
@stringfilter
def fa_observation_icon(observation_value):
    """Turn a given accuracy value into a complete fontawesome icon class.

    Uses ``wastd.observations.OBSERVATION_ICONS`` to resolve values for:

    * present: confirmed yes
    * absent: confirmed no
    * na: did not measure
    """
    return OBSERVATION_ICONS[observation_value]
