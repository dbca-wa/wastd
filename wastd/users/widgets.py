# -*- coding: utf-8 -*-
"""User widgets."""
from django.contrib.auth import get_user_model

from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget


class UserWidget(ModelSelect2Widget):
    """User widget."""

    queryset = get_user_model().objects.filter(is_active=True)
    search_fields=[
                "pk__icontains",
                "username__icontains",
                "name__icontains",
                "aliases__icontains",
                "role__icontains",
                "affiliation__icontains",
                "email__icontains"]


class UserMultipleWidget(ModelSelect2MultipleWidget):
    """User widget."""

    queryset = get_user_model().objects.filter(is_active=True)
    search_fields=[
                "pk__icontains",
                "username__icontains",
                "name__icontains",
                "aliases__icontains",
                "role__icontains",
                "affiliation__icontains",
                "email__icontains"]
