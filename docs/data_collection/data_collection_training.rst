========================
Data collection training
========================

This chapter provides the training resources for prospective data collectors.

Using the data collection device and software
=============================================

* Android tablets
* ODK Collect

Topics covered:

* Basic device management: WiFi, GPS, camera and location, Photo upload, accounts, on-board storage vs SD cards.
* Basic data collection software maintenance: download new and delete outdated data collection forms, set server and credentials, manage upload settings.
* Links to further documentation on Android and ODK Collect.

Device management
=================

We assume that you'll have been given an already set up Android tablet.
This section summarises the minimum you should know about how the tablet is set up.
Link to device setup (admin).

Tested devices
--------------

* Samsung Tab S2, 10" and 8"
* Lenovo Tab3 7"
* Moto G4+ 5"

Best field device: Lenovo Tab3 7"

Link to device comparison

WiFi and GPS
------------

* When to turn on

Camera
------

* Enable location capture

Accounts
--------

* Auto-upload photos to Google Photos

Storage
-------

* Storage options for app data depends on Android version
* SD cards can be formatted as "internal storage" on Android 6+, don't bother with SD cards on Android 5 

Data collection software management
===================================

Setup
=====

* Server, credentials, upload settings

Maintenance
===========

Download new forms
------------------

Delete old forms
----------------


Fill in a new form
------------------

Understand that one filled in ODK form is one data record.


Preparing a device pre survey
=============================
Run through this section every time before heading out to collect data.
Ideally, the admin handing out the Android device will double-check these settings together with the data collector.

