==========
Data entry
==========
Current POC data model has the concept of an AnimalEncounter, during which
different kinds of observations are made. The kind of observations depend
on the species and health/behaviour of the animal - e.g. "dead and not doing much else"
is a Stranding Observation (morphometrics, tags, photos, damage, disposal, biopsy,
necropsy), while "alive and nesting" is a Tagging Observation (morphometrics,
tags, photos, damage, nest, eggs).


The following sections will

* link to example data sheets of all supported formats, and
* for each format, map the fields of the paper form to the online form.


Turtle Strandings
=================
For each data entry, first convert all files to non-proprietary formats, such as
PDF, images, or plain text.

* Emails saved as Outlook msg: open with Outlook, save as plain text.
* Paper forms: scan to PDF, make sure the quality is readable enough.
* Images: jpg, png are preferred. Insane resolutions (file sizes far above 2 MB) should be resized.
* Photos embedded in MS Word documents: save separately as jpg or png.
* MS Word documents: save as PDF.

Create users if not existing for observer and reporter. Assign a dummy password
(they will never login using the password, only via DPaW SSO), enter at least
name and email.

Then, `create a new AnimalEncounter <https://strandings-test.dpaw.wa.gov.au/admin/observations/animalencounter/add/>`_.

* Observed at: if written coordinates are supplied, click anywhere on map and enter given
  coordinates into the text field underneath the map widget.
  If locality names are supplied, look them up on Google Maps and pick an
  approximate location on the location widget.
* Location accuracy: give your best estimate for the accuracy.
* Observer, reporter: users must exist in the system.

Hit "Save and continue editing". This is the minimal Encounter record.

Fill in, as supplied, the fields in the "Animal" section and save. This is the
minimal useful stranding record.

Add subsequent sections as available in the original data sheet or communication
records.

Attach all files - data sheet scan, communication records, stranding form - as
Media Attachments preferrably in this order. Pick a descriptive, but short title
for the files - the title will be displayed in map popups.


Cetacean Strandings
===================
The data currently lives in another departmental Strandings database.

AnimalEncounter + CetaceanMorphometricObservation + CetaceanDagameObservation etc.

Turtle Tagging
==============
The data currently lives in WAMTRAM 2.

AnimalEncounter + TagObservation + MediaAttachment (datasheet PDFs) + etc.

Tag returns
===========
When TOs harvest and eat a tagged turtle, they return the
tags to the Department.

Encounter + TagObservation.

Turtle Tracks
=============
Track count is captured by the Ningaloo Turtle Program's
Access database.

Encounter + TrackTallyObservation

=======
Data QA
=======
Talking points:

* Proofreading: compare data sheets to entered data
* Subject matter experts: making sense of the data (and determining which data don't)

============
Data release
============
Marking data as "publication ready"
