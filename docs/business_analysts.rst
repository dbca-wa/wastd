=================
Business Analysts
=================
This chapter draws the big picture of the turtle data ecosystem
by presenting business, functional and stakeholders' requirements as readable use cases.

We apply IBM's
`simple pattern for requirements analysis <https://www.ibm.com/developerworks/architecture/library/ar-analpat/ar-analpat-pdf.pdf>`_
to structure the problem space into business processes (stranding, tagging, and
track/nest count) and IT processes (for each business process: data capture,
data QA and curation, data analysis). Legacy systems and their ties to the current
implementation (WAStD) are discussed as well.

Business Process Turtle Strandings
==================================
This business process was the first information management challenge to solve,
and has led to the design and development of WAStD in its current form.

To illustrate the design process, the background is discussed in greater detail here.

Problem
-------
Reports of turtle strandings exist as hard copy (paper, photos, datasheets),
electronic files (scanned datasheets, emails, photos), in databases
(Turtle Tagging DB WAMTRAM2), and in regional offices.

For ministerial inquiries on turtle strandings, there is no timely, defensible,
reproducible, and accessible insight available.
Monitoring and research questions suffer the same problem.

REQ Insight on turtle strandings must be available in a timely, defensible,
reproducible and accessible manner.

Task
----
* Improve the information pipeline from databased, stranded animal to
ministerial / managerial inquiry, so that timely, defensible, reproducible,
and accessible insight is available.
* Digitise and curate the backlog of old stranding reports, while retaining the full data lineage.

Constraints
-----------
The solution architecture must consider the following contraints:

* Biosys aims to deliver similar functionality, but not within the required time.
* REQ The solution shall be either disposable (to be re-implemented in BioSys),
  re-usable (to be integrated in BioSys), or scalable (to become a part of BioSys).
* REQ The solution shall be SOE, follow OIM's standards and integrate into their
  infrastructure ecosystem.
* Double handling of data entry shall be avoided - do it once, and do it
  properly (complete, correct, consistent).
* REQ There must be a standardised, accessible way to import and export all data
  into and out of the solution.
* REQ The solution shall be compatible on a raw data level with Queensland's
  StrandNet, Parks & Wildlife's Turtle Tagging database WAMTRAM 2,
  and the Ningaloo Turtle Program's track count database.

Current implementation
----------------------

Turtle Strandings
^^^^^^^^^^^^^^^^^
* Stranding paper forms are being updated (SFo and FM, Nov 2016 - Mar 2017).
* An updated incident response workflow for turtles has been sent to regional
  offices by the affiliated Murdoch Vet (EY Dec 2016).
* A digital data capture form caters for turtle strandings (can be extended to others)
  and is in beta testing (not officially released yet).
* WAStD allows data entry from legacy paper forms, as well as data export and query.
* Live workbooks can query, analyse and visualise data from WAStD via its API.

Cetacean strandings
^^^^^^^^^^^^^^^^^^^
Nature Conservation kept a Filemaker Pro database of Cetacean strandings.
The database custodian has retired after extended leave.

It shall be known that the custodian of the legacy turtle tagging database
WAMTRAM 2 understood that strandings of tagged turtles are a vital part of their
life history (and used in mark-capture-recapture analysis)
and aimed to include the strandings process into the database;
however, this process was not completely implemented and is not operational.

IT process Stranding incident report
------------------------------------
A ranger or other departmental field worker responds to a stranding incident.
The stranding (using a mobile data collection app) is reported to HQ,
and further actions are taken as per latest instructions (to be updated).

The current paper-based process involves paper-based stranding report forms, scanning, emailing,
manually entering and proofreading. It feeds into the workflow documented
at :ref:`itp-stranding-curation`.

A new digital reporting process is in beta-testing, ready to incorporate other
taxonomic groups of strandings and documented at :ref:`itp-stranding-report`.

An updated workflow for turtle strandings is being distributed to field offices
at the time of writing (Jan 2017), but requires further updates to include
other priority taxa (cetaceans, pinnipeds, dugong, sea snakes etc.).

REQ Data should be born digitally to minimize the costly and error-prone crossing
of the analog-digital barrier.

REQ The incident responder shall be provided with a comprehensive, easy to follow,
work flow (as flow chart printout, handbook, or in a digital format).

