# -*- coding: utf-8 -*-
"""Conservation view test suite.

https://model-mommy.readthedocs.io/en/latest/
https://github.com/sigma-geosistemas/mommy_spatial_generators
"""
from __future__ import unicode_literals

from django.utils import timezone  # noqa

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry  # Point, Polygon   # noqa
from django.test import TestCase
from django.urls import reverse  # noqa
from model_mommy import mommy  # noqa
from mommy_spatial_generators import MOMMY_SPATIAL_FIELDS  # noqa

from conservation.models import (  # noqa
    ConservationList,
    TaxonGazettal,
    ConservationActionCategory,
    ConservationAction,
    ConservationActivity
)


class ConservationListViewTests(TestCase):
    """ConservationList view tests."""

    def setUp(self):
        """Setup: create a new list."""
        self.user = get_user_model().objects.create_superuser(
            username="superuser",
            email="super@gmail.com",
            password="test")
        self.user.save()
        self.client.force_login(self.user)

        self.cl = ConservationList(
            code='test',
            label='test list',
            approval_level=ConservationList.APPROVAL_IMMEDIATE)

    def test_conservation_list_absolute_admin_url(self):
        """Test ConservationList absolute admin url."""
        response = self.client.get(self.cl.absolute_admin_url)
        self.assertEqual(response.status_code, 200)


class ConservationActionCategoryViewTests(TestCase):
    """View tests for ConservationActionCategory."""

    def setUp(self):
        """Set up."""
        self.consactioncat = ConservationActionCategory.objects.create(
            code="burn", label="Burn", description="Burn everything")
        self.consaction = ConservationAction.objects.create(
            category=self.consactioncat,
            instructions="burn some stuff"
        )
        self.user = get_user_model().objects.create_superuser(
            username="superuser",
            email="super@gmail.com",
            password="test")
        self.user.save()
        self.client.force_login(self.user)

    def test_conservation_action_category_absolute_admin_url(self):
        """Test ConservationActionCategory absolute admin url."""
        response = self.client.get(self.consactioncat.absolute_admin_url)
        self.assertEqual(response.status_code, 200)


class ConservationActionViewTests(TestCase):
    """View tests for ConservationAction."""

    def setUp(self):
        """Set up."""
        self.consactioncat = ConservationActionCategory.objects.create(
            code="burn", label="Burn", description="Burn everything")
        self.consaction = ConservationAction.objects.create(
            category=self.consactioncat,
            instructions="burn some stuff"
        )
        self.user = get_user_model().objects.create_superuser(
            username="superuser",
            email="super@gmail.com",
            password="test")
        self.user.save()
        self.client.force_login(self.user)

    def test_conservation_action_absolute_admin_url(self):
        """Test ConservationAction absolute admin url."""
        response = self.client.get(self.consaction.absolute_admin_url)
        self.assertEqual(response.status_code, 200)

    def test_conservation_action_list_url_loads(self):
        """Test conservationaction-list."""
        url = reverse('conservationaction-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class ConservationActivityViewTests(TestCase):
    """View tests for ConservationActivity."""

    def setUp(self):
        """Set up."""
        self.consactioncat = ConservationActionCategory.objects.create(
            code="burn", label="Burn", description="Burn everything")
        self.consaction = ConservationAction.objects.create(
            category=self.consactioncat,
            instructions="burn some stuff"
        )
        self.consact = ConservationActivity.objects.create(
            conservation_action=self.consaction,
        )
        self.user = get_user_model().objects.create_superuser(
            username="superuser",
            email="super@gmail.com",
            password="test")
        self.user.save()
        self.client.force_login(self.user)

    def test_conservation_activity_absolute_admin_url(self):
        """Test ConservationActivity absolute admin url."""
        response = self.client.get(self.consact.absolute_admin_url)
        self.assertEqual(response.status_code, 200)

    def test_conservation_activity_str(self):
        """Test ConservationActivity str."""
        label = "[{0}][{1}] {2}".format(
            self.consact.conservation_action.category,
            self.consact.completion_date.strftime("%d/%m/%Y") if self.consact.completion_date else "in progress",
            self.consact.implementation_notes)
        self.assertEqual(label, self.consact.__str__())
