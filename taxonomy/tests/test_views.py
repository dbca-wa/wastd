# -*- coding: utf-8 -*-
"""Taxonomy view test suite testing URLs, templates, and views."""
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
from conservation import models as cons_models
from taxonomy.models import Community, Taxon, Crossreference
# from django.contrib.contenttypes.models import ContentType

MOMMY_CUSTOM_FIELDS_GEN = MOMMY_SPATIAL_FIELDS


from taxonomy.models import Community, Taxon  # noqa


class CommunityViewTests(TestCase):
    """Community tests."""

    def setUp(self):
        """Shared objects."""
        self.com0 = mommy.make(
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
        self.assertTrue(isinstance(self.com0, Community))

    def test_com_absolute_admin_url_loads(self):
        """Test Community absolute_admin_url."""
        response = self.client.get(self.com0.absolute_admin_url)
        self.assertEqual(response.status_code, 200)

    def test_com_list_url_loads(self):
        """Test community-list."""
        response = self.client.get(self.com0.list_url())
        self.assertEqual(response.status_code, 200)

    def test_com_detail_url_loads(self):
        """Test Community detail_url."""
        response = self.client.get(self.com0.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    # def test_com_update_url_loads(self):
    #     """Test Community update_url."""
    #     response = self.client.get(self.com0.update_url)
    #     self.assertEqual(response.status_code, 200)


class TaxonViewTests(TestCase):
    """Taxon view tests."""

    def setUp(self):
        """Shared objects."""
        self.com0 = mommy.make(
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

        self.taxon1 = mommy.make(
            Taxon,
            name_id=1001,
            name="name1",
            _fill_optional=['rank', 'eoo'])
        self.taxon1.save()

        self.taxon2 = mommy.make(
            Taxon,
            name_id=1002,
            name="name2",
            _fill_optional=['rank', 'eoo'])
        self.taxon2.save()

        self.xref01 = Crossreference.objects.create(
            predecessor=self.taxon1,
            successor=self.taxon0,
            reason=Crossreference.REASON_TSY
        )

        self.xref12 = Crossreference.objects.create(
            predecessor=self.taxon0,
            successor=self.taxon2,
            reason=Crossreference.REASON_TSY
        )

        self.user = get_user_model().objects.create_superuser(
            username="superuser",
            email="super@gmail.com",
            password="test")
        self.user.save()

        self.doc = mommy.make(cons_models.Document)
        self.doc.taxa.add(self.taxon0)
        self.doc.save()

        self.client.force_login(self.user)

    def test_taxon_creation(self):
        """Test creating a Taxon."""
        self.assertTrue(isinstance(self.taxon0, Taxon))

    def test_taxon_absolute_admin_url_loads(self):
        """Test Taxon absolute_admin_url."""
        response = self.client.get(self.taxon0.absolute_admin_url)
        self.assertEqual(response.status_code, 200)

    def test_taxon_list_url_loads(self):
        """Test taxon-list."""
        response = self.client.get(self.taxon0.list_url())
        self.assertEqual(response.status_code, 200)

    def test_taxon_detail_url_loads(self):
        """Test Taxon detail_url."""
        response = self.client.get(self.taxon0.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        # TODO test crossreference urls

    # def test_taxon_update_url_loads(self):
    #     """Test Taxon update_url."""
    #     response = self.client.get(self.taxon0.update_url)
    #     self.assertEqual(response.status_code, 200)
