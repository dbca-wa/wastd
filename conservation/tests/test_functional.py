# -*- coding: utf-8 -*-
"""
Conservation functional test suite.

This test suite is a walk-through of the following conservation business processes:

* Conservation listing: life cycle, permissions, query, list, export
* Conservation activity: create, list, filter, export, task list for different roles
* Document: approval, approval permissions, publication
* Animal Ethics (AE): Document type "SOP". Standard operating procedures (SOPs) exist
  for all the aspects of animal handling i.e. "best practice".
  The system needs to track SOP approval life cycle. e.g. approvals, reviews, minor changes.
* [OOS] Declared Rare Flora (DRF) permits are handled by Wildlife Licensing System (WLS)

[REQ 1] Allow for recording of conservation status details of a species:
* It must be possible to include a recorded species in one or more threatened species lists.
* The system must allow for a species to be included in a threatened or priority species list,
  and a Single Operational List for nationally threatened species.
* The system must keep track of the history of species included in any list.

[REQ 2] Allow for the creation of multiple lists for threatened species.
Each species can be listed on zero or more lists.
New type of lists can be added by business at any time.

[REQ 3] Allow for the creation of additional species data fields on a per species type basis.
Comment: Common set of attributes in TSC. Extra data goes on a per-dataset level to BioSys
but is accessible at analysis time.

[REQ 8] Publish any document attached to any entity in the system,
or any communication recorded in the context of such entity, in the Department’s
record keeping system. This requirement is covered by being in a corporate system (TSC) under
OIM's SLA for data retention and backups.

On conservation status:
"The Wildlife Conservation Act 1950 and Biodiversity Conservation Act 2016 provide for the listing of
threatened native species and (in the future) ecological communities that need special protection.
Where insufficient information is available to undertake a conservation assessment, the Department
may assign a “priority” status.

Species and ecological community listing or priority assignment affect operational
management approach and data visibility.

Changes may be made at either State or Commonwealth level via submissions made to the
relevant committees (Threatened Species Scientific Committee = TSSC, Threatened
Ecological Communities Scientific Committee = TECSC). A historical record of these
assignments, and critical decision-making steps, is required to be captured and maintained.

This information is consumed in many departmental systems, firstly by WACensus, and then
by downstream sites such as FloraBase, NatureMap, BioSys and the departmental website,
as well as sent on to relevant stakeholders. Conservation status flows through to external
systems such as the Atlas of Living Australia, providing broader data visibility. The timely
maintenance and distribution of conservation status is therefore crucial to retaining the
integrity of threatened species populations and communities.

Static reports are also generated for the DBCA web site." Paul 5.2

On management actions:

"Given that other DBCA work areas implement management actions, any system support
implemented for SCB should be considered and managed as part of a coordinated response
to departmental requirements." Paul 1

On managment plans:

"Management plans (e.g. recovery plans, interim recovery plans and species management plans) may
be written for specific species, communities (or logical groups of both, based on area or ecological or
other relationships) to assist in their protection and maintenance. Formal approvals processes exist
to govern the proposal, assessment, endorsement, publication, implementation and review of plans.
System support is required for the entire management plan life cycle, including audit trails and,
ideally, version control." Paul 5.3

On Fauna Translocations:
"From Corporate Guideline 36, the Department undertakes the recovery of threatened species
through translocation and captive breeding or propagation, where the primary objective is a
conservation benefit. (Recovery plans may include translocations as a recovery action.) SCB
coordinates flora and fauna translocations, and oversees the approvals processes for threatened
flora and fauna translocation proposals.
System support is required for the translocation proposal life cycle, including proposal submission,
assessment, approval, amendment and review." Paul 5.4

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


class ConservationListingLifeCycleTests(TestCase):
    """Functional tests for the ConservationListing (Gazettal) life cycle.

    This test suite tests:

    * Create a conservation listing
    * Approval steps through instances (committee, branch manager,
      director, director general, minister) - who is allowed to approve what when
      (permissions, conditions, consequences)
    * Gazettal, date and time, publication, where is it shown (DBCA website?)
    * Review at set dates - reminders, todo lists, who is responsible
    * Retiring a CL: through creting a new gazettal, through ministerial decision,
    through notice (national) or API  (international)
    """

    def setUp(self):
        """Set up."""
        pass

    def test_only_admin_can_create_gazettal(self):
        """Conservation Listings can only be created by admins.

        Only data curators with admin access can create new conservation listings.
        """
        pass


class ConservationListingReportingTests(TestCase):
    """Functional tests for ConservationListing (Gazettal) reporting.

    This test suite tests:

    * Query and export conservation listing history (several CL of one taxon or community)
    * Query and export conservation listing approval history (within one CL)
    * Query and export conservation lists (all taxa listed as conservation category X)
    """

    def setUp(self):
        """Set up."""
        pass


class DocumentLifeCycleTests(TestCase):
    """Functional tests for Document life cycles.

    This test suite tests:

    * Document creation: who can create which document type?
    * Document approval - for each type
    * Document review - notification, todo lists, who is responsible

    *

    """

    pass
