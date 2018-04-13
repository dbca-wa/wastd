# -*- coding: utf-8 -*-
"""Unit tests for Conservation module."""
from __future__ import unicode_literals

from django.test import TestCase

from taxonomy.models import Taxon
from conservation.models import ConservationList, TaxonGazettal

# from requests import RequestsClient
# client = RequestsClient()
# response = client.get('http://localhost:8220')
# assert response.status_code == 200


class TestConservationList(TestCase):
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


class TestTaxonGazettal(TestCase):
    """Unit tests for TaxonGazettal."""

    def setUp(self):
        """Set up."""
        self.taxon, created = Taxon.objects.update_or_create(
            name_id=0,
            defaults=dict(name="Eukarya",
                          rank=Taxon.RANK_DOMAIN,
                          current=True,
                          parent=None))

        self.gaz = TaxonGazettal.objects.create(
            taxon=self.taxon,
            scope=TaxonGazettal.SCOPE_WESTERN_AUSTRALIA,
        )
        # add cat and crit to gaz

    def test__str__(self):
        """Test str."""
        pass
