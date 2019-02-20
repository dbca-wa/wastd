# -*- coding: utf-8 -*-
"""Taxonomy test suite.

https://model-mommy.readthedocs.io/en/latest/
https://github.com/sigma-geosistemas/mommy_spatial_generators
"""
from __future__ import unicode_literals

from django.utils import timezone  # noqa

from django.contrib.auth import get_user_model  # noqa
from django.contrib.gis.geos import GEOSGeometry  # Point, Polygon  # noqa
from django.test import TestCase  # noqa
from django.urls import reverse  # noqa
from model_mommy import mommy  # noqa
from mommy_spatial_generators import MOMMY_SPATIAL_FIELDS  # noqa
from occurrence.models import (  # noqa
    CommunityAreaEncounter,
    TaxonAreaEncounter,
    AssociatedSpeciesObservation,
    FireHistoryObservation
)
from taxonomy.models import Community, Taxon  # noqa
# from django.contrib.contenttypes.models import ContentType

MOMMY_CUSTOM_FIELDS_GEN = MOMMY_SPATIAL_FIELDS


from taxonomy.models import Community, Taxon  # noqa


class CommunityViewTests(TestCase):
    """Community tests."""

    def setUp(self):
        """Shared objects."""
        self.com = mommy.make(
            Community,
            code="code0",
            name="name0",
            _fill_optional=['eoo'])
        self.com0.save()

        self.com1 = mommy.make(
            Community,
            code="code1",
            name="name1",
            _fill_optional=['eoo'])
        self.com1.save()

        self.taxon0 = mommy.make(
            Taxon,
            name_id=1000,
            name="name0",
            _fill_optional=['rank', 'eoo'])
        self.taxon0.save()

        self.user = get_user_model().objects.create_superuser(
            username="superuser",
            email="super@gmail.com",
            password="test")
        self.user.save()
        self.client.force_login(self.user)

    def test_com_creation(self):
        """Test creating a Community."""
        self.assertTrue(isinstance(self.com, Community))

    def test_com_absolute_admin_url_loads(self):
        """Test Community absolute_admin_url."""
        response = self.client.get(self.com.absolute_admin_url)
        self.assertEqual(response.status_code, 200)

    def test_com_list_url_loads(self):
        """Test community-list."""
        url = reverse('community-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_com_detail_url_loads(self):
        """Test Community detail_url."""
        url = reverse('community-detail', kwargs={'pk': self.com.pk})
        self.assertEqual(url, self.com.detail_url)

        response = self.client.get(self.com.detail_url)
        self.assertEqual(response.status_code, 200)

    def test_com_update_url_loads(self):
        """Test Community update_url."""
        url = reverse('community-update', kwargs={'pk': self.com.pk})
        self.assertEqual(url, self.com.update_url)

        response = self.client.get(self.com.update_url)
        self.assertEqual(response.status_code, 200)


class TaxonViewTests(TestCase):
    """Taxon view tests."""

    def setUp(self):
        """Shared objects."""
        self.com = mommy.make(
            Community,
            code="code0",
            name="name0",
            _fill_optional=['eoo'])
        self.com0.save()

        self.com1 = mommy.make(
            Community,
            code="code1",
            name="name1",
            _fill_optional=['eoo'])
        self.com1.save()

        self.taxon = mommy.make(
            Taxon,
            name_id=1000,
            name="name0",
            _fill_optional=['rank', 'eoo'])
        self.taxon0.save()

        self.user = get_user_model().objects.create_superuser(
            username="superuser",
            email="super@gmail.com",
            password="test")
        self.user.save()

        self.client.force_login(self.user)

    def test_taxon_creation(self):
        """Test creating a Taxon."""
        self.assertTrue(isinstance(self.taxon, Taxon))

    def test_taxon_absolute_admin_url_loads(self):
        """Test Taxon absolute_admin_url."""
        response = self.client.get(self.taxon.absolute_admin_url)
        self.assertEqual(response.status_code, 200)

    def test_taxon_list_url_loads(self):
        """Test taxon-list."""
        url = reverse('taxon-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_taxon_detail_url_loads(self):
        """Test Taxon detail_url."""
        url = reverse('taxon-detail', kwargs={'name_id': self.taxon.name_id})
        self.assertEqual(url, self.taxon.detail_url)

        response = self.client.get(self.taxon.detail_url)
        self.assertEqual(response.status_code, 200)

    def test_taxon_update_url_loads(self):
        """Test Taxon update_url."""
        url = reverse('taxon-update', kwargs={'name_id': self.taxon.name_id})
        self.assertEqual(url, self.taxon.update_url)

        response = self.client.get(self.taxon.update_url)
        self.assertEqual(response.status_code, 200)
