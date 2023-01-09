import os

import logging

# import pypandoc
from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
from django_fsm_log.models import StateLog
from rest_framework.authtoken.models import Token

from observations.models import OBSERVATION_ICONS, OBSERVATION_COLOURS, Encounter

logger = logging.getLogger(__name__)
register = template.Library()


@register.simple_tag
def google_maps_apikey(*args, **kwargs):
    """Return the settings key GOOGLE_MAPS_API_KEY."""
    return settings.GOOGLE_MAPS_API_KEY


@register.simple_tag
def apitoken(user, **kwargs):
    return Token.objects.get_or_create(user=user)[0].key


@register.inclusion_tag("tx_logs.html", takes_context=False)
def tx_logs(obj):
    """Render the FSM transition logs for an object to HTML."""
    return {"logs": [log for log in StateLog.objects.for_(obj)]}


@register.filter
@stringfilter
def mm_as_cm(mm_value):
    """Turn a given mm value into a cm value."""
    if mm_value == "None":
        return None
    return float(mm_value) / 10


@register.filter
@stringfilter
def mm_as_m(mm_value):
    """Turn a given mm value into a m value."""
    if mm_value == "None":
        return None
    return float(mm_value) / 1000


@register.filter
@stringfilter
def tb_status_icon(status_value):
    """Turn a given status value into a complete twitter-boootstrap v4 CSS class.

    Uses ``Encounter.STATUS_LABELS`` to resolve values for:

    * new = red
    * proofread = orange
    * curated = blue
    * published = green
    """
    return Encounter.STATUS_LABELS[status_value]


@register.filter
@stringfilter
def fa_observation_icon(observation_value):
    """Turn a given accuracy value into a complete fontawesome icon class.

    Uses ``observations.OBSERVATION_ICONS`` to resolve values for:

    * present: confirmed yes
    * absent: confirmed no
    * na: did not measure
    """
    return OBSERVATION_ICONS[observation_value]


@register.filter
@stringfilter
def obs_colour(observation_value):
    """Turn a given present/absent/na value into a twitter-bootstrap colour

    Uses ``observations.OBSERVATION_ICONS`` to resolve values for:

    * present: primary
    * absent: secondary
    * na: dark

    Key errors indicate that the obs_colour tag wasn't called on the correct instance.
    E.g. an Encounter card was rendered with a Survey as object.
    """
    if observation_value == "":
        observation_value = "na"
    try:
        col = OBSERVATION_COLOURS[observation_value]
    except:
        logger.warning(
            "Not found: OBSERVATION_COLOURS key {0}".format(observation_value)
        )
        col = "secondary"
    return col


@register.filter
def filename(value):
    return os.path.basename(value)


# @register.filter
# @stringfilter
# def tex(string_value):
#    """Convert a text or HTML string to tex."""
#    return pypandoc.convert_text(string_value, 'tex', format='html')
