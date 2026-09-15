from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase

from wamtram2.export_config import PROCESSED_EXPORT_HEADERS
from wamtram2.export_helpers import get_processed_export_row
from wamtram2.views import ExportDataView


def processed_row_dict(row):
    return dict(zip(PROCESSED_EXPORT_HEADERS, row))

def obj(**attrs):
    return SimpleNamespace(**attrs)

def make_processed_export_test_data():
    place = obj(
        place_code="MN01",
        place_name="Munda Beach",
        location_code=obj(
            location_code="MN",
            location_name="Munda",
        ),
    )

    turtle = obj(
        turtle_id=1002,
        species_code=obj(
            species_code="FB",
            common_name="Flatback Turtle",
        ),
        species_code_id="FB",
        sex="F",
        location_code=None,
        turtle_status_id="T",
        turtle_status=None,
        identification_confidence="A",
    )

    observation = obj(
        observation_id=2002,
        turtle=turtle,
        turtle_id=1002,
        observation_date=datetime(2025, 12, 2, 21, 0),
        observation_time=datetime(1899, 12, 30, 21, 0),
        date_entered=None,
        place_code=place,
        place_code_id="MN01",
        place_description="",
        observation_status="Initial Nesting",
        entry_batch_id=3002,
    )

    context = {
        "observations": {
            observation.observation_id: observation,
        },
        "data_entries": {},
        "first_observations": {
            turtle.turtle_id: (
                observation.observation_date,
                observation.observation_id,
            ),
        },
        "recorded_tags": {},
        "recorded_pit_tags": {},
        "pit_tag_states": {},
        "measurements": {},
        "samples": {},
        "damages": {},
        "identifications": {},
    }

    return turtle, observation, context

