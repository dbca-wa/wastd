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


@register.inclusion_tag('include/taxongazettal_add.html', takes_context=True)
def taxongazettal_add(context, user):
    """Render an "add cons listing" link for staff."""
    return {
        "original": context["original"],
        "is_staff": user.is_staff
    }


@register.inclusion_tag('include/communitygazettal_add.html', takes_context=True)
def communitygazettal_add(context, user):
    """Render an "add cons listing" link for staff."""
    return {
        "original": context["original"],
        "is_staff": user.is_staff
    }


@register.inclusion_tag('include/document.html', takes_context=True)
def document_listgroupitem(context, user):
    """Render a Document in a card."""
    return {
        "original": context["original"],
        "is_staff": user.is_staff
    }


@register.inclusion_tag('include/document_add.html', takes_context=True)
def document_add(context, user, subject):
    """Render an "add document" link for staff."""
    return {
        "original": context["original"],
        "is_staff": user.is_staff,
        "subject": subject
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
