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
