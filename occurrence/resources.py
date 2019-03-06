# -*- coding: utf-8 -*-
"""Conservation views."""
from import_export import resources

from occurrence import models as occ_models


class TaxonAreaEncounterResource(resources.ModelResource):
    """TaxonAreaEncounter resource class for CSV download."""

    class Meta:
        """Class opts."""

        model = occ_models.TaxonAreaEncounter
        fields = [
            "taxon__name_id",
            "taxon__taxonomic_name",
            "taxon__vernacular_names",
            "area_type",
            "code",
            "name",
            "description",
            "point",
            "geom",
            "accuracy",
            "source",
            "source_id",
            "encountered_on",
            "encountered_by",
        ]


class CommunityAreaEncounterResource(resources.ModelResource):
    """CommunityAreaEncounter resource class for CSV download."""

    class Meta:
        """Class opts."""

        model = occ_models.CommunityAreaEncounter
        fields = [
            "community__code",
            "community__name",
            "area_type",
            "code",
            "name",
            "description",
            "point",
            "geom",
            "accuracy",
            "source",
            "source_id",
            "encountered_on",
            "encountered_by",
        ]
