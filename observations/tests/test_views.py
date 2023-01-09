"""observations view test suite testing URLs, templates, and views."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.gis.geos import GEOSGeometry
from django.test import TestCase
from django.urls import reverse  # noqa
from django.utils import timezone  # noqa

from observations.models import (  # noqa
    NA,
    TAXON_CHOICES_DEFAULT,
    AnimalEncounter,
    Area,
    DispatchRecord,
    DugongMorphometricObservation,
    Encounter,
    HatchlingMorphometricObservation,
    LineTransectEncounter,
    LoggerEncounter,
    ManagementAction,
    MediaAttachment,
    NestTagObservation,
    Survey,
    TagObservation,
    TemperatureLoggerDeployment,
    TemperatureLoggerSettings,
    TrackTallyObservation,
    TurtleDamageObservation,
    TurtleMorphometricObservation,
    TurtleNestDisturbanceObservation,
    TurtleNestDisturbanceTallyObservation,
    TurtleNestEncounter,
    TurtleNestObservation,
    PathToSea,
    TurtleHatchlingEmergenceObservation,
    TurtleHatchlingEmergenceOutlierObservation,
    LightSourceObservation,
    LoggerObservation,
)


class HomeViewTestsSuperuser(TestCase):
    """Home view tests for superusers."""

    def setUp(self):
        """Setup: create a new list."""
        self.superuser = get_user_model().objects.create_superuser(
            username="superuser", email="super@gmail.com", password="test"
        )

        self.superuser.save()

        self.client.force_login(self.superuser)

    def test_superuser_can_view_home(self):
        """A superuser should see the Home view."""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)


class HomeViewTestsInternal(TestCase):
    """Home view tests for internal users."""

    def setUp(self):
        """Setup: create a new user."""
        self.internal_user = get_user_model().objects.create_user(
            username="internaluser", email="internal@gmail.com", password="test"
        )

        self.internal_user.save()

        # Get or create Group "viewers"
        self.viewers, _ = Group.objects.get_or_create(name="data viewer")

        # Add internal user to Group "viewers"
        self.internal_user.groups.add(self.viewers)

        self.client.force_login(self.internal_user)

    def test_internaluser_is_data_viewer(self):
        """The internal user should belong to Group self.viewers."""
        self.assertTrue(self.viewers in self.internal_user.groups.all())

    def test_internaluser_can_view_home(self):
        """An interal user should see the Home view.

        Internal users belong to the Group "viewers".
        They should be able to see all data read-only.
        """
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)


class HomeViewTestsExternal(TestCase):
    """Home view tests for external users."""

    def setUp(self):
        """Setup: create a new user."""
        self.external_user = get_user_model().objects.create_user(
            username="externaluser", email="external@gmail.com", password="test"
        )

        self.external_user.save()

        # Get or create Group "viewers"
        self.viewers, _ = Group.objects.get_or_create(name="data viewer")

        self.client.force_login(self.external_user)

    def test_externaluser_is_not_data_viewer(self):
        """The external user should not belong to Group self.viewers."""
        self.assertTrue(self.viewers not in self.external_user.groups.all())

    def test_externaluser_can_view_home(self):
        """An exteral user should see the Home view.

        External users do not belong to the Group "viewers".
        They should not be able to see all data read-only.
        """
        response = self.client.get(reverse("home"))

        # TODO user should see a "forbidden" message
        self.assertEqual(response.status_code, 200)


class EncounterViewTests(TestCase):
    """Encounter view tests."""

    def setUp(self):
        """Setup: create a new list."""
        self.user = get_user_model().objects.create_superuser(
            username="superuser", email="super@gmail.com", password="test"
        )
        self.cl = Encounter.objects.create(
            where=GEOSGeometry("POINT (115 -32)", srid=4326),
            when=timezone.now(),
            source_id="12345",
            observer=self.user,
            reporter=self.user,
        )
        self.user.save()
        self.client.force_login(self.user)

    def test_absolute_admin_url(self):
        """Test absolute admin url."""
        response = self.client.get(self.cl.absolute_admin_url)
        self.assertEqual(response.status_code, 200)

    def test_absolute_url(self):
        """Test absolute url."""
        response = self.client.get(self.cl.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def encounter_list_loads(self):
        """Test "encounter_list" view."""
        response = self.client.get(reverse("encounter_list"))
        self.assertEqual(response.status_code, 200)

    def encounter_list_loads(self):
        """Test "observations:animalencounter-list" view."""
        response = self.client.get(reverse("observations:encounter-list"))
        self.assertEqual(response.status_code, 200)

    def encounter_detail_loads(self):
        """Test "observations:animalencounter-detail" view."""
        response = self.client.get(
            reverse("observations:encounter-detail", pk=self.cl.pk)
        )
        self.assertEqual(response.status_code, 200)


class AnimalEncounterViewTests(TestCase):
    """AnimalEncounter view tests."""

    def setUp(self):
        """Setup: create a new list."""
        self.user = get_user_model().objects.create_superuser(
            username="superuser", email="super@gmail.com", password="test"
        )
        self.cl = AnimalEncounter.objects.create(
            where=GEOSGeometry("POINT (115 -32)", srid=4326),
            when=timezone.now(),
            taxon=TAXON_CHOICES_DEFAULT,
            species=NA,
            source_id="12345",
            observer=self.user,
            reporter=self.user,
        )
        self.user.save()
        self.client.force_login(self.user)

    def test_absolute_admin_url(self):
        """Test absolute admin url."""
        response = self.client.get(self.cl.absolute_admin_url)
        self.assertEqual(response.status_code, 200)

    def test_absolute_url(self):
        """Test absolute url."""
        response = self.client.get(self.cl.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def encounter_list_loads(self):
        """Test "encounter_list" view."""
        response = self.client.get(reverse("encounter_list"))
        self.assertEqual(response.status_code, 200)

    def animalencounter_list_loads(self):
        """Test "observations:animalencounter-list" view."""
        response = self.client.get(reverse("observations:animalencounter-list"))
        self.assertEqual(response.status_code, 200)

    def animalencounter_detail_loads(self):
        """Test "observations:animalencounter-detail" view."""
        response = self.client.get(
            reverse("observations:animalencounter-detail", pk=self.cl.pk)
        )
        self.assertEqual(response.status_code, 200)


class TurtleNestEncounterViewTests(TestCase):
    """TurtleNestEncounter view tests."""

    def setUp(self):
        """Setup: create a new list."""
        self.user = get_user_model().objects.create_superuser(
            username="superuser", email="super@gmail.com", password="test"
        )
        self.cl = TurtleNestEncounter.objects.create(
            where=GEOSGeometry("POINT (115 -32)", srid=4326),
            when=timezone.now(),
            species="natator-depressus",
            source_id="12345",
            observer=self.user,
            reporter=self.user,
        )
        self.user.save()
        self.client.force_login(self.user)

    def test_absolute_admin_url(self):
        """Test absolute admin url."""
        response = self.client.get(self.cl.absolute_admin_url)
        self.assertEqual(response.status_code, 200)

    def test_absolute_url(self):
        """Test absolute url."""
        response = self.client.get(self.cl.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def encounter_list_loads(self):
        """Test "encounter_list" view."""
        response = self.client.get(reverse("encounter_list"))
        self.assertEqual(response.status_code, 200)

    def turtlenestencounter_list_loads(self):
        """Test "observations:turtlenestencounter-list" view."""
        response = self.client.get(reverse("observations:turtlenestencounter-list"))
        self.assertEqual(response.status_code, 200)

    def turtlenestencounter_detail_loads(self):
        """Test "observations:turtlenestencounterdetail" view."""
        response = self.client.get(
            reverse("observations:turtlenestencounter-detail", pk=self.cl.pk)
        )
        self.assertEqual(response.status_code, 200)