REQ The incident responder shall be able to capture the data offline, with the
necessary reference at hand (species ID guides, relevant data from the central
database, "next steps" flow chart), using cheap and readily available
technology (e.g. tablets or smart phones), and be able to auto-upload the data
once online (office WiFi or mobile reception) without manual effort.

REQ The digital data capture tool shall record location and time automatically.

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

REQ Data consumers shall be able to query, filter and export the raw data.

REQ Data access shall be restricted role-based, so that sensitive data is accessible
only to trusted and authorised data consumers.

REQ The system shall default data restrictions to be suitable for the general audience.

.. _usecase-stranding-mininsterial-inquiry:
Use case: Ministerial inquiry, annual report, strategic advice
--------------------------------------------------------------
This section discusses requirements of each stakeholder role involved in

* the response to a ministerial inquiry,
* annual reporting for a steering committee,
* strategic advice to a policy officer,

and demonstrates the current implementation in WAStD.

Minister, steering committee, policy officer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The minister sends an inquiry to the Department.

The Turtle Monitoring Program's steering committee requires semi-annual reports
on turtle population metrics like mortality (strandings) or nesting (tagging and
track counts).

A policy officer needs to relate infrastructure developments (e.g. new boat ramps)
or management actions (e.g. boating exclusion zones) with turtle population metrics
(e.g. number of boat strikes).

There haven't been any ministerial inquiries about turtle strandings yet,
but we assume they could ask e.g.:

* How many `boat strikes to turtles <https://strandings.dpaw.wa.gov.au/admin/observations/animalencounter/?cause_of_death__exact=boat-strike&taxon__exact=Cheloniidae>`_ have been recorded?
* How many turtle strandings happened `in 2016 <https://strandings.dpaw.wa.gov.au/admin/observations/animalencounter/?encounter_type__exact=stranding&taxon__exact=Cheloniidae&when__year=2016>`_?
* How many turtle strandings happened within the `80 Mile Beach MPA <https://strandings.dpaw.wa.gov.au/admin/observations/animalencounter/?encounter_type__exact=stranding&taxon__exact=Cheloniidae&where=3>`_?

These examples show only a few out of many possible combinations of search filters.
All results can be exported to spreadsheets for further analysis.
The same results can also be generated through the API for consumption by software.
See :ref:`data-consumers-api` for working examples.

Manager
^^^^^^^
The manager requires timely and defensible insight to answer the ministerial
inquiry, to fulfil reporting obligations to the steering committee, or to provide
data-driven, strategic advice.
Insight could be required as

* `data <https://strandings.dpaw.wa.gov.au/admin/observations/animalencounter/>`_
  (spreadsheet - "List all incidents of <species> within <region> and <date range>"),
* `summarised numbers <https://strandings.dpaw.wa.gov.au/admin/observations/animalencounter/>`_
  (spreadsheet totals - "How many <species> within <region> suffered incidents?"),
