# -*- coding: utf-8 -*-
""".

Taxonomy API tests
^^^^^^^^^^^^^^^^^^
The API is the beer tap for data. This test suite makes sure the beer is fresh and cold.

Applications in general:

* Load legacy data: create and update data
* Retrieve TSC data for analysis: list and filter data
* Provide TSC data to other services: list in various detail level

This suite tests the following use cases:

* Import WACensus: An
  `external script <https://github.com/dbca-wa/scarab-scripts/blob/master/data_etl_wacensus.Rmd>`_
  reads published WACensus views from the KMI GeoServer as JSON and uploads it
  into the corresponding taxonomy.Hbv* API endpoints.
  Related: `Occurrences from WAHerb <https://github.com/dbca-wa/scarab-scripts/blob/master/waherb.Rmd>`_.

* Communities: An `external script <https://github.com/dbca-wa/scarab-scripts/blob/master/data_etl_tec.Rmd>`_
  loads a list of communities through the community API endpoint.
"""
from __future__ import unicode_literals

import json
# from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth import get_user_model  # noqa
from django.test import TestCase
from django.template import Context, Template  # noqa
from django.template.loader import get_template  # noqa
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

# from model_mommy import mommy
from mommy_spatial_generators import MOMMY_SPATIAL_FIELDS  # noqa

from taxonomy import models as tax_models  # noqa


class HbvAPITests(TestCase):
    """API tests for the WACensus staging models taxonomy.models.Hbv*."""

    def setUp(self):
        """Provide test data.

        In real-world scenarios, the data used to feed the WACensus staging
        tables (Hbv*) of the Taxonomy API comes from KMI's GeoServer.
        For the purpose of testing, we'll save a representative subset as JSON
        fixtures.

        Data from the KMI GeoServer's views of WACensus data views is saved
        as a local JSON fixture for the purpose of testing.
        """
        pass

    def create_hbv_models(self):
        """Test the API create views of Hbv* models.

        Applications:

        * Test WACensus data import: The data from WACensus as JSON is
        POSTed to the taxon API endpoint.
        TSC creates Hbv* instances as exact copy of WACensus Hbv* views.
        """
        pass

    def list_and_filter_hbv_models(self):
        """Test the API list views and filters of Hbv* staging models.

        Applications:

        * Verify KMI to TSC import of WACensus data: compare KMI JSON to TSC JSON.
        * Filter the list of Hbv* staging models to identify problematic records.
        * Filter the list of Hbv* models to find specific records.
        """
        pass

    def view_hbv_models(self):
        """Test the API detail views of Hbv* staging models."""
        pass

    def update_hbv_models(self):
        """Test the API update views of Hbv* staging models.

        Applications:

        * Test repeated WACensus data import: make sure existing models are updated
          (based on unique fields) rather than duplicates created.
        """
        pass


