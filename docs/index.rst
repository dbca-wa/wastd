=====================================================================
WAStD - WA Sea Turtle and Strandings Database
=====================================================================

.. image:: https://img.shields.io/badge/License-MIT-green.svg
     :target: https://opensource.org/licenses/MIT
     :alt: MIT License

========
Overview
========

WAStD is a data warehouse for:

* Turtle strandings in WA, as reported to the
  Department of Biodiversity, Conservation and Attractions, WA.
* Turtle nesting census, which counts nests and tracks on mornings after nesting nights
  (can involve nests, tracks, predation, nest tags, temperature loggers, egg excavations,
  hatchling measurements, hatchling emergence track measurements, light pollution observations).
* Temperature logger asset management.
* Turtle tagging observations.

WAStD offers as main functionalities:

* A user-friendly interface to trawl through the data, do QA and data exports.
* An access-restricted data curation portal, through which trained and trusted data curators
  can enter data from paper data sheets, then proofread and QA the data.
* Restricted access to the "backstage" area for trusted data consumers, where
  they can search, filter and export the raw data, but not change or delete them.
* A RESTful API that allows authenticated users to create, update, and download
  the data.

WAStD integrates in the Departmental information landscape as follows:

* Legacy data (starting with Turtle strandings) is manually entered from paper forms.
* Legacy data living in legacy systems can be batch-uploaded to WAStD, initially as a read-only copy.
* Data collected digitally can be imported automatically into WAStD.
* WAStD can batch-upload its data to other corporate data warehouses.
* Analytical applications anwering defined management questions (informing
  monitoring reports, ministerial inquries, conservation planning decisions) can be
  built right now consuming the WAStD API, and later refactored to consume data from
  departmental data warehouses, once these become the point of truth for the data.
* Departmental data consumers can use the R package `wastdr <https://dbca-wa.github.io/wastdr/>`_ to access
  data directly from the WAStD API. ``wastdr`` provides working examples and extensive documentation.

If any of the legacy systems were to experience an acute business risk -- e.g.
data being siloed in outdated software,
insufficient database curation functionality (missing sanity checks)
corrupting core departmental data,
data custodians retiring or not being salaried,
outdated datasheets collecting incomplete, inconsistent, incorrect data --,
then a solution much like WAStD or BioSys would be required to mitigate that risk,
and sufficient care had to be taken to hand over the not always fully documented,
often living business knowledge from current custodians to permanent departmental staff.

The roll-out of the improvements in handling turtle strandings will cross over
with existing workflows of the above mentioned, out of scope business processes.

WAStD's design philosophy follows
`The Basics of Unix Philosophy <http://www.catb.org/esr/writings/taoup/html/ch01s06.html#id2877537>`_

The journey so far:

* April 2016: Requirements Analysis
* July 2016: Implementation
* August - Sept 2016: Agile iterations, weekly stakeholder workshops to refine
  requirements and update business processes understanding and requirements
* Oct 2016: Production deployment, start of turtle stranding data entry,
  "dog fooding" the data entry manual, usability improvements, working on datasheets.
* Nov 2016: Development of digital data capture for turtle tracks. Form revised 10 times.
* Nov/Dec 2016: 2300+ tracks recorded digitally, replacing paper forms.
* Dec 2016: Track app deployed to two more field teams (Karratha, Broome).
* Jan 2017: Automated pipeline from digital capture to WAStD.
* Jan 2017: Digital form for tracks revised 15 more times to include nest tags,
  egg, hatchling and logger measurements.
* Feb 2017: Revised tracks form used in field.
* Season 2017/2018: Six regions join digital data collection of turtle track census.
* 2018: Threatened species and communities.
* Season 2018/19: Bar two programs, all WA regions join digital data collection of
  turtle track census. One program is relatively small and remote, the other lacks basic literacy among available data collectors, favouring pictogram-based and established solutions like CyberTracker.
* Season 2019-20: Migration from ODK Aggregate to ODK Central, ETL via API and R packages wastdr and etlTurtleNesting.
* Season 2020-21: Inclusion of turtle tagging in electronic data capture.
* 2022: Third party access for non-DBCA users enabled.

What is where
=============
* `WAStD <https://wastd.dbca.wa.gov.au/>`_ - DBCA staff login
* `WAStD data curation portal <https://wastd.dbca.wa.gov.au/>`_ > Curators > Data Curation Portal - privileged DBCA staff
* `WAStD docs <https://wastd.dbca.wa.gov.au/>`_ > Manual - public
* `Turtle Nesting metadata on data catalogue <https://data.dbca.wa.gov.au/dataset/turtle-tracks>`_ - pending update. DBCA intranet.
* `Turtle Tagging metadata on data catalogue <https://data.dbca.wa.gov.au/dataset/wa-marine-turtle-tagging-database-wamtram-2>`_ - pending update. DBCA intranet.

.. toctree::
   :maxdepth: 3

   data_entry
   data_qa
   data_consumers
   business_analysts
   developers
   third_party_access

=======================
Technical documentation
=======================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
