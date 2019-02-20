=============
Data curators
=============
This chapter addresses data curators, who enter and maintain the data.

WAStD's data model is built around the concept of an AnimalEncounter, which is
the physical encounter of an observer an an animal at one point in time and space,
during which different kinds of observations and measurements are made.
The kind of observations depend on the species and health/behaviour of the
animal - e.g. "dead and not doing much else" is a Stranding Observation
(morphometrics, tags, photos, damage, disposal, biopsy, necropsy),
while "alive and nesting" is a Tagging Observation (morphometrics, tags, photos,
damage, nest, eggs).

TSC's data model is built around an extended concept of AreaEncounter, which is
the physical encounter of an observer with individuals of a species (mainly animals or plants)
or an ecological community (threatened, priority, or neither) at a location.
The extent occupied by the species or community can be described either as a point
(animal location) or polygon (community boundary or plant population).
The encounter can incur any range of additional observations of the species or community,
the location, or the surroundings.

The following sections will instruct data curators how to enter data from
supported data sources into WAStD/TSC.

.. * link to example data sheets of all supported formats, and
.. * for each format, map the fields of the paper form to the online form.


.. _itp-species-fauna:
Threatened Fauna Occurrence
===========================

Paper form
----------
This section discusses changes to the legacy paper form to streamline it for TSC use.

Audience: TSC stakeholders, Species and Communities Branch.

Form version: NA, long version

* Species ID: proof (photos, samples, text description), certainty of ID,
* Specimen: label, location
* Population Observation: number at age classes
* Survey: methodology, type
* Animal observation: secondary signs, cause of death, reproductive state
* Habitat: landform, veg type
* Fire history
* Associated flora species
* Associated communities

Digital form
------------
Needs a lot of thought to streamline the very different scenarios in which an animal occurrence might be recorded.


.. _itp-species-flora:
Threatened Flora Occurrence
===========================

Paper form
----------
This section discusses changes to the legacy paper form to streamline it for TSC use.

Audience: TSC stakeholders, Species and Communities Branch.

Form version: 1.1 Jan 2012

* DRF permit
* Area assessment
* Quadrats
* Population structure
* Population condition
* Threats
* Habitat information
* Habitat condition
* Fire history
* Vegetation classification
* Associated species



.. _itp-community:
Ecological Community Occurrence
===============================

TEC Occurrence Report Form
--------------------------
This section discusses changes to the legacy paper form to streamline it for TSC use.

Audience: TSC stakeholders, Species and Communities Branch.

Form version: 6.0 July 2013

Glossary
^^^^^^^^

* [A] Assumption
* [D] Derived information, can be reconstructed from other information, not required to capture. Exclude from paper form.
* [R] Redundant information, duplicates other information, not required to capture.
* [K] Keep, already implemented.
* [N] New, add.
* [X] Remove as per stakeholder advice.

Part 1: Encounter details
^^^^^^^^^^^^^^^^^^^^^^^^^
The "w"s: Who, when, where, what.

Section "Community":

* Community: [K][A] The data collector must know the community code.
* Observation date: [K] ``encountered_on``.
* New occurrence: [D]
* Observers: ``encountered_by`` is the primary observer. [A] Clearly associated responsibility of reported information and person reporting.
* Role, email, organisation: [D] already in TSC. [A] every data reporter is or will be registered as user in TSC.

Section "Submission":

* Person submitting record [A] is that person entering record in TSC?

Section "Location":

* Description of location: [R] hand-waving about location is replaced with polygon or point.
* District, LGA, Reserve no: [D]
* Land manager present: [N] - what other fields are included in "Land manager attendance"?
* Datum: [R] default is WGS84.
* Coodinates: [R] replaced by polygon / point map widgets.
* Method used: [R] replaced by ``location_accuracy``.
* Land tenure: [D]

Section "Area assessment" -- keep and migrate legacy data, no new form

