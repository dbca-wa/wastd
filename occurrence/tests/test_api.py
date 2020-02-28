from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from io import BytesIO
import json
# from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from unittest import skip

from occurrence.models import (
    AreaEncounter, ObservationGroup, HabitatComposition, PlantCount, CountMethod, CountAccuracy,
    AnimalObservation, SecondarySigns, FileAttachment,
)

User = get_user_model()


class ObservationGroupSerializerTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('testuser', 'testuser@test.com', 'pass')
        self.user.is_staff = True
        self.user.is_superuser = True  # TODO: test user/group permissions properly
        self.user.save()
        self.client.login(username='testuser', password='pass')
        # token = Token.objects.get(user__username='testuser')
        # self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.ae = AreaEncounter.objects.create(description='Test AreaEncounter')
        self.og = ObservationGroup.objects.create(encounter=self.ae)
        self.hc = HabitatComposition.objects.create(encounter=self.ae)
        self.url = reverse('api:occurrence_observation_group-list')

    def test_occ_observation_get(self):
        """Test the occurrence_observation_group API endpoint, unfiltered
        """
        resp = self.client.get(self.url, {'format': 'json'})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        # Response should return two objects.
        self.assertEqual(data['count'], 2)

    def test_occ_observation_get_filtered(self):
        """Test the occurrence_observation_group API endpoint, filtered
        """
        resp = self.client.get(self.url, {'format': 'json', 'obstype': 'HabitatComposition'})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        # Response should return one HabitatComposition object (no ObservationGroup objects).
        self.assertEqual(data['count'], 1)
        self.assertFalse('ObservationGroup' in [i['obstype'] for i in data['results']])

    def test_occ_observation_post(self):
        """Test the occurrence_observation_group API POST endpoint for object types not requiring special cases
        """
        models = [
            'HabitatComposition', 'HabitatCondition', 'AreaAssessment', 'FireHistory', 'VegetationClassification']
        for model in models:
            resp = self.client.post(self.url, {
                'obstype': model,
                'source': self.ae.source,
                'source_id': self.ae.source_id,
            })
            self.assertEqual(resp.status_code, 201)

    def test_occ_observation_post_plantcount(self):
        """Test the PlantCount POST endpoint behaves correctly
        """
        resp = self.client.get(self.url, {'format': 'json', 'obstype': 'PlantCount'})
        data = json.loads(resp.content)
        self.assertEqual(data['count'], 0)
        # The PlantCount API endpoint requires count_method and count_accuracy as valid slug values.
        # Bad request:
        resp = self.client.post(self.url, {
            'obstype': 'PlantCount',
            'source': self.ae.source,
            'source_id': self.ae.source_id,
        })
        self.assertEqual(resp.status_code, 400)
        count_method = CountMethod.objects.create(code='estimate', label='Estimate')
        count_accuracy = CountAccuracy.objects.create(code='estimate', label='Estimate')
        # Good request:
        resp = self.client.post(self.url, {
            'obstype': 'PlantCount',
            'source': self.ae.source,
            'source_id': self.ae.source_id,
            'count_method': count_method.code,
            'count_accuracy': count_accuracy.code,
        })
        self.assertEqual(resp.status_code, 201)
        # Confirm that a PlantCount object was created.
        resp = self.client.get(self.url, {'format': 'json', 'obstype': 'PlantCount'})
        data = json.loads(resp.content)
        self.assertEqual(data['count'], 1)

    def test_occ_observation_post_animalobservation(self):
        """Test the AnimalObservation POST endpoint behaves correctly
        """
        # If secondary_signs values are passed into the endpoint, they need to be parseable as valid slugs.
        SecondarySigns.objects.create(code='fur', label='Fur')
        resp = self.client.post(self.url, data={
            'obstype': 'AnimalObservation',
            'source': self.ae.source,
            'source_id': self.ae.source_id,
            'secondary_signs': ('fur',),
        })
        self.assertEqual(resp.status_code, 201)
        SecondarySigns.objects.create(code='eggs', label='Eggs')
        # Parse >1 secondary_signs value.
        resp = self.client.post(self.url, data={
            'obstype': 'AnimalObservation',
            'source': self.ae.source,
            'source_id': self.ae.source_id,
            'secondary_signs': ('fur', 'eggs'),
        })
        self.assertEqual(resp.status_code, 201)
        # Confirm that secondary_signs is optional.
        resp = self.client.post(self.url, {
            'obstype': 'AnimalObservation',
            'source': self.ae.source,
            'source_id': self.ae.source_id,
        })
        self.assertEqual(resp.status_code, 201)

    @skip("Can't make file uploads work with djangorestframework :(")
    def test_occ_observation_post_fileattachment(self):
        """Test the FileAttachment POST endpoint behaves correctly
        """
        testfile = BytesIO(b'some test binary data')
        testfile.name = 'test.txt'
        resp = self.client.post(self.url, {
            'obstype': 'FileAttachment',
            'source': self.ae.source,
            'source_id': self.ae.source_id,
            'attachment': testfile,
        })
        self.assertEqual(resp.status_code, 201)