* **Credentials** Set the collector's ODK credentials (username and password)
  for the respective ODK Aggregate server, (e.g. https://dpaw-data.appspot.com/)
  **exactly** as given and **before** collecting data.
  The entered username will be stored automatically with each record (only
  correct usernames will ensure correct attribution), and used to authenticate
  data upload to ODK Aggregate (incorrect usernames will result in failed upload).
* **Battery** Make sure the battery is full before you head out.
  Screen and GPS are hungry hippos. Toggle WiFi and GPS depending on situation:
  GPS on only during surveys, WiFi on only during data upload.

**Note** Exact spelling includes capitalisation, interpunctuation and whitespace.
E.g., the username `stephen_king` is not correct if spelled `Stephen_King`,
`StephenK`, `stephen king`, `stephen-king` or `stephenking`.

Collecting turtle data
======================

This section runs through all possible scenarios of turtle data collection.

Data collection protocols
-------------------------

Marine wildlife incidents, such as turtle strandings, are always recorded on a case-by-case basis.
Tracks can be recorded individually (preferred) or tallied over beach sections.

* *Nest* counts: walking in a straight line along the high water mark, each
  uptrack is followed to its apex, where the presence or absence of a nest
  determines the type of track (track without nest, track with nest, track with
  a possible nest).
  If evident, nest disturbance is recorded as well.
  Disturbed unhatched nests without tracks, as well as hatched nests (without
  tracks), if spotted, are recorded as well.
* *Speed run* counts: walking in a straight line along the high water mark, only
  inbound tracks (uptracks) are counted as "tracks with success not assessed".
  The tracks are not followed. Except for the first day, only fresh (younger
  than 24h) tracks are recorded. Nests are recorded if spotted.
* *Track tallies* are recorded only under extreme time pressure, or on saturation
  beaches, where the geo-referencing of individual tracks is not possible within
  the available survey time. However, individual track counts (*nest* or *speed run*)
  are preferred.

Track count work flow
---------------------
.. image:: https://www.lucidchart.com/publicSegments/view/14429a0a-bc5c-4bbb-8bd1-527294874920/image.png
    :target: https://www.lucidchart.com/publicSegments/view/14429a0a-bc5c-4bbb-8bd1-527294874920/image.png
    :alt: Track Count work flow

Collector: Collect "speed run" data
-----------------------------------
* Walk along the high water mark on the beach until you encounter either
  an unmarked inbound track ("uptrack") or unmarked outbound hatchling tracks.
* "Fill Blank Form" > Track or Treat (latest version)
* Track age: fresh (default) if less than 24 h old, or old if older than 24 h.
  If the beach was surveyed within the last day, all unmarked tracks are "fresh".
* Species: select species if possible, else if unsure, keep default "turtle".
* Take photo of track if unsure about species ID. Landscape format is preferred!
  Place a length reference (measuring tape) across the whole track, lining up
  the end with the edge of the track. This allows curators to gauge the track
  width easily from the photo.
  Select angle of camera, sun and track so that the track is clearly visible.

Adult turtle tracks:

* Track type: keep default "track, not checked for nest"
* Location: Start GeoPoint. Required. Can be saved as soon as "accuracy" is
  shown, will auto-save once accuracy drops below 5m. The fix should not take
  longer than 5 to 10 seconds. The acquisition speed depends on the device's GPS
  chip and available satellites. The first fix can take a bit longer, subsequent
  GPS fixes should be faster.

Hatchling tracks:

* Track type: "nest, hatched"
* Location: Follow to hatched nest, capture location of nest.
* Swipe right and fill in subsequent nest-related screens. A senior field worker
  will conduct the nest excavation.

You should at least set species and GeoPoint, if the other value defaults are correct.

Review the data, then swipe right to finish the form.

If you are sure of species ID, keep "Mark form as finalized" ticked and "Save Form and Exit".

If you are unsure of the species ID, (species is "turtle" and photo of track is
provided), untick "Mark form as finalized" and "Save Form and Exit".
This gives the field supervisors a chance to review and possibly determine species ID
(based on the photo taken) before uploading.

This form will take a trained operator about 13 taps and swipes over 
about 15 seconds plus the time to take a photo.

Repeat for each track.

Collect "nest" data
-------------------
Look for both tracks (crossing your path) and nests (may be inland).

**Track** same screen as uptrack up to photo of track. Resuming from track type:

* Follow the track until you find the nest or downtrack.
* Depending on presence of nest, set Track or nest type: "track without nest",
  "track with nest", or "track, checked for nest, unsure if nest".
* If you're unsure about the presence of a nest, take a photo of the nest and
  do not mark the record as "finalized". This gives the field supervisors a
  chance to review and possibly determine nesting success
  (based on the photo taken) before uploading.
* Record the location of the nest, or (if no nest found) the track apex.

**Nest** choose whether nest is unhatched (no shells) or hatched (shells).

Swipe right. If nest is present, fill in the "nest" screen.
Indicate whether:

* disturbance was evident,
* eggs were counted,
* the nest had an ID tag buried within the eggs (or tied to a nest marker pole),
* there was a temperature logger in the nest, or
* hatchlings were found and measured.

Swipe right. Depending on the indications above, extra screens will be shown.

**Disturbance**

* "Add a new Disturbance observation group" for each distinct disturbance cause.
* Record disturbances before excavating nests, take photos of evidence.

**Eggs**
This step assumes that a trained operator has now excavated the nest, and sorted
the eggs into the categories defined by Miller (1999) on top of a cutting board
with a reference grid.

* egg category tallies are required (0 if none found)
* nest depth (caution - millimeters) is optional
* photograph the eggs on top of the reference cutting board and take as many
  pictures as required.

**Nest tag**
Some nests may contain a nest tag, which consists of builders' ribbon with the
nest tag ID written in text marker on it.
A nest tag ID consists of up to three parts:

* Flipper tag ID: provide **exactly one**, and **do not** include any other information.
  e.g. `WA1234`. Whitespace and capitalisation will be ignored, so `wa1234`,
  `WA 1234` and `wa 1234` are equivalent. However, `WA1234 and some words` will
  **not** match up with flipper tag `WA1234` unless manually rectified.
  Operators are encouraged to enter this value with greatest care and precision.
  The turtle flipper tag may have been unavailable or unknown at the time of
  writing the nest tag, so it can be blank.
* Date nest laid: this is the **calendar** date of the nesting event. If a nest
  was tagged after the initial nesting event, the date may be unknown, and
  therefore also blank.
* Nest label: any extra information that is not the first flipper tag or the
  lay date will go here, e.g. an informal nest name like `M1`. The nest label
  may also be blank.

**Temperature logger**
In hatched nests, one or two temperature loggers can be found, and will always
be retrieved for later data download.

* Logger ID: the number underneath the bar code.
* Photo: take a photo of the logger ID / serial / bar code area if lighting allows.
  This is a good backup for proofreading the logger ID.
* Why not barcode: the white-on-black HOBO logger barcode does not scan quickly,
  and barcode scanners can mistakenly OCR the logger ID (from plain text).

**Hatchling measurement**
Enter straight carapace length in mm, straight carapace width in mm and weight in grams.

This is the end of the form. Proceed to the next track or nest and repeat.

At the end of the survey, turn off location services, and hand the device back to the admin.

.. _dct-stranding-report:

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
time, and it preserves valuable and volatile information.


Training beach
==============
Welcome to the training beach! Let's apply the protocols to a (nearly realistic)
data collection scenario.

You'll need:

* A data collection device (smartphone or tablet) set up and ready to go
* Knowledge of the protocols above

.. image:: https://www.lucidchart.com/publicSegments/view/97f2cc34-d19b-403d-a349-814390f3b6c4/image.png
    :target: https://www.lucidchart.com/publicSegments/view/97f2cc34-d19b-403d-a349-814390f3b6c4/image.png
    :alt: Example nesting beach

Training walk-through
---------------------

1 Survey start
^^^^^^^^^^^^^^

2 Fox track
^^^^^^^^^^^

3 Track without nest
^^^^^^^^^^^^^^^^^^^^

4 Track with nest
^^^^^^^^^^^^^^^^^

5 Track, unsure if nest
^^^^^^^^^^^^^^^^^^^^^^^

6 Nest without track
^^^^^^^^^^^^^^^^^^^^

7 Nest without track, predated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

8 Hatched nest, predated
^^^^^^^^^^^^^^^^^^^^^^^^

9 Signs of disturbance or predation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

10 Dead turtle
^^^^^^^^^^^^^^

11 A noteworthy find
^^^^^^^^^^^^^^^^^^^^

12 Survey end
^^^^^^^^^^^^^
