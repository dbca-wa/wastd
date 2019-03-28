# -*- coding: utf-8 -*-
"""Conservation views."""
from import_export import resources

from conservation import models as cons_models


class ConservationThreatResource(resources.ModelResource):
    """ConservationThreat resource class for CSV download."""

    class Meta:
        """Class opts."""

        model = cons_models.ConservationThreat
        fields = [
            "taxon_list",
            "com_list",
            "document__title",
            "occurrence_area_code",
            "category__label",
            "encountered_by__name",
            "encountered_on",
            "area_affected_percent",
            "current_impact",
            "potential_impact",
            "potential_onset",
        ]


class ConservationActionResource(resources.ModelResource):
    """ConservationAction resource class for CSV download."""

    class Meta:
        """Class opts."""

        model = cons_models.ConservationAction
        fields = [
            "taxon_list",
            "com_list",
            "document__title",
            "occurrence_area_code",
            "category__label",
            "instructions",
            "implementation_notes",
            "completion_date",
            "expenditure",
            "status"
        ]
