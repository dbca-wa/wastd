# -*- coding: utf-8 -*-
""".

Conservation functional tests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This test suite is a walk-through of the following conservation business processes:

* Conservation listing: life cycle, permissions, query, list, export
* Conservation activity: create, list, filter, export, task list for different roles
* Document: approval, approval permissions, publication
* Animal Ethics (AE): Document type "SOP". Standard operating procedures (SOPs) exist
  for all the aspects of animal handling i.e. "best practice".
  The system needs to track SOP approval life cycle. e.g. approvals, reviews, minor changes.
* [OOS] Declared Rare Flora (DRF) permits are handled by Wildlife Licensing System (WLS)
* [REQ 1] Allow for recording of conservation status details of a species:
  * It must be possible to include a recorded species in one or more threatened species lists.
  * The system must allow for a species to be included in a threatened or priority species list,
    and a Single Operational List for nationally threatened species.
  * The system must keep track of the history of species included in any list.
* [REQ 2] Allow for the creation of multiple lists for threatened species.
  Each species can be listed on zero or more lists.
  New type of lists can be added by business at any time.
* [REQ 3] Allow for the creation of additional species data fields on a per species type basis.
  Comment: Common set of attributes in TSC. Extra data goes on a per-dataset level to BioSys
  but is accessible at analysis time.
* [REQ 8] Publish any document attached to any entity in the system,
  or any communication recorded in the context of such entity, in the Department’s
  record keeping system. This requirement is covered by being in a corporate system (TSC) under
  OIM's SLA for data retention and backups.
* [REQ 26][OAG 2a] Provide for the storage and management of conservation status information for
  flora, fauna and communities. Provide support for local, national and international listings,
  and provide a full history of changes.
* [REQ 29] Provide information regarding Threatened Fauna conservation status for
  BioSys and NatureMap websites automatically. Test: provide this data via API.
* [REQ 30] Produce various conservation status list reports in various formats
  (PDF, Microsoft word, Microsoft Excel) created using a variety of search criteria.
  Test: list, filter, export taxon/community list including conservation status.
* [REQ 31][OAG 2a] Allow for periodical of species or community listing,
  and alert an officer by the review date.
* [REQ 32] Capture the following attributes from species/communities nomination workflow:
  * Date of TSSC/TECSC assessment
  * Date of ministerial approval
  * Date of ConservationListing
  * Date referred to Commonwealth
  * Date listed under EPBC Act
* [REQ 33][REQ 39] Allow for the recording, per species or community, of
  * One or more management plans (could apply to any species or community)
  * One or more recovery plans (threatened species and communities)
  * One or more interim recovery plans (as per recovery plan but less detailed)
  Allow a plan to be linked to a threatened species or community included in a specific list;
  system must allow for different plans for one species or community included in different lists
* [REQ 34] Allow for the recording of one or more recovery or management actions for each plan.
  Allow for the recording of one or more success criteria to facilitate capturing management effectiveness.
* [REQ 35] Capture the following attributes from management/recovery plan workflow:
  * document type: Whether full, interim or national recovery plan,
  * any additional attributes
  * Date of approval by Director + DG + Minister + ConservationListing date
* [REQ 36] Allow the recovery team to record the annual report;
  the system is to remind the recovery team that the annual report is due;
  system is to alert officer if annual report is not submitted by due date.
  The annual report to at least cover the success criteria listed in the plan. (Impossible to test)
* [REQ 37] Allow for renewal of an existing plan at expiry date;
  approval workflow for renewal plan is same as workflow for new plan, including ministerial/CEO approval
  Test that at expiry date, plan approval status transitions to "EXPIRED", send notifications to owner,
  show up in todo lists
* [REQ 38] Alert officer that renewal for existing plan is coming up to start review process;
  review process results in either of:
  * Closure of plan
  * Renewal of plan
  * Writing of new plan
* [REQ 46] Allow for the storing of generated reports, so that user can retrieve the report
  that was generated at a date in the past. Note: This will swamp the /media folder.
* [REQ 47] Conservation Action / cons activity linked to documents.
  Allow Departmental recovery team members to record outcomes against any recovery action linked to the plan.
  Reporting against recovery actions is not mandatory.
* [REQ 48] Allow for the linking, as an action in the plan, between a management plan or
  (interim) recovery plan and a translocation plan recorded in the translocation module.
* [REQ 49] Allow for recording any communication related to any entity recorded in the system; recording a phone call,
  email exchange, etc. The details must include, the parties involved, type of communication (phone call, email, etc.),
  free text to record content, attachment of any relevant document.
  Test: attach text file as document type "Communication record" to a taxon or community.

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
    """Functional tests for the ConservationListing (ConservationListing) life cycle.

    This test suite tests:

    * Create a conservation listing
    * Approval steps through instances (committee, branch manager,
      director, director general, minister) - who is allowed to approve what when
      (permissions, conditions, consequences)
    * ConservationListing, date and time, publication, where is it shown (DBCA website?)
    * Review at set dates - reminders, todo lists, who is responsible
    * Retiring a CL: through creting a new ConservationListing, through ministerial decision,
    through notice (national) or API  (international)
    """

    def setUp(self):
        """Set up."""
        pass

    def test_only_admin_can_create_ConservationListing(self):
        """Conservation Listings can only be created by admins.

        Only data curators with admin access can create new conservation listings.
        """
        pass


class HerbariumConsListingSuggestions(TestCase):
    """Notification form Herbarium about new names requiring cons listing."""

    pass


class TaxonomicNameChanges(TestCase):
    """Taxonomic name changes (xrefs) require cons listing et al to be moved to new name.

    * new Taxa, new xrefs
    * For Taxa with cons listings: review and assign new cons listings to new names
    * Custodian reviews/assigns cons listings
    * Notify WAHerb and WACensus of new cons listings (only new ones)

    * A is WAPS P1
    * species A -> species B as SYN
    * species B should become WAPS P1

    """

    pass


class ConservationListingReportingTests(TestCase):
    """Functional tests for ConservationListing (ConservationListing) reporting.

    This test suite tests:

    * Query and export conservation listing history (several CL of one taxon or community)
    * Query and export conservation listing approval history (within one CL)
    * Query and export conservation lists (all taxa listed as conservation category X)
    * Export all taxa listed as Threatened or Priority, include District/Region
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


class DocumentReportingTests(TestCase):
    """Functional tests for Document reporting.

    This test suite tests:

    * List, filter, and export Documents matching filter criteria
    * Document review: find docs coming up for review

    """

    pass
