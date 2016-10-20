=============
Specification
=============
High Level Business Requirements
================================

Problem
-------
Reports of turtle strandings exist as hard copy (paper, photos, datasheets),
electronic files (scanned datasheets, emails, photos), in databases
(Turtle Tagging DB WAMTRAM2), and in regional offices.

For ministerial inquiries on turtle strandings, there is no timely, defensible,
reproducible, and accessible insight available.
Monitoring and research questions suffer the same problem.


Scope
-----
Current scope of WAStD: Strandings of sea turtles.
Data entry is restricted to trained and trusted admins through "backstage" admin forms.
WAStD will interact, and eventually integrate with BioSys.

Departmental business related to turtle strandings:

* Strandings of other marine animals (marine mammals, reptiles)
* other turtle related data (tagging, nest and track count)
* other administrative data related to turtle monitoring (temperature loggers)
* Data entry (tagging) by field operators through standalone, offline, desktop capture tool
* Mobile app, read-only, with a browseable data snapshot "have I seen this turtle before?"
* Data entry (strandings) by less trained regional staff (Rangers), web based (not offline), through streamlined forms
* Data entry (tagging) by field operators online through stramlined forms
* Data ingestion from mobile data collection devices (existing Cybertracker fleet)


If any of the above scopes were to experience an acute business risk -- e.g.
data being siloed in outdated software,
insufficient database curation functionality corrupting core departmental data,
data custodians retiring or not being salaried,
outdated datasheets collecting incomplete, inconsistent, incorrect data --,
then a solution much like WAStD or BioSys would be required to mitigate that risk,
and sufficient care had to be taken to hand over the not always documented,
often living business knowledge from current custodians to permanent departmental staff.

The roll-out of the improvements in handling turtle strandings will cross over
with existing workflows of the above mentioned, out of scope business processes.

Task
----
Improve the information pipeline from stranded animal to ministerial / managerial inquiry,
so that timely, defensible, reproducible, and accessible insight is available.
Digitise and curate the backlog of old stranding reports, while retaining the full data lineage.

Constraints
-----------
The solution architecture must consider the following contraints:

* Biosys will eventually deliver similar functionality, but not within the required time.
* Any software built must be either disposable (to be re-implemented in BioSys),
  re-usable (to be integrated in BioSys), or scalable (to become a part of BioSys).
* Any solution built must be SOE, follow OIM's standards and integrate into their
  infrastructure ecosystem.
* Avoid double handling of data entry - do it once, and do it properly.
* There must be a standardised, accessible way to import and export all data into
  and out of the system.
* The application has to be compatible on a raw data level with Queensland's
  StrandNet, Parks & Wildlife's Turtle Tagging database WAMTRAM 2, and the Ningaloo Turtle Program's
  track count database.


Use case: Ministerial inquiry, annual report, strategic advice
--------------------------------------------------------------
This section discusses requirements of each role involved in

* the response to a ministerial inquiry,
* annual reporting for a steering committee,
* strategic advice to a policy officer.

Minister, steering committee, policy officer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The minister sends an inquiry to the Department.

The Turtle Monitoring Program's steering committee requires semi-annual reports
on turtle population metrics like mortality (strandings) or nesting (tagging and
track counts).

A policy officer needs to relate infrastructure developments (e.g. new boat ramps)
or management actions (e.g. boating exclusion zones) with turtle population metrics
(e.g. number of boat strikes).

There haven't been any ministerial inquiries yet, but we assume they could ask e.g.:

* How many `boat strikes to turtles <https://strandings.dpaw.wa.gov.au/admin/observations/animalencounter/?cause_of_death__exact=boat-strike&taxon__exact=Cheloniidae>`_ have been recorded?
* How many turtle strandings happened `in 2016 <https://strandings.dpaw.wa.gov.au/admin/observations/animalencounter/?encounter_type__exact=stranding&taxon__exact=Cheloniidae&when__year=2016>`_?
* How many turtle strandings happened in the `80 Mile Beach MPA <https://strandings.dpaw.wa.gov.au/admin/observations/animalencounter/?encounter_type__exact=stranding&taxon__exact=Cheloniidae&where=3>`_?

