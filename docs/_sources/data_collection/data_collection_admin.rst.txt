.. _data-collection-admin:

==============================
Data collection administrators
==============================

This chapter provides all required knowledge for data collection admins.
The admins form a bridge between the ODK data maintainer (Florian Mayer)
and the data collectors (staff and volunteers).

Tasks covered:

* Getting started
* Set up tablets
* Provide training
* Prepare tablets for data collection
* Receive tablets after data collection

Admin: Getting started
======================
* Admin's computer: set Chrome or Firefox as default browser
* Bookmark TSC

Admin: Prepare field packs
==========================
For each team collecting data at the same time:

* One neoprene pouch containing:
* Two data collection tablets
* Two Micro USB cables to charge tablets
* One power bank (mobile battery) 20000mAh
* One wooden folding ruler with turtle track widths (min and max) marked in coloured tape
* One whiteboard
* One whiteboard marker
* Turtle track ID guide
* Predator track ID guide

Admin: Create offline background imagery
========================================
* Use QGIS 3.14 or higher
* Add ArcGIS Map Service as title "ESRI World Imagery" and with URL
  https://server.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer
* Add "High Resolution 30cm imagery" and zoom to target location (e.g. Thevenard Island)
* Change Project CRS to WGS84 (EPSG:4326)
* Open QGIS Processing Toolbox > Raster tools > Generate XYZ tiles (MBTiles)
* Run with settings:
  * Extent: draw on map
  * DPI 96
  * Zoom max 20, min 5. Figure out max zoom vs max avail zoom of ESRI imagery.
  * Format png
  * save to file (e.g. THV.mbtiles) with extension ``.mbtiles``
* Repeat for each program's location and distribute resulting files to local coordinators.

Example log:

  Algorithm 'Generate XYZ tiles (MBTiles)' starting…
  Input parameters:
  { 'BACKGROUND_COLOR' : QColor(0, 0, 0, 0), 'DPI' : 96,
  'EXTENT' : '113.488658367,114.279178912,-22.808838676,-21.702109913 [EPSG:4326]',
  'METATILESIZE' : 4, 'OUTPUT_FILE' : '/home/florianm/projects/GIS/NIN.mbtiles',
  'QUALITY' : 75, 'TILE_FORMAT' : 0, 'ZOOM_MAX' : 20, 'ZOOM_MIN' : 5 }


Admin: First time setup
=======================

These steps have to be run once per new tablet.
They are the minimum steps to provide a production ready data collection tablet.

Setup the tablet
----------------

* Start fully charged, plug into charger to lengthen screen timeout
* Language: English / Australia
* Wifi: do not use DBCA's Wongi, use guest.dbca.wa.gov.au
* Sign into a work-only Google account - all tablets handed out from turtle program are linked to wa.turtles@gmail.com.
  If you are not Florian Mayer, use your own work-only Google account.
* Skip restore from backup.
* Google services: untick "help improve..." options. Keep "Back up apps etc" and "Location services" option.
* Skip creating a Lenovo/Samsung account. The "Start using your new device" button is hidden under the keyboard. Press "Back" to minimize keyboard.
* Update Android apps if prompted and address any notifications.

Device settings:

* Date & time: Set time zone to AWST (GMT+08)
* Security: do not configure any screen lock (leave as is)

App settings:

* Camera: Open app, enable location capture, so that all photos are geo-referenced with
  the coordinates they were taken at. This turns the camera into a generic
  data collection form (image, time, location).
* Google Photos: open app, settings, auto-backup all photos in "high resolution" (about 2MP) to Google Photos.

Setup the tablet after a season
-------------------------------
This section is for administrators updating tablets for a new field season.

* Fully charge tablets
* Turn on tablets, apply all available system updates:

  * Settings > Software > Check for updates (or follow notifications).
  * There can be multiple big (>1GB, new Android version) and smaller (~200MB security patches) updates.
* Google Play: update all apps, ODK Collect first.
* Scan new QR code as and when instructed.
* Delete and re-create all home screen widgets.


Setup ODK Collect from QR code
------------------------------
Open ODK Collect. 2020 update: accept message to migrate forms to "private storage".

If you were provided with a QR code, you can speed up the ODK Collect setup.

