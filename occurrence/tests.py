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


class TaxonAreaEncounterTestMommy(TestCase):
    """TaxonAreaEncounter tests."""

    def setUp(self):
        """Shared objects.

        BUG: https://github.com/django-polymorphic/django-polymorphic/issues/280


          polymorphic/models.py", line 112, in get_real_instance_class
          and not issubclass(model, self.__class__._meta.proxy_for_model):
          TypeError: issubclass() arg 2 must be a class or tuple of classes
        """
        self.taxon0 = mommy.make(Taxon, name_id=1000, name="name0", _fill_optional=['rank', 'eoo'])
        self.taxon0.save()

        self.taxon1 = mommy.make(Taxon, name_id=1001, name="name1", _fill_optional=['rank', 'eoo'])
        self.taxon1.save()

        self.taxon2 = mommy.make(Taxon, name_id=1002, name="name2", _fill_optional=['rank', 'eoo'])
        self.taxon2.save()

        self.user = get_user_model().objects.create_superuser(
            username="superuser", email="super@gmail.com", password="test")
        self.user.save()

        # self.tae = mommy.make(TaxonAreaEncounter, taxon=self.taxon0, _fill_optional=True)
        # Fixes django-polymorphic/django-polymorphic/issues/280. sometimes.
        # self.tae.save()

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
        # new_ct = ContentType.objects.get_for_model(TaxonAreaEncounter)
        # TaxonAreaEncounter.objects.filter(polymorphic_ctype__isnull=True
        # ).update(polymorphic_ctype=new_ct)

        self.client.force_login(self.user)

    def test_tae_creation_mommy(self):
        """Test creating a TaxonAreaEncounter."""
        self.assertTrue(isinstance(self.tae, TaxonAreaEncounter))
        # self.assertEqual(what.__unicode__(), what.title)

    def test_tae_absolute_admin_url_loads(self):
        """Test absolute admin url."""
        url = self.tae.absolute_admin_url
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_tae_detail_url_loads(self):
        """Test taxon detail url works and loads."""
        detail_url_constructed = reverse(
            'taxon-occurrence-detail',
            kwargs={'name_id': self.tae.taxon.name_id, 'occ_pk': self.tae.pk})
        self.assertEqual(detail_url_constructed, self.tae.detail_url)

        # throws https://github.com/django-polymorphic/django-polymorphic/issues/109
        response = self.client.get(self.tae.detail_url)
        self.assertEqual(response.status_code, 200)
