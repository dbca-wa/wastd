# -*- coding: utf-8 -*-
"""Unit tests for Conservation module."""
from __future__ import unicode_literals

from datetime import timedelta

from django.utils import timezone
from django.test import TestCase

from taxonomy.models import Taxon
from conservation.models import (  # noqa
    ConservationList,
    TaxonGazettal,
    ConservationActionCategory,
    ConservationAction,
    ConservationActivity
)

# from requests import RequestsClient
# client = RequestsClient()
# response = client.get('http://localhost:8220')
# assert response.status_code == 200


class ConservationListModelTests(TestCase):
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


class TaxonGazettalModelTests(TestCase):
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


class ConservationActionModelTests(TestCase):
    """Unit tests for ConservationAction."""

    def setUp(self):
        """Set up."""
        self.consactioncat = ConservationActionCategory.objects.create(
            code="burn", label="Burn", description="Burn everything")
        self.consaction = ConservationAction.objects.create(
            category=self.consactioncat,
            instructions="burn some stuff"
        )

    def test_consaction_created_is_status_new(self):
        """Test that a new conservation action shows status NEW."""
        self.assertEqual(self.consaction.status, ConservationAction.STATUS_NEW)

    def test_consaction_with_past_completion_date_is_status_completed(self):
        """Test that a conservation action with a past completion date shows status COMPLETED."""
        self.consaction.completion_date = timezone.now()
        self.consaction.save()
        self.assertEqual(self.consaction.status, ConservationAction.STATUS_COMPLETED)

        self.consaction.completion_date = timezone.now() - timedelta(1)  # tomorrow
        self.consaction.save()
        self.assertEqual(self.consaction.status, ConservationAction.STATUS_COMPLETED)

    def test_consaction_with_future_completion_date_is_status_completed(self):
        """Test that a conservation action with a future completion date shows status NEW or INPROGRESS."""
        self.consaction.completion_date = timezone.now() + timedelta(1)  # tomorrow
        self.consaction.save()
        self.assertEqual(self.consaction.implementation_notes, None)
        self.assertEqual(self.consaction.status, ConservationAction.STATUS_NEW)

        self.consaction.implementation_notes = "Some notes have been added to show progress."
        self.consaction.save()
        self.assertEqual(self.consaction.status, ConservationAction.STATUS_INPROGRESS)