* Settings (three dots top right) > Configure via QR code
  (if asked, grant ODK Collect required permissions to access camera)
* Update the username to a real name, e.g. "Florian Mayer".
* Get blank forms on each tablet. This both prepares the tablets for field work,
  and verifies username/password/server url.

Distribute offline background imagery
-------------------------------------
* You will be provided the background imagery files (extension ``.mbtiles``).
* Connect each tablet via USB, unlock screen, confirm dialogue to allow file transfer on tablet.
* Copy the mbtiles files into ``/Android/data/org.odk.collect.android/files/layers`` on each tablet.
* You can provide multiple mbtiles. Mind available disk space (16GB ish) vs mbtiles size
  (200-500MB each) vs storage for ODK records including media files (photos).
* Open ODK Collect, Fill blank form, hit any map symbol next to the forms, tap the layers button,
  select the correct reference layer (named after your location).

Providing training
==================
Run all data collectors through the chapter "Data collection training" until they
are competent and comfortable with the hardware and software.

Admin: Prepare devices pre survey
=================================
If the logistics allow, the admin handing out the Android device will execute the steps of
:ref:`dct-pre-survey` together with the data collector.

Admin: Prepare a length reference pre survey
============================================
For situations where the data collector is unsure of the turtle species causing a given turtle track,
the data collection form offers to take a picture of the track for later review and species identification.
Having a length reference in the photos helps the reviewer immensely with species identification.

A simple and cheap length reference for tricky turtle tracks
can be fabricated from a  foldable wooden rule (2m folding into 20cm segments),
marked with goloured duct tape ($5 per roll) at the minimum and maximum track width
for each turtle species expected to occur in the surveyed area.

Tomato stick prototype:

.. image:: https://photos.app.goo.gl/lc6kjZMTrPlpjCoG3
    :target: https://photos.app.goo.gl/lc6kjZMTrPlpjCoG3
    :alt: Turtle track length reference

The reference can be simplified, e.g. if only green and flatback turtles are expected,
a stick can be cut to the maximum flatback track width, with one marking for the
minimum green track width.

Additional length markings, e.g. intervals of 10cm, can be added as required.

This method is preferred over the use of a measuring tape as length reference in
photos of tracks of unknown species for the following reasons:

* A rigid rule will lay on top of sand ripples,
  while measuring tape will distort measurement by bending over them.
* The coloured, centimeter-wide markings on the rule will be visible at lower image quality
  than the millimeter-wide centimeter markings on a measuring tape.
* The coloured tape wraps around the rule and is thereby visible from any angle,
  while tape can flip over and hide its markings.
* By reducing length references to relevant lengths, cognitive load is taken off the data collector.
  One can simply read off the markings which species' track width range a given track falls into.

Prepare one length reference per data collection team.

Collector: Collect data
=======================
Now the data collector will head out into the field and collect data following
the protocols from the "Data collection training" chapter.
The admin should be intimately acquainted with this chapter.

Admin: Review data
==================
**Note** In 2018, we have configured ODK Collect to never leave forms unfinalized,
so this section applies up to season 2017-18.

"Edit Saved Form" lists all unfinalized forms pending review and species / nest ID:

* Tap once to view read-only, tap again to edit
* review and update data (e.g. species ID)
* mark as finalized and save.

Delete unwanted repeating groups:

* Tap and hold a group title bar, select "delete".

TODO error "form not existing" - notify admin (Florian) to re-enable missing forms in ODK Aggregate,
get blank form, then saved form is editable and uploadable again.

If GPS point is missing, record GPS (which will be incorrect), note record datetime and other details, let form upload,
let data import into WAStD, find record again (based on datetime and details), update location as appropriate.
Mark record as "proofread".

Admin: Upload data
==================
When surveys are done in locations where the device can return to the comforts
of WiFi and power points daily, data can be uploaded directly to the clearinghouse.

* Settings: the correct username and password have been configured during device setup.
* Turn on the WiFi hotspot or move into WiFi range.
* Turn on the device's WiFi.

With "Auto-send in WiFi" settings enabled, the device will automatically upload
all data marked as "finalized".
This will leave all non-finalised forms requiring review in "Edit Saved Forms".
Review each form and "save as finalized".

