from django.core.management import call_command
from django.test import TestCase
from unittest.mock import patch, MagicMock
from observations.models import TurtleNestEncounter, TurtleNestDisturbanceObservation, TurtleNestDisturbanceTallyObservation, AnimalEncounter, Area, User, Encounter
from observations.lookups import TURTLE_SPECIES_DEFAULT, NEST_TYPE_TRACK_UNSURE, NEST_AGE_DEFAULT
from django.contrib.gis.geos import Polygon, Point
from datetime import datetime
import pytz
import uuid

"""
Unit Test Suite for Automated QA Checks Management Command

This test suite is designed to validate the functionality of the `automated_qa_checks`
management command in the `observations` application. The command performs various 
automated QA checks on turtle nest encounters and flags records for manual curation 
based on different criteria.

Tests include:
1. Flagging turtle nest encounters with site labels containing specific terms 
   (e.g., "training", "testing").
2. Flagging turtle nest encounters with uncertain species, nesting outcomes, nest ages, 
   and predation.
3. Flagging turtle nest encounters using test species.
4. Flagging turtle nest encounters and animal encounters reported by an unknown user.
5. Marking all imported turtle nest encounters as curated if they pass all QA checks.
6. Flagging turtle nest encounters with specific species in specific areas, 
   including Ningaloo and other specified localities.
7. Validating the command's behavior with multiple records (test_flag_multiple_nests_with_training_in_site_name).

Each test uses the `unittest.mock` library to patch the logging mechanism, ensuring 
that the command logs the expected messages. The tests create necessary data in the 
database, execute the command, and then verify that the correct log messages are 
produced, indicating that the appropriate records were flagged or marked as curated.
"""


TEST_SPECIES = 'test-turtle'
TURTLE_SPECIES = 'chelonia-mydas'
NEST_AGE = 'fresh'
NEST_TYPE = 'nest'
LOCALITY = 'Port Hedland'
TURTLE_SPECIFIC_SPECIES = "dermochelys-coriacea"  # Leatherback turtle

