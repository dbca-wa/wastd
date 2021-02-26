# -*- coding: utf-8 -*-
"""Filters for WAStD Users."""
# from leaflet.forms.widgets import LeafletWidget
# import rest_framework_filters as filters
# import logging
# from django.contrib.admin import SimpleListFilter
# from django.contrib.gis.db import models as geo_models
# from django.utils.translation import ugettext_lazy as _
from django_filters import FilterSet
from django_filters.filters import (  # noqa
    BooleanFilter, CharFilter, RangeFilter,
    ChoiceFilter, MultipleChoiceFilter,
    ModelChoiceFilter, ModelMultipleChoiceFilter)
from shared.filters import FILTER_OVERRIDES
from wastd.users.models import User

# logger = logging.getLogger(__name__)


class UserFilter(FilterSet):
    """User Filter.

    https://django-filter.readthedocs.io/en/latest/usage.html
    """

    class Meta:
        """Options for EncounterFilter."""
        model = User
        filter_overrides = FILTER_OVERRIDES
        fields = [
            'username',
            'name',
            'nickname',
            'aliases',
            'role',
            'email',
            'phone',
            'affiliation',
            'is_staff',
            'is_active',
            'date_joined',
            'last_login',
            'is_superuser',
        ]
