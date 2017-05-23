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

The following sections will instruct data curators how to enter data from
supported data sources into WAStD.

.. * link to example data sheets of all supported formats, and
.. * for each format, map the fields of the paper form to the online form.


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
This section documents how to ingest data from digital data collection forms.
ODK forms are undergoing improvements, and therefore are versioned.

On the ODK Aggregate server, the administrator opens the "Submissions > Filter
submissios" tab and selects "Export" to "JSON". Under "Exported submissions",
the administrator downloads the JSON file (once ready).

On the production server, the application maintainer transfers the downloaded
JSON file to the "wastd/data" folder and runs::

    fab shell
    from wastd.observations.utils import *
    import_odk('data/TrackCount_0_10_results.json', flavour="odk-tc010")
    import_odk('data/Track_or_Treat_0_26_results.json', flavour="odk-tt026")
    import_odk('data/Track_or_Treat_0_31_results.json', flavour="odk-tt031")

This process contains three manual steps for each form,
which at the current churn rate of forms (and corresponding import routines)
is the most efficient solution.

The downloaded JSON files contain all data (excluding images, which are linked
via URLs) and provide an additional backup.

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
