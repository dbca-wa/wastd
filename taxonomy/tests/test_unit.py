# -*- coding: utf-8 -*-
""".

Taxonomy unit tests
^^^^^^^^^^^^^^^^^^^
Unit tests cover the basic functionality, such as model functions and permissions.
The documentation of unit tests will state the obvious and confirm implementation
details which are implicitly expected as common sense.
This test suite covers:

* [REQ 4] Bulk-load a list of species into the system:
  Test API endpoints for all WACensus tables with real WACensus data.
* Reconstruct taxonomic names from WACensus data in Hbv* staging models.
* Critical habitat of a species or community.

General requirements:

* [REQ 43] Make use of the Department’s central customer database for storing and retrieving
  details of any individual or organisation outside the Department that have access to the system
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

from taxonomy import models as tax_models
from taxonomy.templatetags import taxonomy_tags as tt
from taxonomy.utils import update_taxon  # noqa
from conservation import models as cons_models
MOMMY_CUSTOM_FIELDS_GEN = MOMMY_SPATIAL_FIELDS


class TaxonUtilsTests(TestCase):
    """Unit tests for taxonomy utils."""

    fixtures = [
        'taxonomy/fixtures/test_taxonomy.json',
        # 'taxonomy/fixtures/test_wacensus.json',
    ]

    def test_update_taxon(self):
        """Test reconstructing Taxon, Crossreference and Vernacular from Hbv*."""
        # update_taxon() # requires a consistent subset of the taxonomic tree
        pass


class TaxonUnitTests(TestCase):
    """Taxon unit tests."""

    fixtures = ['taxonomy/fixtures/test_taxonomy.json', ]

    def test_taxon_creation(self):
        """Test creating a Taxon."""
        pass

    def test_taxon_str(self):
        """Test Taxon string representation."""
        t = tax_models.Taxon.objects.last()
        self.assertIn(t.name, t.__str__())

    def test_build_canonical_name(self):
        """Test the canonical name."""
        t = tax_models.Taxon.objects.last()
        self.assertIn(t.name, t.build_canonical_name)

    def test_build_taxonomic_name(self):
        """Test the taxonomic name."""
        t = tax_models.Taxon.objects.last()
        self.assertIn(t.name, t.build_taxonomic_name)

    def test_build_vernacular_name(self):
        """Test the vernacular name."""
        pass

    def test_build_vernacular_names(self):
        """Test the vernacular names."""
        pass

    def test_gazettals(self):
        """Test gazettals."""
        pass

    def test_documents(self):
        """Test documents."""
        pass

    def test_is_listed(self):
        """Test that is_listed tells the conservation listing status."""
        pass


class CommunityUnitTests(TestCase):
    """Community tests."""

    def setUp(self):
        """Shared objects."""
        self.object = mommy.make(tax_models.Community, _fill_optional=['code', 'name', 'eoo'])
        # self.user = get_user_model().objects.create_superuser(
        #     username="superuser", email="super@gmail.com", password="test")
        # self.client.force_login(self.user)

    def test_community_creation(self):
        """Test creating a Community."""
        self.assertTrue(isinstance(self.object, tax_models.Community))
        # self.assertEqual(object.__unicode__(), object.name)


class TemplateTagTests(TestCase):
    """Template tag tests."""

    def setUp(self):
        """Shared objects."""
        self.user = get_user_model().objects.create_superuser(
            username="superuser", email="super@gmail.com", password="test")

        self.taxon, created = tax_models.Taxon.objects.update_or_create(
            name_id=0,
            defaults=dict(name="Eukarya",
                          rank=tax_models.Taxon.RANK_DOMAIN,
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
