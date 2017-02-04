========
Overview
========

This chapter gives a quick overview of the WA Stranding Database WAStD.

**Disclaimer** WAStD is currently in the proof of concept (POC) phase, and not a
production system. This documentation will evolve along with the software
and may describe planned, but unimplemented features.

WAStD is a data clearinghouse for:

* Turtle strandings in WA, as reported to the Department of Parks & Wildlife, WA.
* Turtle track observations, taken at sunrise after nesting (nests and false crawls).
* Temperature logger asset management.

WAStD is built scalable enough to accommodate other, related, data:
* Turtle tagging observations, taken of nesting turtles.
* Cetacean, pinniped, sea snake strandings.

WAStD offers as main functionalities:

* A "backstage" area, through which trained and trusted data curators can enter
  data from paper data sheets, then proofread and QA the data.
* A landing page with an interactive map displaying the data (coming up: filters
  to restrict the data shown, export tools).
* A RESTful API that allows authenticated users to create, update, and download
  the data.

WAStD's purpose is:

* To fill an existing gap in departmental infrastructure (strandings, tracks).
* To develop requirements for an integrated turtle data management ecosystem
  through using real data and real processes.

WAStD will integrate in the Departmental information landscape as follows:

* Legacy data (starting with Turtle strandings) is manually entered from paper forms.
* Legacy data living in legacy systems can be batch-uploaded to WAStD,
  initially as a read-only copy.
* Data collected digitally can be streamed (or imported semi-automatically) into WAStD.
* WAStD can batch-upload its data to corporate data warehouses, once they exist (e.g. BioSys).
* Analytical applications anwering defined management questions (informing
  monitoring reports, ministerial inquries, conservation planning decisions) can be
  built right now consuming the WAStD API, and later refactored to consume data from
  departmental data warehouses, once these become the point of truth for the data.

WAStD's design philosophy follows
`The Basics of Unix Philosophy <http://www.catb.org/esr/writings/taoup/html/ch01s06.html#id2877537>`_

=========
Data flow
=========

.. figure:: https://www.lucidchart.com/publicSegments/view/f1a8e7cf-340a-43d0-8a32-887a004d1e21/image.jpeg
    .. :width: 200px
    :align: left
    .. :height: 100px
    :alt: WAStD data flow as implemented
    :figclass: align-center

    WAStD data flow as implemented

.. figure:: https://www.lucidchart.com/publicSegments/view/bfae841d-0548-44ed-b309-b9f65d3ab082/image.png
    .. :width: 200px
    :align: left
    .. :height: 100px
    :alt: Systems architecture
    :figclass: align-center

    Systems architecture

The remainder of this chapter applies IBM's
`simple pattern for requirements analysis <https://www.ibm.com/developerworks/architecture/library/ar-analpat/ar-analpat-pdf.pdf>`_
to structure the problem space into business processes (stranding, tagging, and
track/nest count) and IT processes (for each business process: data capture,
data QA and curation, data analysis). Legacy systems and their ties to the current
implementation (WAStD) are discussed as well.

Business Process Turtle Strandings
==================================

IT process Stranding incident report
------------------------------------
A ranger or other departmental field worker responds to a stranding incident.
The stranding (using a mobile data collection app) is reported to HQ,
and further actions are taken as per latest instructions (to be updated).

The current process involves paper-based stranding report forms, scanning, emailing,
manually entering and proofreading. It feeds into the workflow documented
at :ref:`itp-stranding-curation`.

A new digital reporting process is ready for beta-testing and documented
at :ref:`itp-stranding-report`.

An updated workflow for turtle strandings is being distributed to field offices
at the time of writing (Jan 2017), but requires further updates to include
other priority taxa (cetaceans, pinnipeds, dugong, sea snakes etc.).

IT process Stranding data curation
----------------------------------
Data curation requires at least four steps:

* A data entry operator digitises legacy data from emails, old paper-based
  stranding reports and other, unstructured information.
