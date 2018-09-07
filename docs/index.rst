=====================================================================
WAStD - WA Sea Turtle Data / TSC - Threatened Species and Communities
=====================================================================

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django
.. image:: https://circleci.com/gh/dbca-wa/wastd.svg?style=svg
     :target: https://circleci.com/gh/dbca-wa/wastd
     :alt: Test status
.. image:: https://coveralls.io/repos/github/dbca-wa/wastd/badge.svg?branch=master
     :target: https://coveralls.io/github/dbca-wa/wastd?branch=master
     :alt: Test coverage
.. image:: https://readthedocs.org/projects/wastd/badge/?version=latest
     :target: http://wastd.readthedocs.io/
     :alt: Documentation Status
.. image:: https://badge.waffle.io/dbca-wa/wastd.svg?label=ready&title=Ready
     :target: https://waffle.io/dbca-wa/wastd
     :alt: Open Issues

.. "WA STD - now you've got it, too"

.. "Strandings are red, tagged ones are blue, nests are green and tracks are there, too"

.. toctree::
   :maxdepth: 2

   data_collection/data_collection_overview
   data_collection/data_collection_admin
   data_collection/data_collection_training
   data_curators
   data_consumers
   business_analysts
   maintainers
   developers

Overview
========

WAStD is a data clearinghouse for:

* Turtle strandings in WA, as reported to the Department of Biodiversity, Conservation and Attractions, WA.
* Dugong and sea snake strandings in WA.
* Turtle track observations, taken at sunrise after nesting (can involve nests,
  predation, nest tags, temperature loggers, egg excavation and hatchling measurements).
* Temperature logger asset management.
* Threatened Species and Communities of WA: occurrence, conservation status, management plans.

WAStD is built scalable enough to accommodate other, related, data:

* Turtle tagging observations, taken of nesting turtles.
* Cetacean (whales and dolphins) and pinniped (seals and sea lions) strandings.

WAStD offers as main functionalities:

* A "backstage" area, through which trained and trusted data curators can enter
  data from paper data sheets, and other curators can proofread and QA the data.
* A landing page with an interactive map displaying the data (coming up: filters
  to restrict the data shown, export tools).
* Restricted access to the "backstage" area for trusted data consumers, where
  they can search, filter and export the raw data, but not change or delete them.
* A RESTful API that allows authenticated users to create, update, and download
  the data.

WAStD's purpose is:

* To fill an existing gap in departmental infrastructure (strandings, tracks).
* To develop requirements for an integrated turtle data management ecosystem
  through using real data and real processes.

WAStD will integrate in the Departmental information landscape as follows:

* Legacy data (starting with Turtle strandings) is manually entered from paper forms.
* Legacy data living in legacy systems can be batch-uploaded to WAStD, initially as a read-only copy.
* Data collected digitally can be streamed (or imported semi-automatically) into WAStD.
* WAStD can batch-upload its data to corporate data warehouses, once they exist (e.g. BioSys).
* Analytical applications anwering defined management questions (informing
  monitoring reports, ministerial inquries, conservation planning decisions) can be
  built right now consuming the WAStD API, and later refactored to consume data from
  departmental data warehouses, once these become the point of truth for the data.

Departmental business related to turtle strandings:

Documented at https://confluence.dpaw.wa.gov.au/display/MSIM/Legacy+systems

If any of the legacy systems were to experience an acute business risk -- e.g.
data being siloed in outdated software,
insufficient database curation functionality (missing sanity checks)
corrupting core departmental data,
data custodians retiring or not being salaried,
outdated datasheets collecting incomplete, inconsistent, incorrect data --,
then a solution much like WAStD or BioSys would be required to mitigate that risk,
and sufficient care had to be taken to hand over the not always documented,
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

WAStD is part of the BioSys ecosystem of data warehousing, data curation, data exchange standards and
analytical knowledge pipelines.

WAStD data flow as implemented

.. image:: https://www.lucidchart.com/publicSegments/view/f1a8e7cf-340a-43d0-8a32-887a004d1e21/image.jpeg
    :target: https://www.lucidchart.com/publicSegments/view/f1a8e7cf-340a-43d0-8a32-887a004d1e21/image.jpeg
    :alt: WAStD data flow as implemented

Systems architecture

.. image:: https://www.lucidchart.com/publicSegments/view/bfae841d-0548-44ed-b309-b9f65d3ab082/image.png
    :target: https://www.lucidchart.com/publicSegments/view/bfae841d-0548-44ed-b309-b9f65d3ab082/image.png
    :alt: Systems architecture


Technical documentation
=======================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
