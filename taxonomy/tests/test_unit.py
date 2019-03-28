# -*- coding: utf-8 -*-
"""Taxonomy unit test suite.

This test suite covers:

* [REQ 4] Bulk-load a list of species into the system:
  Test API endpoints for all WACensus tables with real WACensus data.
* Taxonomy is reconstructed from WACensus data
  (imported into staging models Hbv* via the API)
* Critical habitat of a species or community

General requirements:
* [REQ 43] Make use of the Department’s central customer database
  for storing and retrieving details of any individual or organisation
  outside the Department that have access to the system
* [REQ 44] Support single sign on security access for Department users accessing the system
* [REQ 45] A snapshot of current databases to be taken, and legacy data migrated into the new system.
  See Data ETL workbooks. Test API endpoints with example data. Add examples to wastdr vignettes.



On critical habitat:
"With the proclamation of the Biodiversity Conservation Act 2016, there will be a requirement to map
and maintain critical habitat. Adding a mapping capability to threatened flora and fauna occurrence
databases will inform the mapping of critical habitat, facilitate mapping population boundaries and
provide increased alignment with protocols for managing ecological communities." Paul 5.1
"""
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.template import Context, Template  # noqa
from django.template.loader import get_template  # noqa

from model_mommy import mommy
from mommy_spatial_generators import MOMMY_SPATIAL_FIELDS  # noqa

from taxonomy.models import Community, Taxon
from taxonomy.templatetags import taxonomy_tags as tt
from conservation import models as cons_models
MOMMY_CUSTOM_FIELDS_GEN = MOMMY_SPATIAL_FIELDS


class TaxonUnitTests(TestCase):
    """Taxon tests."""

    def setUp(self):
        """Shared objects."""
        self.object = mommy.make(Taxon, name_id=1000, _fill_optional=['name', 'rank', 'eoo'])
        self.user = get_user_model().objects.create_superuser(
            username="superuser", email="super@gmail.com", password="test")
        self.client.force_login(self.user)

    def test_taxon_creation(self):
        """Test creating a Taxon."""
        self.assertTrue(isinstance(self.object, Taxon))
        # self.assertEqual(what.__unicode__(), what.title)


class CommunityUnitTests(TestCase):
    """Community tests."""

    def setUp(self):
        """Shared objects."""
        self.object = mommy.make(Community, _fill_optional=['code', 'name', 'eoo'])
        self.user = get_user_model().objects.create_superuser(
            username="superuser", email="super@gmail.com", password="test")
        self.client.force_login(self.user)

    def test_community_creation(self):
        """Test creating a Community."""
        self.assertTrue(isinstance(self.object, Community))
        # self.assertEqual(object.__unicode__(), object.name)

# Test import WACensus: create a few HbV instances, run make_taxon_names, test resulting names.


class TemplateTagTests(TestCase):
    """Template tag tests."""

    def setUp(self):
        """Shared objects."""
        self.user = get_user_model().objects.create_superuser(
            username="superuser", email="super@gmail.com", password="test")

        self.taxon, created = Taxon.objects.update_or_create(
            name_id=0,
            defaults=dict(name="Eukarya",
                          rank=Taxon.RANK_DOMAIN,
                          current=True,
                          parent=None))

        self.gaz = cons_models.TaxonGazettal.objects.create(
            taxon=self.taxon,
            scope=cons_models.TaxonGazettal.SCOPE_WESTERN_AUSTRALIA,
            # TODO cons category, cons criteria
        )

    # def test_gazettal_labels(self):
    #     """Template tag test example."""
    #     c = {'original': self.taxon, 'user': self.user}
    #     t = get_template('include/gazettal.html')
    #     r = t.render(c)
    #     self.assertInHTML(r, '<h6 class="card-subtitle mb-2">')

    def test_rangify(self):
        """Test the rangify filter."""
        self.assertEqual(tt.rangify(10), range(5, 15))
