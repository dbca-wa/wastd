from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter(name='perth_time')
def perth_time(value):
    if isinstance(value, timezone.datetime):
        return value + timedelta(hours=8)
    return value

@register.filter(name='perth_date')
def perth_date(value):
    if isinstance(value, timezone.datetime):
        perth_datetime = value + timedelta(hours=8)
        return perth_datetime.date()
    return value

@register.filter(name='perth_time_only')
def perth_time_only(value):
    if isinstance(value, timezone.datetime):
        perth_datetime = value + timedelta(hours=8)
        return perth_datetime.time()
    return value