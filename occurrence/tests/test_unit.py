# -*- coding: utf-8 -*-
"""Occurrence unit test suite.

Test creation of occurrence data:

* TaxonAreaEncounters (TAE)
* CommunityAreaEncouters (CAE)
* ObservationGroups (Obs) and sub-models
* [REQ 6] AOO and EOO threshold alerts for reviewing status:
  Using updated occurrence data, flag a review of species or
  community conservation status when metrics such as
  AOO or EOO change by more than a given threshold, and alert an officer.
* Occurrences not handled by TSC can be stored in BioSys
* Show Biosys occurrences on map for reference
* When analysing TSC data, also query BioSys for data (wastdr?)

On Faunafile:

"This is a desktop Microsoft Access-based system that maintains much of the Department’s fauna
monitoring records for DBCA’s South West, Wheatbelt and South Coast Regions. Data from the most
recent version can be merged and warehoused in Oracle, and there is a program from upgrading
data from old formats to facilitate this process." Paul 6.3

"While FaunaFile has a long historical connection with SCD, and there are overlapping
processes and data, custodianship for its maintenance and development lies with FEMD.
While improvements to FaunaFile per se are out scope for this initial phase of
development, there are collaborative opportunities for alignment and integration in
subsequent phases." Paul 7

On Fauna Distribution Information System (FDIS):

"FDIS predicts the effects on fauna following forest operations and is used in the establishment of
fauna habitat zones. FDIS is currently the subject of a major redevelopment." Paul 6.4

On fire response data:
"Fire response data is not part of SCB management responsibility. The Threatened and
Priority Flora Database (TPFL) contains a recently added module for fire response data at
occurrence level, and TEC/PEC fire history data is recorded in the TEC database, but
summary-level information is not being maintained, and custodianship is unclear. The
extent to which current or additional system support is required, if any, will need to be
clarified during feature prioritisation." Paul 7

"Any business process or system not explicitly mentioned above as part of threatened
flora, fauna and ecological community management is deemed out of scope." Paul 7

[REQ 13] Data able to be exported to external systems such as the
Corporate Data Delivery Program (CDDP), environmental
impact assessment and ad hoc data requests.
Test: all data available through API. Taxonomy, occurrence, conservation.

[REQ 15] Admin user able to make global changes to fields (e.g. species names).
Test permissions, precisely which models. Species names come from WACensus.

[REQ 16] Allow user to choose a locality from a map (i.e. auto-complete coordinates).
Map widget in forms: geocoder.

[REQ 18] Allow for different security roles to be granted to the
users, including at a minimum read-only, officer, and system administrator.
TODO: what are the roles, what are the permissions, test each one.

[REQ 20] Admin users able to edit lookups (i.e. drop-down lists) used for data validation/entry.

[REQ 21] User able to extraction drop down field lists to external text and spreadsheet formats.

[REQ 22] Records for the same observation to be stored in more than one database. I
Implement a method that identifies record provenance.
Test for existence of source, source ID.

[REQ 23] Enable mapping of population boundaries and critical habitats (i.e. polygons, not just centroids).
Test TAE and CAE geom. Create, validate, view, export.

[REQ 42] Record all actions (e.g. changes to data) in an audit trail. Tax, Cons, Occ.
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

        Objects are not created with TestMommy.

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
            code="testcode",
            encountered_on=timezone.now(),
            encountered_by=self.user,
            point=GEOSGeometry('POINT (115 -32)', srid=4326)
        )
        self.cae.save()

        self.asssp1 = occ_models.AssociatedSpecies.objects.create(
            encounter=self.cae,
            taxon=self.taxon0
        )
        self.asssp1.save()

        self.fh1 = occ_models.FireHistory.objects.create(
            encounter=self.cae,
            last_fire_date=timezone.now().date(),
            fire_intensity=occ_models.FireHistory.HMLN_HIGH
        )
        self.fh1.save()

        self.aa0 = occ_models.AreaAssessment.objects.create(
            encounter=self.cae,
            area_surveyed_m2=None,
            survey_duration_min=None
        )
        self.aa0.save()

        self.aa1 = occ_models.AreaAssessment.objects.create(
            encounter=self.cae,
            area_surveyed_m2=200,
            survey_duration_min=None
        )
        self.aa1.save()

        self.aa2 = occ_models.AreaAssessment.objects.create(
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

    def test_cae_latitude(self):
        """Test the latitude from the point."""
        self.assertEqual(self.cae.latitude, -32)

    def test_cae_longitude(self):
        """Test the longitude from the point."""
        self.assertEqual(self.cae.longitude, 115)

    def test_derived_point(self):
        """Test that the derived point is either the centroid of geom or None."""
        self.assertIsNone(self.cae.geom)
        self.assertIsNone(self.cae.derived_point)

    def test_popup(self):
        """Test HTML popup."""
        self.assertIn(self.cae.code, self.cae.as_html)
        self.assertIn(self.cae.code, self.cae.derived_html)

    # ------------------------------------------------------------------------#
    # CAE AssociatedSpeciesObservation
    def test_asssp_creation(self):
        """Test creating a AssociatedSpeciesObservation."""
        self.assertTrue(isinstance(self.asssp1, occ_models.AssociatedSpecies))

    # ------------------------------------------------------------------------#
    # CAE FireHistoryObservation
    def test_fh_creation(self):
        """Test creating a FireHistoryObservation."""
        self.assertTrue(isinstance(self.fh1, occ_models.FireHistory))

    # ------------------------------------------------------------------------#
    # CAE AreaAssessmentObservation
    def test_aa_creation(self):
        """Test creating an AreaAssessmentObservation."""
        self.assertTrue(isinstance(self.aa0, occ_models.AreaAssessment))
        self.assertTrue(isinstance(self.aa1, occ_models.AreaAssessment))
        self.assertTrue(isinstance(self.aa2, occ_models.AreaAssessment))

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

        Save TAE/CAE twice to populate caches.

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
            code="testcode",
            encountered_on=timezone.now(),
            encountered_by=self.user,
            point=GEOSGeometry('POINT (115 -32)', srid=4326)
        )
        self.tae.save()

        self.asssp1 = occ_models.AssociatedSpecies.objects.create(
            encounter=self.tae,
            taxon=self.taxon1
        )
        self.asssp1.save()

        self.asssp2 = occ_models.AssociatedSpecies.objects.create(
            encounter=self.tae,
            taxon=self.taxon2
        )
        self.asssp2.save()

        self.fh1 = occ_models.FireHistory.objects.create(
            encounter=self.tae,
            last_fire_date=timezone.now(),
            fire_intensity=occ_models.FireHistory.HMLN_HIGH
        )
        self.fh1.save()

        self.fatt = occ_models.FileAttachment.objects.create(
            encounter=self.tae,
            attachment=SimpleUploadedFile(
                'testfile.txt', b'These are the file contents.'),
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

    def test_popup(self):
        """Test HTML popup."""
        self.assertIn(self.tae.code, self.tae.as_html)
        self.assertIn(self.tae.code, self.tae.derived_html)

    # ------------------------------------------------------------------------#
    # TAE AssociatedSpeciesObservation
    def test_asssp_creation(self):
        """Test creating a AssociatedSpecies."""
        self.assertTrue(isinstance(self.asssp1, occ_models.AssociatedSpecies))

    # ------------------------------------------------------------------------#
    # TAE FireHistoryObservation
    def test_fh_creation(self):
        """Test creating a FireHistory."""
        self.assertTrue(isinstance(self.fh1, occ_models.FireHistory))

    # ------------------------------------------------------------------------#
    # TAE FileAttachmentObservation
    def test_fatt_creation(self):
        """Test creating a FileAttachment."""
        self.assertTrue(isinstance(self.fatt, occ_models.FileAttachment))
