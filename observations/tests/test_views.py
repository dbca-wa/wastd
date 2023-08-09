from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from uuid import uuid4

from observations.models import (
    Encounter,
    AnimalEncounter,
    TurtleNestEncounter,
    TurtleNestObservation,
)


class ViewsTestCase(TestCase):

    def setUp(self):
        User = get_user_model()
        self.superuser = User.objects.create_superuser(
            username="superuser",
            email="superuser@email.com",
            password="test",
            name="Super user",
        )
        self.staff = User.objects.create_user(
            username="staffuser",
            email="staff@email.com",
            password="test",
            is_staff=True,
            name="Staff user",
        )
        self.staff.save()
        self.user = User.objects.create_user(
            username="user",
            email="user@email.com",
            password="test",
            name="Normal user",
        )
        self.user.save()
        self.enc = Encounter.objects.create(
            where=GEOSGeometry("POINT (115 -32)", srid=4326),
            when=timezone.now(),
            source_id=uuid4(),
            observer=self.staff,
            reporter=self.user,
        )
        self.stranding = AnimalEncounter.objects.create(
            where=GEOSGeometry("POINT (115 -32)", srid=4326),
            when=timezone.now(),
            source_id=uuid4(),
            observer=self.staff,
            reporter=self.user,
            species="cheloniidae-fam",
        )
        self.nest = TurtleNestEncounter.objects.create(
            where=GEOSGeometry("POINT (115 -32)", srid=4326),
            when=timezone.now(),
            observer=self.staff,
            reporter=self.user,
            species="cheloniidae-fam",
            nest_type="nest",
        )
        self.nest_observation = TurtleNestObservation.objects.create(
            encounter=self.nest,
            comments="Test data",
        )


class HomeViewTests(ViewsTestCase):

    def setUp(self):
        super().setUp()
        self.home_url = reverse("home")

    def test_home_staff(self):
        """The home view will load for a staff/superuser and contain a link to the curation portal
        """
        for user in [self.staff, self.superuser]:
            self.client.force_login(user)
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


class EncounterViewTests(ViewsTestCase):

    def setUp(self):
        super().setUp()
        self.list_url = reverse("observations:encounter-list")
        self.detail_url = reverse("observations:encounter-detail", kwargs={"pk": self.enc.pk})
        self.list_url_stranding = reverse("observations:animalencounter-list")
        self.detail_url_stranding = reverse("observations:animalencounter-detail", kwargs={"pk": self.stranding.pk})

    def test_encounter_list(self):
        """The encounter list view will load for all users and contain common elements
        """
        for user in [self.staff, self.superuser, self.user]:
            self.client.force_login(user)
            # Encounter list
            response = self.client.get(self.list_url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, str(self.enc))
            self.assertContains(response, f"QA status: {self.enc.get_status_display()}")
            # AnimalEncounter list
            response = self.client.get(self.list_url_stranding)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, str(self.stranding.get_card_title()))
            self.assertContains(response, f"QA status: {self.stranding.get_status_display()}")

    def test_encounter_list_staff(self):
        """The encounter list view will contain edit/curation links for authorised users
        """
        for user in [self.staff, self.superuser]:
            self.client.force_login(user)
            # Encounter list
            response = self.client.get(self.list_url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, self.enc.absolute_admin_url)
            for transition in self.enc.get_available_status_transitions():
                curate_url = f"{self.enc.get_absolute_url()}{transition.custom['url_path']}"
                self.assertContains(response, curate_url)
            # AnimalEncounter list
            response = self.client.get(self.list_url_stranding)
            self.assertEqual(response.status_code, 200)
            for transition in self.stranding.get_available_status_transitions():
                curate_url = f"{self.stranding.get_absolute_url()}{transition.custom['url_path']}"
                self.assertContains(response, curate_url)

    def test_encounter_list_user(self):
        """The encounter list view will not contain edit/curation links for normal users
        """
        self.client.force_login(self.user)
        # Encounter list
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.enc.absolute_admin_url)
        for transition in self.enc.get_available_status_transitions():
            curate_url = f"{self.enc.get_absolute_url()}{transition.custom['url_path']}"
            self.assertNotContains(response, curate_url)
        # AnimalEncounter list
        response = self.client.get(self.list_url_stranding)
        self.assertEqual(response.status_code, 200)
        for transition in self.stranding.get_available_status_transitions():
            curate_url = f"{self.stranding.get_absolute_url()}{transition.custom['url_path']}"
            self.assertNotContains(response, curate_url)

    def test_encounter_detail(self):
        """The encounter detail view will load for all users and contain common elements
        """
        for user in [self.staff, self.superuser, self.user]:
            self.client.force_login(user)
            # Encounter detail
            response = self.client.get(self.detail_url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, str(self.enc))
            self.assertContains(response, f"QA status: {self.enc.get_status_display()}")
            # AnimalEncounter detail
            response = self.client.get(self.detail_url_stranding)
            self.assertEqual(response.status_code, 200)
            title = f"{self.stranding.get_taxon_display()} - {self.stranding.get_species_display()}"
            self.assertContains(response, title)
            self.assertContains(response, f"QA status: {self.stranding.get_status_display()}")

    def test_encounter_detail_staff(self):
        """The encounter detail view will contain edit/curation links for authorised users
        """
        for user in [self.staff, self.superuser]:
            self.client.force_login(user)
            # Encounter detail
            response = self.client.get(self.detail_url)
            self.assertContains(response, self.enc.absolute_admin_url)
            for transition in self.enc.get_available_status_transitions():
                curate_url = f"{self.enc.get_absolute_url()}{transition.custom['url_path']}"
                self.assertContains(response, curate_url)
            # AnimalEncounter detail
            response = self.client.get(self.detail_url_stranding)
            self.assertContains(response, self.stranding.absolute_admin_url)
            for transition in self.stranding.get_available_status_transitions():
                curate_url = f"{self.stranding.get_absolute_url()}{transition.custom['url_path']}"
                self.assertContains(response, curate_url)

    def test_encounter_detail_user(self):
        """The encounter detail view will not contain edit/curation links for normal users
        """
        self.client.force_login(self.user)
        # Encounter detail
        response = self.client.get(self.detail_url)
        self.assertNotContains(response, self.enc.absolute_admin_url)
        for transition in self.enc.get_available_status_transitions():
            curate_url = f"{self.enc.get_absolute_url()}{transition.custom['url_path']}"
            self.assertNotContains(response, curate_url)
        # AnimalEncounter detail
        response = self.client.get(self.detail_url_stranding)
        self.assertNotContains(response, self.stranding.absolute_admin_url)
        for transition in self.stranding.get_available_status_transitions():
            curate_url = f"{self.stranding.get_absolute_url()}{transition.custom['url_path']}"
            self.assertNotContains(response, curate_url)
