from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
import json
#from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from occurrence.models import AreaEncounter, ObservationGroup, HabitatComposition


User = get_user_model()


class ObservationGroupSerializerTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('testuser', 'testuser@test.com', 'pass')
        self.user.is_staff = True
        self.user.is_superuser = True  # TODO: test user/group permissions properly
        self.user.save()
        self.client.login(username='testuser', password='pass')
        #token = Token.objects.get(user__username='testuser')
        #self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.ae = AreaEncounter(description='Test AreaEncounter')
        self.ae.save()
        self.og = ObservationGroup(encounter=self.ae)
        self.og.save()
        self.hc = HabitatComposition(encounter=self.ae)
        self.hc.save()
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
        """Test the occurrence_observation_group API POST endpoint
        """
        resp = self.client.post(self.url, {
            'format': 'json',
            'obstype': 'HabitatComposition',
            'source': self.ae.source,
            'source_id': self.ae.source_id,
        })
        self.assertEqual(resp.status_code, 201)
        resp = self.client.get(self.url, {'format': 'json', 'obstype': 'HabitatComposition'})
        data = json.loads(resp.content)
        # Response should return two HabitatComposition objects.
        self.assertEqual(data['count'], 2)
