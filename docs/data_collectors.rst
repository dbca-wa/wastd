===============
Data collectors
===============

Each field in the data sheets should be questioned:

* Is this information used in any of the analytical outputs?
* Does this information serve any QA purpose?
* Is this information used to derive other information, e.g. deformities being
  used to identify an animal identity?
* Will anyone in the future require this information?

Turtle tracks or nests
======================
Turtle track counts can be collected on mobile apps (OpenDataKit or ESRI collector),
or on paper data sheets.

Track counts can be recorded individually (preferred) or tallied over beach sections.

Track counts can be done in two methodologies:

* *Uptrack* counts: walking in a straight line along the high water mark, only
  inbound tracks (uptracks) are counted as "tracks with success not assessed".
  The tracks are not followed. Except for the first day, only fresh (younger
  than 24h) tracks are recorded.
* *Nest* counts: walking in a straight line along the high water mark, each
  uptrack is followed to its apex, where the presence or absence of a nest
  determines the type of track (false crawl without nest, successful crawl with
  nest, unknown if unclear whether nest exists). If evident, nest disturbance is
  recorded as well.

Mobile data collection using Open Data Kit
------------------------------------------

First time setup
^^^^^^^^^^^^^^^^
These steps have to be run once per device while online. Less than 10 MB will be
downloaded.

* On your Android device, install
  `ODK Collect <https://play.google.com/store/apps/details?id=org.odk.collect.android>`_
* In ODK Collect > General Settings > Server Settings > Configure platform settings:
* URL: https://dpaw-data.appspot.com, plus username and password as provided to
  you by the ODK admin. These credentials determine whether you can retrieve new
  forms and submit data.
* In ODK Collect > General Settings > Username / Password: your credentials again.
  These credentials can be different from the credentials in Server Settings,
  and they will be used to automatically set the reporter in the forms.
* Auto send: "only with Wifi" if few data points are collected. Disable for vigorous
  data collection in remote areas with limited Wifi - don't swamp the Wifi hotspot
  by auto-uploading data with photos.
* Default to finalized
* Delete after send
* If the device is used by many volunteers who are new to the software, enable
  the "Admin Settings" (set password) and disable menu options that are not needed
  or risk data loss (delete forms).


**Note** You **must not** share your credentials, and
**always use your own credentials** in General Settings > Username/Password
to collect data. Failure to do so will result in data loss, data corruption and
loss of attribution.


Prepare to collect data
^^^^^^^^^^^^^^^^^^^^^^^
These steps have to be run at least before each field trip while online,
and verified before each survey. Less than 1 MB will be downloaded.

* **Form** Make sure you've got the latest Track count form:
  In ODK Collect, "Get Blank Form", select the latest TrackCount form and "Get Selected".
  The form should not change during the field trip.
* **Credentials** Set your ODK credentials for the respective ODK Aggregate server,
  e.g. https://dpaw-data.appspot.com/ before collecting data.
  Setting the credentials (username, password) can be done while offline.
* **Battery** Make sure the battery is full before you head out.
  Screen and GPS are hungry hippos.

Collect "uptrack" data
^^^^^^^^^^^^^^^^^^^^^^

* Walk along the high water mark of the beach, record each (day 1) or each fresh
  (after day 1) uptrack as follows.
* "Fill Blank Form" > Track Count (latest version) > swipe right.
* Fill in the first screen with following fields:
* Track age: fresh (default) or old.
  No interaction required on "fresh tracks only" surveys after day 1.
* Species: keep default "turtle"  if unsure of species ID, else select species.
* Take photo of track if unsure about species ID. Landscape format preferred!
  Select angle of camera, sun and track so that the track is clearly visible.
* Track type: defaults to "turtle track, success not assessed".
  No interaction required for "uptrack" surveys.
* Location: Start GeoPoint. Required. Auto-saves once accuracy drops below 5m.

You should at least set species and GeoPoint, if the other value defaults are correct.

Swipe right, "Save Form and Exit" saves the record of the track.
This will take about 13 taps and swipes over about 15 seconds plus the time to take a photo.

Repeat for each track.

Collect "nest" data
^^^^^^^^^^^^^^^^^^^

Part 1: same screen as uptrack up to photo of track. Resuming from track type:

* Follow the track until you find the nest or downtrack.
* Depending on presence of nest, set type (false crawl if no nest present,
  successful crawl if nest present).
* Record the location of the nest, or track apex.
* Swipe right. If nest is present, fill in the "nest" screen.
* Swipe right. If disturbance is evident, you will be asked to
  "Add a new Disturbance observation group" - do this for each distinct
  disturbance cause.
* Once all (typically one) disturbance causes are recorded, swipe right, select
  "Do not add", "Save form and Exit".

Review data (optional)
^^^^^^^^^^^^^^^^^^^^^^
"Edit Saved Form" lists all forms and allows you to edit as required.
With above settings, do this while still offline.
Typically, records should only require to be edited immediately after capture
while the encounter is still freshly in mind.
Any other updates can be done once the data are in the main database.

Upload data (automatic)
^^^^^^^^^^^^^^^^^^^^^^^
With "Auto-send in Wifi" settings enabled, your device will automatically upload all data marked as
"finalized". This is ideal for sparse use, such as Rangers reporting strandings
before returning to a broadband Wifi'd office.

With "Auto-send in Wifi" settings disabled, you need to backup data by downloading
it manually and keeping the downloaded data safe (multiple copies over separate
storage media). With the mobile device connected and "MTP file transfer" enabled,
ODK data is located in either internal or SD storage in ``odk/instances``.
Each form will be stored in a separate folder, containing both the filled in form
as XML file, and all related pictures and media.

Where's the data now?
^^^^^^^^^^^^^^^^^^^^^
ODK Collect uploads data to the configured ODK Aggregate clearinghouse.
In our case, this is https://dpaw-data.appspot.com/.
Data collectors will have received credentials to login.

A synchronised copy of the data is streamed to Google Fusion Tables. Access to
the respective table is provided on demand and requires a Google account.

**In development**:
Data will be piped from ODK Aggregate into WAStD.
Access to WAStD is restricted to DPaW staff only.
Once data arrive in WAStD, WAStD becomes the point of truth, as curation (e.g.
double-checking species ID based on submitted photos) can change the data compared
to the initial submission on ODK Aggregate.
Analysis will consume the curated data through the WAStD API.


Turtle Stranding
================

Setup the device as described above and select the latest "Turtle Stranding" form
in "Get blank forms".

The expected work flow is:

* A member of the public reports a stranded animal, a field officer responds to
  the report and inspects the stranded animal personally.
* A field officer discovers a stranded animal during a patrol.
* In both cases, the field officer carries a mobile device with ODK Collect and
  the latest "Turtle Stranding" form.
* The field officer fills in the form while attending to the stranded animal.
* All freshly dead turtles (D1 and D2) should be frozen and sent to Perth
  (Erina Young) for a necropsy.

The form should be self-explanatory. Some fields default to the "not assessed / NA"
option, however effort should be untertaken to determine the correct option.

Photographs are very important, in that they allow data curators to verify the field
operator's choice of available options.

If possible, photographs should be taken in landscape format.

The habitat photo should be taken from about 10 m distance to the animal.

Although taking several photos next to a decomposing animal may pose an olfactory
challenge, taking a photo is invaluable, in that it cannot be taken at a later
time, but preserves valuable and volatile information.
