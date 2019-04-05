# -*- coding: utf-8 -*-
"""User widgets."""
from django.contrib.auth import get_user_model

from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget


class UserWidget(ModelSelect2Widget):
    """User widget."""

    model = get_user_model()
    queryset = get_user_model().objects.all()
    search_fields = [
        "name__icontains",
        "username__icontains",
        "role__icontains",
        "email__icontains"
    ]


class UserMultipleWidget(ModelSelect2MultipleWidget):
    """User widget."""

    model = get_user_model()
    queryset = get_user_model().objects.all()
    search_fields = [
        "name__icontains",
        "username__icontains",
        "role__icontains",
        "email__icontains"
    ]
