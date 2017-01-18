========
Overview
========

This chapter gives a quick overview of the WA Stranding Database WAStD.

**Disclaimer** WAStD is currently in the proof of concept (POC) phase, and not a
production system. This documentation will evolve along with the software
and may describe planned, but unimplemented features.

WAStD is a data clearinghouse for:

* Turtle strandings in WA, as reported to the Department of Parks & Wildlife, WA.

WAStD is built scalable enough to accommodate other, related, data:

* Turtle tagging observations, taken of nesting turtles.
* Turtle track observations, taken at sunrise after nesting (nests and false crawls).
* Cetacean and pinniped strandings.

WAStD offers as main functionalities:

* A "backstage" area, through which trained and trusted data curators can enter
  data from paper data sheets, then proofread and QA the data.
* A landing page with an interactive map displaying the data (coming up: filters
  to restrict the data shown, export tools).
* A RESTful API that allows authenticated users to create, update, and download
  the data.

WAStD's purpose is:

* To fill an existing gap in departmental infrastructure (strandings, tracks)
* To develop requirements for an integrated turtle data management ecosystem
using real data and real processes to get the best interaction with all stakeholders.

WAStD will integrate in the Departmental information landscape as follows:

* Legacy data (starting with Turtle strandings) is manually entered from paper forms.
* Legacy data that lives in ageing systems can (if desired) be batch-uploaded to WAStD.
* Data collected digitally can be streamed into WAStD.
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

.. image:: https://www.lucidchart.com/publicSegments/view/f1a8e7cf-340a-43d0-8a32-887a004d1e21/image.jpeg
     :alt: WAStD data flow

Turtle Strandings
=================

See the chapter "Specification" for a detailed use case and its current implementation.

Turtle Tagging
==============

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

* WAMTRAM to WAStD ETL complete and correct
* A new electronic data entry tool (cybertracker or similar)
* A new desktop data entry tool to digitise data sheets (= WAStD offline)
* WAStD to implement all sanity checks and QA operations of WAMTRAM 2

Insight from tagging data
-------------------------
It is important to create insight from the raw data early on in the process of
understanding, extracting and cleaning WAMTRAM 2 data.

This helps to update and complete the data model based on analytical requirements,
as well as delivering insight in incremental steps, rather than at the end of the
process.

Insight can be generated initially from WAMTRAM 2's CSV snapshots, and later on
source the data from the WAStD API.


Turtle Tracks
=============

Legacy system: Ningaloo Track count database
--------------------------------------------
Links:

* Ningaloo Turtle Program
  `data <internal-data.dpaw.wa.gov.au/dataset/ningaloo-turtle-program-data>`_
  on the internal data catalogue
* Ningaloo Turtle Program `homepage <http://www.ningalooturtles.org.au/>`_
* `Code repository <https://github.com/parksandwildlife/ningaloo-turtle-etl/>`_

**Note** Data sheets and field guide are being updated at the moment.

The Ningaloo Turtle Program (NTP) database consists of an MS Access database
and frontend. Volunteers conduct track count surveys, enter data, and curate
the database.

Interim solution: ETL to WAStD
------------------------------
The Ningaloo ETL RMarkdown workbook
(`source <https://github.com/parksandwildlife/ningaloo-turtle-etl/blob/master/ningaloo-etl.Rmd>`_)
extracts data from the NTP database snapshot on the internal data catalogue into
CSV and GeoJSON files, and uploads them to the NTP
`dataset <internal-data.dpaw.wa.gov.au/dataset/ningaloo-turtle-program-data>`_.

The workbook can be extended to also upload the data into WAStD's API.

Long term solution: Digital data collection into WAStD
------------------------------------------------------
As on now, a trained and trusted data entry operator can digitise NTP field
datasheets using the WAStD "Backstage" area.

At the time of writing (Nov-Dec 2016), digital data collection tools are evaluated
and used in production by the core team, replacing the paper forms.

See the chapter "Data collectors" on the current implementation.

Insight
-------
The RMarkdown workbook
`Ningaloo spatial modelling <internal-data.dpaw.wa.gov.au/dataset/ningaloo-turtle-program-data/resource/422c91ca-7673-432f-911a-449d3dc2e35a>`_,
runs a few exemplary analyses on the NTP data snapshots as extracted by the
Ningaloo ETL workbook. It can be expanded to include any desired analysis or
summary of the NTP data.
