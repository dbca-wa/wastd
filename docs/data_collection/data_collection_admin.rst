==============================
Data collection administrators
==============================

This chapter provides all required knowledge for data collection admins.
The admins form a bridge between the ODK data maintainer (Florian Mayer) 
and the data collectors (staff and volunteers).

Tasks covered:

* Set up tablets
* Provide training
* Prepare tablets for data collection
* Receive tablets after data collection

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
* Update apps and address any notifications.

Device settings:

* Date & time: Set time zone to AWST (GMT+08)
* Security: do not configure any screen lock

App settings:

* Camera: Enable location capture, so that all photos are geo-referenced with
  the coordinates they were taken at. This turns the camera into a generic 
  data collection form (image, time, location).
* Google Photos: auto-upload all photos in original resolution to Google Photos.

If not linked to florianm.dec@gmail.com, install apps:

* ODK Collect


Setup ODK Collect
-----------------

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
  * Auto send: "WiFi only" if few data points are collected.
    Disable for vigorous data collection in remote areas with limited bandwidth 
    provided by WiFi hotspots - don't swamp the WiFi hotspot by auto-uploading data with photos.
  * Delete after send: yes.
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
Take a garden stake (length 1.50 m) and mark minimum and maximum track width of 
expected species with coloured tape. Prepare one stake per tablet.

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
ODK Collect uploads data to the configured ODK Aggregate clearinghouse.
In our case, this is https://dpaw-data.appspot.com/.
Data collectors will have received credentials to login, which are the credentials
to be used in ODK Collect.

A synchronised copy of the data is streamed to Google Fusion Tables (GFT)
for immediate visualization. A confidential link is shared with admins on request.

After each field trip, data from ODK Aggregate are exported (as JSON) and ingested
into WAStD by the maintainer (FM). 
The process can be repeated; data that has been changed in WAStD and
marked as "proofread" or even "curated" will not be overwritten.

Once data are marked as "proofread" (or higher levels of QA) in WAStD,
WAStD becomes the point of truth, as proofreading and curation (e.g.
double-checking species ID based on submitted photos) can change the data compared
to the initial submission on ODK Aggregate.

Once data is ingested into WAStD, it is visible and accessible to DPaW staff at
`https://strandings.dpaw.wa.gov.au/ <https://strandings.dpaw.wa.gov.au/>`_. 
See chapter "Data consumers" for working examples.

The final analysis consumes curated data through the WAStD API using the R package ``wastdR``.
