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
    span = 5
    min_val = max(value - span, 1)
    max_val = max(value + span, span * 2)
    return xrange(min_val, max_val)
