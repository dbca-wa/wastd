.. _data-entry:
**********
Data entry
**********
This chapter addresses data curators, who enter, proofread and curate data from sources like paper datasheets and email.

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
supported data sources into WAStD.

.. * link to example data sheets of all supported formats, and
.. * for each format, map the fields of the paper form to the online form.


.. _itp-campaigns:
Campaigns
=========
The bulk of data is captured in electronic forms using ODK and imported into WAStD on an automated schedule.

To allocate data ownership and visibility to users of participating organisations,
Surveys and Encounters are associated with an overarching Campaign.

A Campaign represents a contiguous set of Surveys instigated by one Organisation (DBCA or external partners).

Campaigns have to be created manually in WAStD as follows:

Find Campaign corner dates
--------------------------
* In the Turtle Data Dashboard, find the "Surveys" tab.
* Select a Locality. This is the Campaign destination.
* In the "Surveys" tab, review the calendar heatmap and the season overview.
* Find the first and last dates of each contiguous set of Surveys.
  
  * E.g., for summer nesters (most of NWS shelf), the Campaigns will run in Oct - Dec and return Jan - Feb.
  * If no other Organisation has conducted Surveys in the Christmas break, you can use something like 1 Oct to 1 Mar as corner dates.
  * Any targeted trips, e.g. winter nesters in Aug, become their own Campaign.

Create a Campaign
-----------------
* In the WAStD Data Curation Portal, under "Places, Campaigns, Surveys", find Campaigns.
* Create a new Campaign by either of:

  * From the "Site Administration" overview, click on the <kbd>+</kbd> button, or
  * From the Campaign list view, click "Add Campaign", or
  * From a Campaign detail view, click "Save and add another" (warning this will take a few minutes).
* Enter mandatory details:

  * Destination: Locality.
  * Campaign start and end: Corner dates, can be buffered by a day to ensure complete overlap. Set time to 00:00.
  * Owner: The Organisation that created the Campaign.
  * Viewers: The list of organisations that are allowed to see the Campaign.
* Enter optional details:

  * Team: If available, you can add the list of volunteers to the Campaign. This can help matching observer names to WAStD Users.
  * Media attachments: If available, the scanned PDFs of datasheets, any available documentation relevant to data, volunteer lists, etc.
* Save the Campaign. This will take a few minutes while the Campaign adopts all Surveys and Encounters within.


.. _itp-tracks-curation:
Turtle Tracks or Nests
======================
If data is not captured via the digital forms, it is still possible to enter data manually.

With data curator access, open the `Data curation portal <https://wastd.dbca.wa.gov.au/admin/>`_
and `add a new TurtleNestEncounter <https://wastd.dbca.wa.gov.au/admin/observations/turtlenestencounter/add/>`_.

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

.. _itp-tracks-backfill:

Backfill Tracks from Paper (Track Tally)
========================================

Some field trips were confused between capturing data on paper or digitally.
These may have paper records of tracks which need to be backfilled into WAStD.

Since the paper datasheets did not record coordinates for individual tracks,
we consider missed tracks during tagging and morning tracks from after tagging as one TrackTally
and backfill these Track Tallies as LineTransectEncounters with TrackTallyObservations and MediaAttachments in WAStD.

Protocol:

Scan paper datasheets
---------------------

* Find paper records for one day. These might contain:

  * Track count datasheets for missed tracks during night tagging.
  * Track count datasheets for morning surveys (missed tracks after night tagging).
  * Datasheets for night tagging - ignored here as we only backfill tracks.
* Determine whether the paper record has already been entered (digitally or typed in by hand):

  * Review plain Encounters for that night at that location, e.g.
    `Encounters at Delambre in 2017 <https://wastd.dbca.wa.gov.au/admin/observations/encounter/?area__id__exact=143&when__year=2017>`_ shows only December records from 2017-12-09 onwards.
  * Review Surveys, e.g. `Surveys DEL 2017 <https://wastd.dbca.wa.gov.au/admin/observations/survey/?area__id__exact=143&start_time__year=2017>`_
* If you are sure that no data has been entered yet, continue and scan all paper datasheets:

  * Sort Track counts first, tagging sheets last in each day's batch of datasheets.
  * Using the printer/scanner's batch input slot, scan all datasheets back and front for that day into a single PDF.
  * Once transferred to your local computer, rename the PDFs as ``YYYY-MM-DD_datasheets.pdf``.

Summarise Tracks into TrackTallies
----------------------------------

