from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter(name='perth_time')
def perth_time(value):
    if isinstance(value, timezone.datetime):
        return value - timedelta(hours=8)
    return value