* A second data entry operator proof-reads the digitised records.
* A qualified curator with good business knowledge of turtle ecology reviews the
  records.
* A manager with data publication permission flags records as ready for public
  release.

Detailed instructions for each role are documented at :ref:`itp-stranding-curation`.

IT process Stranding data analysis
----------------------------------
As documented at :ref:`usecase-stranding-mininsterial-inquiry`, the current
implementation serves several analytical requirements:

* A ministerial inquiry seeks a summary of "how many, which species, where, when".
* A manager seeks to inform management decisions.
* A researcher seeks to infer knowledge about ecological processes, their change
  over space and time, and possible drivers.

Legacy systems
--------------
Nature Conservation kept a Filemaker Pro database of Cetacean strandings.
The database custodian has retired after extended leave.

The custodian of the legacy turtle tagging database WAMTRAM 2 understood that
strandings of tagged turtles are a vital part of their life history (and used
in mark-capture-recapture analysis) and aimed to include the strandings process
into the database; however, this process was not completely implemented and is
not operational.

Business Process Turtle Tagging
===============================

IT process Turtle tagging field data collection
-----------------------------------------------
Currently, data is collected on paper forms, and then fed into the legacy system
WAMTRAM 2 (see below).

Digital data capture, if done well, could help to reduce the workload of the
field workers, field supervisors, and data custodians, while improving data quality
by reducing the number of time-consuming and error-prone steps.
See :ref:`cost-benefit-analysis-digital-data-capture`.

Digital data capture of tagging-related data happens under time pressure
and in harsh conditions (night, low light, operator fatigue, beach, sand, heat,
humidity). The workflow is non-linear, as the tagged, biopsied, restrained,
but also very powerful turtle does not always follow the field protocol in sequence.
The technology currently used for digital data capture of strandings and tracks
is not flexible enough to provide a viable tagging data capture form.


IT process Turtle tagging data curation (field and office)
----------------------------------------------------------
Tagging data captured in the field is particularly error-prone due to the stressful
circumstances of the field work.

Currently, a first round of data curation occurs during data entry of paper data
forms into the WAMTRAM field database on the morning after a tagging night, when
memory of any possible irrregularity is still fresh.
Anecdotal use cases are reported at :ref:`lessons-learnt-paper-based-data-capture`.


IT process Turtle tagging data analysis
---------------------------------------
Tagged turtles are useful for mark-capture-recapture analysis. Stranded tagged
turtles are part of this scope.

:ref:`data-analysis-animal-life-cycle` illustrates M-C-R analysis.


Legacy system: WAMTRAM 2
------------------------

* `Documentation (access restricted to Turtle team) <https://confluence.dpaw.wa.gov.au/display/sd/MSP%20Turtle%20Tagging%20DB>`_
* Data backend is an MS SQL Server 2012 database on kens-mssql-001-prod
* Curator Bob Prince administrates data through an MS Access admin front-end
* For each field team, Bob uses the admin frontend to export the
  entire current database into a data collection database
* Field teams receive a data collection database backend (MS Access
  mdb) plus data collection frontend (MS Access mde) which allows data entry,
  does rudimentary data validation, and allows looking up existing data (e.g.
  tag history, turtle history)
* Field teams return the data collection backend, which Bob imports into WAMTRAM 2
* If WAMTRAM 2 reports import errors, Bob changes field data using his subject
  matter expertise and scans of original data sheets (if available) to resolve
  typos and incorrectly entered data
* Once import validation passes, WAMTRAM ingests the new data batch

Interim solution: ETL to WAStD
------------------------------
The task of extraction, transformation and loading (ETL) of tagging data is
automated and documented in an RMarkdown workbook
`Tagging ETL <https://github.com/parksandwildlife/ningaloo-turtle-etl/blob/master/tagging-etl.Rmd>`_.
The workbook is under version control in the repository
`Ningaloo Turtle ETL <https://github.com/parksandwildlife/ningaloo-turtle-etl/>`_.

