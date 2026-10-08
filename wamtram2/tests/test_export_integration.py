from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from wamtram2.export_config import PROCESSED_EXPORT_HEADERS
from wamtram2.export_helpers import build_export_headers, get_processed_export_row
from wamtram2.tests.test_export_helpers import make_processed_export_test_data
from wamtram2.models import TrtDataEntry
from pathlib import Path
from django.test import RequestFactory, SimpleTestCase
from django.utils import timezone

from wamtram2.views import ExportDataView


class ExportCsvResponseTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = ExportDataView()

    @patch("wamtram2.views.TrtTagStates.objects")
    @patch("wamtram2.views.TrtTissueTypes.objects")
    @patch("wamtram2.views.TrtDamageCodes.objects")
    @patch("wamtram2.views.TrtBodyParts.objects")
    @patch("wamtram2.views.TrtMeasurementTypes.objects")
    @patch("wamtram2.views.TrtBeachPositions.objects")
    @patch("wamtram2.views.TrtEntryBatchOrganisation.objects")
    @patch("wamtram2.views.TrtObservations.objects")
    def test_processed_csv_response_and_filename(
        self,
        observations_manager,
        batch_org_manager,
        beach_position_manager,
        measurement_type_manager,
        body_part_manager,
        damage_code_manager,
        tissue_type_manager,
        tag_state_manager,
    ):
        queryset = MagicMock()
        observations_manager.all.return_value = queryset

        queryset.filter.return_value = queryset
        queryset.select_related.return_value = queryset
        queryset.exists.return_value = True
        queryset.values_list.return_value = []

        batch_org_manager.filter.return_value.values.return_value = []

        beach_position_manager.all.return_value = []
        measurement_type_manager.all.return_value = []
        body_part_manager.all.return_value = []
        damage_code_manager.all.return_value = []
        tissue_type_manager.all.return_value = []
        tag_state_manager.all.return_value = []

        request = self.factory.get(
            "/wamtram2/export/",
            {
                "observation_date_from": "2023-12-12",
                "observation_date_to": "2023-12-12",
                "location_code": "TH",
                "format": "csv",
                "entry_type": "processed",
            },
        )

        request.user = SimpleNamespace(
            is_superuser=True,
        )

        with patch.object(
            self.view,
            "_iter_export_rows",
            return_value=[],
        ), patch.object(
            timezone,
            "now",
            return_value=datetime(2026, 10, 1),
        ):
            response = self.view.export_data(request)

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response["Content-Type"],
            "text/csv",
        )

        self.assertEqual(
            response["Content-Disposition"],
            'attachment; filename="Observations_TH_12122023_12122023_Export01102026.csv"',
        )
        csv_content = "".join(
            chunk.decode() if isinstance(chunk, bytes) else chunk
            for chunk in response.streaming_content
        )

        self.assertTrue(
            csv_content.startswith("OBSERVATION_ID,"),
        )
class FieldExportRegressionTests(SimpleTestCase):
    def test_field_export_header_schema(self):
        headers = build_export_headers(
            TrtDataEntry._meta,
            "field",
        )

        self.assertEqual(
            len(headers),
            224,
        )

        self.assertEqual(
            headers[:6],
            [
                "ENTRY_ID",
                "DATA_ENTRY_ID",
                "ENTRY_BATCH_ID",
                "USER_ENTRY_ID",
                "TURTLE_ID",
                "OBSERVATION_ID",
            ],
        )

        self.assertIn(
            "CURVED_CARAPACE_LENGTH",
            headers,
        )
        self.assertIn(
            "CURVED_CARAPACE_WIDTH",
            headers,
        )
        self.assertIn(
            "CURVED_CARAPACE_LENGTH_NOTCH",
            headers,
        )

        self.assertEqual(
            headers[-2:],
            [
                "ORGANISATIONS",
                "OBSERVATION_STATUS",
            ],
        )

        self.assertEqual(
            len(headers),
            len(set(headers)),
        )
