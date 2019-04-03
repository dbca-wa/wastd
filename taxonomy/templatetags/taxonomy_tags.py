# -*- coding: utf-8 -*-
"""Template tags for taxonomy."""
# import json

# import django
# from django.contrib.admin.util import lookup_field, quote
# from django.conf import settings
# from django.core.urlresolvers import resolve, reverse
# from django.utils.encoding import force_str
from django import template

register = template.Library()


@register.filter
def rangify(value):
    """Return a range around a given number."""
    span = 5
    min_val = max(value - span, 1)
    max_val = max(value + span, span * 2)
    return range(min_val, max_val)


@register.inclusion_tag('include/taxon_change.html', takes_context=True)
def admin_taxon_change_link(context, user, btn=True, block=False, label=False):
    """Render a link to the admin taxon change view."""
    return {
        "object": context["object"],
        "is_staff": user.is_staff,
        "btn": btn,
        "block": block,
        "label": label
    }


@register.inclusion_tag('include/taxon_detail.html', takes_context=True)
def taxon_detail(context, block=False, label=False):
    """Render a link to the taxon detail view."""
    return {
        "object": context["object"],
        "block": block,
        "label": label
    }


@register.inclusion_tag('include/gazettal_row.html', takes_context=True)
def taxongazettal_rows(context, user):
    """Render a Gazettal as row."""
    return {
        "object": context["object"],
        "is_staff": user.is_staff,
        "gazettals": context["object"].taxon_gazettal.all
    }


@register.inclusion_tag('include/gazettal_row.html', takes_context=True)
def communitygazettal_rows(context, user):
    """Render a Gazettal as row."""
    return {
        "object": context["object"],
        "is_staff": user.is_staff,
        "gazettals": context["object"].community_gazettal.all
    }


@register.inclusion_tag('include/taxongazettal_add.html', takes_context=True)
def taxongazettal_add(context, user, block=False, label=False):
    """Render an "add cons listing" link for staff."""
    return {
        "object": context["object"],
        "is_staff": user.is_staff,
        "block": block,
        "label": label
    }


@register.inclusion_tag('include/communitygazettal_add.html', takes_context=True)
def communitygazettal_add(context, user, block=False, label=False):
    """Render an "add cons listing" link for staff."""
    return {
        "object": context["object"],
        "is_staff": user.is_staff,
        "block": block,
        "label": label
    }


@register.inclusion_tag('include/document.html', takes_context=True)
def document_listgroupitem(context, user):
    """Render a Document in a card listgroup item."""
    return {
        "object": context["object"],
        "is_staff": user.is_staff
    }


@register.inclusion_tag('include/document_row.html', takes_context=True)
def document_row(context, user):
    """Render a Document in a card."""
    return {
        "object": context["object"],
        "is_staff": user.is_staff,
        "user": user
    }


@register.inclusion_tag('include/document_add.html', takes_context=True)
def document_add(context, subject, block=False, label=False):
    """Render an "add document" link for staff."""
    return {
        "object": context["object"],
        "is_staff": True,
        "subject": subject,
        "block": block,
        "label": label
    }


# -----------------------------------------------------------------------------
# Conservation threats
#
# @register.inclusion_tag('include/conservationthreat_rows.html', takes_context=False)
# def conservationthreat_rows(user, threats, area=None):
#     """Render a conservation threat in a row."""
#     return {
#         "is_staff": user.is_staff,
#         "threats": threats.filter(occurrence_area_code=area) if area else threats
#     }


@register.inclusion_tag('include/conservationthreat_cards.html', takes_context=False)
def conservationthreat_cards(user, threats, area=None):
    """Render a conservation threat in a card."""
    return {
        "is_staff": user.is_staff,
        "threats": threats.filter(occurrence_area_code=area) if area else threats
    }


@register.inclusion_tag('include/conservationthreat_add.html', takes_context=True)
def conservationthreat_add(context, user, subject,
                           document_id=None, area=None,
                           block=False, label=False):
    """Render an "add conservation threat" link for staff."""
    return {
        "object": context["object"],
        "is_staff": user.is_staff,
        "subject": subject,
        "document_id": document_id,
        "area": area,
        "block": block,
        "label": label
    }


# -----------------------------------------------------------------------------
# Conservation actions
#
# @register.inclusion_tag('include/conservationaction_rows.html', takes_context=False)
# def conservationaction_rows(user, actions, area=None):
#     """Render a conservation Action in a row."""
#     return {
#         "is_staff": user.is_staff,
#         "actions": actions.filter(occurrence_area_code=area) if area else actions
#     }


@register.inclusion_tag('include/conservationaction_cards.html', takes_context=False)
def conservationaction_cards(user, actions, area=None):
    """Render a conservation Action in a card."""
    return {
        "is_staff": user.is_staff,
        "actions": actions.filter(occurrence_area_code=area) if area else actions
    }


@register.inclusion_tag('include/conservationaction_add.html', takes_context=True)
def conservationaction_add(context, subject,
                           document_id=None, area=None,
                           block=False, label=False):
    """Render an "add conservation action" link for staff."""
    return {
        "object": context["object"],
        "is_staff": True,
        "subject": subject,
        "document_id": document_id,
        "area": area,
        "block": block,
        "label": label
    }


@register.inclusion_tag('include/vernaculars.html', takes_context=True)
def vernacular_names(context):
    """Render a Taxon's vernacular names in a card."""
    return {
        "object": context["object"],
    }


@register.inclusion_tag('include/taxonomic_status.html', takes_context=True)
def taxonomic_status(context):
    """Render a Taxon's taxonomic status in a card."""
    return {
        "object": context["object"],
    }
