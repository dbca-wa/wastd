.. _data-collection-admini:

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

Admin: First time setup
=======================

These steps have to be run once per new tablet.
They are the minimum steps to provide a production ready data collection tablet.

Setup the tablet
----------------

* Start fully charged, plug into charger to lengthen screen timeout
* Language: English / Australia
* Wifi: do not use DBCA's Wongi, use guest.dbca.wa.gov.au
* Sign into a work-only Google account - all tablets handed out from turtle program are linked to florianm.dec@gmail.com.
  If you are not Florian Mayer, use your own work-only Google account.
* If you have other tablets already set up and linked against your Google account, let the tablet restore from backup (installs apps).
* Google services: untick "help improve..." options. Keep "Back up apps etc" and "Location services" option.
* Wait for restore to finish.
* Skip creating a Lenovo ID. The "Start using your new device" button is hidden under the keyboard. Press "Back" to minimize keyboard.
* Update Android apps if prompted and address any notifications.

Device settings:

* Date & time: Set time zone to AWST (GMT+08)
* Security: do not configure any screen lock (leave as is)

App settings:

* Camera: Enable location capture, so that all photos are geo-referenced with
  the coordinates they were taken at. This turns the camera into a generic
  data collection form (image, time, location).
* Google Photos: auto-backup all photos in original resolution to Google Photos.


Setup ODK Collect from QR code
------------------------------
If you were provided with a QR code, you can speed up the ODK Collect setup.

* Settings > Admin settings > Import/Export settings > Scan code from other device > Scan provided QR code
  (if asked, grant ODK Collect required permissions to access camera)
* If you were provided with one QR code (e.g. for ODK Aggregate username Murujuga1) for a range of tablets
  (with usernames Murujuga2 through Murujuga8), set the ODK Aggregate username as follows:

  * Settings > General settings > Server > Username > Change the trailing number (e.g. 1)
    to create the other usernames (e.g. 2 through 8).
  * Every tablet must have a separate ODK Aggregate username.
  * Label the tablets (e.g. gaffa tape on the back) with the username to easily identify them,
    e.g. when asking Florian for support.

* Get blank forms on each tablet. This both prepares the tablets for field work,
  and verifies username/password/server url.

Setup ODK Collect from scratch
------------------------------

These steps have to be run once by the admin per device while online.
Less than 10 MB will be downloaded.
These steps can also be run by an interested data collector on their own Android
device.

Requirements:

* An Android device
* A valid username and password for https://dpaw-data.appspot.com as provided to you by Florian Mayer.
  The username and password will be per tablet, not per data collector.

* On your Android device, install
  `ODK Collect <https://play.google.com/store/apps/details?id=org.odk.collect.android>`_
* Drop a shortcut to ODK Collect onto the home screen.
* In ODK Collect > Settings (three dots top or bottom right) > General Settings > Server >

  * URL: https://dpaw-data.appspot.com
  * username and password as provided to you by the ODK data maintainer.

  These credentials determine whether you can retrieve new
  forms and submit data, and the username will be automatically recorded when
  collecting data. It is crucial to spell the credentials exactly as provided.
* Form management:
  * Form update: check every hour for form updates,
    automatic download of updated versions, hide old versions.
  * Auto send: "WiFi only"
  * Delete after send: yes
* User and device identity > Form metadata > Username: set to the data collector's username.
  This name will be automatically recorded in ODK forms as "observed by".
* ODK Collect > Settings > Admin settings > User settings: de-select all but "Form metadata".
* ODK Collect > Settings > Admin settings > Admin password: set and remember.

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

Track or Treat
--------------
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


Fox Sake
--------
* 0.4 Add predator "cat"
* 0.3

Marine Wildlife Incident
------------------------
* 0.6 (2018-01-29) Allow capturing location as "here" or manual entry (if not on site)



