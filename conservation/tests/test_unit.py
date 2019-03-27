# -*- coding: utf-8 -*-
"""Unit tests for Conservation module."""
from __future__ import unicode_literals

from datetime import timedelta

from django.utils import timezone
from django.test import TestCase

from taxonomy.models import Taxon
from conservation import models as cons_models

# from requests import RequestsClient
# client = RequestsClient()
# response = client.get('http://localhost:8220')
# assert response.status_code == 200

# Test fileattachment creation, str
# Test cons crit, cons cat
# Test gazettal


class ConservationListModelTests(TestCase):
    """ConservationList unit tests."""

    def setUp(self):
        """Setup: create a new list."""
        self.cl = cons_models.ConservationList(
            code='test',
            label='test list',
            approval_level=cons_models.ConservationList.APPROVAL_IMMEDIATE)

    def test__str__(self):
        """Test the string method."""
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

        self.gaz = cons_models.TaxonGazettal.objects.create(
            taxon=self.taxon,
            scope=cons_models.TaxonGazettal.SCOPE_WESTERN_AUSTRALIA,
        )

    def test__str__(self):
        """Test the string method."""
        x = "{0} {1} {2} {3}".format(
            self.gaz.get_scope_display(),
            self.gaz.taxon,
            self.gaz.category_cache,
            self.gaz.criteria_cache
        ).strip()
        self.assertEqual(self.gaz.__str__(), x)


class ConservationThreatModelTests(TestCase):
    """Unit tests for ConservationThreat."""

    def setUp(self):
        """Set up."""
        self.consthreatcat = cons_models.ConservationThreatCategory.objects.create(
            code="weeds", label="Weeds", description="invasive weeds")
        self.consthreat = cons_models.ConservationThreat.objects.create(
            category=self.consthreatcat,
            cause="burn some stuff"
        )

    def test_consthreat_str(self):
        """Test cons threat string."""
        label = "[{0}] {1}".format(
            self.consthreat.category.label,
            self.consthreat.cause)
        self.assertEqual(label, self.consthreat.__str__())


class ConservationActionModelTests(TestCase):
    """Unit tests for ConservationAction."""

    def setUp(self):
        """Set up."""
        self.consactioncat = cons_models.ConservationActionCategory.objects.create(
            code="burn", label="Burn", description="Burn everything")
        self.consaction = cons_models.ConservationAction.objects.create(
            category=self.consactioncat,
            instructions="burn some stuff"
        )

    def test_consaction_created_is_status_new(self):
        """Test that a newly created conservation action shows status NEW."""
        self.assertEqual(self.consaction.status, cons_models.ConservationAction.STATUS_NEW)

    def test_consaction_with_past_completion_date_is_status_completed(self):
        """Test that a conservation action with a past completion date shows status COMPLETED."""
        self.consaction.completion_date = timezone.now()
        self.consaction.save()
        self.assertEqual(self.consaction.status, cons_models.ConservationAction.STATUS_COMPLETED)

        self.consaction.completion_date = timezone.now() - timedelta(1)  # tomorrow
        self.consaction.save()
        self.assertEqual(self.consaction.status, cons_models.ConservationAction.STATUS_COMPLETED)

    def test_consaction_with_future_completion_date_is_status_completed(self):
        """Test that a conservation action with a future completion date shows status NEW or INPROGRESS."""
        self.consaction.completion_date = timezone.now() + timedelta(1)  # tomorrow
        self.consaction.save()
        self.assertEqual(self.consaction.implementation_notes, None)
        self.assertEqual(self.consaction.status, cons_models.ConservationAction.STATUS_NEW)

        self.consaction.implementation_notes = "Some notes have been added to show progress."
        self.consaction.save()
        self.assertEqual(self.consaction.status, cons_models.ConservationAction.STATUS_INPROGRESS)

    def test_create_consactivity(self):
        """Test that creating a conservation activity sets the conservation action status to INPROGRESS."""
        ca = cons_models.ConservationActivity.objects.create(
            conservation_action=self.consaction
        )
        self.assertTrue(isinstance(ca, cons_models.ConservationActivity))
        self.assertEqual(self.consaction.conservationactivity_set.count(), 1)
        self.assertEqual(self.consaction.implementation_notes, None)
        self.assertEqual(self.consaction.status, cons_models.ConservationAction.STATUS_INPROGRESS)


class ConservationActivityModelTests(TestCase):
    """Unit tests for ConservationActivity."""

    def setUp(self):
        """Set up."""
        self.consactioncat = cons_models.ConservationActionCategory.objects.create(
            code="burn", label="Burn", description="Burn everything")
        self.consaction = cons_models.ConservationAction.objects.create(
            category=self.consactioncat,
            instructions="burn some stuff"
        )
        self.consact = cons_models.ConservationActivity.objects.create(
            conservation_action=self.consaction,
        )

    def test_conservation_activity_str(self):
        """Test ConservationActivity str.

        ConservationActivity string contains cons action category, completion date,
        completion status and implementation notes.
        """
        label = "[{0}][{1}] {2}".format(
            self.consact.conservation_action.category,
            self.consact.completion_date.strftime("%d/%m/%Y") if self.consact.completion_date else "in progress",
            self.consact.implementation_notes)
        self.assertEqual(label, self.consact.__str__())


class DocumentModelTests(TestCase):
    """Document unit tests.

    * Recovery plan must have ID (number), date approved, plan type.
    * Document (such as rec plan) can be linked to onr or many species
      and/or one or many communities.
    * [REQ 25] Store original and final version of nomination form as Word + PDF documents,
      plus additional attributes to facilitate reporting.
    * [REQ 41] Plans automatically numbered from a single number pool. Test that documents have PK.
    """

    pass
