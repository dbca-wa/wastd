from django.core.exceptions import ValidationError
from import_export import fields, resources, widgets

from wamtram2.models import TrtLocations
from .models import (
    Organisation,
    OrganisationExportAssignment,
    OrganisationExportDelegation,
)

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

    class Meta:
        model = OrganisationExportAssignment
        import_id_fields = ("id",)
        fields = (
            "id",
            "organisation",
            "location_code",
            "data_from",
            "data_to",
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

        row["organisation_code"] = organisation_code
        row["location_code"] = location_code

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

        assignment_id = row.get("id")

        if not assignment_id:
            organisation = self.fields["organisation"].clean(row)
            data_from = self.fields["data_from"].clean(row)
            data_to = self.fields["data_to"].clean(row)

            existing_id = (
                OrganisationExportAssignment.objects.filter(
                    organisation=organisation,
                    location_code=location_code,
                    data_from=data_from,
                    data_to=data_to,
                )
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

class OrganisationExportDelegationResource(resources.ModelResource):
    source_organisation = fields.Field(
        attribute="source_organisation",
        column_name="source_organisation_code",
        widget=widgets.ForeignKeyWidget(
            Organisation,
            field="code",
        ),
    )

    authorised_organisation = fields.Field(
        attribute="authorised_organisation",
        column_name="authorised_organisation_code",
        widget=widgets.ForeignKeyWidget(
            Organisation,
            field="code",
        ),
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
        model = OrganisationExportDelegation
        import_id_fields = ("id",)
        fields = (
            "id",
            "source_organisation",
            "authorised_organisation",
            "valid_from",
            "valid_to",
        )
        export_order = fields
        clean_model_instances = True
        use_transactions = True
        skip_unchanged = True
        report_skipped = True

    def before_import_row(self, row, **kwargs):
        source_code = str(
            row.get("source_organisation_code") or ""
        ).strip()

        authorised_code = str(
            row.get("authorised_organisation_code") or ""
        ).strip()

        row["source_organisation_code"] = source_code
        row["authorised_organisation_code"] = authorised_code

        if not source_code:
            raise ValidationError(
                "source_organisation_code is required."
            )

        if not authorised_code:
            raise ValidationError(
                "authorised_organisation_code is required."
            )

        if source_code == authorised_code:
            raise ValidationError(
                "Data source and authorised organisation must be different."
            )

        if not Organisation.objects.filter(
            code=source_code
        ).exists():
            raise ValidationError(
                f"Unknown source_organisation_code: {source_code}"
            )

        if not Organisation.objects.filter(
            code=authorised_code
        ).exists():
            raise ValidationError(
                f"Unknown authorised_organisation_code: {authorised_code}"
            )

        source = self.fields["source_organisation"].clean(row)
        authorised = self.fields["authorised_organisation"].clean(row)
        valid_from = self.fields["valid_from"].clean(row)
        valid_to = self.fields["valid_to"].clean(row)

        if not valid_from:
            raise ValidationError(
                "valid_from is required."
            )

        if not valid_to:
            raise ValidationError(
                "valid_to is required."
            )

        if valid_from > valid_to:
            raise ValidationError(
                "valid_to must be on or after valid_from."
            )

        delegation_id = row.get("id")

        if not delegation_id:
            existing = (
                OrganisationExportDelegation.objects.filter(
                    source_organisation=source,
                    authorised_organisation=authorised,
                )
                .order_by("pk")
                .first()
            )

            if existing:
                row["id"] = existing.pk

                if (
                    existing.valid_from == valid_from
                    and existing.valid_to == valid_to
                ):
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