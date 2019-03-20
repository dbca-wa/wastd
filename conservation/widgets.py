# -*- coding: utf-8 -*-
"""Conservation widgets."""
from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget


from conservation import models as cons_models


class DocumentWidget(ModelSelect2Widget):
    """Document ModelSelect2Widget."""

    model = cons_models.Document
    search_fields = [
        "title__icontains",
        "comments__icontains",
    ]


class DocumentMultipleWidget(ModelSelect2MultipleWidget):
    """Document ModelSelect2MultipleWidget."""

    model = cons_models.Document
    search_fields = [
        "title__icontains",
        "comments__icontains",
    ]


class ConservationActionCategoryWidget(ModelSelect2Widget):
    """ConservationActionCategory ModelSelect2Widget."""

    model = cons_models.ConservationActionCategory
    search_fields = [
        "code__icontains",
        "label__icontains",
        "description__icontains",
    ]


class ConservationActionCategoryMultipleWidget(ModelSelect2MultipleWidget):
    """ConservationActionCategory ModelSelect2MultipleWidget."""

    model = cons_models.ConservationActionCategory
    search_fields = [
        "code__icontains",
        "label__icontains",
        "description__icontains",
    ]


class ConservationActionWidget(ModelSelect2Widget):
    """ConservationAction ModelSelect2Widget."""

    model = cons_models.ConservationAction
    search_fields = [
        "category__icontains",
        "instructions__icontains",
    ]


class ConservationActionMultipleWidget(ModelSelect2MultipleWidget):
    """ConservationAction ModelSelect2MultipleWidget."""

    model = cons_models.ConservationAction
    search_fields = [
        "category__icontains",
        "instructions__icontains",
    ]
