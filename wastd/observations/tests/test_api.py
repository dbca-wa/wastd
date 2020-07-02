from datetime import date
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from io import BytesIO
from rest_framework.test import APIClient

from wastd.observations.models import Encounter, TagObservation

User = get_user_model()


class EncounterSerializerTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # TODO: test user/group permissions properly
        self.user = User.objects.create_superuser('testuser', 'testuser@test.com', 'pass')
        self.client.login(username='testuser', password='pass')
        self.encounter = Encounter.objects.create(
            source='odk',
            source_id='uuid:b2910a04-fc7b-4bb0-8570-febcb939022e',
            where=Point((114.0, -21.0)),
            when=timezone.now(),
            reporter=self.user,
            observer=self.user
        )

    def test_get_list_endpoints(self):
        for i in [
                'encounters_full',
                'encounters_fast',
                'encounters_src',
                'animalencounter',
                'turtlenestencounter',
        ]:
            url = reverse('api:{}-list'.format(i))
            resp = self.client.get(url, {'format': 'json'})
            self.assertEqual(resp.status_code, 200)

    def test_post_encounter(self):
        """Test the POST endpoint for Encounter
        """
        url = reverse('api:encounters_full-list')
        resp = self.client.post(
            url,
            {
                'source': 'odk',
                'source_id': 'uuid:673f1150-4d60-4cc5-846a-ebca5a98d4eb',
                'where': 'POINT (114.0 -21.0)',
                'when': '2020-01-01 12:00:00',
                'observer_id': self.user.pk,
                'reporter_id': self.user.pk,
            }
        )
        self.assertEqual(resp.status_code, 201)

    def test_post_turtlenestencounter(self):
        """Test the POST endpoint for TurtleNestEncounter
        """
        url = reverse('api:turtlenestencounter-list') + "?format=json"
        resp = self.client.post(
            url,
            {
                'source': 'odk',
                'source_id': 'uuid:673f1150-4d60-4cc5-846a-ebca5a98d4eb',
                'where': 'POINT (114.0 -21.0)',
                'when': '2020-01-01 12:00:00',
                'observer_id': self.user.pk,
                'reporter_id': self.user.pk,
                'nest_age': 'fresh',
                'nest_type': 'false-crawl',
                'species': 'chelonia-mydas',
            }
        )
        self.assertEqual(resp.status_code, 201)


