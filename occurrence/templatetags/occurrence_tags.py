# -*- coding: utf-8 -*-
"""Template tags for occurrence."""
# import json
# import django
# from django.utils.encoding import force_str
from django import template
# from django.contrib.admin.util import lookup_field, quote
# from django.conf import settings
# from django.urls import reverse  # resolve
from shared.utils import sanitize_tag_label

register = template.Library()

register.filter('sanitize_tag_label', sanitize_tag_label)