class TaxonAPITests(TestCase):
    """API tests for Taxon.

    Taxa are expected to be created as reconstructed from WACensus data in the Hbv* staging models.
    Temporary taxonomic names could be created in TSC, but this is expected to happen through the admin.

    The Taxon API is expected to serve taxonomic names together with their associated conservation
    and occurrence data to downstream services.
    """

    fixtures = ['taxonomy/fixtures/test_taxonomy.json', ]

    def setUp(self):
        """Set up Taxon API tests."""
        self.user = get_user_model().objects.filter(is_superuser=True).first()
        if not self.user:
            self.user = get_user_model().objects.create_superuser(
                username="superuser",
                email="super@gmail.com",
                password="test")
        self.user.save()

        # Use data from text fixtures over constants from settings
        self.animal_pk = tax_models.HbvSupra.objects.get(supra_code="ANIMALS").pk
        self.plant_pk = tax_models.HbvSupra.objects.get(supra_code="PLANTS").pk

        self.client = APIClient()
        # Option 1: use Token authentication
        # self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user.auth_token.key)
        # Option 2: bypass authentication
        self.client.force_authenticate(user=self.user)

    def list_taxon(self):
        """Test the list and filter of taxon API endpoints for both full and partial field sets.

        Applications:

        * Provide a list of taxonomic names to external services.
        * Provide full detail or cut down, fast subsets.
        """
        
        taxon_list = self.client.get("/api/1/taxon/")
        self.assertEqual(taxon_list.status_code, 200)
        # taxon list is a featurecollection
        self.assertTrue("type" in taxon_list.data)
        self.assertTrue("features" in taxon_list.data)
        self.assertTrue(taxon_list.data["type"], "FeatureCollection")

    def test_taxon_list_filters_animals(self):
        """Test that the taxon list can be filtered to only animals.

        The request ``/api/1/taxon/?paraphyletic_groups=20`` returns only animal taxa:

        * Each taxon must contain paraphyletic group settings.ANIMALS_PK (e.g. 20).
        * No taxon must contain paraphyletic group settings.PLANTS_PK (e.g. 21).
        """
        animal_list = self.client.get("/api/1/taxon/?paraphyletic_groups={0}".format(self.animal_pk))
        
        # Smoke test
        self.assertEqual(animal_list.status_code, 200)
        
        # Each taxon must contain paraphyletic group settings.ANIMALS_PK
        self.assertEqual(
            set([self.animal_pk in x["paraphyletic_groups"] for x in animal_list.data["features"]]), 
            {True}
        )
        # No taxon must contain paraphyletic group settings.PLANTS_PK
        self.assertEqual(
            set([self.plant_pk in x["paraphyletic_groups"] for x in animal_list.data["features"]]), 
            {False}
        )

    def test_taxon_list_filters_plants(self):
        """Test that the taxon list can be filtered to only plants (sensu latu).


        The request ``/api/1/taxon/?paraphyletic_groups=21`` returns only plant taxa (sensu latu):

        * Each taxon must contain paraphyletic group settings.PLANTS_PK (e.g. 21).
        * No taxon must contain paraphyletic group settings.ANIMALS_PK (e.g. 20).
        """
        plant_list = self.client.get("/api/1/taxon/?paraphyletic_groups={0}".format(self.plant_pk))

        # Smoke test
        self.assertEqual(plant_list.status_code, 200)
        
        # No taxon must contain paraphyletic group settings.ANIMALS_PK
        self.assertEqual(
            set([self.animal_pk in x["paraphyletic_groups"] for x in plant_list.data["features"]]), 
            {False}
        )
        
        # Each taxon must contain paraphyletic group settings.PLANTS_PK
        self.assertEqual(
            set([self.plant_pk in x["paraphyletic_groups"] for x in plant_list.data["features"]]), 
            {True}
        )


    def test_taxon_with_conservation_status(self):
        """Test publishing the conservation status of taxa to other services e.g. WACensus.

        See `#166 <https://github.com/dbca-wa/wastd/issues/166>`_.

        WACensus currently hosts a view of TPFL's conservation status and a local, temporary,
        implementation of fauna conservation. This information is disseminated to a wide variety of
        downstream systems, including NatureMap, PubSys (from there to FloraBase),
        Max (distributed to external companies) and Wildlife Licensing.
        With the sunsetting of TFL, conservation status must be available to WACensus through TSC's API.

        The data required is as follows:

        ::

          NAME_ID,CONSV_CODE,LIST_CODE,EPBC,WA_IUCN,IUCN_CRITERIA
          228,3,Priority,,,
          297,T,WCA_1991,EN,VU,D1+2
          436,T,WCA_1991,EN,EN,B1+2c
          473,3,Priority,,,
          474,1,Priority,,,
        """
        pass


class CommunityAPITests(TestCase):
    """Community tests."""

    def setUp(self):
        """Read JSON from fixture."""
        pass

    def create_communities(self):
        """The data from TEC as JSON is POSTed to the community API endpoint."""
        pass

    def list_communities(self):
        """Test the API list view of communities."""
        pass

    def view_communities(self):
        """Test the API detail view of communities."""
        pass

    def update_communities(self):
        """Test that updating communities overwrites existing ones."""
        pass