When WiFi is not available daily, the admin needs to backup data by downloading
it manually and keeping the downloaded data safe (multiple copies over separate
storage media). With the mobile device connected and "MTP file transfer" enabled,
ODK data is located in either internal or SD storage in ``odk/instances``.
Each form will be stored in a separate folder, containing both the filled in form
as XML file, and all related pictures and media.

Simplest backup: periodically take a copy of ``odk/instances``.
If data upload works at the end, no further steps have to be taken and the copy of
``odk/instances`` can be archived.

Where's the data now?
=====================
ODK Collect uploads data to the specified ODK Aggregate clearinghouse.
In our case, we run ODK Aggregate at
`https://dpaw-data.appspot.com/ <https://dpaw-data.appspot.com/>`_.

A synchronised copy of the data is streamed to Google Fusion Tables (GFT)
for immediate visualization.
A confidential link is shared with admins on request.
DBCA staff can find the links to the data
`here <https://confluence.dpaw.wa.gov.au/display/MSIM/ODK+data+views>`_.

After each field trip, data from ODK Aggregate are exported (as JSON) and ingested into WAStD by the maintainer (FM).
The process can be repeated; data that has been changed in WAStD and
marked as "proofread" or even "curated" will not be overwritten.

Once data are marked as "proofread" (or higher levels of QA) in WAStD,
WAStD becomes the point of truth, as proofreading and curation (e.g.
double-checking species ID based on submitted photos) can change the data compared to the initial submission on ODK Aggregate.

Once data is ingested into WAStD, it is visible and accessible to DPaW staff at
`https://strandings.dpaw.wa.gov.au/ <https://strandings.dpaw.wa.gov.au/>`_.
See chapter "Data consumers" for working examples.

The final analysis consumes curated data through the WAStD API using the R package
``wastdR``. Working examples can be found at the
`wastdr documentation <https://parksandwildlife.github.io/wastdr/index.html>`_.

Admin: Update forms
===================
From time to time the forms might be updated.
In this case, all data collection admins (and volunteers using their private devices) will be notified,
and each of their tablets need to run through the following steps:

* ODK Collect > Get blank form > (the new forms should already be selected, e.g. Track or Treat 0.36) > Get selected forms
* ODK Collect > Delete saved form > Blank forms > select the old form (e.g. Track or Treat 0.35) > delete
* Once all tablets are updated, notify the maintainer (Florian Mayer).
* Once all devices are updated, the old form version can be retired.

Admin: Form versions and change log
===================================
Always use the latest available version of a form.
Some older forms may be available for download - this is to allow import to WAStD.

Process to upgrade:

* Send all unsent saved forms
* Delete saved form > both Saved forms / Blank forms: Delete all
* Get blank form > get latest version of each form

Site Visit Start
----------------
* 0.3 (2018-08-01) Capture team
* 0.2 (2017-11-16) Auto-capture device ID

Site Visit End
--------------
* 0.2 (2017-11-16) Auto-capture device ID

Turtle Track or Nest / "Track or Treat"
---------------------------------------
* 0.54 Renamed ToT 0.53 to clarify its purpose. Re-worded the nest tag section.
* 0.53 Add predator "cat"
* 0.52
* 0.51 (2018-01-29) Bug fix: cloud cover now includes 0 (clear sky)
* 0.50 (2018-01-27) Add informative prompts for missing required fields, simplify bearing measurements (hand-held compass only)
* 0.49 (2018-01-18)
* 0.47 (2017-12-05)
* 0.46 (2017-12-01)
* 0.45 (2017-11-19)
* 0.44 (2017-10-31) Add fan angles (early version)

Turtle Tagging
--------------
* 0.3 (2018-01-29) Manual location capture uses map widget (needs to be online to show background maps)
* 0.2 (2018-01-29) Allow capturing location as "here" or manual entry (if not on site) - animal first encountered at, nest location


Predator or Disturbance / "Fox Sake"
------------------------------------
* Predator or Dustirbance 1.0 - renamed FS0.4 to make form name more palatable to a broader audience.
* 0.4 Add predator "cat"
* 0.3

Marine Wildlife Incident
------------------------
* 0.6 (2018-01-29) Allow capturing location as "here" or manual entry (if not on site)