Based on WAMTRAM 1 developer Simon Woodman's technical documentation, the
workbook aims:

* to document WAMTRAM 2 data model and business logic,
* to extract data into CSV snapshots, and upload them to Parks and Wildlife's
  internal data catalogue, and
* to transform and load data into WAStD using WAStD's API

Loading data into WAStD assumes:

* WAMTRAM 2 remains point of truth and curation interface for data until data
  are collected/entered directly into WAStD;
* Loading data into WAStD is repeatable without creating duplicates;
* WAStD will contain a full representation of WAMTRAM's data and will be able to
  deliver the same insight.

Long term solution: New data entry tool
---------------------------------------
To retire WAMTRAM 2, the following is required:

* WAMTRAM to WAStD ETL is complete and correct.
* A new electronic data entry tool, likely a progressive web app, is created
  to both collect data in the field, curate data on "the morning after", and
  to digitise data sheets.
* WAStD to implement all sanity checks and QA operations of WAMTRAM 2.

Insight from tagging data
-------------------------
It is important to create insight from the raw data early on in the process of
understanding, extracting and cleaning WAMTRAM 2 data.

This helps to update and complete the data model based on analytical requirements,
as well as delivering insight in incremental steps, rather than at the end of the
process.

Insight can be generated initially from WAMTRAM 2's CSV snapshots, and later on
source the data from the WAStD API.


Business Process Turtle Tracks
==============================
IT process Turtle track and nest count
--------------------------------------
See :ref:`data-capture-tracks` for digital data capture of tracks and nests,
which is curretly in production use by the core Turtle team, and in beta testing
at Cable Beach and the Karratha office.

IT process Turtle track and nest data curation
----------------------------------------------
The same processes as described in turtle strandings apply.

IT process Legacy data ETL
--------------------------
The Ningaloo ETL RMarkdown workbook
(`source <https://github.com/parksandwildlife/ningaloo-turtle-etl/blob/master/ningaloo-etl.Rmd>`_)
extracts data from the NTP database snapshot on the internal data catalogue into
CSV and GeoJSON files, and uploads them to the NTP
`dataset <internal-data.dpaw.wa.gov.au/dataset/ningaloo-turtle-program-data>`_.

The workbook can be extended to also upload the data into WAStD's API.


IT process Turtle track and nest count analysis
-----------------------------------------------
Fundamentally, the same process as in turtle stranding analysis applies.

As a first working example, production data from 2016, captured digitally with the new
mobile data capture app, are shown `here <http://rpubs.com/florian_mayer/track-counts>`_.

As a second example, the RMarkdown workbook
`Ningaloo spatial modelling <internal-data.dpaw.wa.gov.au/dataset/ningaloo-turtle-program-data/resource/422c91ca-7673-432f-911a-449d3dc2e35a>`_,
runs a few exemplary analyses on the NTP data snapshots as extracted by the
Ningaloo ETL workbook. It can be expanded to include any desired analysis or
summary of the NTP data.

More analyses are required and scheduled for implementation, e.g.:

* Spatio-temporal patterns and variation of tracks on Thevenard Is
* Nesting success at Thevenard Is


Legacy system: Ningaloo Track count database
--------------------------------------------
Links:

* Ningaloo Turtle Program
  `data snapshot <internal-data.dpaw.wa.gov.au/dataset/ningaloo-turtle-program-data>`_
  on the internal data catalogue
* Ningaloo Turtle Program `homepage <http://www.ningalooturtles.org.au/>`_
* `Code repository <https://github.com/parksandwildlife/ningaloo-turtle-etl/>`_

**Note** Data sheets and field guide are being updated at the moment.

The Ningaloo Turtle Program (NTP) database consists of an MS Access database
and frontend. Volunteers conduct track count surveys, enter data, and curate
the database.