class ObservationSerializerTests(EncounterSerializerTests):

    def test_get_list_endpoints(self):
        for i in [
                'observation',
                'mediaattachment',
                'tagobservation',
                'nesttagobservation',
                'managementaction',
                'turtledamageobservation',
                'turtlemorphometricobservation',
                'hatchlingmorphometricobservation',
                'turtlenestdisturbanceobservation',
                'turtlenestobservation',
                'turtlehatchlingemergenceobservation',
                'turtlehatchlingemergenceoutlierobservation',
                'lightsourceobservation',
        ]:
            url = reverse('api:{}-list'.format(i))
            resp = self.client.get(url, {'format': 'json'})
            self.assertEqual(resp.status_code, 200)

    def test_post_observation(self):
        url = reverse('api:observation-list')
        resp = self.client.post(
            url,
            {
            'source': 'odk',
            'source_id': 'uuid:b2910a04-fc7b-4bb0-8570-febcb939022e'
            }
        )
        self.assertEqual(resp.status_code, 201)

    def test_post_duplicate(self):
        """Test that exact duplicate objects aren't created via POST.
        """
        self.assertEqual(TagObservation.objects.count(), 0)
        url = reverse('api:tagobservation-list')
        data = {
            'source': 'odk',
            'source_id': 'uuid:b2910a04-fc7b-4bb0-8570-febcb939022e',
            'name': 'ABC123',
            'tag_type': 'flipper-tag',
            'tag_location': 'flipper-front-left-1',
            'status': 'resighted',
            'recorder_id': self.user.id,
            'handler_id': self.user.id,
        }
        # POST once, create an object.
        resp = self.client.post(url, data)
        self.assertEqual(TagObservation.objects.count(), 1)
        # POST a second time, no duplicate created.
        resp = self.client.post(url, data)
        self.assertEqual(TagObservation.objects.count(), 1)

    def test_post_media_attachment(self):
        url = reverse('api:mediaattachment-list')
        testfile = BytesIO(b'some test binary data')
        testfile.name = 'test.txt'
        resp = self.client.post(
            url,
            {
                'source': 'odk',
                'source_id': 'uuid:b2910a04-fc7b-4bb0-8570-febcb939022e',
                'title': 'Media attachment',
                'attachment': testfile,
            },
            format='multipart',
        )
        self.assertEqual(resp.status_code, 201)

    def test_post_tag_observation(self):
        url = reverse('api:tagobservation-list')
        resp = self.client.post(
            url,
            {
                'source': 'odk',
                'source_id': 'uuid:b2910a04-fc7b-4bb0-8570-febcb939022e',
                'name': 'ABC123',
                'recorder_id': self.user.id,
                'handler_id': self.user.id,
                'tag_type': 'flipper-tag',
                'tag_location': 'flipper-front-left-1',
                'status': 'resighted'
            }
        )
        self.assertEqual(resp.status_code, 201)

    def test_post_nest_tag_observation(self):
        url = reverse('api:nesttagobservation-list')
        resp = self.client.post(
            url,
            {
                'source': 'odk',
                'source_id': 'uuid:b2910a04-fc7b-4bb0-8570-febcb939022e',
                'flipper_tag_id': 'ABC123',
                'date_nest_laid': date.today(),
            }
        )
        self.assertEqual(resp.status_code, 201)

    def test_post_management_action(self):
        url = reverse('api:managementaction-list')
        resp = self.client.post(
            url,
            {
                'source': 'odk',
                'source_id': 'uuid:b2910a04-fc7b-4bb0-8570-febcb939022e',
                'management_actions': 'Some actions',
                'comments': 'A comment',
            }
        )
        self.assertEqual(resp.status_code, 201)

    def test_post_turtle_damageobs(self):
        url = reverse('api:turtledamageobservation-list')
        resp = self.client.post(
            url,
            {
                'source': 'odk',
                'source_id': 'uuid:b2910a04-fc7b-4bb0-8570-febcb939022e',
                'body_part': 'flipper-front-left-1',
                'damage_type': 'tip-amputated',
                'damage_age': 'fresh',
                'description': 'test description'
            }
        )
        self.assertEqual(resp.status_code, 201)

    def test_post_turtle_morphometrics(self):
        url = reverse('api:turtlemorphometricobservation-list')
        resp = self.client.post(
            url,
            {
                'source': 'odk',
                'source_id': 'uuid:b2910a04-fc7b-4bb0-8570-febcb939022e',
                'handler': self.user.pk,
                'recorder': self.user.pk,
            }
        )
        self.assertEqual(resp.status_code, 201)

    def test_post_turtle_hatchling_morphometrics(self):
        url = reverse('api:hatchlingmorphometricobservation-list')
        resp = self.client.post(
            url,
            {
                'source': 'odk',
                'source_id': 'uuid:b2910a04-fc7b-4bb0-8570-febcb939022e',
                'body_weight_g': 20,
            }
        )
        self.assertEqual(resp.status_code, 201)

    def test_post_turtlenestdisturbanceobservation(self):
        """Test the POST endpoint for a TurtleNestDisturbanceObservation obj
        """
        url = reverse('api:turtlenestdisturbanceobservation-list')
        # A request with no encounter reference should fail.
        resp = self.client.post(
            url,
            {
                'comments': 'Device ID 91c7fbd10d6f294b\nDug up, but crab prints obscured cause',
                'disturbance_cause': 'unknown',
                'disturbance_cause_confidence': 'guess',
                'disturbance_severity': 'partly',
            }
        )
        self.assertEqual(resp.status_code, 400)
        # A request with an Encounter PK should succeed.
        resp = self.client.post(
            url,
            {
                'encounter': self.encounter.pk,
                'comments': 'Device ID 91c7fbd10d6f294b\nDug up, but crab prints obscured cause',
                'disturbance_cause': 'unknown',
                'disturbance_cause_confidence': 'guess',
                'disturbance_severity': 'partly',
            }
        )
        self.assertEqual(resp.status_code, 201)
        # A request with source and source_id should succeed.
        resp = self.client.post(
            url,
            {
                'source': 'odk',
                'source_id': 'uuid:b2910a04-fc7b-4bb0-8570-febcb939022e',
                'comments': 'Device ID 91c7fbd10d6f294b\nDug up, but crab prints obscured cause',
                'disturbance_cause': 'unknown',
                'disturbance_cause_confidence': 'guess',
                'disturbance_severity': 'partly',
            }
        )
        self.assertEqual(resp.status_code, 201)

    def test_post_turtle_nest_observation(self):
        url = reverse('api:turtlenestobservation-list')
        resp = self.client.post(
            url,
            {
                'source': 'odk',
                'source_id': 'uuid:b2910a04-fc7b-4bb0-8570-febcb939022e',
                'eggs_laid': True,
                'egg_count': 10,
            }
        )
        self.assertEqual(resp.status_code, 201)

    def test_post_turtle_nest_hatchling_emergences(self):
        url = reverse('api:turtlehatchlingemergenceobservation-list')
        resp = self.client.post(
            url,
            {
                'source': 'odk',
                'source_id': 'uuid:b2910a04-fc7b-4bb0-8570-febcb939022e',
                'bearing_to_water_degrees': 0,
            }
        )
        self.assertEqual(resp.status_code, 201)

    def test_post_turtle_nest_hatchling_emergence_outliers(self):
        url = reverse('api:turtlehatchlingemergenceoutlierobservation-list')
        resp = self.client.post(
            url,
            {
                'source': 'odk',
                'source_id': 'uuid:b2910a04-fc7b-4bb0-8570-febcb939022e',
                'bearing_outlier_track_degrees': 0,
            }
        )
        self.assertEqual(resp.status_code, 201)

    def test_post_light_source_observation(self):
        url = reverse('api:lightsourceobservation-list')
        resp = self.client.post(
            url,
            {
                'source': 'odk',
                'source_id': 'uuid:b2910a04-fc7b-4bb0-8570-febcb939022e',
                'bearing_light_degrees': 0,
            }
        )
        self.assertEqual(resp.status_code, 201)
