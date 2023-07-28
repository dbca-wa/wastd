=================
Business Analysts
=================

This chapter draws the big picture of the turtle data ecosystem
by presenting business, functional and stakeholders' requirements as readable
use cases and describing existing implementations.

We apply IBM's `simple pattern for requirements analysis
<https://www.ibm.com/developerworks/architecture/library/ar-analpat/ar-analpat-pdf.pdf>`_
to structure the problem space into business processes (stranding, tagging, and
track/nest count) and IT processes (for each business process: data collection,
capture, proofreading and curation, query, export and data analysis).
Legacy systems and their ties to the current implementation (WAStD) are discussed as well.

Glossary
========
* **Data collection** refers to the collection of information gained from an
  observation onto a paper datasheet.
* **Data capture** refers to **data entry**, the process of entering information
  either from a datasheet or from a direct observation into an electronic form.
* A **data record** is one data point, e.g. one observation, in a digital
  system, e.g. in a database. A data record is often kept as one row in a table.
* **Data QA** refers to the various stages of ensuring that data records are as
  true and reliable as possible. Data QA includes proofreading and what we call
  curation.
* **Proofreading** is the process of comparing the primary data source, e.g.
  a hand-written datasheet or an email, to the digital record to eliminate
  typographical errors, mis-readings, and overall to make sure that the record
  represents the observer's intent as closely as possible.
* **Curation** is the process of validating and possibly updating records against
  subject matter expertise.

Aims
====
NdS OA AF 3: "Establish efficient Information Management systems."

* `Develop systems for the compilation, management and long-term storage of datasets
  and their metadata related to sea turtles and their habitats
  <https://github.com/parksandwildlife/biosys-turtles/issues/14>`_

* `Develop a stranding information database
  <https://github.com/parksandwildlife/biosys-turtles/issues/15>`_

* `Improve current marine turtle database to ensure functionality across user
  groups for tagged turtles, beach surveys and other information
  <https://github.com/parksandwildlife/biosys-turtles/issues/16>`_

* `Develop project management systems (projects, scientific papers, reports, plans)
  that complement existing corporate systems
  <https://github.com/parksandwildlife/biosys-turtles/issues/17>`_

Overview - Turtle monitoring
============================
This section provides a quick overview of turtle monitoring activities along the
life cycle of a turtle.

.. image:: https://www.lucidchart.com/publicSegments/view/8c466bd4-bd12-4bf0-890e-9ad372d7bec4/image.png
    :target: https://www.lucidchart.com/publicSegments/view/8c466bd4-bd12-4bf0-890e-9ad372d7bec4/image.png
    :alt: Turtle life cycle

Here, a simplified turtle life cycle  is shown together with data captured along it.
Note that duration and frequency of individual stages may differ between turtle species.
E.g., leatherbacks do not nest at all in WA, but are encountered occasionally.

The three main areas of monitoring work are:

* Tagging of nesting female turtles (during nesting season, on nesting beach, directly after nesting or nesting attempt) - "tagging"
* Track and nest count (during nesting season, on nesting beach, on morning after nesting) - "tracks"
* Marine wildlife incidents involving turtles (any place, any time) - "strandings"

Overview - Data management
==========================
This section gives a brief overview of the information management ecosystem
("the system" referring to current implementation, or "the solution" referring
to ideal solution) described in this chapter.

.. _dm-roles:

Data management roles
---------------------

.. image:: https://www.lucidchart.com/publicSegments/view/c1ac7e17-c178-462d-8aab-1de6458b11bc/image.png
   :target: https://www.lucidchart.com/publicSegments/view/c1ac7e17-c178-462d-8aab-1de6458b11bc/image.png
   :alt: Turtle program data management roles

Stakeholders interact with the system in different roles:

* data collection
* data entry
* data QA (proofreading and curation)
* data query and export
* data analysis
* knowledge inference and advice

A person can occupy none, one or several roles. Each role has a different set of
requirements and goals.

.. _dm-overview:

Turtle business processes current state
---------------------------------------

.. image:: https://www.lucidchart.com/publicSegments/view/5561395b-f450-4f21-b670-acbddb540c97/image.png
   :target: https://www.lucidchart.com/publicSegments/view/5561395b-f450-4f21-b670-acbddb540c97/image.png
   :alt: Turtle data management overview - current state

Each data stream on the left hand side will be discussed below in more detail.

.. _dm-ideal-system:

Turtle business processes ideal state
-------------------------------------

.. image:: https://www.lucidchart.com/publicSegments/view/dbd47e49-d636-4d90-b455-3edb3dbe455f/image.png
   :target: https://www.lucidchart.com/publicSegments/view/dbd47e49-d636-4d90-b455-3edb3dbe455f/image.png
   :alt: Turtle information management system overview

This diagram shows a simlified ideal system architecture.
Each core data stream is implemented in the Turtle Information Management System (TIMS).
TIMS interacts with the data repository BioSys through the BioSys API.
Other core systems also have an API.
The APIs are accessible through an Enterprise Service Bus (ESB).
An ESB is like a phone network between APIs: Applications interact with data
repositories through the ESB, like humans can talk to each other on the phone.
Requirements to TIMS will be largely shared by all data streams.

.. _dm-data-entry:

IT processes along the Data life cycle
--------------------------------------

.. image:: https://www.lucidchart.com/publicSegments/view/e903e543-e5b9-4b4e-b05f-035772f5bb36/image.png
   :target: https://www.lucidchart.com/publicSegments/view/e903e543-e5b9-4b4e-b05f-035772f5bb36/image.png
   :alt: Turtle data flow, ideal state

Each data stream goes through parts of this process:

* Collecting data: capturing an observation onto a datasheet
* Scanning & filing datasheets
* Converting digital data formats to standard formats
* Capturing data: Entering data from datasheets into an online system, or entering
  observations directly into digital forms
* Importing records from one digital system into another
* Proofreading entered data against paper datasheets
* Curating data with subject matter expertise
* Marking data as embargoed or ready to release
* Querying / exporting data
* Analysing, visualising, modelling data
* Inferring knowledge

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

`REQ #18 <https://github.com/parksandwildlife/biosys-turtles/issues/18>`_
Insight on turtle strandings must be available in a timely, defensible,
reproducible and accessible manner.

Task
----

