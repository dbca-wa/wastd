from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
import json
from rest_framework.test import APIClient

User = get_user_model()


class UserAPITests(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser('testuser', 'testuser@test.com', 'pass')
        self.client = APIClient()
        self.client.login(username='testuser', password='pass')

    def test_get_list(self):
        url = reverse('api:user-list')
        resp = self.client.get(url, {'format': 'json'})
        self.assertEqual(resp.status_code, 200)

    def test_filter(self):
        self.user.name = 'Test User'
        self.user.save()
        url = reverse('api:user-list')
        resp = self.client.get(url, {'format': 'json', 'name': 'Test User'})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data['count'], 1)

    def test_get_detail(self):
        url = reverse('api:user-detail', kwargs={'pk': self.user.pk})
        resp = self.client.get(url, {'format': 'json'})
        self.assertEqual(resp.status_code, 200)

    def test_post(self):
        url = reverse('api:user-list')
        resp = self.client.post(
            url,
            {
                'username': 'newuser',
                'email': 'newuser@test.com',
                'name': 'New User',
            }
        )
        self.assertEqual(resp.status_code, 201)

    def test_patch(self):
        url = reverse('api:user-detail', kwargs={'pk': self.user.pk})
        resp = self.client.patch(
            url,
            {
                'nickname': 'nick',
            }
        )
        self.assertEqual(resp.status_code, 200)

