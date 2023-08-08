from django.urls import reverse
from .test_views import ViewsTestCase


class ApiTests(ViewsTestCase):

    def test_encounter_api_list(self):
        list_url = reverse("api_v2:encounter_list_resource")
        self.client.force_login(self.user)
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)

    def test_encounter_detail(self):
        detail_url = reverse("api_v2:encounter_detail_resource", kwargs={"pk": self.enc.pk})
        self.client.force_login(self.user)
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)

    def test_animalencounter_api_list(self):
        list_url = reverse("api_v2:animal_encounter_list_resource")
        self.client.force_login(self.user)
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)

    def test_animalencounter_detail(self):
        detail_url = reverse("api_v2:animal_encounter_detail_resource", kwargs={"pk": self.stranding.pk})
        self.client.force_login(self.user)
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)

    def test_turtlenestencounter_api_list(self):
        list_url = reverse("api_v2:turtle_nest_encounter_list_resource")
        self.client.force_login(self.user)
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)

    def test_turtlenestencounter_detail(self):
        detail_url = reverse("api_v2:turtle_nest_encounter_detail_resource", kwargs={"pk": self.nest.pk})
        self.client.force_login(self.user)
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
