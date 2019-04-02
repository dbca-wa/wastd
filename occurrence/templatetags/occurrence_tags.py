# -*- coding: utf-8 -*-
"""Template tags for occurrence."""
# import json


# import django
# from django.utils.encoding import force_str
from django import template
# from django.contrib.admin.util import lookup_field, quote
# from django.conf import settings
from django.urls import reverse  # resolve
from shared.utils import sanitize_tag_label

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
def admin_absoluteadminurl_link(original, subject, block=False, label=False):
    """Render a link to the original's admin change_view."""
    return {
        "change_url": original.absolute_admin_url,
        "subject": subject,
        "block": block,
        "label": label
    }


@register.inclusion_tag('occurrence/include/admin_areaencounter_list_link.html', takes_context=False)
def admin_areaencounter_list_link(pk, subject, block=False, label=False):
    """Render an "list subject area occurrences" link for a subject."""
    return {
        "list_url": reverse('admin:occurrence_{0}areaencounter_changelist'.format(subject)) +
        "?{0}__id__exact={1}".format(subject, pk),
        "pk": pk,
        "subject": subject,
        "block": block,
        "label": label
    }


@register.inclusion_tag('occurrence/include/areaencounter_add_link.html', takes_context=False)
def taxonareaencounter_add_link(name_id, area_code=None, block=False, label=False):
    """Render an "add taxon area occurrence" link for a taxon."""
    if area_code:
        add_url = reverse('occurrence:taxon-occurrence-area-create',
                          kwargs={'name_id': name_id,
                                  'area_code': sanitize_tag_label(area_code)})
    else:
        add_url = reverse("occurrence:taxon-occurrence-create",
                          kwargs={"name_id": name_id})

    return {
        "add_url": add_url,
        "subject": "taxon",
        "area_code": sanitize_tag_label(area_code),
        "block": block,
        "label": label
    }


@register.inclusion_tag('occurrence/include/areaencounter_add_link.html', takes_context=False)
def communityareaencounter_add_link(pk, area_code=None, block=False, label=False):
    """Render an "add community area occurrence" link for a community."""
    if area_code:
        add_url = reverse('occurrence:community-occurrence-area-create',
                          kwargs={'pk': pk, 'area_code': sanitize_tag_label(area_code)})
    else:
        add_url = reverse('occurrence:community-occurrence-create',
                          kwargs={'pk': pk})

    return {
        "add_url": add_url,
        "subject": "community",
        "area_code": sanitize_tag_label(area_code),
        "block": block,
        "label": label
    }


@register.inclusion_tag('occurrence/include/areaencounter_card.html', takes_context=False)
def areaencounter_card(occurrence, subject, user, block=False, label=False):
    """Render a card for a taxon or comunity area encounter."""
    return {
        "object": occurrence,
        "subject": subject,
        "is_staff": user.is_staff,
        "block": block,
        "label": label
    }


@register.inclusion_tag('occurrence/include/areaencounter_detail_link.html', takes_context=False)
def taxonareaencounter_detail_link(original, block=False, label=False):
    """Render an "view taxon area occurrence" link for a taxon."""
    return {
        "detail_url": original.get_absolute_url(),
        "subject": "taxon",
        "block": block,
        "label": label
    }


@register.inclusion_tag('occurrence/include/areaencounter_detail_link.html', takes_context=False)
def communityareaencounter_detail_link(original, block=False, label=False):
    """Render an "view community area occurrence" link for a community."""
    return {
        "detail_url": original.get_absolute_url(),
        "subject": "community",
        "block": block,
        "label": label
    }


@register.inclusion_tag('occurrence/include/areaencounter_update_link.html', takes_context=False)
def areaencounter_update_link(original, block=False, label=False):
    """Render an "update taxon area occurrence" link for a taxon."""
    return {
        "update_url": original.update_url,
        "block": block,
        "label": label
    }


@register.inclusion_tag('occurrence/include/areaencounter_detail_link.html', takes_context=False)
def areaencounter_detail_link(original, block=False, label=False):
    """Render an "view area occurrence" link."""
    return {
        "detail_url": original.get_absolute_url(),
        "block": block,
        "label": label
    }
