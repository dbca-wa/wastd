from django.urls import reverse
from .test_views import ViewsTestCase


class ApiTests(ViewsTestCase):

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def test_encounter_api_list(self):
        list_url = reverse("api_v2:encounter_list_resource")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.enc.source_id)

    def test_encounter_detail(self):
        detail_url = reverse("api_v2:encounter_detail_resource", kwargs={"pk": self.enc.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.enc.source_id)

    def test_animalencounter_api_list(self):
        list_url = reverse("api_v2:animal_encounter_list_resource")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.stranding.source_id)

    def test_animalencounter_detail(self):
        detail_url = reverse("api_v2:animal_encounter_detail_resource", kwargs={"pk": self.stranding.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.stranding.source_id)

    def test_turtlenestencounter_api_list(self):
        list_url = reverse("api_v2:turtle_nest_encounter_list_resource")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.nest.source_id)

    def test_turtlenestencounter_detail(self):
        detail_url = reverse("api_v2:turtle_nest_encounter_detail_resource", kwargs={"pk": self.nest.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.nest.source_id)

    def test_turtlenestobservation_api_list(self):
        list_url = reverse("api_v2:turtle_nest_observation_list_resource")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.nest_observation.source_id)

    def test_turtlenestobservation_detail(self):
        detail_url = reverse("api_v2:turtle_nest_observation_detail_resource", kwargs={"pk": self.nest_observation.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.nest_observation.source_id)
