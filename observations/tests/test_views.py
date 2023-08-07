from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from observations.lookups import (
    NA,
    TAXON_CHOICES_DEFAULT,
)
from observations.models import (
    AnimalEncounter,
    TurtleNestEncounter,
    Encounter,
)


class ViewsTestCase(TestCase):

    def setUp(self):
        User = get_user_model()
        self.superuser = User.objects.create_superuser(
            username="superuser", email="superuser@email.com", password="test")
        self.staff = User.objects.create_user(
            username="staffuser", email="staff@email.com", password="test", is_staff=True)
        self.staff.save()
        self.user = User.objects.create_user(
            username="user", email="user@email.com", password="test")
        self.user.save()


class HomeViewTests(ViewsTestCase):

    def setUp(self):
        super().setUp()
        self.home_url = reverse("home")

    def test_home_superuser(self):
        """The home view will load for a superuser and contain a link to the curation portal
        """
        self.client.force_login(self.superuser)
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Curation portal")

    def test_home_staff(self):
        """The home view will load for a staff user and contain a link to the curation portal
        """
        self.client.force_login(self.staff)
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Curation portal")

    def test_home_user(self):
        """The home view will load for a normal user and contain no link to the curation portal
        """
        self.client.force_login(self.user)
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Curation portal")


class TurtleNestEncounterViewTests(ViewsTestCase):
    """TurtleNestEncounter view tests."""

    def setUp(self):
        super().setUp()
        self.enc = TurtleNestEncounter.objects.create(
            where=GEOSGeometry("POINT (115 -32)", srid=4326),
            when=timezone.now(),
            species="natator-depressus",
            source_id="12345",
            observer=self.staff,
            reporter=self.user,
        )

    #def test_absolute_admin_url(self):
    #    """Test absolute admin url."""
    #    response = self.client.get(self.cl.absolute_admin_url)
    #    self.assertEqual(response.status_code, 200)

    #def test_absolute_url(self):
    #    """Test absolute url."""
    #    response = self.client.get(self.cl.get_absolute_url())
    #    self.assertEqual(response.status_code, 200)

    #def encounter_list_loads(self):
    #    """Test "encounter_list" view."""
    #    response = self.client.get(reverse("encounter_list"))
    #    self.assertEqual(response.status_code, 200)

    def test_turtlenestencounter_list_staff(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("observations:turtlenestencounter-list"))
        self.assertEqual(response.status_code, 200)
        print(response.content)

    #def turtlenestencounter_detail_loads(self):
    #    """Test "observations:turtlenestencounterdetail" view."""
    #    response = self.client.get(
    #        reverse("observations:turtlenestencounter-detail", pk=self.cl.pk)
    #    )
    #    self.assertEqual(response.status_code, 200)
