# -*- coding: utf-8 -*-
"""Shared widgets."""
from django_select2.forms import ModelSelect2Widget  # ModelSelect2MultipleWidget
from occurrence import models as occ_models


class AreaEncounterWidget(ModelSelect2Widget):
    """A reusable AreaEncounter ModelSelect2Widget."""

    model = occ_models.AreaEncounter
    search_fields = [
        "code__icontains",
        "name__icontains",
        "area_type__label__icontains",
    ]
    attrs = {"size": 80}
