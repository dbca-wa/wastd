# -*- coding: utf-8 -*-
"""Taxonomy test suite.

https://model-mommy.readthedocs.io/en/latest/
https://github.com/sigma-geosistemas/mommy_spatial_generators
"""
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from model_mommy import mommy
from mommy_spatial_generators import MOMMY_SPATIAL_FIELDS  # noqa
from taxonomy.models import Community, Taxon

MOMMY_CUSTOM_FIELDS_GEN = MOMMY_SPATIAL_FIELDS


class TaxonTestMommy(TestCase):
    """Taxon tests."""

    def setUp(self):
        """Shared objects."""
        self.object = mommy.make(Taxon, name_id=1000, _fill_optional=['name', 'rank', 'eoo'])
        self.user = get_user_model().objects.create_superuser(
            username="superuser", email="super@gmail.com", password="test")
        self.client.force_login(self.user)

    def test_taxon_creation_mommy(self):
        """Test creating a Taxon."""
        self.assertTrue(isinstance(self.object, Taxon))
        # self.assertEqual(what.__unicode__(), what.title)

    def test_taxon_absolute_admin_url_loads(self):
        """Test absolute admin url."""
        response = self.client.get(self.object.absolute_admin_url)
        self.assertEqual(response.status_code, 200)

    def test_taxon_detail_url_loads(self):
        """Test taxon detail url works and loads."""
        url_detail = reverse('taxonomy:taxon-detail', kwargs={"name_id": self.object.name_id})
        self.assertEqual(url_detail, self.object.get_absolute_url())

        response = self.client.get(self.object.get_absolute_url())
        self.assertEqual(response.status_code, 200)


class CommunityTestMommy(TestCase):
    """Community tests."""

    def setUp(self):
        """Shared objects."""
        self.object = mommy.make(Community, _fill_optional=['code', 'name', 'eoo'])
        self.user = get_user_model().objects.create_superuser(
            username="superuser", email="super@gmail.com", password="test")
        self.client.force_login(self.user)

    def test_community_creation_mommy(self):
        """Test creating a Community."""
        self.assertTrue(isinstance(self.object, Community))
        # self.assertEqual(object.__unicode__(), object.name)

    def test_taxon_absolute_admin_url_loads(self):
        """Test absolute admin url."""
        url = self.object.absolute_admin_url
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_community_detail_url_loads(self):
        """Test community detail url works and loads."""
        url_detail = reverse('taxonomy:community-detail', kwargs={"pk": self.object.pk})
        self.assertEqual(url_detail, self.object.get_absolute_url())

        response = self.client.get(self.object.get_absolute_url())
        self.assertEqual(response.status_code, 200)