* With the TrackTally paper datasheet in hand or on screen, 
  fill in a new TrackTally paper datasheet by going through the original datasheets.
  
  * Mark the sheet clearly as "Summary of original datasheets".
  * This step will be the most time-intensive and error-prone step in the process.
  * Take the time and diligence to make sure the individual tracks are correctly tallied up.
  * Be aware that some tracks on the original paper datasheets are marked up as tallies of several tracks,
    or are annotated on the side.

Create WAStD LineTransectEncounters from TrackTallies
-----------------------------------------------------

* Next, backfill the TrackTally as a
  `new LineTransectEncounter <https://wastd.dbca.wa.gov.au/admin/observations/linetransectencounter/add/>`_:

  * ``Area`` (Locality), ``Site``, ``Survey``: leave blank, they will be auto-filled. 
    Locality and Site will be inferred from the Transect. The Survey will be reconstructed later and linked automatically.
  * ``Observed at``: select one point within the surveyed site.
    E.g. for Delambre ``{"type":"Point","coordinates":[117.07911,-20.460469]}``
  * ``Location accuracy``: GPS.
  * ``Loc accuracy in metres``: 10.
  * ``Observed on``: click current date, then change the date (by then in correct formatting) to the desired date. Use calendar date.
    E.g. for the virtual TrackTally after the night of 27-28/11/2017, it's the calendar date of the morning after, 28/11/2017.
    E.g. ``28/11/2017`` with time ``06:00``.
  * ``Observed by``: Use the field leader's name. 
  * ``Data source``: leave at "Direct entry".
  * ``Source ID``: leave blank, will be auto-filled.
  * ``Transect line``: Capture one good track tally geotrace and re-use in other LTE. In layers, turn on WAStD Sites.
    Draw a line along the surveyed coastline staying on the sandy bits as far as possible.
    E.g. for Delambre: ``{"type":"LineString","coordinates":[[117.079024,-20.460389],[117.077157,-20.463284],[117.074883,-20.46646],[117.072737,-20.461113],[117.072179,-20.458439],[117.071943,-20.457072]]}``
  * You can ``Save and continue editing`` whenever you want, but only really need to do so once at the end.
  * Add the number of required TrackTallyObservations, one for each tally number, 
      via ``Add another Turtle Track Tally Observation``.
  * For each TrackTallyObservation, fill in the following fields:

    * ``Data source``: Leave at ``Direct entry``.
    * ``Source ID``: Leave the auto-generated ID, but append a running number, e.g. ``1``, ``2``, ``3``, etc. to create unique IDs.
      The system generates the same ID for multiple TrackTallyObservations if added without a ``Save and continue editing``.
      Since we only need a unique ID, but don't enforce format or length, we can simply add a running number to generate a unique ID.
    * ``Species``: set as required.
    * ``Age``: Fresh for tracks with and without nest, or Old for hatched nests and anything without a track.
    * ``Type``: either ``track with nest`` or ``track without nest``, ``hatched nest``.
    * ``Tally``: number of tracks for given species and track type.
  * Hit ``Save and continue editing`` and review the record.
    
    * ``Area`` and ``Site`` should be set now.
    * ``Survey`` can still be blank. We will reconstruct them later.
    * The maps should show ``Observed at`` point and ``Transect line`` at correct sites.
    * The datasheet photo should preview in the MediaAttachments; filename and content should match the ``Observed on`` date and TrackTallies.
  * When done backfilling this TrackTally, hit ``Save and add another`` to add another TrackTally.
  * When done backfilling all TrackTallies, as admin run "Curators > Reconstruct missing surveys" from the WAStD front page.
    This will reconstruct surveys and link the TrackTallies (LineTransectEncounters) to its respective survey.

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

Cetacean Stranding data (if they were entered into WAStD):

* Create a `new AnimalEncounter <https://strandings.dpaw.wa.gov.au/admin/observations/animalencounter/add/>`_.
* Media Attachments following instructions above
* CetaceanMorphometricObservation (TODO)
* CetaceanDagameObservation (TODO)

Turtle Tagging
==============
The production data currently live in WAMTRAM 2. Migration is underway.

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


Data upload from ODK
====================
WAStD still supports the import of electronically captured data from ODK Aggregate.

All electronically captured data from the newer ODK Central are imported in a scripted
and automated process using the R package `etlTurtleNesting <https://github.com/dbca-wa/etlTurtleNesting>`_.
All data flow through the WAStD API.