class FieldExportPipelineTests(SimpleTestCase):
    def test_field_export_row_matches_header_count(self):
        view = ExportDataView()

        entry = MagicMock(spec=TrtDataEntry)

        for field in TrtDataEntry._meta.fields:
            setattr(entry, field.name, None)

            if field.is_relation and field.many_to_one:
                setattr(entry, f"{field.name}_id", None)

        entry.data_entry_id = 1001
        entry.entry_batch_id = 2001
        entry.observation_id_id = None
        entry.turtle_id_id = None

        location = SimpleNamespace(
            location_code="TH",
            location_name="Thevenard Island",
        )

        place = SimpleNamespace(
            place_code="TH01",
            place_name="Thevenard Island Beach",
            location_code=location,
        )

        species = SimpleNamespace(
            species_code="GN",
            common_name="Green Turtle",
        )

        entry.place_code = place
        entry.place_code_id = "TH01"

        entry.species_code = species
        entry.species_code_id = "GN"

        entry.observation_date = datetime(
            2023,
            12,
            12,
            20,
            33,
        )

        entry.sex = "F"
        entry.curved_carapace_length = 95
        entry.curved_carapace_width = 88

        class FakeQuerySet:
            def __init__(self, values):
                self.values = values

            def order_by(self, *_fields):
                return self

            def filter(self, **kwargs):
                min_id = kwargs["data_entry_id__gt"]
                return FakeQuerySet(
                    [
                        item
                        for item in self.values
                        if item.data_entry_id > min_id
                    ]
                )

            def __getitem__(self, item):
                return self.values[item]

        queryset = FakeQuerySet([entry])

        rows = list(
            view._iter_export_rows(
                queryset=queryset,
                entry_type="field",
                new_turtle=None,
                model_meta=TrtDataEntry._meta,
                org_dict={2001: ["DBCA"]},
                beach_position_dict={},
                measurement_type_dict={},
                body_part_dict={},
                damage_code_dict={},
                tissue_type_dict={},
                tag_state_dict={},
            )
        )

        headers = build_export_headers(
            TrtDataEntry._meta,
            "field",
        )

        self.assertEqual(
            len(rows),
            1,
        )

        self.assertEqual(
            len(rows[0]),
            len(headers),
        )

        self.assertEqual(
            len(rows[0]),
            224,
        )
        csv_content = "".join(
            view._stream_csv_rows(
                headers,
                rows,
            )
        )
        reference_path = Path(
            "wamtram2/tests/reference/field_export.csv"
        )
        expected_csv = reference_path.read_text(
            encoding="utf-8",
        )

        self.assertEqual(
            csv_content.replace("\r\n", "\n"),
            expected_csv.replace("\r\n", "\n"),
        )
        csv_lines = csv_content.splitlines()

        self.assertEqual(
            len(csv_lines),
            2,
        )

        self.assertTrue(
            csv_lines[0].startswith(
                "ENTRY_ID,DATA_ENTRY_ID,ENTRY_BATCH_ID,"
            )
        )

        self.assertIn(
            ",ORGANISATIONS,OBSERVATION_STATUS",
            csv_lines[0],
        )

        self.assertTrue(
            csv_lines[1].startswith(
                "1001,1001,2001,"
            )
        )

        self.assertIn(
            "DBCA",
            csv_lines[1],
        )
        header_values = csv_lines[0].split(",")

        row_values = csv_lines[1].split(",")

        exported = dict(
            zip(
                header_values,
                row_values,
            )
        )

        expected_values = {
            "ENTRY_ID": "1001",
            "DATA_ENTRY_ID": "1001",
            "ENTRY_BATCH_ID": "2001",
            "PLACE_CODE": "TH01",
            "PLACE_DESCRIPTION": "Thevenard Island Beach",
            "PLACE_NAME": "Thevenard Island Beach",
            "LOCATION_CODE": "TH",
            "OBSERVED_LOCATION_CODE": "TH",
            "OBSERVED_LOCATION_NAME": "Thevenard Island",
            "OBSERVATION_DATE": "12/12/2023",
            "SPECIES_CODE": "GN",
            "COMMON_NAME": "Green Turtle",
            "SEX": "F",
            "CURVED_CARAPACE_LENGTH": "95",
            "CURVED_CARAPACE_WIDTH": "88",
            "ORGANISATIONS": "DBCA",
        }

        for header, expected in expected_values.items():
            with self.subTest(header=header):
                self.assertEqual(
                    exported[header],
                    expected,
                )
class ProcessedExportPipelineTests(SimpleTestCase):
    def test_processed_export_matches_golden_csv(self):
        _, observation, context = make_processed_export_test_data()

        row = get_processed_export_row(
            observation,
            context,
        )

        self.assertEqual(
            len(row),
            len(PROCESSED_EXPORT_HEADERS),
        )

        self.assertEqual(
            len(row),
            100,
        )

        view = ExportDataView()

        csv_content = "".join(
            view._stream_csv_rows(
                PROCESSED_EXPORT_HEADERS,
                [row],
            )
        )

        reference_path = Path(
            "wamtram2/tests/reference/processed_export.csv"
        )

        expected_csv = reference_path.read_text(
            encoding="utf-8",
        )

        self.assertEqual(
            csv_content.replace("\r\n", "\n"),
            expected_csv.replace("\r\n", "\n"),
        )