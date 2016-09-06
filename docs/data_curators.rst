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

* Emails saved as Outlook *.msg*: open with Outlook (requires Windows OS),
  save attachments (data sheet, images) separately, then save email as plain text.
* Multiple emails: merge messages chronologically into one text file.
* Paper forms: scan to PDF, make sure the quality is readable enough.
* Images: jpg, png are preferred. Insane resolutions (file sizes far above 2 MB)
  should be resized to below 1 MB per image.
* Photos embedded in MS Word documents: save separately as jpg or png.
* MS Word documents: save as PDF.

After this process, there should be present:

* One PDF of the strandings data sheet,
* one text file containing all communication (emails),
* all images separately,
* all other documents as PDF,
* legacy versions in subfolder "duplicates".

WAStD minimal record and identifier
-----------------------------------
Create a new `AnimalEncounter <https://strandings-test.dpaw.wa.gov.au/admin/observations/animalencounter/add/>`_.

* **Observed at** refers to the location of the encounter with the animal.
* If written coordinates are supplied, click anywhere on map and enter given
  coordinates into the text field underneath the map widget.
  If locality names are supplied, look them up (e.g on Google Maps) and pick an
  approximate location on the location widget.
* Location accuracy: give your best estimate for the accuracy.
* Observer, reporter: Create users (if not existing) for observer and reporter.
  Use ``firstname_lastname`` as the username, assign a dummy password
  (they will never login using the password, only via DPaW SSO),
  and enter at least the full name and email - more if available.

Hit "Save and continue editing". This is the **minimal Encounter record**.

Fill in, as supplied, the fields in the "Animal" section and save. This is the
**minimal stranding record**.

WAStD will auto-generate a record ID for the record from the metadata (
encounter date, lon, lat, animal health, maturity, and species) and populate
the *source ID* field with it. This ID will be the link between paper forms,
digital files and WAStD records.

Example record ID: ``2016-09-02-113-7242-22-496-dead-edible-adult-corolla-corolla``

In the edge case of multiple strandings of animals of the same species, maturity
and health, this auto-generated source ID will not be unique, and WAStD will
show an error.
In this case, make the source ID unique by appending a running number (e.g. ``-1``).

Rename legacy files using WAStD record identifier
-------------------------------------------------
Now that we have a record ID, turn to the files for a moment.

Store the original files (scanned data sheets, pictures, emails)
in a new folder in a backed up location using WAStD's auto-generated source ID
to facilitate discoverability across storage media.
Rename each file with the source ID a prefix, plus a simple descriptive title, e.g.:

* ``M:/turtles/strandings/2016-09-02-113-7242-22-496-dead-edible-adult-corolla-corolla/``,
  containing:
* ``2016-09-02-113-7242-22-496-dead-edible-adult-corolla-corolla_datasheet.pdf``
* ``2016-09-02-113-7242-22-496-dead-edible-adult-corolla-corolla_emails.txt``
* ``2016-09-02-113-7242-22-496-dead-edible-adult-corolla-corolla_photo_total_side.txt``
* ``2016-09-02-113-7242-22-496-dead-edible-adult-corolla-corolla_photo_total_top.txt``
* ``2016-09-02-113-7242-22-496-dead-edible-adult-corolla-corolla_photo_head_side.txt``

This naming convention will ensure that each file can be associated with the
corresponding record in WAStD even without the context of being attached to a
WAStD record, or being located in an appropriately named folder.

Upload files
------------
It is very important to rename the files **before** uploading them, in order to
preserve the new filename (containing the record ID) in the uploaded file name.

Back in WAStD, attach all files - data sheet scan, communication records,
stranding form - as Media Attachments to the Encounter, preferrably in this order.
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

* Distinguishing Feature Observation
* Turtle Damage Observation
* Turtle Morphometric Observations
* Management Actions
* Tag Observations

Turtle Damage Observations also cater for tag scars and tags that were seen,
but not identified (e.g. the animal had to leave before the operator could read
the tag).

Tag Observations support the following identifying tags or "things with an ID":

* Flipper Tag
* PIT Tag
* Satellite Tag
* Blood Sample
* Biopsy Sample
* Egg Sample
* Physical Sample
* Whister ID
* Other

After adding these data to the Encounter, save the Encounter and refresh WAStD's
home page to see a summary as popup on the Encounter's place marker.


Cetacean Strandings
===================
The data currently lives in another departmental Strandings database.

Cetacean Stranding data:

* AnimalEncounter following instructions above
* Media Attachments following instructions above
* CetaceanMorphometricObservation (TODO)
* CetaceanDagameObservation (TODO)

Turtle Tagging
==============
The data currently lives in WAMTRAM 2.

Turtle Tagging data:

* AnimalEncounter
* Media Attachments
* Distinguishing Feature Observation
* Turtle Damage Observation
* Turtle Morphometric Observations
* Turtle Nest Observations
* Management Actions
* Tag Observations

Tag returns
===========
When TOs harvest and eat a tagged turtle, they return the
tags to the Department.

Tag Return data:

* Encounter
* TagObservation

Turtle Tracks
=============
Track count is captured by the Ningaloo Turtle Program's
Access database.

Turtle Track data:

* Encounter
* TrackTallyObservation (TODO)

=======
Data QA
=======
This section addresses QA operators, who have two jobs:

* Proofreading: compare data sheets to entered data
* Subject matter expertise: making sense of the data

============
Data release
============
This section addresses data publishers, who authorise data release (mark records
as "publication ready") or embargo data (to prevent publication).