* Improve the information pipeline from databased, stranded animal to
  ministerial / managerial inquiry, so that timely, defensible, reproducible,
  and accessible insight is available.
* Digitise and curate the backlog of old stranding reports, while retaining
  full data lineage.

Constraints
-----------
The solution architecture must consider the following contraints:

* Biosys aims to deliver similar functionality, but not within the required time.
* `REQ #47 <https://github.com/parksandwildlife/biosys-turtles/issues/47>`_
  The interim solution shall be either disposable (to be re-implemented in BioSys),
  re-usable (to be integrated in BioSys), or scalable (to become a part of BioSys).
* `REQ #5 <https://github.com/parksandwildlife/biosys-turtles/issues/5)>`_
  The solution shall be SOE, follow OIM's standards and integrate into their
  infrastructure ecosystem.
* `REQ #7 <https://github.com/parksandwildlife/biosys-turtles/issues/7>`_
  Double handling of data entry shall be avoided - do it once, and do it
  properly (complete, correct, consistent).
* `REQ #6 <https://github.com/parksandwildlife/biosys-turtles/issues/6>`_
  There must be a standardised, accessible way to import and export all data
  into and out of the solution.
* `REQ #8 <https://github.com/parksandwildlife/biosys-turtles/issues/8>`_
  The solution shall be compatible on a raw data level with Queensland's
  StrandNet, Parks & Wildlife's Turtle Tagging database WAMTRAM 2,
  and the Ningaloo Turtle Program's track count database.

Current implementation
----------------------

Turtle Strandings
^^^^^^^^^^^^^^^^^
* The data flow is shown in :ref:`dm-data-entry`.
* Stranding paper forms are being updated (SFo and FM, Nov 2016 - Mar 2017).
* `REQ #23 <https://github.com/parksandwildlife/biosys-turtles/issues/23>`_
  An updated incident response workflow for marine wildlife incidents is in
  development (May 2017, KimO).
  The affiliated Murdoch Vet (EY Dec 2016) has her own requirements.
* A digital data capture form caters for turtle strandings (can be extended to others)
  and is in beta testing (not officially released yet).
* WAStD allows data entry from legacy paper forms, as well as data export and query.
* `Live workbooks <http://rpubs.com/florian_mayer/strandings>`_
  can query, analyse and visualise data from WAStD via its API.

The following figure details the data flow for turtle strandings:

.. image:: https://www.lucidchart.com/publicSegments/view/792bc100-204d-41ff-8bd4-84a26d604fd8/image.png
   :target: https://www.lucidchart.com/publicSegments/view/792bc100-204d-41ff-8bd4-84a26d604fd8/image.png
   :alt: Turtle strandings data management: current implementation

Cetacean strandings
^^^^^^^^^^^^^^^^^^^
Nature Conservation kept a Filemaker Pro database of Cetacean strandings.
The database custodian has retired after extended leave.

It shall be noted that the custodian of the legacy turtle tagging database
WAMTRAM 2 understood correctly that strandings of tagged turtles are a vital
part of their life history -- as they are used in mark-capture-recapture analysis --
and aimed to include the strandings process into the database;
however, this process was not completely implemented and is not fully operational.

The following figure shows current implementation and possible transition of
Cetacean stranding data management.

.. image:: https://www.lucidchart.com/publicSegments/view/516fb077-229c-4110-9c6a-f60a14f9fe61/image.png
   :target: https://www.lucidchart.com/publicSegments/view/516fb077-229c-4110-9c6a-f60a14f9fe61/image.png
   :alt: Cetacean strandings data management: current implementation and transition process

IT process Stranding incident report
------------------------------------
A ranger or other departmental field worker responds to a stranding incident.
The stranding (using a mobile data collection app) is reported to HQ,
and further actions are taken as per latest instructions (to be updated).

The current paper-based process involves paper-based stranding report forms,
scanning, emailing, manually entering and proofreading.
It feeds into the workflow documented at :ref:`itp-stranding-curation`.

A new digital reporting process is in beta-testing, ready to incorporate other
taxonomic groups of strandings and documented at :ref:`itp-stranding-report`.

An updated workflow for turtle strandings is being distributed to field offices
at the time of writing (Jan 2017), but requires further updates to include
other priority taxa (cetaceans, pinnipeds, dugong, sea snakes etc.).

`REQ #19 <https://github.com/parksandwildlife/biosys-turtles/issues/19>`_
Data should, where feasible, be "born digitally" to minimize the costly and
error-prone crossing of the analog-digital barrier.

`REQ #21 <https://github.com/parksandwildlife/biosys-turtles/issues/21>`_
The incident responder shall be able to capture the data offline, with the
necessary reference at hand (species ID guides, relevant data from the central
database, "next steps" flow chart), using cheap and readily available
technology (e.g. tablets or smart phones), and be able to auto-upload the data
once online (office WiFi or mobile reception) without manual effort.

`REQ #22 <https://github.com/parksandwildlife/biosys-turtles/issues/22>`_
The digital data capture tool shall record location and time automatically.

`REQ #20 <https://github.com/parksandwildlife/biosys-turtles/issues/20>`_
The incident responder shall be provided with a comprehensive, easy to follow,
work flow (as flow chart printout, handbook, or in a digital format).

`REQ #23 <https://github.com/parksandwildlife/biosys-turtles/issues/23>`_
There shall be one centralised wildlife incident response contact within DPaW,
which shall direct the incidents to the respective responders both within and
external to the Department.

IT process Stranding data curation
----------------------------------
Data curation requires at least four steps
(`REQ #26 <https://github.com/parksandwildlife/biosys-turtles/issues/26>`_):

* A data entry operator digitises legacy data from emails, old paper-based
  stranding reports and other, unstructured information.
  `REQ #25 <https://github.com/parksandwildlife/biosys-turtles/issues/25>`_
* A second data entry operator proof-reads the digitised records.
* A qualified curator with good business knowledge of turtle ecology reviews the
  records.
* A manager with data publication permission flags records as ready for public
  release, or embargoes the data.

Detailed instructions for each role are documented at
:ref:`itp-stranding-curation`.

IT process Stranding data analysis
----------------------------------
As documented at :ref:`usecase-stranding-ministerial-inquiry`, the current
implementation serves several analytical requirements:

* A ministerial inquiry seeks a summary of "how many, which species, where, when".
* A manager seeks to inform management decisions.
* A researcher seeks to infer knowledge about ecological processes, their change
  over space and time, and possible drivers.

`REQ #43 <https://github.com/parksandwildlife/biosys-turtles/issues/43>`_
`REQ #31 <https://github.com/parksandwildlife/biosys-turtles/issues/31>`_
Data consumers shall be able to query, filter and export the raw data.
Data access shall be restricted role-based, so that sensitive data is accessible
only to trusted and authorised data consumers.
The system shall default data restrictions to be suitable for the general audience.

.. _usecase-stranding-ministerial-inquiry:

Use case: Ministerial inquiry, annual report, strategic advice
--------------------------------------------------------------

This section discusses requirements of each stakeholder role involved in

* the response to a ministerial inquiry,
* annual reporting for a steering committee,
* strategic advice to a policy officer,

and demonstrates the current implementation in WAStD.

The data life cycle in this particular case is shown below.

.. image:: https://www.lucidchart.com/publicSegments/view/ff4a25e1-8efc-4936-baec-5dbe54ac7204/image.png
     :target: https://www.lucidchart.com/publicSegments/view/ff4a25e1-8efc-4936-baec-5dbe54ac7204/image.png
     :alt: Stranding data life cycle

The following use case traces the data life cycle back to front to keep the
narrative engaging.

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
(see also `REQ #43 <https://github.com/parksandwildlife/biosys-turtles/issues/43>`_)

* How many `boat strikes to turtles <https://strandings.dpaw.wa.gov.au/admin/observations/animalencounter/?cause_of_death__exact=boat-strike&taxon__exact=Cheloniidae>`_ have been recorded?
* How many turtle strandings happened `in 2016 <https://strandings.dpaw.wa.gov.au/admin/observations/animalencounter/?encounter_type__exact=stranding&taxon__exact=Cheloniidae&when__year=2016>`_?
* How many turtle strandings happened within the `80 Mile Beach MPA <https://strandings.dpaw.wa.gov.au/admin/observations/animalencounter/?encounter_type__exact=stranding&taxon__exact=Cheloniidae&where=3>`_?

These examples show only a few out of many possible combinations of search filters.
All results can be exported to spreadsheets for further analysis.
The same results can also be generated through the API for consumption by software.
See :ref:`data-consumers-api` for working examples.

Manager
^^^^^^^
The manager requires timely and defensible insight

* to answer a ministerial inquiry,
* to fulfil reporting obligations e.g. to a steering committee, or
* to provide data-driven, strategic advice for management interventions or plans.

Insight could be required as
(see also `REQ #43 <https://github.com/parksandwildlife/biosys-turtles/issues/43>`_):

* `data <https://strandings.dpaw.wa.gov.au/admin/observations/animalencounter/>`_
  (spreadsheet - "List all incidents of <species> within <region> and <date range>"),
* `summarised numbers <https://strandings.dpaw.wa.gov.au/admin/observations/animalencounter/>`_
  (spreadsheet totals - "How many <species> within <region> suffered incidents?"),
