# -*- coding: utf-8 -*-
"""Taxonomy resources."""
from import_export import resources
from import_export.fields import Field

from taxonomy import models as tax_models


class TaxonResource(resources.ModelResource):
    """Taxon resource class for REsource download."""

    publication_status = Field(
        attribute='get_publication_status_display',
        column_name='publication_status')
    currently_listed = Field(
        attribute='is_currently_listed',
        column_name='currently_listed')
    currently_listed = Field(
        attribute='is_currently_listed',
        column_name='currently_listed')
    conservation_code_state = Field(
        attribute='conservation_code_state',
        column_name='conservation_code_state')
    conservation_list_state = Field(
        attribute='conservation_list_state',
        column_name='conservation_list_state')
    conservation_category_state = Field(
        attribute='conservation_category_state',
        column_name='conservation_category_state')
    conservation_categories_state = Field(
        attribute='conservation_categories_state',
        column_name='conservation_categories_state')
    conservation_criteria_state = Field(
        attribute='conservation_criteria_state',
        column_name='conservation_criteria_state')
    conservation_category_national = Field(
        attribute='conservation_category_national',
        column_name='conservation_category_national')

    class Meta:
        """Class opts."""

        model = tax_models.Taxon
        fields = [
            "name_id",
            "taxonomic_name",
            "vernacular_names",
            "field_code",
            "publication_status",
            "current",
            "currently_listed",
            "conservation_code_state",
            "conservation_list_state",
            "conservation_category_state",
            "conservation_categories_state",
            "conservation_criteria_state",
            "conservation_category_national",
        ]


class CommunityResource(resources.ModelResource):
    """Community resource class for REsource download."""

    currently_listed = Field(
        attribute='is_currently_listed',
        column_name='currently_listed')
    currently_listed = Field(
        attribute='is_currently_listed',
        column_name='currently_listed')
    conservation_code_state = Field(
        attribute='conservation_code_state',
        column_name='conservation_code_state')
    conservation_list_state = Field(
        attribute='conservation_list_state',
        column_name='conservation_list_state')
    conservation_category_state = Field(
        attribute='conservation_category_state',
        column_name='conservation_category_state')
    conservation_categories_state = Field(
        attribute='conservation_categories_state',
        column_name='conservation_categories_state')
    conservation_criteria_state = Field(
        attribute='conservation_criteria_state',
        column_name='conservation_criteria_state')
    conservation_category_national = Field(
        attribute='conservation_category_national',
        column_name='conservation_category_national')

    class Meta:
        """Class opts."""

        model = tax_models.Community
        fields = [
            "code",
            "name",
            "description",
            "currently_listed",
            "conservation_code_state",
            "conservation_list_state",
            "conservation_category_state",
            "conservation_categories_state",
            "conservation_criteria_state",
            "conservation_category_national",
        ]
