# -*- coding: utf-8 -*-
"""Shared filter utilities."""
from collections import OrderedDict  # noqa
from dateutil.relativedelta import relativedelta

from django.contrib.gis.db import models as geo_models
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

import django_filters
from leaflet.forms.widgets import LeafletWidget

from shared.admin import LEAFLET_SETTINGS


class CustomDateRangeFilter(django_filters.DateRangeFilter):
    """A django-filters DateRangeFilter with useful presets."""

    choices = [
        # ('today', _('Today')),
        # ('yesterday', _('Yesterday')),
        ('past-six-months', _('Within past 6 months')),
        ('past-three-months', _('Within past 3 months')),
        ('this-month', _('This month')),
        # ('past-week', _('Within past week')),
        ('next-three-months', _('Within next 3 months')),
        ('next-six-months', _('Within next 6 months')),
        ('this-year', _('Anytime this year')),
    ]

    filters = {
        # 'today': lambda qs, name: qs.filter(**{
        #     '%s__year' % name: now().date().year,
        #     '%s__month' % name: now().date().month,
        #     '%s__day' % name: now().date().day
        # }),
        # 'yesterday': lambda qs, name: qs.filter(**{
        #     '%s__year' % name: (now().date() - relativedelta(days=+1)).year,
        #     '%s__month' % name: (now().date() - relativedelta(days=+1)).month,
        #     '%s__day' % name: (now().date() - relativedelta(days=+1)).day,
        # }),
        # 'past-week': lambda qs, name: qs.filter(**{
        #     '%s__gte' % name: now().date() - relativedelta(days=-7),
        #     '%s__lt' % name: now().date() + relativedelta(days=+1),
        # }),
        'this-month': lambda qs, name: qs.filter(**{
            '%s__year' % name: now().year,
            '%s__month' % name: now().month
        }),
        'this-year': lambda qs, name: qs.filter(**{
            '%s__year' % name: now().year,
        }),
        'past-three-months': lambda qs, name: qs.filter(**{
            '%s__gte' % name: now().date() + relativedelta(months=-3),
            '%s__lt' % name: now().date(),
        }),
        'past-six-months': lambda qs, name: qs.filter(**{
            '%s__gte' % name: now().date() + relativedelta(months=-6),
            '%s__lt' % name: now().date(),
        }),
        'next-three-months': lambda qs, name: qs.filter(**{
            '%s__gte' % name: now().date(),
            '%s__lt' % name: now().date() + relativedelta(months=+3),
        }),
        'next-six-months': lambda qs, name: qs.filter(**{
            '%s__gte' % name: now().date(),
            '%s__lt' % name: now().date() + relativedelta(months=+6),
        }),
    }


class CustomDateTimeRangeFilter(django_filters.DateRangeFilter):
    """A django-filters DateTimeRangeFilter with useful presets."""

    choices = [
        # ('today', _('Today')),
        # ('yesterday', _('Yesterday')),
        ('past-six-months', _('Within past 6 months')),
        ('past-three-months', _('Within past 3 months')),
        ('this-month', _('This month')),
        # ('past-week', _('Within past week')),
        ('next-three-months', _('Within next 3 months')),
        ('next-six-months', _('Within next 6 months')),
        ('this-year', _('Anytime this year')),
    ]

    filters = {
        # 'today': lambda qs, name: qs.filter(**{
        #     '%s__year' % name: now().date().year,
        #     '%s__month' % name: now().date().month,
        #     '%s__day' % name: now().date().day
        # }),
        # 'yesterday': lambda qs, name: qs.filter(**{
        #     '%s__year' % name: (now().date() - relativedelta(days=+1)).year,
        #     '%s__month' % name: (now().date() - relativedelta(days=+1)).month,
        #     '%s__day' % name: (now().date() - relativedelta(days=+1)).day,
        # }),
        # 'past-week': lambda qs, name: qs.filter(**{
        #     '%s__gte' % name: now().date() - relativedelta(days=-7),
        #     '%s__lt' % name: now().date() + relativedelta(days=+1),
        # }),
        'this-month': lambda qs, name: qs.filter(**{
            '%s__year' % name: now().year,
            '%s__month' % name: now().month
        }),
        'this-year': lambda qs, name: qs.filter(**{
            '%s__year' % name: now().year,
        }),
        'past-three-months': lambda qs, name: qs.filter(**{
            '%s__gte' % name: now() + relativedelta(months=-3),
            '%s__lt' % name: now(),
        }),
        'past-six-months': lambda qs, name: qs.filter(**{
            '%s__gte' % name: now() + relativedelta(months=-6),
            '%s__lt' % name: now(),
        }),
        'next-three-months': lambda qs, name: qs.filter(**{
            '%s__gte' % name: now(),
            '%s__lt' % name: now() + relativedelta(months=+3),
        }),
        'next-six-months': lambda qs, name: qs.filter(**{
            '%s__gte' % name: now(),
            '%s__lt' % name: now() + relativedelta(months=+6),
        }),
    }

FILTER_OVERRIDES = {
    models.CharField: {
        'filter_class': django_filters.CharFilter,
        'extra': lambda f: {'lookup_expr': 'icontains', },
    },
    models.TextField: {
        'filter_class': django_filters.CharFilter,
        'extra': lambda f: {'lookup_expr': 'icontains', },
    },
    models.DateField: {
        'filter_class': CustomDateRangeFilter,
    },
    models.DateTimeField: {
        'filter_class': CustomDateTimeRangeFilter,
    },
    geo_models.PointField: {
        'filter_class': django_filters.CharFilter,
        'extra': lambda f: {
            'lookup_expr': 'intersects',
            'widget': LeafletWidget(attrs=LEAFLET_SETTINGS)
        },
    },
    geo_models.PolygonField: {
        'filter_class': django_filters.CharFilter,
        'extra': lambda f: {
            'lookup_expr': 'intersects',
            'widget': LeafletWidget(attrs=LEAFLET_SETTINGS)
        },
    },
    geo_models.MultiPolygonField: {
        'filter_class': django_filters.CharFilter,
        'extra': lambda f: {
            'lookup_expr': 'intersects',
            'widget': LeafletWidget(attrs=LEAFLET_SETTINGS)
        },
    }
}
