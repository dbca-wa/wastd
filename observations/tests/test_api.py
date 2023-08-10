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

    def test_encounter_api_detail(self):
        detail_url = reverse("api_v2:encounter_detail_resource", kwargs={"pk": self.enc.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.enc.source_id)

    def test_animalencounter_api_list(self):
        list_url = reverse("api_v2:animal_encounter_list_resource")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.stranding.source_id)

    def test_animalencounter_api_detail(self):
        detail_url = reverse("api_v2:animal_encounter_detail_resource", kwargs={"pk": self.stranding.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.stranding.source_id)

    def test_turtlenestencounter_api_list(self):
        list_url = reverse("api_v2:turtle_nest_encounter_list_resource")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.nest.source_id)
        self.assertContains(response, self.track.source_id)

    def test_turtlenestencounter_api_list_filter(self):
        list_url = reverse("api_v2:turtle_nest_encounter_list_resource")
        response = self.client.get(list_url, {"nest_type": "nest"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.nest.source_id)
        self.assertNotContains(response, self.track.source_id)

    def test_turtlenestencounter_api_detail(self):
        detail_url = reverse("api_v2:turtle_nest_encounter_detail_resource", kwargs={"pk": self.nest.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.nest.source_id)

    def test_turtlenestobservation_api_list(self):
        list_url = reverse("api_v2:turtle_nest_observation_list_resource")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.nest_observation.source_id)

    def test_turtlenestobservation_api_list_filter(self):
        list_url = reverse("api_v2:turtle_nest_observation_list_resource")
        response = self.client.get(list_url, {"encounter_id": self.nest.pk})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.nest_observation.source_id)

    def test_turtlenestobservation_api_detail(self):
        detail_url = reverse("api_v2:turtle_nest_observation_detail_resource", kwargs={"pk": self.nest_observation.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.nest_observation.source_id)

    def test_turtlehatchlingemergenceobservation_api_list(self):
        list_url = reverse("api_v2:turtle_hatchling_emergence_observation_list_resource")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.emergence_observation.source_id)

    def test_turtlehatchlingemergenceobservation_api_detail(self):
        detail_url = reverse("api_v2:turtle_hatchling_emergence_observation_detail_resource", kwargs={"pk": self.emergence_observation.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.emergence_observation.source_id)

    def test_nesttagobservation_api_list(self):
        list_url = reverse("api_v2:nest_tag_observation_list_resource")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.nest_tag_observation.source_id)

    def test_nesttagobservation_api_detail(self):
        detail_url = reverse("api_v2:nest_tag_observation_detail_resource", kwargs={"pk": self.nest_tag_observation.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.nest_tag_observation.source_id)

    def test_turtlenestdisturbanceobservation_api_list(self):
        list_url = reverse("api_v2:turtle_nest_disturbance_observation_list_resource")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.disturbance1.source_id)
        self.assertContains(response, self.disturbance2.source_id)

    def test_turtlenestdisturbanceobservation_api_list_filter(self):
        list_url = reverse("api_v2:turtle_nest_disturbance_observation_list_resource")
        response = self.client.get(list_url, {"encounter_id": self.nest.pk})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.disturbance1.source_id)
        self.assertNotContains(response, self.disturbance2.source_id)

    def test_turtlenestdisturbanceobservation_api_detail(self):
        detail_url = reverse("api_v2:turtle_nest_disturbance_observation_detail_resource", kwargs={"pk": self.disturbance1.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.disturbance1.source_id)
        self.assertNotContains(response, self.disturbance2.source_id)

    def test_loggerobservation_api_list(self):
        list_url = reverse("api_v2:logger_observation_list_resource")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.logger.source_id)

    def test_loggerobservation_api_detail(self):
        detail_url = reverse("api_v2:logger_observation_detail_resource", kwargs={"pk": self.logger.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.logger.source_id)

    def test_hatchlingmorphometricobservation_api_list(self):
        list_url = reverse("api_v2:hatchling_morphometric_observation_list_resource")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.hatchling.source_id)

    def test_hatchlingmorphometricobservation_api_detail(self):
        detail_url = reverse("api_v2:hatchling_morphometric_observation_detail_resource", kwargs={"pk": self.hatchling.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.hatchling.source_id)

    def test_turtlehatchlingemergenceoutlierobservation_api_list(self):
        list_url = reverse("api_v2:turtle_hatchling_emergence_outlier_observation_list_resource")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.outlier.source_id)

    def test_turtlehatchlingemergenceoutlierobservation_api_detail(self):
        detail_url = reverse("api_v2:turtle_hatchling_emergence_outlier_observation_detail_resource", kwargs={"pk": self.outlier.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.outlier.source_id)

    def test_lightsourceobservation_api_list(self):
        list_url = reverse("api_v2:light_source_list_resource")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.light_source.source_id)

    def test_lightsourceobservation_api_detail(self):
        detail_url = reverse("api_v2:light_source_detail_resource", kwargs={"pk": self.light_source.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.light_source.source_id)
