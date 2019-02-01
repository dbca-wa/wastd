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


@register.inclusion_tag('occurrence/include/admin_areaencounter_create_link.html', takes_context=False)
def admin_areaencounter_create_link(pk, subject, block=False, label=False):
    """Render an "add occurrence" link for staff."""
    return {
        "pk": pk,
        "subject": subject,
        "change_url": reverse('admin:occurrence_{0}areaencounter_add'.format(subject)),
        "block": block,
        "label": label
    }


@register.inclusion_tag('occurrence/include/admin_absoluteadminurl_link.html', takes_context=False)
def admin_absoluteadminurl_link(original, block=False, label=False):
    """Render an "add occurrence" link for staff."""
    return {
        "change_url": original.absolute_admin_url,
        "block": block,
        "label": label
    }


@register.inclusion_tag('occurrence/include/admin_taxonareaencounter_list_link.html', takes_context=False)
def admin_taxonareaencounter_list_link(pk, block=False, label=False):
    """Render an "list taxon area occurrences" link for a taxon."""
    return {
        "pk": pk,
        "block": block,
        "label": label
    }


@register.inclusion_tag('occurrence/include/taxonareaencounter_add_link.html', takes_context=True)
def taxonareaencounter_add_link(context, area_code=None, block=False, label=False):
    """Render an "add taxon area occurrence" link for a taxon."""
    return {
        "original": context["original"],
        "area_code": area_code,
        "block": block,
        "label": label
    }


@register.inclusion_tag('occurrence/include/taxonareaencounter_card.html', takes_context=False)
def taxonareaencounter_card(occurrence, user, block=False, label=False):
    """Render a card for a taxon area encounter."""
    return {
        "original": occurrence,
        "is_staff": user.is_staff,
        "block": block,
        "label": label
    }
