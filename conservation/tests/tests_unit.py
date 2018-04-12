# -*- coding: utf-8 -*-
"""Unit tests for Conservation module."""
from __future__ import unicode_literals

from django.test import TestCase

from ..models import ConservationList

# from requests import RequestsClient
# client = RequestsClient()
# response = client.get('http://localhost:8220')
# assert response.status_code == 200


class TestConervationList(TestCase):
    """ConservationList unit tests."""

    def setUp(self):
        """Setup: create a new list."""
        self.cl = ConservationList(
            code='test',
            label='test list',
            approval_level=ConservationList.APPROVAL_IMMEDIATE)

    def test__str__(self):
        """Test that the string method ."""
        self.assertEqual(
            self.cl.__str__(),
            'test')
