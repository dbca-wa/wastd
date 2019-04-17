# -*- coding: utf-8 -*-
""".

Functional tests
^^^^^^^^^^^^^^^^
Functional tests are walk-throughs of all implemented real-world use cases.
Expected scenarios are the "happy path". Unexpected scenarios should be tested
as they become apparent, either as "this should never happen" or as bugs.
The documentation of functional test should read almost like a detailed user manual.

The documentation of functional tests is:

* the main resource for business to review correct implementation,
* a UAT test script for business,
* a structured and comprehensive way for the developers to match requirements.

This test suite is a walk-through of the following taxonomy business processes:

* List, filter, export selection of species or communities
* Traverse phylogeny of a taxon
* Traverse name history of a taxon (older / newer names)
* [WACensus] Create new taxon
* [WACensus] Create xref
* [WACensus] Change xref
* [WACensus] View xref change history
* What if a taxon's phylogenic or name history sibling is conservation listed?
* [REQ 5] Include the following dashboard pages:
* Dashboard of all species included in the system
* Dashboard of all lists of threatened or priority species
* Dashboard of all occurrence reports (draft or approved) per species
* Filter the data shown on the dashboard pages by clicking a location on a map,
  on species file number or species group
* [REQ 19] Enable the user to choose authoritative names from WACensus. (= select from dropdowns).
  Allow for temporarily entering species names not yet been included in the
  species master list (WACensus) in use by the Department (i.e. informal or phrase names).
  This is to facilitate batch upload of data from sources that may not have authoritative names.
  Align entered species with the species master list once the species has been added to the master list.
* [REQ 27] Integrate with the WACensus system to fetch an authoritative list of species.
  Test: WACensus ETL
* [REQ 28] Integrate with the WAHerb Specimen Database and BioSys to cross-reference locational information regarding
  rare flora occurrences (eg via sheet number). Pending WAHerb upgrade.
"""

from __future__ import unicode_literals

from django.utils import timezone  # noqa

from django.contrib.auth import get_user_model  # noqa
from django.contrib.gis.geos import GEOSGeometry  # Point, Polygon   # noqa
from django.test import TestCase  # noqa
from django.urls import reverse  # noqa
from model_mommy import mommy  # noqa
from mommy_spatial_generators import MOMMY_SPATIAL_FIELDS  # noqa
from taxonomy.models import Taxon, Community  # noqa
from conservation import models as cons_models  # noqa


class TaxonListFilterTests(TestCase):
    """Test that the Taxon list is useable.

    * During a phone call, filter taxon list to candidate taxa as per phone conversation.
    * Filter by area
    * Filter by cons listing (all threatened, all prio, both), cons list scope (WA, CWTH, INTL)

    """

    fixtures = ['taxonomy/fixtures/test_taxonomy.json', ]
