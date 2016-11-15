===============
Data collectors
===============

Each field in the data sheets should be questioned:

* Is this information used in any of the analytical outputs?
* Does this information serve any QA purpose?
* Is this information used to derive other information, e.g. deformities being
  used to identify an animal identity?
* Will anyone in the future require this information?

Turtle Stranding
================

Improve data sheet:

Photo guidelines
----------------
If possible, take pictures of the stranded animal:

* Totals: the whole animal from above,  from each side, from the front and the back.
  Include a length reference, such as a shoe, or an object of known lengh.
* Details: Every flipper tag, every visible damage, notable details (fresh and healed
  injuries, deformities)
* Location: the surroundings showing about 20 meters or more to show beach position
  (relative to high water line, edge of vegetation) and location (so that we can
  find the location on Google Maps).


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

* On your Android device, install `ODK Collect <https://play.google.com/store/apps/details?id=org.odk.collect.android>`_
* In ODK Collect > General Settings > Configure platform settings:
* URL: https://dpaw-data.appspot.com
* Your username and password as provided to you by the ODK admin.
* Auto send: only with Wifi
* Default to finalized
* Delete after send

**Note** You must not share your credentials, and always use your own to collect data.
Failure to do so will result in data loss or corruption.

Get the form
^^^^^^^^^^^^



Preparing to collect data
^^^^^^^^^^^^^^^^^^^^^^^^^
These steps have to be run before field trip while online,
and verified before each survey.
Less than 1 MB will be downloaded.

* **Credentials** Make sure that your ODK credentials
  (for the respective ODK Aggregate server, e.g. dpaw-data.appspot.com) are set
  before collecting data, as these will be recorded as well (saving you to type
  your name multiple times). Setting the credentials (username, password) in
  ODK Collect's General Settings can be done while offline.
* **Form** Make sure you've got the latest Track count form. The form should not change
  during the field trip. In ODK Collect, "Get Blank Form", select the latest
  TrackCount form and "Get Selected".
* **Battery** Make sure the battery is full. Screen and GPS are hungry hippos.

Collecting "uptrack" data
^^^^^^^^^^^^^^^^^^^^^^^^^

* Walk along the high water mark of the beach, record each (day 1) or each fresh
  (after day 1) uptrack as follows.
* "Fill Blank Form" > Track Count (latest version) > swipe right.
* Fill in the first screen with following fields:
* Track age: fresh or old. Defaults to fresh, no interaction required on "fresh
  tracks only" surveys after day 1.
* Species: defaults to "turtle" as value for "unsure".
* Take photo of track if unsure about species ID
* Track type: defaults to "turtle track, success not assessed". No interaction
  required for "uptrack" surveys.
* Location: Start GeoPoint. Auto-saves once accuracy drops below 5m.

You should at least set species and GeoPoint, if the other value defaults are correct.
This will take about 15 seconds plus time to take a photo (if desired).

Swipe right, "Save Form and Exit" saves the record of the track.
Repeat for each track.

Collecting "nest" data
^^^^^^^^^^^^^^^^^^^^^^

Part 1, same as uptrack:

* Walk along the high water mark of the beach, record each (day 1) or each fresh
  (after day 1) uptrack as follows.
* "Fill Blank Form" > Track Count (latest version) > swipe right.
* Fill in the first screen with following fields:
* Track age: fresh or old. Defaults to fresh, no interaction required on "fresh
  tracks only" surveys after day 1.
* Species: defaults to "turtle" as value for "unsure".
* Take photo of track if unsure about species ID. Landscape is preferred!

Part 2, in addition to uptrack:

* Follow the track until you find the nest or downtrack
* Depending on presence of nest, set type (false crawl if no nest present,
  successful crawl if nest present)
* Record the location of the nest, or track apex.
* Swipe right. If nest is present, fill in the "nest" screen.
* Swipe right. If disturbance is evident, you will be asked to
  "Add a new Disturbance observation group" - do this for each distinct disturbance
  cause.
* Once all (typically one) disturbance causes are recorded, swipe right, select
  "Do not add", "Save form and Exit".

Reviewing data
^^^^^^^^^^^^^^
"Edit Saved Form" lists all forms and allows you to edit as required.
With above settings, do this while still offline.
Typically, records should only require to be edited immediately after capture
while the encounter is still freshly in mind.
Any other updates can be done once the data are in the main database.

Uploading data
^^^^^^^^^^^^^^
With above settings, your device will automatically upload all data marked as
"finalized".