* Type (edge, partial, full): [N] add as area types: TEC boundary (edge), TEC boundary (partial)
* Area observed (m2): [D] from polygon
* Effort: [D] from [N] survey start time / [N] survey end time
* Time spent per area: [D] from survey end - start time / area observed

Part 2: The occurrence
^^^^^^^^^^^^^^^^^^^^^^
Condition, composition, threats and mitigation.

Section "Condition of occurrence":

* Single group. [N]
* Percentage of occurrence being rated on the Bush Forever scale as Decimal(2,0):

  * Pristine
  * Excellent
  * Very good
  * Good
  * Degraded
  * Completely degraded

Fields must add up to 100.

Section "Associated species":
* Repeating group. [N] m2m to species.

Section "Threats": make compatible with IUCN criteria.


* Repeating group. [N]
* Threat [N] - category or free text?
* Cause / agent [X]
* Area affected percentage [N]
* Current impact severity [N] Nil, low, medium, high, extreme
* Potential impact severity [N] low, medium, high, extreme
* Potential threat onset [N] short term (whithin next 12 months), medium term (within 1-5 years), long term (after more than 5 years)

Section "Recommended management actions" & "Actions implemented":

* Repeating groups, correspond to area management actions (including reporting).

Part 3: Location
^^^^^^^^^^^^^^^^
Habitat, fire history.

Section "Habitat information": Add "other, see comments", "comments".

* Single group. [N]
* Land form: multiple select.
* Rock type: multiple select.
* Loose rock: [X], but keep legacy.
* Soil type: multiple select.
* Soil colour: multiple select.
* Drainage: single select.
* Specific landform element (see field manual) [X] but keep legacy.
* Soil condition -> rename as soil moisture: single select.
* Vegetation classification: [X] but keep legacy.

Section "Fire history":

* Single group. [N]
* Last fire (date)
* Fire intensity (high/medium/low)
* No evidence of fire


Part 4: Attachments and additional information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Section "Comments":

* Single group. [N]
* Text comments.

Section "Attachments"

* Repeating group.
* File, title, category.


TEC Bushland Plant Survey Recording Sheet
-----------------------------------------
* Encounter
* Location
* Habitat
* Veg structure and cover [R]

  * life form (trees over 30m, trees 10-30m, trees < 10m, mallees > 8m, mallees < 8m, ...)
  * cover class (select)
  * dominant species (m2m)
* Section "Condition of occurrence"
* Species presence observation

  * Taxon
  * Collecting ID: made up in the field, unique to collected specimen within survey
  * Reproductive state: flowering or not etc
  * Identified in the field or not




TSC data entry
--------------
This section explains how to use the TSC data entry forms.

Coming soon.

Plan:

* One form for each part.
* Common fields (as per "Taxon/Community Area Encounter") are the basic unit of an encounter with an occurrence.
* Additional groups are added as separate forms to the basic encounter.

Occurrences can be reported

* from the home page (any species or community),
* from a species or community detail page (the species or community is then already prefilled),
* from a species or community area, such as a flora (sub)population or a TEC boundary (area "code" which links occurrence to that area is then also prefilled).

Each occurrence has a detail page (coming soon), where additional data can be added (such as habitat information, fire history, etc).


.. _itp-tracks-curation:
Turtle Tracks or Nests
======================
If data is not captured via the digital forms, it is still possible to enter data manually.

