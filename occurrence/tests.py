# -*- coding: utf-8 -*-
"""Occurrence test suite.

https://model-mommy.readthedocs.io/en/latest/
https://github.com/sigma-geosistemas/mommy_spatial_generators
"""
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from model_mommy import mommy
from mommy_spatial_generators import MOMMY_SPATIAL_FIELDS  # noqa
from occurrence.models import CommunityAreaEncounter, TaxonAreaEncounter
from taxonomy.models import Community, Taxon

MOMMY_CUSTOM_FIELDS_GEN = MOMMY_SPATIAL_FIELDS


class TaxonAreaEncounterTestMommy(TestCase):
    """TaxonAreaEncounter tests."""

    def setUp(self):
        """Shared objects."""
        self.taxon = mommy.make(Taxon, name_id=1000, _fill_optional=['name', 'rank', 'eoo'])
        self.obj = mommy.make(TaxonAreaEncounter, taxon=self.taxon, _fill_optional=True)
        self.user = get_user_model().objects.create_superuser(
            username="superuser", email="super@gmail.com", password="test")
        self.client.force_login(self.user)

    def test_tae_creation_mommy(self):
        """Test creating a TaxonAreaEncounter."""
        self.assertTrue(isinstance(self.obj, TaxonAreaEncounter))
        # self.assertEqual(what.__unicode__(), what.title)

    def test_tae_absolute_admin_url_loads(self):
        """Test absolute admin url."""
        url = self.obj.absolute_admin_url
        # response = self.client.get(url)
        # self.assertEqual(response.status_code, 200)
        pass

    def test_tae_detail_url_loads(self):
        """Test taxon detail url works and loads."""
        detail_url_constructed = reverse(
            'taxon-occurrence-detail',
            kwargs={'name_id': self.obj.taxon.name_id, 'occ_pk': self.obj.pk})
        self.assertEqual(detail_url_constructed, self.obj.detail_url)

        # throws https://github.com/django-polymorphic/django-polymorphic/issues/109
        # response = self.client.get(self.obj.detail_url)
        # self.assertEqual(response.status_code, 200)