class ProcessedExportRowTests(SimpleTestCase):
    def test_processed_export_location_uses_observation_place_location(self):
        turtle_location = obj(location_code="DB", location_name="Dampier")
        observation_location = obj(location_code="TH", location_name="Thevenard Island")
        place = obj(
            place_code="TH01",
            place_name="Thevenard Main Beach",
            location_code=observation_location,
        )
        species = obj(species_code="FB", common_name="Flatback Turtle")
        turtle = obj(
            turtle_id=1001,
            species_code=species,
            species_code_id="FB",
            sex="F",
            location_code=turtle_location,
            location_code_id="DB",
            turtle_status_id="T",
            turtle_status=None,
            identification_confidence="A",
        )
        observation = obj(
            observation_id=2001,
            turtle=turtle,
            turtle_id=1001,
            observation_date=datetime(2025, 12, 1, 20, 30),
            observation_time=datetime(1899, 12, 30, 20, 30),
            date_entered=None,
            place_code=place,
            place_code_id="TH01",
            place_description="",
            observation_status="Initial Sighting",
            entry_batch_id=3001,
        )
        context = {
            "observations": {observation.observation_id: observation},
            "data_entries": {},
            "first_observations": {1001: (observation.observation_date, observation.observation_id)},
            "recorded_tags": {},
            "recorded_pit_tags": {},
            "pit_tag_states": {},
            "measurements": {},
            "samples": {},
            "damages": {},
            "identifications": {},
        }

        row = processed_row_dict(get_processed_export_row(observation, context))

        self.assertEqual(row["LOCATION_CODE"], "TH")
        self.assertEqual(row["OBSERVED_LOCATION_CODE"], "TH")
        self.assertEqual(row["OBSERVED_LOCATION_NAME"], "Thevenard Island")
        self.assertNotEqual(row["LOCATION_CODE"], "DB")
    
    def test_processed_export_data_enterer_columns(self):
        _, observation, context = make_processed_export_test_data()

        context["data_entries"][observation.observation_id] = obj(
            data_entry_id=4002,
            user_entry_id="UE-4002",
            entered_by_id_id=5002,
            entered_by="Data Enterer",
            comments="Data entry comment",
        )

        row = processed_row_dict(
            get_processed_export_row(
                observation,
                context,
            )
        )
        self.assertEqual(
            row["DATA_ENTERER_ID"],
            "5002",
        )
        self.assertEqual(
            row["DATA_ENTERER_NAME"],
            "Data Enterer",
        )
    def test_processed_export_flipper_tag_columns(self):
        _, observation, context = make_processed_export_test_data()

        new_state = obj(
            tag_state="A1",
            existing_tag_list=False,
            new_tag_list=True,
        )

        existing_state = obj(
            tag_state="R",
            existing_tag_list=True,
            new_tag_list=False,
        )

        context["recorded_tags"][observation.observation_id] = [
            obj(
                tag_id_id="WA11111",
                other_tag_id=None,
                side="L",
                tag_state=new_state,
                tag_state_id="A1",
                comments="new left",
                tag_position=1,
                barnacles=False,
            ),
            obj(
                tag_id_id="WA22222",
                other_tag_id=None,
                side="R",
                tag_state=new_state,
                tag_state_id="A1",
                comments="new right",
                tag_position=1,
                barnacles=False,
            ),
            obj(
                tag_id_id="WB33333",
                other_tag_id=None,
                side="L",
                tag_state=existing_state,
                tag_state_id="R",
                comments="old left",
                tag_position=1,
                barnacles=False,
            ),
            obj(
                tag_id_id="WB44444",
                other_tag_id=None,
                side="R",
                tag_state=existing_state,
                tag_state_id="R",
                comments="old right",
                tag_position=1,
                barnacles=False,
            ),
        ]

        row = processed_row_dict(
            get_processed_export_row(
                observation,
                context,
            )
        )

        self.assertEqual(row["TAG_1"], "WA11111")
        self.assertEqual(row["TAG_2"], "WA22222")
        self.assertEqual(row["TAG_3"], "WB33333")
        self.assertEqual(row["TAG_4"], "WB44444")
    def test_processed_export_identifications(self):
        turtle, observation, context = make_processed_export_test_data()

        context["identifications"][turtle.turtle_id] = [
            obj(
                identification_type=obj(
                    description="Mund ID",
                ),
                identification_type_id="MUND",
                identifier="M123",
                comments="identification comment",
            ),
        ]

        row = processed_row_dict(
            get_processed_export_row(
                observation,
                context,
            )
        )

        self.assertIn(
            "M123",
            row["IDENTIFICATIONS"],
        )

    def test_processed_export_samples(self):
        _, observation, context = make_processed_export_test_data()

        context["samples"][observation.observation_id] = [
            obj(
                sample_id=6002,
                sample_date=None,
                sample_label="SAMPLE-1",
                tissue_type=None,
                tissue_type_id="SKIN",
                comments="sample comment",
            ),
        ]

        row = processed_row_dict(
            get_processed_export_row(
                observation,
                context,
            )
        )

        self.assertIn(
            "SAMPLE-1",
            row["SAMPLES"],
        )
    def test_processed_export_new_turtle(self):
        turtle, observation, context = make_processed_export_test_data()

        context["first_observations"][turtle.turtle_id] = (
            observation.observation_date,
            observation.observation_id,
        )

        row = processed_row_dict(
            get_processed_export_row(
                observation,
                context,
            )
        )

        self.assertEqual(
            row["NEW_TURTLE"],
            "Y",
        )
    def test_processed_row_generation_does_not_requery_observations_when_context_is_preloaded(self):
        _, observation, context = make_processed_export_test_data()

        with patch(
            "wamtram2.export_helpers.TrtObservations.objects"
        ) as observations_manager:
            get_processed_export_row(
                observation,
                context,
            )
        observations_manager.assert_not_called()

    def test_processed_export_existing_turtle(self):
        turtle, observation, context = make_processed_export_test_data()

        context["first_observations"][turtle.turtle_id] = (
            datetime(2025, 12, 1, 20, 0),
            1999,
        )

        row = processed_row_dict(
            get_processed_export_row(
                observation,
                context,
            )
        )

        self.assertEqual(
            row["NEW_TURTLE"],
            "N",
        )
class ProcessedExportPerformanceTests(TestCase):
    def test_processed_row_generation_uses_zero_database_queries_when_context_is_preloaded(self):
        _, observation, context = make_processed_export_test_data()

        with self.assertNumQueries(0):
            get_processed_export_row(
                observation,
                context,
            )
            
class ExportChunkingTests(SimpleTestCase):
    def test_processed_keyset_chunking_has_no_missing_or_duplicate_rows_with_id_gaps(self):
        view = ExportDataView()
        view.export_chunk_size = 2

        entries = [
            obj(observation_id=1),
            obj(observation_id=4),
            obj(observation_id=10),
            obj(observation_id=11),
            obj(observation_id=25),
        ]

        class FakeQuerySet:
            def __init__(self, values):
                self.values = values

            def order_by(self, *_fields):
                return self

            def filter(self, **kwargs):
                min_observation_id = kwargs["observation_id__gt"]
                return FakeQuerySet(
                    [
                        entry
                        for entry in self.values
                        if entry.observation_id > min_observation_id
                    ]
                )

            def __getitem__(self, value):
                return self.values[value]

        chunks = list(view._iter_processed_queryset_chunks(FakeQuerySet(entries)))
        flattened_ids = [
            entry.observation_id
            for chunk in chunks
            for entry in chunk
        ]

        self.assertEqual(
            [len(chunk) for chunk in chunks],
            [2, 2, 1],
        )

        self.assertEqual(
            flattened_ids,
            [1, 4, 10, 11, 25],
        )

        self.assertEqual(
            len(flattened_ids),
            len(set(flattened_ids)),
        )
