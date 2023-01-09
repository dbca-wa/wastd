# -*- coding: utf-8 -*-
"""Shared forms."""
from django import forms


class DateInput(forms.DateInput):
    """Bog standard date input."""

    input_type = "date"
    format = "%Y-%m-%d"


class DateTimeInput(forms.DateInput):
    """Bog standard datetime input."""

    input_type = "datetime-local"
    format = "%Y-%m-%d %H:%i"
