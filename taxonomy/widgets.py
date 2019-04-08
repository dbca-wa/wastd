# -*- coding: utf-8 -*-
"""Taxonomy widgets."""
from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget
from taxonomy import models as tax_models


class TaxonWidget(ModelSelect2Widget):
    """A reusable Taxon ModelSelect2Widget."""

    model = tax_models.Taxon
    queryset = tax_models.Taxon.objects.filter(current=True)
    search_fields = [
        "taxonomic_name__icontains",
        "vernacular_names__icontains",
        "field_code__icontains"
    ]


class TaxonMultipleWidget(ModelSelect2MultipleWidget):
    """A reusable Taxon ModelSelect2MultipleWidget."""

    model = tax_models.Taxon
    queryset = tax_models.Taxon.objects.filter(current=True)
    search_fields = [
        "taxonomic_name__icontains",
        "vernacular_names__icontains",
        "field_code__icontains"
    ]


class CommunityWidget(ModelSelect2Widget):
    """Community ModelSelect2Widget."""

    model = tax_models.Community
    search_fields = [
        "code__icontains",
        "name__icontains",
        "description__icontains",
    ]


class CommunityMultipleWidget(ModelSelect2MultipleWidget):
    """Community ModelSelect2MultipleWidget."""

    model = tax_models.Community
    search_fields = [
        "code__icontains",
        "name__icontains",
        "description__icontains",
    ]
