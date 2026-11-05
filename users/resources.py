from django.core.exceptions import ValidationError
from import_export import fields, resources, widgets

from wamtram2.models import TrtLocations

from .models import Organisation, OrganisationExportAssignment


class OrganisationExportAssignmentResource(resources.ModelResource):
    organisation = fields.Field(
        attribute="organisation",
        column_name="organisation_code",
        widget=widgets.ForeignKeyWidget(
            Organisation,
            field="code",
        ),
    )

    data_from = fields.Field(
        attribute="data_from",
        column_name="data_from",
        widget=widgets.DateWidget(format="%d/%m/%Y"),
    )

    data_to = fields.Field(
        attribute="data_to",
        column_name="data_to",
        widget=widgets.DateWidget(format="%d/%m/%Y"),
    )

    valid_from = fields.Field(
        attribute="valid_from",
        column_name="valid_from",
        widget=widgets.DateWidget(format="%d/%m/%Y"),
    )

    valid_to = fields.Field(
        attribute="valid_to",
        column_name="valid_to",
        widget=widgets.DateWidget(format="%d/%m/%Y"),
    )

    class Meta:
        model = OrganisationExportAssignment
        import_id_fields = ("id",)
        fields = (
            "id",
            "organisation",
            "location_code",
            "data_from",
            "data_to",
            "validity_type",
            "valid_from",
            "valid_to",
        )
        export_order = fields
        clean_model_instances = True
        use_transactions = True
        skip_unchanged = True
        report_skipped = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._location_codes = None

    def get_valid_location_codes(self):
        if self._location_codes is None:
            self._location_codes = set(
                TrtLocations.objects.values_list(
                    "location_code",
                    flat=True,
                )
            )

        return self._location_codes

    def before_import_row(self, row, **kwargs):
        organisation_code = str(
            row.get("organisation_code") or ""
        ).strip()

        location_code = str(
            row.get("location_code") or ""
        ).strip().upper()

        validity_type = str(
            row.get("validity_type") or ""
        ).strip().lower()

        row["organisation_code"] = organisation_code
        row["location_code"] = location_code
        row["validity_type"] = validity_type

        if not organisation_code:
            raise ValidationError(
                "organisation_code is required."
            )

        if not Organisation.objects.filter(
            code=organisation_code
        ).exists():
            raise ValidationError(
                f"Unknown organisation_code: {organisation_code}"
            )

        if not location_code:
            raise ValidationError(
                "location_code is required."
            )

        if location_code not in self.get_valid_location_codes():
            raise ValidationError(
                f"Unknown WAMTRAM location_code: {location_code}"
            )

        valid_types = {
            OrganisationExportAssignment.ValidityType.PERMANENT,
            OrganisationExportAssignment.ValidityType.TIME_LIMITED,
        }

        if validity_type not in valid_types:
            raise ValidationError(
                "validity_type must be permanent or time_limited."
            )

        # Add the duplicate detection here.
        assignment_id = row.get("id")

        if not assignment_id:
            organisation = self.fields["organisation"].clean(row)
            data_from = self.fields["data_from"].clean(row)
            data_to = self.fields["data_to"].clean(row)
            valid_from = self.fields["valid_from"].clean(row)
            valid_to = self.fields["valid_to"].clean(row)

            existing_assignments = (
                OrganisationExportAssignment.objects.filter(
                    organisation=organisation,
                    location_code=location_code,
                    data_from=data_from,
                    data_to=data_to,
                    validity_type=validity_type,
                    valid_from=valid_from,
                    valid_to=valid_to,
                )
            )

            existing_id = (
                existing_assignments
                .order_by("pk")
                .values_list("pk", flat=True)
                .first()
            )

            if existing_id:
                row["id"] = existing_id
                row["_skip_identical"] = True

    def skip_row(
        self,
        instance,
        original,
        row,
        import_validation_errors=None,
    ):
        if row.get("_skip_identical"):
            return True

        return super().skip_row(
            instance,
            original,
            row,
            import_validation_errors,
        )