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
def areaencounter_add(context, user, subject, block=True, show_label_text=True):
    """Render an "add occurrence" link for staff."""
    return {
        "original": context["original"],
        "is_staff": user.is_staff,
        "block": block,
        "subject": subject,
        "change_url": reverse('admin:occurrence_{0}areaencounter_add'.format(subject)),
        "show_label_text": show_label_text
    }
