========================
Data collection training
========================

This chapter provides the training resources for prospective data collectors.

* Hardware: Android devices (tablets, phablets, phones), current default: Lenovo Tab3 7"
* Software: ODK Collect


.. _dct-pre-survey:

Preparing a device pre survey
=============================
Run through this section every time before heading out to collect data.
Ideally, the admin handing out the Android device will double-check these settings 
together with the data collector.

* Settings > General Settings > User and device identity > Form metadata > Username:
  * This username will be recorded during data collection - 
    we need this so we can say "thank you".
  * For volunteers, this should be firstname_lastname, e.g. florian_mayer in all 
    lower case and underscore separated.
  * For DBCA staff, this should be the DBCA username, e.g. FlorianM or JoanneKi, 
    with initials capitalised and last name abbreviated.
* **Battery** Make sure the battery is full before you head out.
  Screen and GPS are hungry hippos. Toggle WiFi and GPS depending on situation:
  GPS on only during surveys, WiFi on only during data upload.
* **Length reference** A stick with markings for the minimum and maximum track width
  for each expected species.

**Note** While a typo in the username will not break anything (but make our life harder), 
exact spelling would be greatly appreciated.
Exact spelling includes capitalisation, interpunctuation and whitespace.
E.g., the username `stephen_king` is not correct if spelled `Stephen_King`,
`StephenK`, `stephen king`, `stephen-king` or `stephenking`.

Length reference
================
For situations where the data collector is unsure of the turtle species causing a given turtle track,
the data collection form offers to take a picture of the track for later review and species identification.
Having a length reference in the photos helps the reviewer immensely with species identification.

A simple and cheap length reference for tricky turtle tracks
can be fabricated from a  plastic, non-bendy tomato garden stake ($5),
marked with goloured duct tape ($5 per roll) at the minimum and maximum track width 
for each turtle species expected to occur in the surveyed area.

A folding rule is a more portable, but more expensive alterative to the tomato stake.

https://photos.app.goo.gl/lc6kjZMTrPlpjCoG3
    :target: https://photos.app.goo.gl/lc6kjZMTrPlpjCoG3
    :alt: Turtle track length reference

The stick can be simplified, e.g. if only green and flatback turtles are expected,
a stick can be cut to the maximum flatback track width, with one marking for the 
minimum green track width.

Additional length markings, e.g. intervals of 10cm, can be added as required.

This method is preferred over the use of a measuring tape as length reference in 
photos of tracks of unknown species for the following reasons:

* A rigid stick will lay on top of sand ripples, 
  while measuring tape will distort measurement by bending over them.
* The coloured, centimeter-wide markings on the stick will be visible at lower image quality 
  than the millimeter-wide centimeter markings on a measuring tape.
* The coloured tape wraps around the stick and is thereby visible from any angle, 
  while tape can flip over and hide its markings.
* By reducing length references to relevant lengths, cognitive load is taken off the data collector. 
  One can simply read off the stick markings which species' track width range 
  a given track falls into.

Collecting turtle data
======================

This section runs through all possible scenarios of turtle data collection.
The data collector should already be trained to recognise species from tracks, as well as 
identify turtle nests and body pits.

Data collection protocol overview
---------------------------------

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

Protocol "speed run" track count
--------------------------------
* Walk along the high water mark on the beach until you encounter either
  an unmarked inbound track ("uptrack") or unmarked outbound hatchling tracks.
* "Fill Blank Form" > Track or Treat (latest version)
* Track age: fresh (default) if less than 24 h old, or old if older than 24 h.
  If the beach was surveyed within the last day, all unmarked tracks are "fresh".
* Species: select species if possible, else if unsure, keep default "Turtle".

Adult turtle tracks:

* Track type: keep default "track, not checked for nest"
* Location: Start GeoPoint. Required. Can be saved as soon as "accuracy" is
  shown, will auto-save once accuracy drops below 5m. The fix should not take
  longer than 5 to 10 seconds. The acquisition speed depends on the device's GPS
  chip and available satellites. The first fix can take a bit longer, subsequent
  GPS fixes should be faster.

