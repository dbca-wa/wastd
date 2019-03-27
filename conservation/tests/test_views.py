# -*- coding: utf-8 -*-
"""Conservation view test suite testing URLs, templates, and views.

* [REQ 40] Include the following dashboard pages:
  * Dashboard of all plans: document list view and templates
  * Dashboard of all annual reports for all plans: document list view, filter plan type
  From within a dashboard, the user to open an entity and view the details.
  Test that document card contains detail link.
  Dashboard to show when details were last edited.
  Test that document card contains date last modified.


See also:
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
from taxonomy.models import Taxon, Community
from conservation import models as cons_models


class ConservationListViewTests(TestCase):
    """ConservationList view tests."""

    def setUp(self):
        """Setup: create a new list."""
        self.cl = cons_models.ConservationList.objects.create(
            code='test',
            label='test list',
            approval_level=cons_models.ConservationList.APPROVAL_IMMEDIATE)
        self.user = get_user_model().objects.create_superuser(
            username="superuser",
            email="super@gmail.com",
            password="test")
        self.user.save()
        self.client.force_login(self.user)

    def test_conservation_list_absolute_admin_url(self):
        """Test ConservationList absolute admin url."""
        response = self.client.get(self.cl.absolute_admin_url)
        self.assertEqual(response.status_code, 200)


class ConservationActionCategoryViewTests(TestCase):
    """View tests for ConservationActionCategory."""

    def setUp(self):
        """Set up."""
        self.object = cons_models.ConservationActionCategory.objects.create(
            code="burn", label="Burn", description="Burn everything")
        self.consaction = cons_models.ConservationAction.objects.create(
            category=self.object,
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
        response = self.client.get(self.object.absolute_admin_url)
        self.assertEqual(response.status_code, 200)


class ConservationThreatViewTests(TestCase):
    """View tests for ConservationThreat."""

    def setUp(self):
        """Set up."""
        self.taxon0 = mommy.make(
            Taxon,
            name_id=1000,
            name="name0",
            _fill_optional=['rank', 'eoo'])
        self.taxon0.save()
        self.com0 = mommy.make(
            Community,
            code="code0",
            name="name0",
            _fill_optional=['eoo'])
        self.com0.save()
        self.consthreatcat = cons_models.ConservationThreatCategory.objects.create(
            code="weeds", label="Weeds", description="invasive weeds")
        self.object = cons_models.ConservationThreat.objects.create(
            category=self.consthreatcat, cause="burn some stuff")
        self.object.taxa.add(self.taxon0)
        self.object.communities.add(self.com0)
        self.user = get_user_model().objects.create_superuser(
            username="superuser",
            email="super@gmail.com",
            password="test")
        self.user.save()
        self.client.force_login(self.user)

    def test_conservation_threat_absolute_admin_url(self):
        """Test ConservationThreat absolute admin url."""
        response = self.client.get(self.object.absolute_admin_url)
        self.assertEqual(response.status_code, 200)

    def test_get_absolute_url(self):
        """Test ConservationAction get absolute url loads."""
        response = self.client.get(self.object.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_list_url_loads(self):
        """Test conservationaction-list loads."""
        response = self.client.get(self.object.list_url())
        self.assertEqual(response.status_code, 200)

    def test_create_url_loads(self):
        """Test conservationaction-create loads."""
        response = self.client.get(self.object.create_url())
        self.assertEqual(response.status_code, 200)

    def test_update_url_loads(self):
        """Test conservationaction-update url loads."""
        response = self.client.get(self.object.update_url)
        self.assertEqual(response.status_code, 200)


class ConservationActionViewTests(TestCase):
    """View tests for ConservationAction."""

    def setUp(self):
        """Set up."""
        self.consactioncat = cons_models.ConservationActionCategory.objects.create(
            code="burn", label="Burn", description="Burn everything")
        self.taxon0 = mommy.make(
            Taxon,
            name_id=1000,
            name="name0",
            _fill_optional=['rank', 'eoo'])
        self.taxon0.save()
        self.com0 = mommy.make(
            Community,
            code="code0",
            name="name0",
            _fill_optional=['eoo'])
        self.com0.save()
        self.object = cons_models.ConservationAction.objects.create(
            category=self.consactioncat,
            instructions="burn some stuff"
        )
        self.object.taxa.add(self.taxon0)
        self.object.communities.add(self.com0)
        self.user = get_user_model().objects.create_superuser(
            username="superuser",
            email="super@gmail.com",
            password="test")
        self.user.save()
        self.client.force_login(self.user)

    def test_conservation_action_absolute_admin_url(self):
        """Test ConservationAction absolute admin url."""
        response = self.client.get(self.object.absolute_admin_url)
        self.assertEqual(response.status_code, 200)

    def test_get_absolute_url(self):
        """Test ConservationAction get absolute url loads."""
        response = self.client.get(self.object.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_list_url_loads(self):
        """Test conservationaction-list loads."""
        response = self.client.get(self.object.list_url())
        self.assertEqual(response.status_code, 200)

    def test_create_url_loads(self):
        """Test conservationaction-create loads."""
        response = self.client.get(self.object.create_url())
        self.assertEqual(response.status_code, 200)

    def test_update_url_loads(self):
        """Test conservationaction-update url loads."""
        response = self.client.get(self.object.update_url)
        self.assertEqual(response.status_code, 200)


class ConservationActivityViewTests(TestCase):
    """View tests for ConservationActivity."""

    def setUp(self):
        """Set up."""
        self.consactioncat = cons_models.ConservationActionCategory.objects.create(
            code="burn", label="Burn", description="Burn everything")
        self.consaction = cons_models.ConservationAction.objects.create(
            category=self.consactioncat,
            instructions="burn some stuff"
        )
        self.object = cons_models.ConservationActivity.objects.create(
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
        response = self.client.get(self.object.absolute_admin_url)
        self.assertEqual(response.status_code, 200)

    def test_get_absolute_url(self):
        """Test ConservationAction get absolute url."""
        response = self.client.get(self.object.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_list_url_loads(self):
        """Test conservationactivity-list."""
        response = self.client.get(self.object.list_url())
        self.assertEqual(response.status_code, 200)

    def test_create_url_loads(self):
        """Test conservationactivity-create."""
        response = self.client.get(self.object.create_url(self.consaction))
        self.assertEqual(response.status_code, 200)

    def test_update_url_loads(self):
        """Test conservationactivity-update."""
        response = self.client.get(self.object.update_url)
        self.assertEqual(response.status_code, 200)

    def test_conservation_activity_str(self):
        """Test ConservationActivity str."""
        label = "[{0}][{1}] {2}".format(
            self.object.conservation_action.category,
            self.object.completion_date.strftime("%d/%m/%Y")
            if self.object.completion_date else "in progress",
            self.object.implementation_notes)
        self.assertEqual(label, self.object.__str__())


class DocumentViewTests(TestCase):
    """View tests for Document."""

    def setUp(self):
        """Set up."""
        self.object = cons_models.Document.objects.create(
            title="test doc",
            document_type=cons_models.Document.TYPE_RECOVERY_PLAN
        )
        self.user = get_user_model().objects.create_superuser(
            username="superuser",
            email="super@gmail.com",
            password="test")
        self.user.save()
        self.client.force_login(self.user)

    def test_absolute_admin_url(self):
        """Test Document absolute admin url."""
        response = self.client.get(self.object.absolute_admin_url)
        self.assertEqual(response.status_code, 200)

    # def test_get_absolute_url(self):
    #     """Test ConservationAction get absolute url."""
    #     response = self.client.get(self.object.get_absolute_url())
    #     self.assertEqual(response.status_code, 200)

    # def test_list_url_loads(self):
    #     """Test conservationaction-list."""
    #     response = self.client.get(self.object.list_url())
    #     self.assertEqual(response.status_code, 200)

    # def test_create_url_loads(self):
    #     """Test conservationaction-create."""
    #     response = self.client.get(self.object.create_url())
    #     self.assertEqual(response.status_code, 200)

    # def test_update_url_loads(self):
    #     """Test conservationaction-update."""
    #     response = self.client.get(self.object.update_url)
    #     self.assertEqual(response.status_code, 200)
