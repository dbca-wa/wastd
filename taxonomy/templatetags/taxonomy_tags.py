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
    """Return an xrange around a given number."""
    span = 5
    min_val = max(value - span, 1)
    max_val = max(value + span, span * 2)
    return xrange(min_val, max_val)


@register.inclusion_tag('include/gazettal.html', takes_context=True)
def gazettal_labels(context, user):
    """Render a Gazettal as label."""
    return {
        "original": context["original"],
        "is_staff": user.is_staff
    }


@register.inclusion_tag('include/taxon_change.html', takes_context=True)
def admin_taxon_change_link(context, user, btn=True, block=False, label=False):
    """Render a link to the admin taxon change view."""
    return {
        "original": context["original"],
        "is_staff": user.is_staff,
        "btn": btn,
        "block": block,
        "label": label
    }


@register.inclusion_tag('include/taxon_detail.html', takes_context=True)
def taxon_detail(context, block=False, show_label_text=False):
    """Render a link to the taxon detail view."""
    return {
        "original": context["original"],
        "block": block,
        "show_label_text": show_label_text
    }


@register.inclusion_tag('include/gazettal_row.html', takes_context=True)
def taxongazettal_rows(context, user):
    """Render a Gazettal as row."""
    return {
        "original": context["original"],
        "is_staff": user.is_staff,
        "gazettals": context["original"].taxon_gazettal.all
    }


@register.inclusion_tag('include/gazettal_row.html', takes_context=True)
def communitygazettal_rows(context, user):
    """Render a Gazettal as row."""
    return {
        "original": context["original"],
        "is_staff": user.is_staff,
        "gazettals": context["original"].community_gazettal.all
    }


@register.inclusion_tag('include/taxongazettal_add.html', takes_context=True)
def taxongazettal_add(context, user, block=False, show_label_text=False):
    """Render an "add cons listing" link for staff."""
    return {
        "original": context["original"],
        "is_staff": user.is_staff,
        "block": block,
        "show_label_text": show_label_text
    }


@register.inclusion_tag('include/communitygazettal_add.html', takes_context=True)
def communitygazettal_add(context, user, block=False, show_label_text=False):
    """Render an "add cons listing" link for staff."""
    return {
        "original": context["original"],
        "is_staff": user.is_staff,
        "block": block,
        "show_label_text": show_label_text
    }


@register.inclusion_tag('include/document.html', takes_context=True)
def document_listgroupitem(context, user):
    """Render a Document in a card listgroup item."""
    return {
        "original": context["original"],
        "is_staff": user.is_staff
    }


@register.inclusion_tag('include/document_row.html', takes_context=True)
def document_row(context, user):
    """Render a Document in a card."""
    return {
        "original": context["original"],
        "is_staff": user.is_staff,
        "user": user
    }


@register.inclusion_tag('include/document_add.html', takes_context=True)
def document_add(context, user, subject, block=False, show_label_text=False):
    """Render an "add document" link for staff."""
    return {
        "original": context["original"],
        "is_staff": user.is_staff,
        "subject": subject,
        "block": block,
        "show_label_text": show_label_text
    }


@register.inclusion_tag('include/conservationaction_rows.html', takes_context=False)
def conservationaction_rows(user, actions, area=None):
    """Render a conservation Action in a row."""
    return {
        "is_staff": user.is_staff,
        "actions": actions.filter(occurrence_area_code=area) if area else actions
    }


@register.inclusion_tag('include/conservationaction_cards.html', takes_context=False)
def conservationaction_cards(user, actions, area=None):
    """Render a conservation Action in a card."""
    return {
        "is_staff": user.is_staff,
        "actions": actions.filter(occurrence_area_code=area) if area else actions
    }


@register.inclusion_tag('include/conservationaction_add.html', takes_context=True)
def conservationaction_add(context, user, subject, document=None, area=None, block=False, show_label_text=False):
    """Render an "add conservation action" link for staff."""
    return {
        "original": context["original"],
        "is_staff": user.is_staff,
        "subject": subject,
        "document": document,
        "area": area,
        "block": block,
        "show_label_text": show_label_text
    }


@register.inclusion_tag('include/vernaculars.html', takes_context=True)
def vernacular_names(context):
    """Render a Taxon's vernacular names in a card."""
    return {
        "original": context["original"],
    }


@register.inclusion_tag('include/taxonomic_status.html', takes_context=True)
def taxonomic_status(context):
    """Render a Taxon's taxonomic status in a card."""
    return {
        "original": context["original"],
    }
