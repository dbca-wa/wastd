# -*- coding: utf-8 -*-
"""Template tags for occurrence."""
# import json

# import django
# from django.contrib.admin.util import lookup_field, quote
# from django.conf import settings
from django.urls import reverse  # resolve
# from django.utils.encoding import force_str
from django import template


register = template.Library()


@register.inclusion_tag('occurrence/include/areaencounter_add.html', takes_context=True)
def areaencounter_add(context, user, subject, block=False, show_label_text=False):
    """Render an "add occurrence" link for staff."""
    return {
        "original": context["original"],
        "is_staff": user.is_staff,
        "block": block,
        "subject": subject,
        "change_url": reverse('admin:occurrence_{0}areaencounter_add'.format(subject)),
        "show_label_text": show_label_text
    }


@register.inclusion_tag('occurrence/include/taxonareaencounter_add.html', takes_context=True)
def taxonareaencounter_add(context, user, area_code=None, block=False, show_label_text=False):
    """Render an "add taxon area occurrence" link for a taxon."""
    return {
        "original": context["original"],
        "is_staff": user.is_staff,
        "area_code": area_code,
        "block": block,
        "show_label_text": show_label_text
    }


@register.inclusion_tag('occurrence/include/taxonareaencounter_list.html', takes_context=True)
def taxonareaencounter_list(context, user, block=False, show_label_text=False):
    """Render an "list taxon area occurrences" link for a taxon."""
    return {
        "original": context["original"],
        "is_staff": user.is_staff,
        "block": block,
        "show_label_text": show_label_text
    }


@register.inclusion_tag('occurrence/include/taxonareaencounter_card.html', takes_context=True)
def taxonareaencounter_card(context, user, subject, block=False, show_label_text=False):
    """Render a card for a taxon area encounter."""
    return {
        "original": subject,
        "is_staff": user.is_staff,
        "block": block,
        "show_label_text": show_label_text
    }
