# -*- coding: utf-8 -*-
"""Taxonomy test suite.

https://model-mommy.readthedocs.io/en/latest/
https://github.com/sigma-geosistemas/mommy_spatial_generators
"""
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase
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
