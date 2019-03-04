# -*- coding: utf-8 -*-
"""Occurrence test suite.

https://model-mommy.readthedocs.io/en/latest/
https://github.com/sigma-geosistemas/mommy_spatial_generators
"""
from __future__ import unicode_literals

from django.utils import timezone

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry  # Point, Polygon
from django.test import TestCase
from django.urls import reverse
from model_mommy import mommy
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


class CommunityAreaEncounterTests(TestCase):
    """CommunityAreaEncounter and related ObservationGroup tests."""

    def setUp(self):
        """Shared objects.

        Bugs with TestMommy vs django-polymorphic:
        https://github.com/django-polymorphic/django-polymorphic/issues/280
        https://github.com/django-polymorphic/django-polymorphic/issues/109


          polymorphic/models.py", line 112, in get_real_instance_class
          and not issubclass(model, self.__class__._meta.proxy_for_model):
          TypeError: issubclass() arg 2 must be a class or tuple of classes
        """
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

        self.cae = CommunityAreaEncounter.objects.create(
            community=self.com0,
            encountered_on=timezone.now(),
            encountered_by=self.user,
            point=GEOSGeometry('POINT (115 -32)', srid=4326)
        )

        self.asssp1 = AssociatedSpeciesObservation.objects.create(
            encounter=self.cae,
            taxon=self.taxon0
        )
        self.asssp1.save()

        self.fh1 = FireHistoryObservation.objects.create(
            encounter=self.cae,
            last_fire_date=timezone.now().date(),
            fire_intensity=FireHistoryObservation.HMLN_HIGH
        )
        self.fh1.save()

        self.client.force_login(self.user)

    def test_cae_creation(self):
        """Test creating a CommunityAreaEncounter."""
        self.assertTrue(isinstance(self.cae, CommunityAreaEncounter))

    def test_cae_str(self):
        """Test CAE str."""
        label = "Encounter of {5} at [{0}] ({1}) {2} on {3} by {4}".format(
            self.cae.get_area_type_display(),
            self.cae.code,
            self.cae.name,
            self.cae.encountered_on,
            self.cae.encountered_by,
            self.cae.community)
        self.assertEqual(label, self.cae.__str__())

    def test_cae_absolute_admin_url_loads(self):
        """Test CommunityAreaEncounter absolute_admin_url."""
        response = self.client.get(self.cae.absolute_admin_url)
        self.assertEqual(response.status_code, 200)

    def test_cae_list_url_loads(self):
        """Test that CommunityAreaEncounter list_url is com detail url and loads."""
        self.assertEqual(self.cae.list_url(), self.cae.community.get_absolute_url())

        response = self.client.get(self.cae.list_url())
        self.assertEqual(response.status_code, 200)

    def test_cae_detail_url_loads(self):
        """Test CommunityAreaEncounter detail_url."""
        url = reverse('occurrence:communityareaencounter-detail',
                      kwargs={'pk': self.cae.community.pk})
        self.assertEqual(url, self.cae.detail_url)

        response = self.client.get(self.cae.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_cae_update_url_loads(self):
        """Test CommunityAreaEncounter update_url."""
        url = reverse(
            'occurrence:communityareaencounter-update',
            kwargs={'pk': self.cae.community.pk})
        self.assertEqual(url, self.cae.update_url)

        response = self.client.get(self.cae.update_url)
        self.assertEqual(response.status_code, 200)

    def test_cae_create_url_loads(self):
        """Test CommunityAreaEncounter create_url."""
        url = reverse('occurrence:communityareaencounter-create')
        self.assertEqual(url, self.cae.update_url)

        response = self.client.get(self.cae.update_url)
        self.assertEqual(response.status_code, 200)

    # ------------------------------------------------------------------------#
    # CAE AssociatedSpeciesObservation
    def test_asssp_creation(self):
        """Test creating a AssociatedSpeciesObservation."""
        self.assertTrue(isinstance(self.asssp1, AssociatedSpeciesObservation))

    def test_asssp_absolute_admin_url_loads(self):
        """Test AssociatedSpeciesObservation absolute_admin_url."""
        response = self.client.get(self.asssp1.absolute_admin_url)
        self.assertEqual(response.status_code, 200)

    def test_asssp_detail_url_loads(self):
        """Test AssociatedSpeciesObservation detail_url."""
        response = self.client.get(self.asssp1.detail_url)
        self.assertEqual(response.status_code, 200)

    def test_asssp_update_url_loads(self):
        """Test AssociatedSpeciesObservation update_url."""
        response = self.client.get(self.asssp1.update_url)
        self.assertEqual(response.status_code, 200)

    # ------------------------------------------------------------------------#
    # CAE FireHistoryObservation
    def test_fh_creation(self):
        """Test creating a FireHistoryObservation."""
        self.assertTrue(isinstance(self.fh1, FireHistoryObservation))

    def test_fh_absolute_admin_url_loads(self):
        """Test FireHistoryObservation absolute_admin_url."""
        response = self.client.get(self.fh1.absolute_admin_url)
        self.assertEqual(response.status_code, 200)

    def test_fh_detail_url_loads(self):
        """Test FireHistoryObservation detail_url."""
        response = self.client.get(self.fh1.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_fh_update_url_loads(self):
        """Test FireHistoryObservation update_url."""
        response = self.client.get(self.fh1.update_url)
        self.assertEqual(response.status_code, 200)


class TaxonAreaEncounterTests(TestCase):
    """TaxonAreaEncounter and related ObservationGroup tests."""

    def setUp(self):
        """Shared objects.

        Bugs with TestMommy vs django-polymorphic:
        https://github.com/django-polymorphic/django-polymorphic/issues/280
        https://github.com/django-polymorphic/django-polymorphic/issues/109


          polymorphic/models.py", line 112, in get_real_instance_class
          and not issubclass(model, self.__class__._meta.proxy_for_model):
          TypeError: issubclass() arg 2 must be a class or tuple of classes
        """
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

        self.user = get_user_model().objects.create_superuser(
            username="superuser",
            email="super@gmail.com",
            password="test")
        self.user.save()

        self.tae = TaxonAreaEncounter.objects.create(
            taxon=self.taxon0,
            encountered_on=timezone.now(),
            encountered_by=self.user,
            point=GEOSGeometry('POINT (115 -32)', srid=4326)
        )

        self.asssp1 = AssociatedSpeciesObservation.objects.create(
            encounter=self.tae,
            taxon=self.taxon1
        )
        self.asssp1.save()

        self.asssp2 = AssociatedSpeciesObservation.objects.create(
            encounter=self.tae,
            taxon=self.taxon2
        )
        self.asssp2.save()

        self.fh1 = FireHistoryObservation.objects.create(
            encounter=self.tae,
            last_fire_date=timezone.now(),
            fire_intensity=FireHistoryObservation.HMLN_HIGH
        )
        self.fh1.save()

        self.client.force_login(self.user)

    def test_tae_creation(self):
        """Test creating a TaxonAreaEncounter."""
        self.assertTrue(isinstance(self.tae, TaxonAreaEncounter))

    def test_tae_str(self):
        """Test TAE str."""
        label = "Encounter of {5} at [{0}] ({1}) {2} on {3} by {4}".format(
            self.tae.get_area_type_display(),
            self.tae.code,
            self.tae.name,
            self.tae.encountered_on,
            self.tae.encountered_by,
            self.tae.taxon)
        self.assertEqual(label, self.tae.__str__())

    def test_tae_absolute_admin_url_loads(self):
        """Test absolute admin url."""
        response = self.client.get(self.tae.absolute_admin_url)
        self.assertEqual(response.status_code, 200)

    def test_tae_list_url_loads(self):
        """Test that TaxonAreaEncounter list_url is taxon detail url and loads."""
        self.assertEqual(self.tae.list_url(), self.tae.taxon.get_absolute_url())

        response = self.client.get(self.tae.list_url())
        self.assertEqual(response.status_code, 200)

    def test_tae_detail_url_loads(self):
        """Test taxon detail url works and loads."""
        detail_url_constructed = reverse('occurrence:taxonareaencounter-detail',
                                         kwargs={'pk': self.tae.pk})
        self.assertEqual(detail_url_constructed, self.tae.get_absolute_url())

        response = self.client.get(self.tae.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_tae_update_url_loads(self):
        """Test taxon update url works and loads."""
        update_url_constructed = reverse('occurrence:taxonareaencounter-update',
                                         kwargs={'pk': self.tae.pk})
        self.assertEqual(update_url_constructed, self.tae.update_url)

        response = self.client.get(self.tae.update_url)
        self.assertEqual(response.status_code, 200)

    # ------------------------------------------------------------------------#
    # TAE AssociatedSpeciesObservation
    def test_asssp_creation(self):
        """Test creating a AssociatedSpeciesObservation."""
        self.assertTrue(isinstance(self.asssp1, AssociatedSpeciesObservation))

    def test_asssp_absolute_admin_url_loads(self):
        """Test AssociatedSpeciesObservation absolute_admin_url."""
        url = self.asssp1.absolute_admin_url
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_asssp_detail_url_loads(self):
        """Test AssociatedSpeciesObservation detail_url."""
        response = self.client.get(self.asssp1.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_asssp_update_url_loads(self):
        """Test AssociatedSpeciesObservation update_url."""
        response = self.client.get(self.asssp1.update_url)
        self.assertEqual(response.status_code, 200)

    # ------------------------------------------------------------------------#
    # TAE FireHistoryObservation
    def test_fh_creation(self):
        """Test creating a FireHistoryObservation."""
        self.assertTrue(isinstance(self.fh1, FireHistoryObservation))

    def test_fh_absolute_admin_url_loads(self):
        """Test FireHistoryObservation absolute_admin_url."""
        response = self.client.get(self.fh1.absolute_admin_url)
        self.assertEqual(response.status_code, 200)

    def test_fh_detail_url_loads(self):
        """Test FireHistoryObservation detail_url."""
        response = self.client.get(self.fh1.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_fh_update_url_loads(self):
        """Test FireHistoryObservation update_url."""
        response = self.client.get(self.fh1.update_url)
        self.assertEqual(response.status_code, 200)