These examples show only a few out of many possible combinations of search filters.
All results can be exported to spreadsheets for further analysis.
The same results can also be generated through the API for consumption by software.

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
  `reproduce the analysis <http://rpubs.com/florian_mayer/wastd-mark>`_ from the
  archived inputs.

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
  analytical frameworks.
* There should be `sufficient documentation <http://wastd.readthedocs.io/data_consumers.html>`_
  to allow statistically trained analysts to efficiently consume data without
  technical knowledge of the system they are stored in.
* Access needs to be following standard protocols and formats, entirely independent of
  both the systems it is stored in, as well as independent of the software packages
  it is analysed with.

Data curator 3: Subject matter expert
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Subject matter experts acting as data curators need to validate the records,
e.g. confirm species identification. This increases **correctness** of the data.

* Data curators need convenient, unrestricted access to the data.
* Data needs to indicate its curation status.
* Data needs to retain its lineage by retaining its editing and status history.

Data curator 2: Proofreader
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Digitising data sheets is an error-prone operation, and allocating vague information
requires some informed decisions, based on guidelines.
Hence, proofreading will help fighting typos and misunderstandings between datasheet
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
* Electronic data entry forms should provide input validation for formats, not content.
* The data portal should
  `accept all formally correct data <http://wastd.readthedocs.io/developers.html#data-model>`_,
  but allow to identify and fix impossible or questionable records.

Data collector: Ranger, regional staff
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The departmental data collector (e.g. a ranger) responds to a stranding report
from the general public, or discovers a stranded animal themselves.

* The data collector needs clear and up to date procedures, and easily useable datasheets.
* Paper is cheap, bad information is costly. Taking the correct pictures in correct
  angles, as well as taking and processing samples, or preserving the carcass for a
  subsequent necropsy correctly is time-critical and cannot be repeated later.
  Instructions to take the right measurements, samples and photographs must be available to the data collector.
* Datasheets need to capture complete, consistent and correct data, while avoiding capturing unneccessary detail.
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
  a reward like branded t-shirts or baseball caps by Marine Science to show their appreciation.

Lessons learnt
==============
The journey so far:

* April 2016: Requirements Analysis (during SDIS main sprint)
* July 2016: Implementation
* August - Sept 2016: Agile iterations, weekly stakeholder workshops to refine
  requirements and update business processes understanding and requirements (during SDIS/ARAR cycle)
* Oct 2016: Production deployment, start of turtle stranding data entry,
  "dog fooding" the data entry manual, usability improvements,
  working on datasheets.

By sharing technology and architecture with BioSys, WAStD is part of the BioSys
ecosystem of data warehousing, data curation, data exchange standards and
analytical knowledge pipelines.

Senior data custodians are gold mines of business knowledge
-----------------------------------------------------------
Extracting their experience and intuition, and solidifing their knowledge into
written documentation takes months to years. Retirement, budget cuts and personal
circumstances can cut this available time short.

Volunteers multiply value six-fold
----------------------------------
For each dollar the Department spends in the field, volunteers contribute about
six dollars in value. Sending them feedback and showing appreciation helps to
uphold motivation levels and retain this free work force.

A picture is worth a thousand badly drawn schematics
----------------------------------------------------
Pictures are cheap to take but expensive not to take. Curators can tell nearly
all details of a stranded animal from good pictures. Often the initial guess
of the first respondent is overruled by expert advice based on photographs later.
Datasheets can be wrong, photos are more objective.
Datasheets should provide a list of desired photographic perspectives and angles,
and a list of details to capture close up.

Data entry is worth every drop of sweat spent on forms, procedure and documentation
-----------------------------------------------------------------------------------
Data entry is a messy process, adding much value to data. Many decisions have to
be made to transform a stranding report into a full stranding record.
Data is only trustworthy if the full data lineage is retained.
Data curation goes through several stages, each adding value (entry, proofreading,
subject matter expertise).

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

Proofreading and curation will take other operators a shorter time. This extra
effort has to be provided, and is a data quality issue, independent of
implementation (WAStD or BioSys).
Proofreading and curation requires trained core staff and cannot be outsourced.