With data curator access, open the [data curation portal](https://tsc.dbca.wa.gov.au/admin/)
and [add a new TurtleNestEncounter](https://tsc.dbca.wa.gov.au/admin/observations/turtlenestencounter/add/).

Section "Encounter"
-------------------

* Area: ignore, will be chosen based on location
* Surveyed site: ignore, will be chosen based on location
* Survey: ignore, will be reconstructed on data import from digital forms
* Observed at (location): this is a hacky way to enter given coordinates in WGS84.

  * Click place marker icon (hover text: "Draw a marker"), then click anywhere on the map.
  * The text field "Geometry" will show the valid GeoJSON geometry for the chosen location.
  * Replace those (arbitrary) coordinates with the given coordinates from the datasheet.

* Location accuracy: Select as appropriate, e.g. GPS (10m)
* Observed on: use calendar and time widgets to select time of observation. Enter local time (AWST = GMT+08).
* Measured by:

  * Type data collector's name and select from auto-complete.
  * If name not in auto-complete, click on the "Lookup" icon (magnifying glass symbol) to pop open the list of users.
  * Search user, or add user as required, then select by clicking on username. This closes the user list popup and populates the form field.

* Recorded by: same as measured by.
* Data source: Direct entry or paper datasheet.
* Source ID: leave blank.

Section "Nest"
--------------

* Enter data as per datasheet, then hit "Save and continue editing".
* Note that source ID is now set, reflecting the data entered above.
* Review the "observed at" location and correct if necessary. Hand-written GPS coordinates are often wrong.

Section "Media Attachments"
---------------------------
"Add another" and upload the scanned datasheet (as PDF). "Save and continue editing".

Other sections
--------------
Add as required. "Save and continue editing".

.. _itp-stranding-curation:

Turtle Strandings
=================
Digitising a stranding record consists of five steps:

* Converting legacy files,
* creating the minimal Stranding record in WAStD, resulting in an auto-generated
  record identifier (record ID),
* renaming legacy files and the containing folder according to WAStD's record ID,
* uploading the files to WAStD, and
* extracting remaining information from the files into WAStD.

Convert legacy files
--------------------

Reports of Turtle Strandings typically arrive as a mixture of files, which
include:

* scanned data sheets,
* emails,
* photos.

Convert all original files to non-proprietary formats, such as PDF, images,
or plain text, separating duplicate information into a subfolder "duplicates".

Emails
^^^^^^
* Emails saved as Outlook *.msg*: open with Outlook (requires Windows OS),
  save attachments (data sheet, images) separately, then save email as plain text.
* Multiple emails: merge messages chronologically into one text file per email
  thread and redact content as follows:
* Delete footers unless they contain contact information
* Replace clearly off topic and personal sentences with ``[...]``. If in doubt, retain.
* Delete blank lines within emails.
* Insert three blank lines between emails.

Printed documents
^^^^^^^^^^^^^^^^^
* Paper forms: scan to PDF, make sure the quality is readable enough.
* Printed photos: scan to jpg, one file per photo.

Electronic documents
^^^^^^^^^^^^^^^^^^^^
* All documents need to be saved as txt (if plain text is sufficient) or PDF (if
  formatting is important).
* Save photos embedded in MS Word documents separately as jpg.

Photographs
^^^^^^^^^^^
* Switch on geotagging before taking phone pictures to include a GPS stamp in the
  image file metadata.
* Images: jpg are preferred.
* Resolution: Files larger than 1 MB should be resized to below 1 MB per image.

**Geek tip** To shrink images in Ubuntu, open terminal in folder and run on
**copies** of the large images with appropriate values for ``resize``::

    mogrify -resize 30% *.jpg

After this process, there should be present:

* One PDF of the strandings data sheet,
* one text file containing all communication (emails),
* all images separately,
* all other documents as PDF,
* legacy versions in subfolder "duplicates".

WAStD minimal record and identifier
-----------------------------------

* Create a `new AnimalEncounter <https://strandings.dpaw.wa.gov.au/admin/observations/animalencounter/add/>`_.
* **Observed at** refers to the location of the encounter with the animal.
* If written coordinates are supplied, click anywhere on map and enter given
  coordinates into the text field underneath the map widget.
  If locality names are supplied, look them up (e.g. pick
  "Place names" from the map widget's layer selector) and pick an
  approximate location on the location widget.
* Location precision: give your best estimate for the error inherent to the source of the location.
* Observer, reporter: Create users (if not existing) for observer and reporter.
  Use ``firstname_lastname`` as the username, assign a dummy password
  (they will never login using the password, only via DPaW SSO),
  and enter at least the full name and email - more if available.

Hit "Save and continue editing". This is the **minimal Encounter record**.

Fill in, as supplied, the fields in the "Animal" section and save.
This is the **minimal stranding record**.

WAStD will auto-generate an ID for the record from the metadata (
encounter date, lon, lat, animal health, maturity, and species) and populate
the *source ID* field with it.
This ID will be the link between paper forms, digital files and WAStD records.

Example source ID: ``2016-09-02-13-30-00-113-7242-22-496-dead-edible-adult-male-corolla-corolla-wa1234``

In the edge case of multiple strandings of animals of the same species, maturity
and health, this auto-generated source ID will not be unique, and WAStD will
show an error.
In this case, make the source ID unique by appending a running number (e.g. ``-1``).

Rename legacy files using WAStD record identifier
-------------------------------------------------
Now that we have a source ID, turn to the files for a moment.

Store the original files (scanned data sheets, pictures, emails)
in a new folder in a backed up location using WAStD's auto-generated source ID
to facilitate discoverability across storage media.
Rename each file with the source ID a prefix, plus a simple descriptive title, e.g.:

* ``M:/turtles/strandings/2016-09-02-13-30-00-113-7242-22-496-dead-edible-adult-male-corolla-corolla-wa1234/``,
  containing:
* ``2016-09-02-13-30-00-113-7242-22-496-dead-edible-adult-male-corolla-corolla-wa1234_datasheet.pdf``
* ``2016-09-02-13-30-00-113-7242-22-496-dead-edible-adult-male-corolla-corolla-wa1234_emails.txt``
* ``2016-09-02-13-30-00-113-7242-22-496-dead-edible-adult-male-corolla-corolla-wa1234_total_lateral.jpg``
* ``2016-09-02-13-30-00-113-7242-22-496-dead-edible-adult-male-corolla-corolla-wa1234_total_dorsal.jpg``
* ``2016-09-02-13-30-00-113-7242-22-496-dead-edible-adult-male-corolla-corolla-wa1234_head.jpg``

This naming convention will ensure that each file can be associated with the
corresponding record in WAStD even without the context of being attached to a
WAStD record, or being located in an appropriately named folder.

Upload files
------------
It is very important to rename the files **before** uploading them, in order to
preserve the new filename (containing the source ID) in the uploaded file name.

This is important, as downloaded files will only be identified by their filename.
If the filename does not uniquely link back to the online record, e.g. by
containing the source ID, the user risks losing its context.

Back in WAStD, attach all files - data sheet scan, communication records,
photographs - as Media Attachments to the Encounter, preferrably in this order.
Pick a descriptive, but short title for the files - the title will be displayed
in map popups, e.g.:

* datasheet
* emails
* photo total side
* photo total top
* photo head side

Information extraction
----------------------
Add subsequent sections if relevant information is given in the original
data sheet or communication records:

* Tag Observations
* Turtle Damage Observation
* Turtle Morphometric Observations
* Management Actions (e.g. disposal, samples sent)


Turtle Damage Observations also cater for tag scars and tags that were seen,
but not identified (e.g. the animal had to leave before the operator could read
the tag).

Tag Observations support the following identifying tags or "things with an ID":

* Flipper Tag
* PIT Tag
* Satellite Tag
* Data logger
* Temperature logger
* Blood Sample
* Biopsy Sample
* Egg Sample
* Physical Sample
* Other

Turtle Morphometric Observations
--------------------------------
The measurement accuracy is set based on informed guesses:

* If the datasheet was filled in by a trained vet or core turtle staff, it's to
  the nearest 1mm.
* If the datasheet specifies "measured", it's to the nearest 5mm.
* If the datasheet specifies "estimated", it's to the nearest value closest to
  10% of the measurement.

Tab Observations and Turtle Morphometric Observations have optional fields to
capture the "handler" and the "recorder", where the handler is the person
physically handling the tag or conducting the measurements, and the recorder
the person who writes the data sheet.
It is important to retain this information, as both activities bring their own
source of errors, which are often linked to the person's respective training or
handwriting.

After adding these data to the Encounter, save the Encounter (twice to update
the map popup) and refresh WAStD's home page to see a summary as popup on the
Encounter's place marker.

Updating an existing stranding record
-------------------------------------
Place the new files into the new case folders (named after WAStD's source ID for
that record) following above defined file standards. Prefix the filenames with
the source ID, then upload them to the corresponding record in WAStD.

Extract new information from the new files into WAStD, updating the AnimalEncounter
and related Observations as required.

If the inputs for the source ID change, delete the source ID, save the AnimalEncounter
to generate a new, correct source ID, then update the case folder name with
the new source ID. Lastly, rename and reupload all files to propagate the new source ID
into filenames and file URLs.
This extra step is extremely important to keep shared identifiers on files and
electronic records in sync.

Outcome
-------
* **Point of truth** is the record in WAStD, which is the most comprehensive and most
  accessible source of information related to a stranding.
* All information in WAStD that came from files requires these files to be
  in standard formats, following the source ID naming convention, and be uploaded
  precicely in the same version that is in the case folder.


Cetacean Strandings
===================
The data currently lives in another departmental Strandings database.

Cetacean Stranding data (rudimentary):

* Create a `new AnimalEncounter <https://strandings.dpaw.wa.gov.au/admin/observations/animalencounter/add/>`_.
* Media Attachments following instructions above
* CetaceanMorphometricObservation (TODO)
* CetaceanDagameObservation (TODO)

Turtle Tagging
==============
The data currently lives in WAMTRAM 2.

Turtle Tagging data:

* Create a `new AnimalEncounter <https://strandings.dpaw.wa.gov.au/admin/observations/animalencounter/add/>`_.
* Tag Observations: For each flipper, PIT and satellite tag; plus for each sample taken.
* Media Attachments: photos, data sheet.
* Distinguishing Feature Observation
* Turtle Damage Observation
* Turtle Morphometric Observations
* Turtle Nest Observations
* Management Actions

Tag returns
===========
When TOs harvest and eat a tagged turtle, they return the tags to the Department.

Tag Return data:

* Create a `new Encounter <https://strandings.dpaw.wa.gov.au/admin/observations/encounter/add/>`_.
* Add a TagObservation for the returned tag.

If the person returning the tag is not a departmental staff member, send them
a "thank you" email including the known history of the animal.

Turtle Tracks
=============
Track count production data are currently captured by the Ningaloo Turtle Program's Access database.

Turtle Track Tally data in WAStD:

* Create a `new (simple) Encounter <https://strandings.dpaw.wa.gov.au/admin/observations/encounter/add/>`_.
* Add a TrackTallyObservation for tallied numbers of tracks, nests etc.

For each nest with a GPS location:

* Create a `new Turtle Nest Encounter <https://strandings.dpaw.wa.gov.au/admin/observations/turtlenestencounter/add/>`_.
* Add a Turtle nest observation for the respective track or nest.
* The fields and available options mirror the datasheet.
* Add MediaAttachments for each photo.

**Note** Data collected with mobile apps are ingested automatically.

Temperature Loggers
===================
The following life cycle stages are supported for Hobo Temperature Loggers:

* programmed (with settings "start date" and "logging interval")
* dispatched (sent to a recipient)
* deployed, resighted, or retrieved (following datasheet)
* downloaded (with attached data files)

Create a `new LoggerEncounter <https://strandings.dpaw.wa.gov.au/admin/observations/loggerencounter/add/>`_:

* Observed at: location of encounter, even if programmed, dispatched or downloaded.
* Source ID: keep empty, will auto-generate on save.
* Type: Temperature Logger.
* Status: the life cycle status as per list above.
* Logger ID: serial number as per sticker on logger.
* If logger was programmed, add one "Temperature logger settings" section.
* If logger was dispatched, add one "Dispatch record" section.
* If logger was deployed, resighted, or retrieved, add one "Temperature logger deployment" section.
* If logger was downloaded, add one Media attachment for each downloaded file and attach the file.

====================
Data upload from ODK
====================
To upload data from ODK, a curator hits "Import ODKA" in WAStD's main menu.
This will automatically read all form definitions published on our own ODK Aggregate
server, retrieve all not yet downloaded form submissions, then ingest each into WAStD
using the Django ORM API. This code runs from inside WAStD's application code.

In future, this functionality will be exposed through WAStD's API, so that the data
ingest can be triggered from a scheduled cron-job.

A better way of ingesting data would be to have a nice writeable API in WAStD (coming soon), and
to ETL data from ODK-A to WAStD from an outside script.
Implementing this solution requires some more work on exposing WAStD's
mildly tricky data model (polymorphic inheritance) through the API (django-restframework).

The remaining section documents how data from digital data collection forms was ingested previously.
ODK forms are undergoing improvements, and therefore are versioned.

On the ODK Aggregate server, the administrator opens the "Submissions > Filter
submissios" tab and selects "Export" to "JSON". Under "Exported submissions",
the administrator downloads the JSON file (once ready).

Export files
============
On the ODK Aggregate server `https://dpaw-data.appspot.com/ <https://dpaw-data.appspot.com/>`_:

* Form Management > Forms List > for each form: Export > JSON
* Submissions > Exported Submissions > Download files.

Transfer the files via gateway server to prod::

  florianm@kens-awesome-001:~/projects/dpaw/wastd⟫ rsync -Pavvr data kens-xenmate-dev:/home/CORPORATEICT/florianm/wastd
  florianm@kens-xenmate-dev ~/wastd $ rsync -Pavvr data aws-eco-001:/mnt/projects/wastd

On the production server, run::

    fab shell
    from wastd.observations.utils import *

    import_odk("data/latest/Track_Tally_0_5_results.json", flavour="odk-tally05")
    #import_odk('data/latest/Track_or_Treat_0_26_results.json', flavour="odk-tt026")
    import_odk('data/latest/Track_or_Treat_0_31_results.json', flavour="odk-tt031")
    import_odk('data/latest/Track_or_Treat_0_35_results.json', flavour="odk-tt036")
    import_odk('data/latest/Track_or_Treat_0_36_results.json', flavour="odk-tt036")
    import_odk('data/latest/Fox_Sake_0_3_results.json', flavour="odk-fs03")


    # TODO:
    # MWI, TS 0.8, 0.9

This process contains three manual steps for each form,
which at the current churn rate of forms (and corresponding import routines)
is the most efficient solution.

The downloaded JSON files contain all data (excluding images, which are linked
via URLs) and provide an additional backup.


.. note:: Fun fact, one could download the JSON from ODK Aggregate directly to the production server,
  substituting the respective URL to the JSON export::
      export ODKUN="my-odk-username"
      export ODKPW="my-odk-password"

      curl -u $ODKUN:$ODKPW -o data/latest/tt036.json https://dpaw-data.appspot.com/view/...

  A better way might be to pursue reading the data from the ODK-A API, and writing to the WAStD API.
  This simplified process could be fully automated and run either on the prod server or locally.

=======
Data QA
=======
This section addresses QA operators, who have two jobs:

* Proofreading: compare data sheets to entered data
* Subject matter expertise: making sense of the data

Proofreading
============
A literate data QA operator can proofread data by simply comparing attached files
to the information present.
If errors are found, data can be updated - WAStD will retain the edit history.
Once the record is deemed "Proofread", the QA operator clicks the transition
"Proofread Encounter".
This step can be reverted by clicking the transition "Require Proofreading Encounter".
WAStD will keep track of each transition.

Curating data
=============
A subject matter expert can review records and e.g. confirm species identification.
Once the expert is satisfied that the record represents accurately the case as
evident from attached pictures, data sheet and communications records, the transition
"Curate Encounter" will mark the encounter as "curated".
The transition can be reversed with "Flag Encounter".

============
Data release
============
This section addresses data publishers, who authorise data release (mark records
as "publication ready") or embargo data (to prevent publication).

The transition "Publish Encounter" will mark the record as "published", but not
actually release information to the general public. The flag serves simply to
mark a record as "ready to publish".
This transition can be reversed with "Embargo Encounter", which will push the record
back to "curated".


Data QA for turtle track census
===============================
This section addresses the regional turtle monitoring program coordinators, who
conduct training and supervise volunteer data collection.

Data flow of surveys
--------------------
WAStD creates or updates (if existing) one
`Survey <https://strandings.dpaw.wa.gov.au/admin/observations/survey/>`_
for each recorded "Site Visit Start".
WAStD guesses the `Site <https://strandings.dpaw.wa.gov.au/admin/observations/area/?area_type__exact=Site>`_
from the Site Visit Start's Geolocation.
WAStD tries to find a corresponding "Site Visit End", or else sets the end time to 6 hours
after the start time, and leaves a note in the "comments at finish".

If the data collectors forgot to record a "Site Visit Start", the QA operator has to create
a new Survey with start and end time before and after the recorded Encounters (Track or Treat, Fox Sake).

When a Survey is saved, it finds all Encounters within its start and end time at the given Site
and links them to itself. This link can be seen in the Encounters' field "survey".

Since data collection unavoidably lossy and incomplete due to human error,
QA operators (coordinators) have to:

* Flag training surveys (to exclude their corresponding Encounters from analysis)
* Double-check reporter names to QA WAStD's automated name matching
* Populate "team" from "comments at start" (to allow estimating volunteer hours)
* QA "survey end time" and set to a realistic time where guessed (to allow estimating volunteer hours)

Flag training surveys
---------------------
Surveys can be marked as training surveys by unticking the "production" checkbox.
This allows to exclude training data from analysis.

Remember to "Save and continue editing", "proofread" and "curate" the record to
protect it from being overwritten with the original data.

Double-check reporter names
---------------------------
Filter the Survey list to each of your sites, compare "reported by" with "comments at start".
WAStD leaves QA messages. Surveys requiring QA will have a "NEEDS QA" remark.

QA Survey end time
------------------
The end time can be incorrect for two reasons:

* If the data collector forgot to capture a Site Visit End, WAStD will guess the end time.
* If WAStD's heuristic picked the wrong Site Visit End (likely in absence of the right one),
  the Survey's "end" fields will be populated, but likely wrong.

In the first case, WAStD leaves a "Needs QA" remark in the "Comments at finish" regarding "Survey end guessed",
try to set the end time to a more realistic time.

Where a Survey's ``device_id`` differs from ``end_device_id``, the data collectors either have
switched to the backup device, or WAStD has mismatched the Site Visit End.
Similarly, a different ``[guess_user]`` comment in the Survey's ``start_comments`` and ``end_comments``
can indicate a mismatch.

In the case of a mismatched Site Visit End, simply delete the incorrect information from the Survey's
``end_comments``, save and proofread. Set ``end time`` to a sensible time, ignore the end point.

Populate team
-------------
From "Comments at start" beginning after the [guess_user] QA message, the team is listed.
Excluding the "reporter", add all team members to the "team" field.

This in combination with an accurate Survey end time assists to accurately estimate
the volunteer hours (hours on ground times number of volunteers)
and survey effort (hours on ground).

**Note** Remember to "Save and continue editing", "proofread" and "curate"
each updated record to protect it from being overwritten with the original data.
It is not necessary to "proofread" and "curate" unchanged records.

Add missing surveys
-------------------
This currently is a job for the admin: Pivot Encounters without a survey by site and date
and extract earliest and latest Encounter. Buffer by a few minutes, extract Encounter's reporter,
and create missing surveys.

Add missing users
-----------------
If a person is not listed in the dropdown menus, you might need to
`add a User <https://strandings.dpaw.wa.gov.au/admin/users/user/add/>`_ for that person.
Use their ``firstname_lastname`` as username, select a password, save, then add the details.

WAStD will create a new user profile at first login for each DBCA staff member, but
the profile will miss the details