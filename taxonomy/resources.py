# -*- coding: utf-8 -*-
"""Taxonomy resources."""
from import_export import resources

from taxonomy import models as tax_models


class TaxonResource(resources.ModelResource):
    """Taxon resource class for CSV download."""

    class Meta:
        """Class opts."""

        model = tax_models.Taxon
        fields = [
            "name_id",
            "taxonomic_name",
            "vernacular_names",
            "field_code",
            "get_publication_status_display",
            "current"
        ]


class CommunityResource(resources.ModelResource):
    """Community resource class for CSV download."""

    class Meta:
        """Class opts."""

        model = tax_models.Community
        # fields = [
        #     "code",
        #     "name",
        #     "description",
        # ]