* `analytical output <http://rpubs.com/florian_mayer/wastd-mark>`_
  (probability of correlations - "Did the new boat ramp
  significantly increase the number of boat strikes to <species>?"),
* `geographic distribution <https://strandings.dpaw.wa.gov.au/>`_
  (maps - "Where did the strandings happen?").

* Insight should be available as **timely** as possible, minimizing human bottlenecks.
* Insight should be **accessible**, in that managers should be able to
  retrieve answers to common questions themselves.
* Insight should be **defensible**, in that the processing steps of both data
  `QA <https://strandings.dpaw.wa.gov.au/admin/observations/animalencounter/10/change/>`_
  (audit trail of QA operations)
  and `analysis <http://rpubs.com/florian_mayer/wastd-mark>`_ are well documented,
  providing a fully transparent data lineage from datasheet to generated insight.
* Insight should be **reproducible**, in that other people with limited
  technical or statistical expertise can
  `reproduce the analysis <http://rpubs.com/florian_mayer/wastd-mark>`_
  from the archived inputs.

Analyst
^^^^^^^
The analyst's role is to bridge the gap between raw data and non-trivial questions
through advanced statistical analysis and visualisation.

* To do so, the analyst needs `universal access <https://strandings.dpaw.wa.gov.au/api/1/>`_
  to machine-readable, trustworthy data.
* The data needs to be complete, consistent and correct.
  The analyst needs to hit the ground running with
  `working examples <https://strandings.dpaw.wa.gov.au/users/FlorianM/>`_
  of loading the data from the machine-readable access point into the most common
  analytical frameworks. (See your own WAStD profile for code examples including
  your own API token).
* There should be sufficient documentation (:ref:`data-consumers`)
  to allow statistically trained analysts to efficiently consume data without
  technical knowledge of the system they are stored in.
* Access needs to be following standard protocols and formats,
  be entirely independent of both the systems it is stored in,
  as well as independent of the software packages it is analysed with.

Data curator 3: Subject matter expert
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Subject matter experts acting as data curators need to validate the records,
e.g. confirm species identification. This increases **correctness** of the data.

* Data curators need convenient, unrestricted access to the data.
* Data needs to indicate its curation status.
* Data needs to retain its lineage by retaining its editing and status history.
* Each human decision by the subject matter expert should be translated into an
  automatic test or filter that flags similar records for review. This feedback
  process aims to distil the subject matter expertise into formal rules.

Data curator 2: Proofreader
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Digitising data sheets is an error-prone operation. Sorting vague information into
the available categories requires some informed decisions, based on guidelines.
Proofreading will help fighting typos and misunderstandings between datasheet
and database, therefore increasing **consistency**.

* The proofreader needs original datasheets, communication records and supplemental
  images accessible close to the data entry/QA forms, ideally displaying in their
  web browser without needing to be downloaded and opened in proprietary software.

Data curator 1: Data entry operator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The data entry operator digitises information from datasheets, emails and photographs,
reconstructs missing information, and transforms files into standard compliant formats.
By doing so, the data entry operator increases **accessibility** and **completeness** of data.

* The electronic data entry form should follow the data sheets to facilitate data entry.
* There should be clear, unambiguous instructions on
  `data entry <http://wastd.readthedocs.io/data_curators.html>`_.
* The instructions must be able to evolve with new edge cases requiring supervisor input.
* Electronic data entry forms should provide input validation for formats, not content.
* The data portal should accept all formally correct data (:ref:`data-model`),
  but allow to identify and fix impossible or questionable records.
* The system should flag impossible or questionable records.

Data collector: Ranger, regional staff
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The departmental data collector (e.g. a ranger) responds to a stranding report
from the general public, or discovers a stranded animal themselves.

* The data collector needs clear and up to date procedures, and easily useable
  datasheets.
* Paper is cheap, bad information is costly. Taking the correct pictures in correct
  angles, as well as taking and processing samples, or preserving the carcass for a
  subsequent necropsy correctly is time-critical and cannot be repeated later.
  Instructions to take the right measurements, samples and photographs must be
  available to the data collector.
* Datasheets need to capture complete, consistent and correct data, while avoiding
  capturing unneccessary detail.
* Datasheets should provide enough guidance to the data collector on providing the
  desired data formats and precision.

The data collector could reduce the workload on core staff by entering the datasheet
themselves, if the data portal had data entry forms with restricted access.
These forms are different to the curation forms - more streamlined for data entry.

Primary reporter: General public
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Members of the general public reporting a stranding need to know how to react -
whom to call, which data to collect (e.g. geo-referenced phone pictures).

* Primary reporters would be pleased to hear how their actions contributed to an
  increased understanding, and ultimately the conservation of the stranded species.
  This could happen in the form of a "thank you" email with an excerpt of the
  final stranding record.
  Example: TOs returning tags after harvesting a tagged turtle usually get sent
  a reward like branded t-shirts or baseball caps by Marine Science to show their
  appreciation.

Gap analysis
------------

* The digital data capture form does not yet include taxa other than turtles.
* Front-line staff are not yet trained in its use.
* Therefore, paper forms are not phased out yet.
* The digital data capture app in its current implementation still requires a few
  manual steps by the application maintainer to import data into WAStD. This process
  is not yet fully automated and does not yet happen in real-time.
* The WAStD API is, although operational, not yet fully optimised.
* Not all possible data products are implemented yet (e.g. as self-service
  dashboards).
* Members of the public who report strandings have not yet web access to "their"
  strandings and related data (e.g. the life history of a stranded, tagged turtle).

Business Process Turtle Tagging
===============================

IT process Turtle tag asset management
--------------------------------------
Tags have a life cycle, characterised by interactions with humans and animals:

* TODO add tag status list
* LLC diagram tag

Use cases:

* Order tag (typically in batches) with running ID e.g. WB1500 - WB3500
* Record tag batches as ordered, produced, delivered (how much detail is required?),
  allocated to field team (important)
* Query: how many tags have we ordered?
* Query: what's the next available tag number?
* Query: which tags are available to hand out to field teams? when do we have to re-order?
* Field teams report tags as "applied new", "re-clinched" or "re-sighted"
  when tagging animals through digital or paper field data forms
* Tag returns from TOs after harvest
* Tags can be found on stranded animals, returned to HQ
* Tags are never re-applied to different animals but destroyed and recorded as such

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
therefore stressed, but also very powerful turtle does not always follow the
field protocol in sequence.
The technology currently used for digital data capture of strandings and tracks
is not flexible enough to provide a viable tagging data capture form.

REQ The solution for a digital turtle tagging field data capture app must be
optimised for harsh environmental conditions and low light, as well as
the non-linear and  opportunistic nature of tagging data capture.

REQ The solution shall carry the complete backlog of tagging records to provide
the field workers with real-time insight about last sighting and in general all
data relating to the encountered turtle (if already tagged), utilised tags, samples,
data loggers and all other uniquely identifiable involved entities.

REQ The solution shall allow daily syncing between multiple field data capture devices
while still in the field.

REQ The solution shall be responsive to different device display widths.

REQ The solution shall be able to toggle interface features and functionality between
field data capture, field data curation, data upload, central data curation and other roles.


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
`Tagging ETL <https://github.com/parksandwildlife/turtle-scripts/blob/master/wamtram/wamtram_etl.Rmd>`_.
The workbook is under version control in the repository
`Turtle Scripts <https://github.com/parksandwildlife/turtle-scripts/>`_.

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


Use case: Turtle Tagging digital data capture
---------------------------------------------
**TODO** expand and link chart "DDC"

* preparation before field trip while online
* field data capture (during tagging)
* field data curation (morning after)
* syncing field data capture devices
* submitting data after field trip
* accessing merged data

Use case: Inquiry about tagged turtle
-------------------------------------
**TODO** expand

See chapter :ref:`data-consumers` on how to get to a `Tag history
<https://strandings.dpaw.wa.gov.au/api/1/tag-observations/?tag_type=flipper-tag&name=WA67541>`_
 or an `animal history
<https://strandings.dpaw.wa.gov.au/api/1/animal-encounters/?name=WA67541>`_.

Gap analysis
------------
Tagging is currently handled in WAMTRAM 2.

To replace WAMTRAM 2, a digital data capture app as well as a central data warehouse
such as BioSys or WAStD are required.

Business Process Turtle Tracks
==============================
IT process Turtle track and nest count
--------------------------------------
See :ref:`data-capture-tracks` for digital data capture of tracks and nests,
which is curretly in production use by the core Turtle team, and in beta testing
at Cable Beach and the Karratha office.

IT process Turtle track and nest data curation
----------------------------------------------
The same processes as described in turtle strandings apply to tracks and nest data.

IT process Legacy data ETL
--------------------------
The Ningaloo ETL RMarkdown workbook
(`source <https://github.com/parksandwildlife/turtle-scripts/blob/master/ningaloo/ningaloo_etl.Rmd>`_)
extracts data from the NTP database snapshot on the internal data catalogue into
CSV and GeoJSON files, and uploads them to the NTP
`dataset <internal-data.dpaw.wa.gov.au/dataset/ningaloo-turtle-program-data>`_.

The workbook can be extended to also upload the data into WAStD's API.


IT process Turtle track and nest count analysis
-----------------------------------------------
Fundamentally, the same process as in turtle stranding analysis applies.

As a first working example, production data from 2016, captured digitally with the new
mobile data capture app, are shown `here <http://rpubs.com/florian_mayer/tracks>`_.

As a second example, the RMarkdown workbook
`Ningaloo spatial modelling <internal-data.dpaw.wa.gov.au/dataset/ningaloo-turtle-program-data/resource/422c91ca-7673-432f-911a-449d3dc2e35a>`_,
runs a few exemplary analyses on the NTP data snapshots as extracted by the
Ningaloo ETL workbook. It can be expanded to include any desired analysis or
summary of the NTP data.

More analyses are required and scheduled for implementation, e.g.:

* Spatio-temporal distribution, patterns and variation of patterns of tracks
* Nesting success at Thevenard Is as ratio of successful over total nesting
  crawls (tracks with, without, unsure, not assessed if nest) on a beach
* Hatching success as ratio of hatched over total eggs in a nest
* Control charts of track / nest abundance over time to detect significant changes
* Significance of nesting beaches
* Control charts of nesting seasons to detect significant shifts in nesting timing
* Disturbance and predation: quantity, spatial and temporal distribution,
  patterns and variation of patterns
* Impact of experimental design and survey effort on measured abundance
* Modelling to get point estimates of nesting effort (what else?) for a given
  time and place

Legacy system: Ningaloo Track count database
--------------------------------------------
Links:

* Ningaloo Turtle Program
  `data snapshot <internal-data.dpaw.wa.gov.au/dataset/ningaloo-turtle-program-data>`_
  on the internal data catalogue
* Ningaloo Turtle Program `homepage <http://www.ningalooturtles.org.au/>`_
* `Code repository <https://github.com/parksandwildlife/turtle-scripts/>`_

**Note** Data sheets and field guide are being updated at the moment.

The Ningaloo Turtle Program (NTP) database consists of an MS Access database
and frontend. Volunteers conduct track count surveys, enter data, and curate
the database.

Use case: Track data collection
-------------------------------
**TODO** expand

Use case: Track data analysis
-----------------------------
**TODO** expand


Non-functional requirements
===========================
This section documents lessons learnt during the requirements analysis, design
 and development of WAStD and anecdotal wisdom of colleagues and data custodians.


Senior data custodians are gold mines of business knowledge
-----------------------------------------------------------
Extracting their experience and intuition, and solidifing their knowledge into
written documentation takes months to years. Retirement, budget cuts and personal
circumstances can cut this available time short.

NFR All custodians and colleagues with deep knowledge of related legacy systems
shall be consulted, their suggestions shall be incorporated into the systems
philosophy and design, and they should sign off on the requirements analysis.

Volunteers multiply value six-fold
----------------------------------
For each dollar the Department spends in the field, volunteers contribute about
six dollars in value. Sending them feedback and showing appreciation helps to
uphold motivation levels and retain this free work force.

NFR The system shall allow the display, export and emailing of the contributions
of each person to the value chain of data.

A picture is worth a thousand badly drawn schematics
----------------------------------------------------
Pictures are cheap to take but expensive not to take. Curators can tell nearly
all details of a stranded animal from good pictures. Often the initial guess
of the first respondent is overruled by expert advice based on photographs later.
Datasheets can be wrong, photos are more objective.
Datasheets should provide a list of desired photographic perspectives and angles,
and a list of details to capture close up.

REQ Data collection shall prompt the user to take photos where feasible to augment
their judgement in the field.

REQ The system shall allow attaching any file (datasheet scans, photographs,
email threads) to any record.

REQ The system shall allow proof-readers and curators to easily compare attached
media with entered data for a given record.

Data entry is worth every drop of sweat spent on forms, procedure and documentation
-----------------------------------------------------------------------------------
Data entry is a messy process, adding much value to data. Many decisions have to
be made to transform a stranding report into a full stranding record.
Data is only trustworthy if the full data lineage is retained.
Data curation goes through several stages, each adding value (entry, proofreading,
subject matter expertise).

REQ The system shall keep an audit trail of well-defined QA steps.

Data curation takes a long time - ca 30 min per stranding record.
Most time is spent transforming original files into standard formats,
e.g. extracting communication records and images from emails, merging
communication records into plain text files, editing out irrelevant information,
converting and resizing images.
This is an important step towards accessibility, as this information must be
accessible through web browsers which are limited to open file formats.
Therefore, resources spent in making information accessible in future-proof formats
is repaid multiple times through its repeated use.

We anticipate the following data entry work load for our .5 FTE Technical Officer:

* 3 months of eletronic stranding reports
* 6 months of paper stranding reports
* unknown quantity, probably months, of reports in regional offices

Data entry can be assisted through additional work force, or by creating data entry
forms for end users (currrently not implemented).

Proofreading and curation will take other operators a shorter, but still
considerable time. This extra effort has to be provided, and is a data quality
issue, independent of implementation (WAStD or BioSys).
Proofreading and curation requires trained core staff and cannot be outsourced.

REQ The business owner shall provide sufficient staff time and resources for
documentation, training, data entry, proofreading and curation.