* `analytical output <http://rpubs.com/florian_mayer/wastd-mark>`_
  (probability of correlations - "Did the new boat ramp
  significantly increase the number of boat strikes to <species>?"),
* `geographic distribution <https://strandings.dpaw.wa.gov.au/>`_
  (maps - "Where did the strandings happen?").

* `REQ #18 <https://github.com/parksandwildlife/biosys-turtles/issues/18>`_
  Insight should be available as **timely** as possible, minimizing human bottlenecks.
* Insight should be **accessible**, in that managers should be able to
  retrieve answers to common questions themselves.
* Insight should be **defensible**, in that the processing steps of both data
  `QA <https://strandings.dpaw.wa.gov.au/admin/observations/animalencounter/10/change/>`_
  (audit trail of QA operations)
  and `analysis <http://rpubs.com/florian_mayer/tracks>`_ are well documented,
  providing a fully transparent data lineage from datasheet to generated insight.
* Insight should be **reproducible**, in that other people with limited
  technical or statistical expertise can
  `reproduce the analysis <http://rpubs.com/florian_mayer/tracks>`_
  from the archived inputs.

Real-world example of Cetacean stranding questions
(see also `REQ #43 <https://github.com/parksandwildlife/biosys-turtles/issues/43>`_):

* incidents with mortality
* incidents with entanglement (ensuing mortality or not)
* other non-entanglement incidents
* strandings (ensuing mortality or not)
* mortalities in cetacean stranding db are cases with "cause of death" not "na"

Analyst
^^^^^^^
The analyst's role is to bridge the gap between raw data and non-trivial questions
through advanced statistical analysis and visualisation.
`REQ #48 <https://github.com/parksandwildlife/biosys-turtles/issues/48>`_

* To do so, the analyst needs
  `universal access <https://strandings.dpaw.wa.gov.au/api/1/>`_
  to machine-readable, trustworthy data.
* The data needs to be complete, consistent and correct.
* `REQ # 39 <https://github.com/parksandwildlife/biosys-turtles/issues/39>`_
  The analyst needs to hit the ground running with
  `working examples <https://strandings.dpaw.wa.gov.au/users/FlorianM/>`_
  of loading the data from the machine-readable access point into the most common
  `analytical frameworks <https://github.com/parksandwildlife/wastdr>`_.
* There should be sufficient documentation (:ref:`data-consumers`)
  to allow statistically trained analysts to efficiently consume data without
  technical knowledge of the system they are stored in.
  (See your own WAStD profile for code examples including your own API token).
* `REQ #6 <https://github.com/parksandwildlife/biosys-turtles/issues/6>`_
  Access needs to be following standard protocols and formats,
  be entirely independent of both the systems it is stored in,
  as well as independent of the software packages it is analysed with.

Data curator 3: Subject matter expert
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Subject matter experts acting as data curators need to validate the records,
e.g. confirm species identification. This increases **correctness** of the data.

* Data curators need convenient, unrestricted access to the data.
* Data needs to indicate its curation status.
* `REQ #26 <https://github.com/parksandwildlife/biosys-turtles/issues/26>`_
  Data needs to retain its lineage by retaining its editing and status history.
* `REQ #55 <https://github.com/parksandwildlife/biosys-turtles/issues/55>`_
  Each human decision by the subject matter expert should be translated into an
  automatic test or filter that flags similar records for review. This feedback
  process aims to distil the subject matter expertise into formal rules.

Data curator 2: Proofreader
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Digitising data sheets is an error-prone operation. Sorting vague information into
the available categories requires some informed decisions, based on guidelines.
Proofreading will help fighting typos and misunderstandings between datasheet
and database, therefore increasing **consistency**.

* `REQ #25 <https://github.com/parksandwildlife/biosys-turtles/issues/25>`_
  `REQ #42 <https://github.com/parksandwildlife/biosys-turtles/issues/42>`_
  The proofreader needs original datasheets, communication records and supplemental
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

* The data collector needs clear and up to date procedures, and easily useable,
  up to date (`REQ #40 <https://github.com/parksandwildlife/biosys-turtles/issues/40>`_)
  datasheets.
* Paper is cheap, bad information is costly. Taking the correct pictures in correct
  angles and lighting, as well as taking and processing samples, or preserving
  the carcass for a subsequent necropsy correctly is time-critical and cannot be
  repeated later.
  `REQ #56 <https://github.com/parksandwildlife/biosys-turtles/issues/56>`_
  Instructions to take the right measurements, samples and photographs must be
  available to the data collector.
* Datasheets need to capture complete, consistent and correct data, while avoiding
  capturing unnecessary detail.
* Datasheets should provide enough guidance to the data collector on providing the
  desired data formats and precision.

`REQ #25 <https://github.com/parksandwildlife/biosys-turtles/issues/25>`_
The data collector could reduce the workload on core staff by entering the datasheet
themselves, if the data portal had data entry forms with restricted access.
These forms are different to the curation forms - more streamlined for data entry.

Primary reporter: General public
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
A member of the public encounters stranded, entangled, or injured wildlife.
Members of the general public reporting a stranding need to know how to react -
whom to call, which data to collect (e.g. geo-referenced phone pictures).
Depending on the urgency, the member of the public will:

* alert DPaW immediately, so a ranger can attend the incident;
* notify DPaW later (e.g. if remote and offline);
* do nothing.

Depending on the efficiency of the notification pathway, the incident information
will find its way to the data entry operator in several ways:

* A DPaW ranger attends the incident fills in the correct datasheet, scans and
  emails it to the correct internal contact.
* A DPaW staff member reports an incident which is too remote or too old to
  attend to the correct internal contact.
* The report from the member of the public finds its way through detours to the
  correct internal contact.

`REQ #57 <https://github.com/parksandwildlife/biosys-turtles/issues/57>`_
Primary reporters would be pleased to hear how their actions contributed to an
increased understanding, and ultimately the conservation of the stranded species.
This could happen in the form of a "thank you" email with an excerpt of the
final stranding record.

Example: TOs returning tags after harvesting a tagged turtle usually get sent
a reward like branded t-shirts or baseball caps by Marine Science to show their
appreciation.

Gap analysis
------------

* Front-line staff are not yet trained in using WAStD.
* Paper forms are not phased out yet.
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
`Milestone Turtle Tagging <https://github.com/parksandwildlife/biosys-turtles/milestone/8>`_

Tags have a life cycle, characterised by interactions with humans and animals:

* `#9 create tag status list <https://github.com/parksandwildlife/biosys-turtles/issues/9>`_
* `#3 LC diagram tag <https://github.com/parksandwildlife/biosys-turtles/issues/3>`_

Use cases along the life cycle of a tag, also mentioned in
`REQ #10 <https://github.com/parksandwildlife/biosys-turtles/issues/10>`_:

* Order tag (typically in batches) with running ID e.g. WB1500 - WB3500
* Record tag batches as ordered, produced, delivered (how much detail is required?),
  allocated to field team (important)
* Query: how many tags have we ordered?
* Query: what's the next available tag number?
* Query: which tags are available to hand out to field teams?
* Query: when do we have to re-order?
* Query: which tags are in possession of field team x?
* Query: where is tag y, who is in possession or tag y?
* Field teams report tags as "applied new", "re-clinched" or "re-sighted"
  when tagging animals through digital or paper field data forms
* Tag returns from TOs after harvest
* Tags can be found on stranded animals, returned to HQ
* Tags are never re-applied to different animals but destroyed and recorded as such

IT process Turtle tagging field data collection
-----------------------------------------------
Ideal process:

.. image:: https://www.lucidchart.com/publicSegments/view/b577a3d7-4314-4421-8752-1299e852ea74/image.png
     :target: https://www.lucidchart.com/publicSegments/view/b577a3d7-4314-4421-8752-1299e852ea74/image.png
     :alt: Tagging data life cycle (ideal)

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

`REQ #12 <https://github.com/parksandwildlife/biosys-turtles/issues/12>`_
The solution for a digital turtle tagging field data capture app must be
optimised for harsh environmental conditions and low light, as well as
the non-linear and  opportunistic nature of tagging data capture.

`REQ #11 <https://github.com/parksandwildlife/biosys-turtles/issues/11>`_
The solution shall carry the complete backlog of tagging records to provide
the field workers with real-time insight about last sighting and in general all
data relating to the encountered turtle (if already tagged), utilised tags,
samples, data loggers and all other uniquely identifiable involved entities.

`REQ #28 <https://github.com/parksandwildlife/biosys-turtles/issues/28>`_
The solution shall allow daily syncing between multiple field data capture
devices while still in the field.

`REQ #29 <https://github.com/parksandwildlife/biosys-turtles/issues/29>`_
The solution shall be able to toggle interface features and functionality
between field data capture, field data curation, data upload, central data
curation and other roles.
The solution shall be responsive to different device display widths.

`REQ #13 <https://github.com/parksandwildlife/biosys-turtles/issues/13>`_
The solution shall provide data entry from paper datasheets (similar to
W2 field data collection database) as well as direct digital data capture
(similar to track count app).


IT process Turtle tagging data curation (field and office)
----------------------------------------------------------
Tagging data captured in the field is particularly error-prone due to the
stressful circumstances of the field work.

Currently, a first round of data curation occurs during data entry of paper data
forms into the WAMTRAM field database on the morning after a tagging night, when
memory of any possible irregularity is still fresh.
Anecdotal use cases are reported at :ref:`lessons-learnt-paper-based-data-capture`.


IT process Turtle tagging data analysis
---------------------------------------
Tagged turtles are useful for mark-capture-recapture analysis.
Stranded tagged turtles are part of this scope.

:ref:`data-analysis-animal-life-cycle` illustrates M-C-R analysis.

`REQ #35 <https://github.com/parksandwildlife/biosys-turtles/issues/35>`_
The system should maintain the location and processing status of physical
samples (biopsy, histology, etc.) taken from a tagged (or stranded) turtle.

Use cases:

* Where is sample S1234 at the moment? Who is in possession of the sample? How
  can I contact them?
* Has the sample been analysed? Where is the data?
* Is there any tissue left from that sample to analyse? How much?

`REQ #37 <https://github.com/parksandwildlife/biosys-turtles/issues/37>`_
The solution should allow adding new groups of measurements as required.
E.g., blood samples may return e.g. 30 defined biochemical measurements per turtle.
The solution should have a way to add those defined fields explicitly, so that
the data can be accessed in a structured way. This paves the way for queries
like "what is the mean / SD / min / max blood sugar level for flatback turtles".

`REQ #5 <https://github.com/parksandwildlife/biosys-turtles/issues/6>`_
The analysts need timely access to the data. The data should be in standardised
formats.

`REQ #39 <https://github.com/parksandwildlife/biosys-turtles/issues/39>`_
Data analysts should be given working examples on how to access the data.
E.g., the R package `wastdr <https://github.com/parksandwildlife/wastdr>`_
provides convenience wrappers around the WAStD API, plus working examples and
example data.

`REQ #31 <https://github.com/parksandwildlife/biosys-turtles/issues/31>`_
Data analysts, like all other stakeholders, require role based access to the data
they are supposed to access, and preventing them from accessing data they are not
supposed to see.

Legacy system: WAMTRAM 2
------------------------

The basic data flow for the current production turtle tagging system WAMTRAM 2
is shown in the following diagram and explained below.

.. image:: https://www.lucidchart.com/publicSegments/view/7b08f661-15d3-411b-8931-d22317f75ee9/image.png
     :target: https://www.lucidchart.com/publicSegments/view/7b08f661-15d3-411b-8931-d22317f75ee9/image.png
     :alt: Tagging data life cycle (current)


* Data backend is an MS SQL Server 2012 database on ``kens-mssql-001-prod``.
* Curator Bob Prince administrates data through an MS Access admin front-end.
* For each field team, Bob uses the admin frontend to export the
  entire current database into a data collection database.
* Field teams receive a data collection database backend (MS Access mdb)
  plus data collection frontend (MS Access mde) which allows data entry,
  does rudimentary data validation, and allows looking up existing data (e.g.
  tag history, turtle history).
* Penv get 2-3k taggings each year from Barrow and Munda.
  This is far more than DPaW themselves tag.
* Field teams return the data collection backend, which Bob imports into W2.
* If W2 reports import errors, Bob changes field data using his subject
  matter expertise and scans of original data sheets (if available) to resolve
  typos and incorrectly entered data. Bob frequently has to contact the field
  teams in order to reconcile conflicting data.
* Once import validation passes, WAMTRAM ingests the new data batch.
* W2 requires data to be entered in chronological order or else it throws errors.
* Flipper tag procurement happens through DPaW as custodians of tag names
  (e.g. "WA1234").
* W2 disallows team 2 to enter tags allocated to team 1, even if team 1's turtles
  migrate to team 2's tagging area.
* Deployment `Documentation
  <https://confluence.dpaw.wa.gov.au/display/sd/MSP%20Turtle%20Tagging%20DB>`_
  is restricted to WAMTRAM 2 maintainers.


A tag asset management system as per
`REQ #35 <https://github.com/parksandwildlife/biosys-turtles/issues/35>`_
will solve the following problems:

* Taggers need to know from existing tags to which tagging area the tag was
  assigned to.
* REQ Flipper and PIT tag asset management: need to know location and beach they
  are assigned to. This allows to QA typos in datasheets by narrowing down
  possible lists of tag names.
* REQ At any point in time we need to know precise location and holder of tags, which
  may change every night during tagging season.

If the solution would allow data entry in random order
`REQ #58 <https://github.com/parksandwildlife/biosys-turtles/issues/58>`_, and
let curators later fix any remaining issues, this would solve the following problems:

* W2 is missing the option to enter a resighted turtle if the original tagging
  is not already recorded or imported.
* W2 assumes all datasheets are available for data entry before the next tagging
  night, and enforces data entry in chronological order. This is seen as a limitation.

`REQ #59 <https://github.com/parksandwildlife/biosys-turtles/issues/59>`_
Limitations impacting digital data collection on gas plants:

* Electronic devices are only recently permitted on Barrow Is.
* All electronic devices must be certified for fire / spark safety.
* Varanus Is would work with tablets.
* Barrow Is is too hectic for tablets.

* `REQ #11 <https://github.com/parksandwildlife/biosys-turtles/issues/11>`_
  Pend do not need to know turtle history when tagging, they treat every turtle
  similarly.

Stakeholder requirements to maintain WAMTRAM 2:

* `REQ #60 <https://github.com/parksandwildlife/biosys-turtles/issues/60>`_
  There should be a SOP on defining activities that are available to enter
  (toggle "display observation" on activity).
* `REQ #61 <https://github.com/parksandwildlife/biosys-turtles/issues/61>`_
  W2 does not export observer name, only observer number.

Other stakeholder feedback on WAMTRAM2:

* `REQ #62 <https://github.com/parksandwildlife/biosys-turtles/issues/62>`_
  W2 field data entry database report Observations is useless.
* `REQ #63 <https://github.com/parksandwildlife/biosys-turtles/issues/63>`_
  W2 beach names contain duplicates: Munda main beach = Cowrie beach
  W2 beaches should be de-duplicated and have a bounding box / poly.
* `REQ #64 <https://github.com/parksandwildlife/biosys-turtles/issues/64>` _
  If entering a re-sighting in W2 field db, operators should not immediately
  see existing tag names. It is too easy to perpetuate an incorrect tag name.
  Data entry operator should be able to flag historic records as
  "suggested edit: WA12341 should be WA12347", but not actually change them.
* `REQ #65 <https://github.com/parksandwildlife/biosys-turtles/issues/65>`_
  The system should keep digital copies of original datasheets with records.
* `REQ #66 <https://github.com/parksandwildlife/biosys-turtles/issues/66>`_
  The Dept should demand datasheets to be returned as part of tagging license.
  Pend does not mind returning datasheets as they scan it anyways.
  There could be resistance from industry partners  to return datasheets.
* `REQ #45 <https://github.com/parksandwildlife/biosys-turtles/issues/45>`_
  W2 does not record surveys, so surveys without sightings (true absence) are
  not recorded.

* `REQ #67 <https://github.com/parksandwildlife/biosys-turtles/issues/67>`_
  Penv: data collection, entry, QA, analysis should be repeatable, standardised
  by DPaW.
* Penv want to capture data through tablets where feasible, otherwise on paper.
* Penv's PW designed the W2 tagging datasheet with W2 developer BR, revision 2017
  by DPaW.
* `REQ #68 <https://github.com/parksandwildlife/biosys-turtles/issues/68>`_
  W2 should add license number to batch of tags,
  compliance check: who tags without license?

Analysis workflow for Analyst of Barrow Is tagging data:

* Contractor (PENV) send workbook with raw data to analyst in April.
* Contractor sends temp logger data when retrieved (end of May).
* Analyst produces report for consumer (CHEV).
* Data: tagging data, hatching success separately, tracks.
* Analyst creates time blocks within season and looks at each animal's recapture
  history between time blocks.

* `REQ #11 <https://github.com/parksandwildlife/biosys-turtles/issues/11>`_
  The analyst needs full animal history of each encountered animal, even if
  some previous encounters were collected by other groups (e.g. by DpaW on THV)
* `REQ #28 <https://github.com/parksandwildlife/biosys-turtles/issues/28>`_
  Data needs to be synced between devices daily during data capture, and
  to master db if online.
* `REQ #36 <https://github.com/parksandwildlife/biosys-turtles/issues/36>`_
  The analyst wants to make model available, accessible, and reproducible as a
  workbook, but this is client's decision (CHEV).
  The analysis needs to be re-run if existing data (incl previous seasons) changes.
  This requires the analysis to be reproducible.

`REQ #26 <https://github.com/parksandwildlife/biosys-turtles/issues/26>`_
Data lineage:

* Analyst has to spend lots of time with data QA and chasing up central custodian's
  QA decisions (deletions, renaming of tags with typos), which is not billable
* Raw data contains edits and deletions from central curation activity (BP), so
  data don't necessarily sum up, and baseline changes minimally
* Analyst cannot easily detect or understand these changes, but gets criticism
  from consumer (CHEV).

* `REQ #26 <https://github.com/parksandwildlife/biosys-turtles/issues/26>`_
  Data lineage must be preserved to explain discrepancies.
* `REQ #69 <https://github.com/parksandwildlife/biosys-turtles/issues/69>`_
  The analyst needs to be able to easily detect changes in tallies of empirical
  data, e.g. implemented as QA gatecheck

Capture survey metadata, include covariates:

* `REQ #45 <https://github.com/parksandwildlife/biosys-turtles/issues/45>`_
  analyst needs to know sampling effort (surveys) even if no data collected
  The analyst also needs covariates (weather, wind, sun, disturbance, predator
  presence, sun angle, tide, beach geomorph, geology, sand moisture content,
  beach slope, location on beach relative to HWM and vegetation)
* ca 3 levels of wind strength would be sufficient from a modelling perspective
* Covariates can help model detection process of track / nest


`REQ #62 <https://github.com/parksandwildlife/biosys-turtles/issues/62>`_
Output:
* LTMMTP Chevron 2015: reports on metrics from tagging
* need "new turtle", "remigrant"
* need "has tag scars"


REQ WAMTRAM requirement to DPaW for Animal ethics:

* The number of turtles per species:
* basic handling: sighted and measured, not tagged or biopsied
* other study: sat tag
* other method on conscious animal:
* any tag applied-new or re-clinched,
* biopsy taken if not already in flipper-tagged

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

Loading data into, and analysing data from WAStD assumes:

* WAMTRAM 2 remains point of truth and curation interface for data until data
  are collected/entered directly into WAStD or other new system;
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

* preparation before field trip while online
* field data capture (during tagging)
* field data curation (morning after)
* syncing field data capture devices
* submitting data after field trip
* accessing merged data

Use case: Inquiry about tagged turtle
-------------------------------------
See chapter :ref:`data-consumers` on how to get to a
`Tag history <https://strandings.dpaw.wa.gov.au/api/1/tag-observations/?tag_type=flipper-tag&name=WA67541>`_
or an `animal history <https://strandings.dpaw.wa.gov.au/api/1/animal-encounters/?name=WA67541>`_.

Gap analysis
------------
Tagging is currently handled in WAMTRAM 2.

To replace WAMTRAM 2, digital / paper-based data capture as well as a central
data warehouse such as BioSys or WAStD are required.

.. _business-process-turtle-tracks:

Business Process Turtle Tracks
==============================
Turtle tracks are evidence of nesting activity. Tracks and taggings together
form a complete picture of a nesting beach.

IT process Turtle track and nest count
--------------------------------------

.. image:: https://www.lucidchart.com/publicSegments/view/b301ca6f-0489-4a2c-b36c-87220419b8dc/image.png
     :target: https://www.lucidchart.com/publicSegments/view/b301ca6f-0489-4a2c-b36c-87220419b8dc/image.png
     :alt: Track and nest count data life cycle (ideal)

.. image:: https://www.lucidchart.com/publicSegments/view/d7ff2850-5ffc-4ccf-838e-d217ee39eca4/image.png
    :target: https://www.lucidchart.com/publicSegments/view/d7ff2850-5ffc-4ccf-838e-d217ee39eca4/image.png
    :alt: Mobile data collection

See :ref:`data-capture-tracks` for the current implementation of
digital data capture of tracks and nests,
which is curretly in production use by the core Turtle team, and in beta testing
at Cable Beach and the Karratha office.

The mobile data collection form implements the following workflow:

.. image:: https://www.lucidchart.com/publicSegments/view/b0a9c41e-9578-4396-a009-a01721757c98/image.png
    :target: https://www.lucidchart.com/publicSegments/view/b0a9c41e-9578-4396-a009-a01721757c98/image.png
    :alt: Form "Track or treat" workflow

IT process Turtle track and nest data curation
----------------------------------------------
The same processes as described in turtle strandings apply to tracks and nest data.

IT process Legacy data ETL
--------------------------
The Ningaloo ETL RMarkdown workbook
(`source <https://github.com/parksandwildlife/turtle-scripts/blob/master/ningaloo/ningaloo_etl.Rmd>`_)
extracts data from the NTP database snapshot on the internal data catalogue into
CSV and GeoJSON files, and uploads them to the NTP
`dataset <http://internal-data.dpaw.wa.gov.au/dataset/ningaloo-turtle-program-data>`_.

The workbook can be extended to also upload the data into WAStD's API.

IT process Aerial imagery track count
-------------------------------------
Aerial imagery was captured of all turtle nesting beaches:

* Survey Nov 2014: Kimberley
* Survey Nov 2016: Pilbara

It is assumed that this imagery captures the overwhelming majority of turtle nesting
beaches, and that no significant nesting sites were missed.

Current process:

* Mosaics from aerial data is inspected in Quantum GIS (v. 2.18) by core turtle staff.
* Each visible track is captured using a copy of a template shapefile with
  associated style, which provides a popup form in line with the digital track
  count app, but highly streamlined for this process, so that the lowest possible
  user interaction is required per track.
* The shapefile can be imported to WAStD through a data ingestion script

Methodology and data ingestion in development. Currently: fresh tracks, success
not assessed, at high tide. Only species is assessed if evident.

UI mockup: view mosaic, clicking each track (protocol: on high water mark)
opens dialog with buttons for each species
choice, clicking any species choice saves feature and closes dialog.
Auto-set "observed by" and "recorded by" to current user's DPaW username.

Data shall be ingested to WAStD. Ingestion should be scripted, but does not need
to be real time, as these surveys happen too seldomly.

How to handle multiple analysis of same beach? This would be useful for analysis
of observer bias.

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

.. image:: https://www.lucidchart.com/publicSegments/view/f64d33a0-bcf4-4dd5-80c6-3204f1925aed/image.png
     :target: https://www.lucidchart.com/publicSegments/view/f64d33a0-bcf4-4dd5-80c6-3204f1925aed/image.png
     :alt: Ningaloo turtle program data management

The Ningaloo Turtle Program (NTP) database consists of an MS Access database
and frontend. Volunteers conduct track count surveys, enter data, and curate
the database.

Use case: Track data collection
-------------------------------
The current implementation is shown in the figure above.

Volunteers are trained by the NTP Coordinator and, following the NTP field manual,
collect turtle track data on paper data forms. Geolocation is collected on
GPS and digital cameras.

The data collection methodology captures tracks with nest individually, but
tracks without nests are only tallied. Predation is only recorded qualitatively.

Other Volunteers digitise the paper forms, GPS and camera into the NTP Access db.
This process is error-prone and resource-intensive.

The NTP Coodinator QAs the data, but does not have the time resources to
comprehensively proofread and compare data sheets vs entered data.

The NTP Coordinator exports data on demand.

The NTP Coordinator and the Ningaloo Marine Park Coodinator (MPC) create data
products (figures and tables) and write, or contribute, to several recurring
reports.

From MPC and NTP Coordinator:

* `REQ #7 <https://github.com/parksandwildlife/biosys-turtles/issues/7>`_
  Minimise data entry, a/d barrier crossings, handling steps, reduce double
  handling at data entry, prefer digital data capture.
* `REQ #70 <https://github.com/parksandwildlife/biosys-turtles/issues/70>`_
  Internet speed is very slow in Exmouth. Online transactions have to be async
  or minimised.
* `REQ #71 <https://github.com/parksandwildlife/biosys-turtles/issues/71>`_
  The system must be able to record at new surveyed sites and times,
  opportunistic sightings, independent of pre-configured exp design.
* `REQ #30 <https://github.com/parksandwildlife/biosys-turtles/issues/30>`_
  MPC and NTP Coordinator need access to other places' turtle data.
* `REQ #72 <https://github.com/parksandwildlife/biosys-turtles/issues/72>`_
  REQ need data in one place.
* `REQ #33 <https://github.com/parksandwildlife/biosys-turtles/issues/33>`_
  REQ Need clear data sharing policies, licences.
* `REQ #73 <https://github.com/parksandwildlife/biosys-turtles/issues/73>`_
  REQ All data should be as open as possible after mitigating data sensitivities.
* `REQ #74 <https://github.com/parksandwildlife/biosys-turtles/issues/74>`_
  Coordinator NTP: digital capture would be preferred if data is compatible and
  legacy data can be migrated.
  NTP database is outdated and requires upgrade, no local capability
  available to maintain / upgrade.
  Have the analysis script automated in a literate programming paradigm.

Use case: Track data analysis
-----------------------------
Known required analytical products:

* nesting success
* hatching / emergence success
* spatial distribution, patterns, change of patterns (temporal patterns)
* modelling: optimal monitoring from beginning / peak / end of hatching

Non-functional requirements
===========================

This section documents lessons learnt during the requirements analysis, design
and development of WAStD and anecdotal wisdom of colleagues and data custodians.

Senior data custodians are gold mines of business knowledge
-----------------------------------------------------------
`REQ #75 <https://github.com/parksandwildlife/biosys-turtles/issues/75>`_
Extracting their experience and intuition, and solidifying their knowledge into
written documentation takes months to years. Retirement, budget cuts and personal
circumstances can cut this available time short.

All custodians and colleagues with deep knowledge of related legacy systems
shall be consulted, their suggestions shall be incorporated into the systems
philosophy and design, and they should sign off on the requirements analysis.

Volunteers multiply value six-fold
----------------------------------
`REQ #57 <https://github.com/parksandwildlife/biosys-turtles/issues/57>`_
For each dollar the Department spends in the field, volunteers contribute about
six dollars in value. Sending them feedback and showing appreciation helps to
uphold motivation levels and retain this free work force.

The system shall allow the display, export and emailing of the contributions
of each person to the value chain of data.

A picture is worth a thousand badly drawn schematics
----------------------------------------------------
`REQ #76 <https://github.com/parksandwildlife/biosys-turtles/issues/76>`_
Pictures are cheap to take but expensive not to take.
Experts can tell nearly all details of a stranded animal from good pictures.
Often the initial guess of the first respondent is overruled by expert advice
based on photographs later.
Datasheets can be wrong, photos are more objective.
Datasheets should provide a list of desired photographic perspectives and angles,
and a list of details to capture close up.

Data collection shall prompt the user to take photos where feasible to augment
their judgement in the field.

The system shall allow attaching any file (datasheet scans, photographs,
email threads) to any record.

The system shall allow proof-readers and curators to easily compare attached
media with entered data for a given record.

Data entry is worth every drop of sweat spent on forms, procedure and documentation
-----------------------------------------------------------------------------------
Data entry is a messy process, adding much value to data. Many decisions have to
be made to transform a stranding report into a full stranding record.
Data is only trustworthy if the full data lineage is retained.
Data curation goes through several stages, each adding value (entry, proofreading,
subject matter expertise).

`REQ #69 <https://github.com/parksandwildlife/biosys-turtles/issues/69>`_
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

The turtle monitoring program will periodically re-evaluate projects, delivery,
priorities, and even the target outcomes. This will cause requirements at the
level discussed here to evolve and change over time.

REQ The solution architecture shall allow an evolution of components and functionality.

`REQ #54 <https://github.com/parksandwildlife/biosys-turtles/issues/54>`_
REQ The solution technology must be supported by DPaW OIM.
REQ The solution technology must be within the skill range of the primary maintainer (FM).

`REQ #77 <https://github.com/parksandwildlife/biosys-turtles/issues/77>`_
REQ (SFo) WAStD surveys should allow attachments (datasheets containing multiple
records so we avoid duplicate attachments to individual records) as well as
comments (e.g. climatic / environmental conditions or systematic errors in
methodology impacting data capture / validity / changing assumptions,
e.g. tracks blown away before capture leading to undersampling).

`REQ #78 <https://github.com/parksandwildlife/biosys-turtles/issues/78>`_
REQ The solution shall be open source under an open license.

`REQ #79 <https://github.com/parksandwildlife/biosys-turtles/issues/79>`_
REQ All requirements shall be translated completely into functional requirements,
and have 100% test coverage.
REQ The solution shall, if the technology allows, implement continuous
integration and testing as well as continuous deployment.

Requirements of the Turtle group
--------------------------------

REQ The group requires basic training in R, reproducible reporting, version control.

REQ The data entry operator (TO) should be trained to be a trainer for others.

REQ With data entry coming more and more from digital sources, the data entry
operator should migrate from a data entry, typist role towards a QA operator.

REQ The turtle group needs a dedicated scientific programmer, or at least
dedicated time of the Information Manager (FM) for scientific programming.

REQ Media collected during field work should be re-usable for media and reporting:

* sound bits
* good pictures with appropriate license for re-use
* short statements for general public
* media opportunities like upcoming field trips
* presenting an easy to understand data summary

The above listed outputs are available early in the process, but required far
later in the process.
In other words, by the time we need them it's too late to collect them.

"Sane management underpinned by robust science"

Business Process Annual Reporting
=================================

IT process data analysis and visualisation
------------------------------------------
REQ DA and DV must be automated and reproducible. Data must be pulled from the
point of truth (database), and a snapshot of the data used in the analysis must,
together with the analytical script, be uploaded to the internal data catalogue.

REQ Data products (e.g. figures and maps), utilised data (snapshots), and scripts
must be discoverable and accessible, and well documented with metadata.

REQ The turtle group must be trained, and willing to be trained, in the use of
the chosen analytical procedures.

REQ Analytical procedures shall require as little effort to re-run (with current
data) from the operator (turtle group members) as possible.

REQ Analytical procedures must be provided with sufficient documentation,
training resources, and ongoing support to allow efficient engagement
of turtle group members with data analysis and reporting.

IT process reporting
--------------------
REQ Reporting must be collaboratively authored, version-controlled, data-driven
and provide a clear separation of structure, content and layout.

REQ The turtle group must be trained in the use of the chosen reporting framework.

REQ Reporting framework procedures must be provided with sufficient
documentation, training resources, and ongoing support to allow efficient
engagement of turtle group members with data analysis and reporting.

How it's made - the process
===========================
Listen - look - touch - understand - build - repeat.

Listen
------
Listen to stakeholders to clarify past, present and future of:

* scope and growth of scope
* data in: data sheets
* work flows: manuals, instructions, communication
* insight out: products

Ask:

* If we can handle all data from data sheets and produce all products, what
  data haven't we touched?
* Who needs to be involved, when and how?
* Who needs to be trained, how often, who trains the trainers?

Writing down the above will evolve into the project's documentation, including
requirements analysis, technical documentation, user-level manuals, and training material.

Look
----
Look at examples of all production data. Review data sheets with stakeholders.
Does all data serve QA or generated insight? What's missing, what's unnecessary?

The combined understanding of production data will evolve into a data model, based
on a good understanding of involved product life cycles and user roles.

Touch
-----
Create live documents (workbooks) loading and inspecting production data
for each legacy system.
Describe and document legacy data in the workbooks.
Clean and transform legacy data, store snapshots in a central place (data catalogue).

These workbooks will evolve into ETL scripts for data in legacy systems.

Understand
----------
Build insight from the sanitised legacy data as raw versions of every product
identified by the stakeholders.

Review often with stakeholders to confirm relevance, validity, and evolve the
data product to optimise insight for data consumers.

Build
-----

Build systems to handle, store, document, process data.

Be modular and agile enough to evolve the systems into production systems.

Deploy systems in production mode to allow stakeholder interaction and to battle-test
deployment and recovery protocols.

Repeat
------

Build features end-to-end, optimize architecture rather than implementation.
Keep iterations small and consult stakeholders.

Verify the necessity of a feature through a product utilising it, and verify the
product's validity (and the correctnenss of data processing) with stakeholders.

Paradigms
=========

* do it, then
* do it right, then
* do it better.

* Build end-to-end pipelines in small iterations (agile)
* Use production data
    * to detect real-world problems,
    * to battle-test implementation approaches,
    * to evolve working solutions into correct, then comprehensive solutions