Hatchling tracks:

* Track type: "nest, hatched".
* Location: Follow to hatched nest, capture location of nest.
* Swipe right and fill in subsequent nest-related screens. A senior field worker
  will conduct the nest excavation.

You should at least set species and GeoPoint, if the other value defaults are correct.

If you were unsure about the species and have therefore kept the default "Turtle", 
you will be shown a subsequent screen "Unsure about species", where you can take photos 
of both the uptrack (water towards land) and the downtrack (returning from land to water).

* Landscape format is preferred!
* Place a length reference (measuring tape or marked stick) across the whole track, 
  lining up the end with the edge of the track. 
  This allows reviewers to easily gauge the track width from the photo.
* Select angle of camera, sun and track so that both track and length reference are clearly visible.

Review the data, then swipe right to finish the form.

If you are sure of species ID and presence or absence of nest, 
keep "Mark form as finalized" ticked and "Save Form and Exit".
Otherwise, untick "Mark form as finalized" and "Save Form and Exit".
This gives the field supervisors a chance to review and possibly determine species ID
(based on the photo taken) before uploading.

This form will take a trained operator about 13 taps and swipes over 
about 15 seconds plus the time to take a photo.

Repeat for each track.

Protocol "Oh no I forgot something"
-----------------------------------
This happens to the best of us. If you want to change your mind about a form:

* ODK Collect > Edit Saved Form > Sort by date (sorting symbol top right) > Tap form to edit.
* Correct errors right away, and at the latest before handing back the device or uploading the data.

Protocol "nest counts"
----------------------
This protocol is the preferred protocol and includes the steps of "speed run".

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

Track tally

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



0 Pre survey
^^^^^^^^^^^^

* Battery full?
* WiFi off
* GPS on
* Set your ODK Collect username

1 Survey start
^^^^^^^^^^^^^^
* Site visit Start
* Any reason you'd expect tracks to be non detectable, e.g. strong winds or rain? Photo, comment
* Mention in comment that this is a training run

2 Fox track
^^^^^^^^^^^
* Fox sake

3 Track without nest
^^^^^^^^^^^^^^^^^^^^
* Track or Treat, track without nest

4 Track with nest
^^^^^^^^^^^^^^^^^
* Track or Treat, track with nest

5 Track, unsure if nest
^^^^^^^^^^^^^^^^^^^^^^^
* Track or Treat, track unsure if nest

6 Nest without track
^^^^^^^^^^^^^^^^^^^^
* Track or Treat, nest, unhatched, no track

7 Nest without track, predated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* Track or Treat, nest, unhatched, no track
* Disturbed or predated: yes
* Add new "Disturbance observation" group for each disturbance

8 Hatched nest, predated
^^^^^^^^^^^^^^^^^^^^^^^^
* Track or Treat, nest, hatched
* Disturbed or predated: yes
* Add new "Disturbance observation" group for each disturbance

Depending on whether your program records these events:

* Pretend we've excavated and counted eggs
* Pretend we've found nest tags
* Pretend we've found a data logger in the nest
* Pretend we've found and measured a few hatchlings

9 Signs of disturbance or predation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* Fox sake

10 Dead turtle
^^^^^^^^^^^^^^
* Marine wildlife incident

11 A noteworthy find
^^^^^^^^^^^^^^^^^^^^
* Take a photo, landscape
* Write on a whiteboard what we're looking at and include as label and length reference

12 Survey end
^^^^^^^^^^^^^
* Site visit end
* Any new reasons impacting data collection? Photo, comment

13 Return device
^^^^^^^^^^^^^^^^
Returning to an office (WiFi and wall power):

* GPS off
* WiFi on

Returning to a deposit box (no WiFi, portable battery):

* GPS off
* Device off
* Plugin battery to charge device