class AutomatedQAChecksCommandTests(TestCase):
    def setUp(self):
        self.system_user = User.objects.create(pk=1, username='system_user')
        self.unknown_user = User.objects.create(name='Unknown user', username='unknown_user')
        self.area = Area.objects.create(
            name="Test Area",
            area_type="Locality",
            geom=Polygon(((0.0, 0.0), (0.0, 1.0), (1.1, 1.0), (1.0, 0.0), (0.0, 0.0))),
        )
        self.localities = [
            "Delambre Island",
            "Thevenard Island",
            "Port Hedland",
            "Rosemary Island",
            "Eco Beach",
            "Barrow Island",
            "Mundabullangana",
            "Ningaloo",
        ]
        for locality in self.localities:
            Area.objects.create(name=locality, area_type="Locality", geom=Polygon(((0.0, 0.0), (0.0, 1.0), (1.1, 1.0), (1.0, 0.0), (0.0, 0.0))))

    @patch('logging.getLogger')
    def test_flag_nests_with_training_in_site_name(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        training_area = Area.objects.create(
            name="training site",
            area_type="Locality",
            geom=Polygon(((0.0, 0.0), (0.0, 1.0), (1.1, 1.0), (1.0, 0.0), (0.0, 0.0))),
        )

        TurtleNestEncounter.objects.create(
            site=training_area,
            status=Encounter.STATUS_IMPORTED,
            when=datetime.now(pytz.utc),
            where=Point(0.0, 0.0)
        )
        call_command('automated_qa_checks')
        mock_logger.info.assert_any_call('Flagging 1 turtle nest encounters for curation due to site containing "Training"')
        
    @patch('logging.getLogger')
    def test_flag_multiple_nests_with_training_in_site_name(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        training_area = Area.objects.create(
            name="training site",
            area_type="Locality",
            geom=Polygon(((0.0, 0.0), (0.0, 1.0), (1.1, 1.0), (1.0, 0.0), (0.0, 0.0))),
        )

        for _ in range(3):
            TurtleNestEncounter.objects.create(
                site=training_area,
                status=Encounter.STATUS_IMPORTED,
                when=datetime.now(pytz.utc),
                where=Point(0.0, 0.0),
                source_id=str(uuid.uuid4())  # Ensure unique source_id
            )
        call_command('automated_qa_checks')
        mock_logger.info.assert_any_call('Flagging 3 turtle nest encounters for curation due to site containing "Training"')


    @patch('logging.getLogger')
    def test_flag_nests_with_testing_in_site_name(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        testing_area = Area.objects.create(
            name="testing site",
            area_type="Locality",
            geom=Polygon(((0.0, 0.0), (0.0, 1.0), (1.1, 1.0), (1.0, 0.0), (0.0, 0.0))),
        )

        TurtleNestEncounter.objects.create(
            site=testing_area,
            status=Encounter.STATUS_IMPORTED,
            when=datetime.now(pytz.utc),
            where=Point(0.0, 0.0)
        )
        call_command('automated_qa_checks')
        mock_logger.info.assert_any_call('Flagging 1 turtle nest encounters for curation due to site containing "testing"')

    @patch('logging.getLogger')
    def test_flag_nests_with_uncertain_species(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        TurtleNestEncounter.objects.create(
            site=self.area,
            status=Encounter.STATUS_IMPORTED,
            species=TURTLE_SPECIES_DEFAULT,
            when=datetime.now(pytz.utc),
            where=Point(0.0, 0.0)
        )
        call_command('automated_qa_checks')
        mock_logger.info.assert_any_call('Flagging 1 turtle nest encounters for curation due to uncertain species')

    @patch('logging.getLogger')
    def test_flag_nests_with_test_species(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        TurtleNestEncounter.objects.create(
            site=self.area,
            status=Encounter.STATUS_IMPORTED,
            species=TEST_SPECIES, 
            when=datetime.now(pytz.utc),
            where=Point(0.0, 0.0)
        )
        call_command('automated_qa_checks')
        mock_logger.info.assert_any_call('Flagging 1 turtle nest encounters for curation due to test species type')
        
    @patch('logging.getLogger')
    def test_flag_nests_with_uncertain_nesting_outcome(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        TurtleNestEncounter.objects.create(
            site=self.area,
            status=Encounter.STATUS_IMPORTED,
            nest_type=NEST_TYPE_TRACK_UNSURE,
            species=TURTLE_SPECIES,
            when=datetime.now(pytz.utc),
            where=Point(0.0, 0.0)
        )
        call_command('automated_qa_checks')
        mock_logger.info.assert_any_call('Flagging 1 turtle nest encounters for curation due to uncertain nesting outcome')
    
    @patch('logging.getLogger')
    def test_flag_nests_with_uncertain_nest_age(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        TurtleNestEncounter.objects.create(
            site=self.area,
            status=Encounter.STATUS_IMPORTED,
            nest_age="unknown",
            species=TURTLE_SPECIES,
            when=datetime.now(pytz.utc),
            where=Point(0.0, 0.0)
        )
        call_command('automated_qa_checks')
        
        print(mock_logger.info.call_args_list)
        mock_logger.info.assert_any_call('Flagging 1 turtle nest encounters for curation due to uncertain nest age')
    
    @patch('logging.getLogger')
    def test_flag_nests_with_uncertain_predation(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        encounter = TurtleNestEncounter.objects.create(
            site=self.area,
            status=Encounter.STATUS_IMPORTED,
            species=TURTLE_SPECIES,
            nest_age=NEST_AGE,
            nest_type=NEST_TYPE,
            when=datetime.now(pytz.utc),
            where=Point(0.0, 0.0)
        )
        TurtleNestDisturbanceObservation.objects.create(
            encounter=encounter,
            disturbance_cause="unknown"
        )
        call_command('automated_qa_checks')
        mock_logger.info.assert_any_call('Flagging 1 turtle nest encounters for curation due to uncertain predation')

        TurtleNestDisturbanceTallyObservation.objects.create(
            encounter=encounter,
            disturbance_cause="unknown"
        )
        call_command('automated_qa_checks')
        mock_logger.info.assert_any_call('Flagging 1 turtle nest encounters for curation due to uncertain predation')
        
    @patch('logging.getLogger')
    def test_flag_nests_with_specific_species_in_specific_areas(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        locality_area = Area.objects.get(name=LOCALITY)
        TurtleNestEncounter.objects.create(
            site=locality_area,
            area=locality_area,
            nest_age=NEST_AGE,
            nest_type=NEST_TYPE,
            status=Encounter.STATUS_IMPORTED,
            species=TURTLE_SPECIFIC_SPECIES,  # Leatherback turtle
            when=datetime.now(pytz.utc),
            where=Point(0.0, 0.0)
        )

        call_command('automated_qa_checks')
        mock_logger.info.assert_any_call(f'Flagging 1 turtle nest encounters for curation: Dermochelys coriacea (Leatherback turtle) at {locality_area.name}')
        
    @patch('logging.getLogger')
    def test_flag_nests_with_specific_species_in_ningaloo(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        ningaloo_area = Area.objects.get(name="Ningaloo")
        
        TurtleNestEncounter.objects.create(
            site=ningaloo_area,
            area=ningaloo_area,
            nest_age=NEST_AGE,
            nest_type=NEST_TYPE,
            status=Encounter.STATUS_IMPORTED,
            species=TURTLE_SPECIFIC_SPECIES,
            when=datetime.now(pytz.utc),
            where=Point(0.0, 0.0)
        )

        call_command('automated_qa_checks')
        mock_logger.info.assert_any_call('Flagging 1 turtle nest encounters for curation: Dermochelys coriacea (Leatherback turtle) at Ningaloo')
        
    @patch('logging.getLogger')
    def test_flag_imported_nests_with_unknown_reporter(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        TurtleNestEncounter.objects.create(
            site=self.area,
            status=Encounter.STATUS_IMPORTED,
            species=TURTLE_SPECIES,
            nest_age=NEST_AGE,
            nest_type=NEST_TYPE,
            reporter=self.unknown_user,
            when=datetime.now(pytz.utc),
            where=Point(0.0, 0.0)
        )

        call_command('automated_qa_checks')
        mock_logger.info.assert_any_call('Flagging 1 turtle nest encounters for curation due to unknown reporter')

    @patch('logging.getLogger')
    def test_mark_imported_nests_as_curated(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        TurtleNestEncounter.objects.create(
            site=self.area,
            status=Encounter.STATUS_IMPORTED,
            species=TURTLE_SPECIES,
            nest_age=NEST_AGE,
            nest_type=NEST_TYPE,
            reporter=self.system_user,
            when=datetime.now(pytz.utc),
            where=Point(0.0, 0.0)
        )

        call_command('automated_qa_checks')
        mock_logger.info.assert_any_call('Marking 1 imported turtle nest encounters as curated (passed QA/QC checks)')

    @patch('logging.getLogger')
    def test_flag_imported_animal_encounters_with_unknown_reporter(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        AnimalEncounter.objects.create(
            site=self.area,
            status=Encounter.STATUS_IMPORTED,
            species=TURTLE_SPECIES,
            reporter=self.unknown_user,
            when=datetime.now(pytz.utc),
            where=Point(0.0, 0.0)
        )

        call_command('automated_qa_checks')
        print(mock_logger.info.call_args_list)
        mock_logger.info.assert_any_call('Flagging 1 animal encounters for curation due to unknown reporter')
