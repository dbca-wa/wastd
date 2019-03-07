# -*- coding: utf-8 -*-
"""Occurrence test suite.

https://model-mommy.readthedocs.io/en/latest/
https://github.com/sigma-geosistemas/mommy_spatial_generators
"""
from __future__ import unicode_literals

from django.utils import timezone


from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry  # Point, Polygon
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
# from django.urls import reverse
from model_mommy import mommy
from mommy_spatial_generators import MOMMY_SPATIAL_FIELDS  # noqa
from occurrence import models as occ_models
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

        self.cae = occ_models.CommunityAreaEncounter.objects.create(
            community=self.com0,
            encountered_on=timezone.now(),
            encountered_by=self.user,
            point=GEOSGeometry('POINT (115 -32)', srid=4326)
        )

        self.asssp1 = occ_models.AssociatedSpeciesObservation.objects.create(
            encounter=self.cae,
            taxon=self.taxon0
        )
        self.asssp1.save()

        self.fh1 = occ_models.FireHistoryObservation.objects.create(
            encounter=self.cae,
            last_fire_date=timezone.now().date(),
            fire_intensity=occ_models.FireHistoryObservation.HMLN_HIGH
        )
        self.fh1.save()

        self.aa0 = occ_models.AreaAssessmentObservation.objects.create(
            encounter=self.cae,
            area_surveyed_m2=None,
            survey_duration_min=None
        )
        self.aa0.save()

        self.aa1 = occ_models.AreaAssessmentObservation.objects.create(
            encounter=self.cae,
            area_surveyed_m2=200,
            survey_duration_min=None
        )
        self.aa1.save()

        self.aa2 = occ_models.AreaAssessmentObservation.objects.create(
            encounter=self.cae,
            area_surveyed_m2=532,
            survey_duration_min=47
        )
        self.aa2.save()

        self.client.force_login(self.user)

    def test_cae_creation(self):
        """Test creating a CommunityAreaEncounter."""
        self.assertTrue(isinstance(self.cae, occ_models.CommunityAreaEncounter))

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

    # ------------------------------------------------------------------------#
    # CAE AssociatedSpeciesObservation
    def test_asssp_creation(self):
        """Test creating a AssociatedSpeciesObservation."""
        self.assertTrue(isinstance(self.asssp1, occ_models.AssociatedSpeciesObservation))

    # ------------------------------------------------------------------------#
    # CAE FireHistoryObservation
    def test_fh_creation(self):
        """Test creating a FireHistoryObservation."""
        self.assertTrue(isinstance(self.fh1, occ_models.FireHistoryObservation))

    # ------------------------------------------------------------------------#
    # CAE AreaAssessmentObservation
    def test_aa_creation(self):
        """Test creating an AreaAssessmentObservation."""
        self.assertTrue(isinstance(self.aa0, occ_models.AreaAssessmentObservation))
        self.assertTrue(isinstance(self.aa1, occ_models.AreaAssessmentObservation))
        self.assertTrue(isinstance(self.aa2, occ_models.AreaAssessmentObservation))

    def test_aa_str(self):
        """Test AreaAssessmentObservation.__str__()."""
        aa0_str = "{0} of {1} m2 in {2} mins".format(
            self.aa0.get_survey_type_display(),
            self.aa0.area_surveyed_m2,
            self.aa0.survey_duration_min)
        self.assertEqual(aa0_str, self.aa0.__str__())
        aa1_str = "{0} of {1} m2 in {2} mins".format(
            self.aa1.get_survey_type_display(),
            self.aa1.area_surveyed_m2,
            self.aa1.survey_duration_min)
        self.assertEqual(aa1_str, self.aa1.__str__())
        aa2_str = "{0} of {1} m2 in {2} mins".format(
            self.aa2.get_survey_type_display(),
            self.aa2.area_surveyed_m2,
            self.aa2.survey_duration_min)
        self.assertEqual(aa2_str, self.aa2.__str__())

    def test_aa_survey_effort_minutes_per_100sqm(self):
        """Test AreaAssessmentObservation.survey_effort_minutes_per_100sqm."""
        se = round(100 * (self.aa2.survey_duration_min / self.aa2.area_surveyed_m2))
        self.assertTrue(self.aa0.survey_effort_minutes_per_100sqm is None)
        self.assertTrue(self.aa1.survey_effort_minutes_per_100sqm is None)
        self.assertTrue(self.aa2.survey_effort_minutes_per_100sqm == se)


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

        self.tae = occ_models.TaxonAreaEncounter.objects.create(
            taxon=self.taxon0,
            encountered_on=timezone.now(),
            encountered_by=self.user,
            point=GEOSGeometry('POINT (115 -32)', srid=4326)
        )

        self.asssp1 = occ_models.AssociatedSpeciesObservation.objects.create(
            encounter=self.tae,
            taxon=self.taxon1
        )
        self.asssp1.save()

        self.asssp2 = occ_models.AssociatedSpeciesObservation.objects.create(
            encounter=self.tae,
            taxon=self.taxon2
        )
        self.asssp2.save()

        self.fh1 = occ_models.FireHistoryObservation.objects.create(
            encounter=self.tae,
            last_fire_date=timezone.now(),
            fire_intensity=occ_models.FireHistoryObservation.HMLN_HIGH
        )
        self.fh1.save()

        self.fatt = occ_models.FileAttachmentObservation.objects.create(
            encounter=self.tae,
            attachment=SimpleUploadedFile('testfile.txt', b'These are the file contents.'),
            title="test",
            author=self.user
        )
        self.fatt.save()

        self.client.force_login(self.user)

    def test_tae_creation(self):
        """Test creating a TaxonAreaEncounter."""
        self.assertTrue(isinstance(self.tae, occ_models.TaxonAreaEncounter))

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

    # ------------------------------------------------------------------------#
    # TAE AssociatedSpeciesObservation
    def test_asssp_creation(self):
        """Test creating a AssociatedSpeciesObservation."""
        self.assertTrue(isinstance(self.asssp1, occ_models.AssociatedSpeciesObservation))

    # ------------------------------------------------------------------------#
    # TAE FireHistoryObservation
    def test_fh_creation(self):
        """Test creating a FireHistoryObservation."""
        self.assertTrue(isinstance(self.fh1, occ_models.FireHistoryObservation))

    # ------------------------------------------------------------------------#
    # TAE FileAttachmentObservation
    def test_fatt_creation(self):
        """Test creating a FileAttachmentObservation."""
        self.assertTrue(isinstance(self.fatt, occ_models.FileAttachmentObservation))
