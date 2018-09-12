.. _data-collection-training:
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
  * Type your full given and surname as it is shown e.g. on your driver's license.
  * Separate your given name and surname with a whitespace (not . or _)
  * No middle names
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

Device checkout Broome - Cable Beach
------------------------------------
* There are two tablets (and one hotspot providing WiFi to the tablets) on a charger.
* Disconnect both tablets from the charger.
* Turn one on (to collect data), one off (as backup).
* Take the tablets and the collection backpack out.

Device checkin Broome - Cable Beach
-----------------------------------
* Deposit the collection backpack.
* Connect both tablets to the charger.
* Any tablets with data on them should be kept running.
* Any tablets which weren't used at all can be kept powered off.

Device checkout Kimberley - Anna Plains
---------------------------------------
* There are four switched off tablets on power packs.
* Disconnect the tablets and take two for each data collection team.
* When at the data collection site, switch on one tablet, turn off WiFi, turn on GPS, connect to car charger (cigarette lighter socket).
* Switch off tablet after site visit.

Device checkin Kimberley - Anna Plains
---------------------------------------
* Make sure all tablets are switched off.
* Connect tablets to solar powered battery pack or to backup battery packs.

TODO Device locations Karratha WPTP
-----------------------------------

TODO link to field kit

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

* Landscape format is preferred, but choose aspect at your own discretion.
* Flip device into landscape **before** tapping "take photo" (else it forgets the first photo taken).
* Place a length reference (measuring tape or marked stick) across the whole track,
  lining up the end with the edge of the track.
  This allows reviewers to easily gauge the track width from the photo.
* Select angle of camera, sun and track so that both track and length reference are clearly visible.

Review the data, then swipe right to finish the form.

If you are sure of species ID and presence or absence of nest,
keep "Mark form as finalized" ticked and "Save Form and Exit".

**If tablets are left unsupervised** E.g. West Pilbara, Cable Beach - simply save and let it upload.
Supervisors will QA the data later.

**If a supervisor regularly checks the devices** De-select "Mark form as finalized" and "Save Form and Exit".
This gives the field supervisors a chance to review and possibly determine species ID
(based on the photo taken) before uploading.

This form will take a trained operator about 13 taps and swipes over
about 15 seconds plus the time to take a photo.

Repeat for each track / nest.

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


Protocol "fan angles"
---------------------
This protocol measures hatchling tracks. The operator will require a hand-held compass
(and knowledge how to use it), a length reference (e.g. wooden folding ruler).

If you come across hatchling tracks but cannot locate the nest they hatched from, ignore them and proceed the survey.

If you come across a hatched nest with visible hatchling tracks:

* Species: OK to keep at unknown (unless identifiable hatchlings are found).
* Type: "nest, hatched".
* Other measurements as applicable.
* Fan angles measured:

  * "No" if fewer than 5 tracks are visible, record the nest as mark the nest with a nest tag and monitor the nest daily.
  * "No" if there is more than one other hatched nest within a 5 m radius and hatchling tracks overlap.
  * "Yes" if there are 5 or more clearly visible hatchling tracks.

Screen "Hatchling track fan angles":

* (If daytime) Take a photo from behind the nest towards the sea. You should show the nest,
  the main track fan, and the approach to the water line. Stand 1m behind the nest.
* (If daytime) Take a second picture, this time choose your position to the nest and your camera height
  to maximise contrast and detail.
* Measure the bearing to water as the compass bearing from the nest
  to the closest point on the high water mark (HWM).
* Identify the densest cluster (fan) of hatchling tracks. This is called the main fan.
* Measure the bearing of the left- and rightmost tracks from the nest to
  exactly 5m away from the nest or to the HWM, whichever is closest.
* Count (if possible) or estimate the number of tracks in the main fan and also
  provide upper and lower estimates.
* If any other individual tracks or groups of tracks exist outside the main, select "outlier tracks present".
* Describe the hatchlings' path to sea by selecting all applicable options. You can select multiple options and add free text comments.
* Is hatchling emergence time known? (e.g. when observing at night)
* Is cloud cover at emergence time known?
* Were light sources present during emergence?

Screen "Hatchling emergece time":

* Best estimate for date and time
* Accuracy of estimate

Screen "Weather during hatchling emergence":

* Could cover in eighths: 0/8 is clear sky, 8/8 is entirely overcast

Screen "Light source" (repeat as required):

* If light source is visible (at night) or discernible (at day),
  take a picture of light source or general direction of source.
* Measure bearing to light source or provide best estimate.
* Type of light source.
* Description:

Thevenard observers can use codes for the four major known artificial light sources:

* **W** Wheatstone
* **O** Onslow
* **R** Resort
* **J** Thevenard Jetty

Screen "Other light source":

This screen is a reminder to capture all known light sources as "Light source" in the previous screen.

* If there are any other known light sources, swipe back and add them as individual "Light source".
* If there were no other light sources, select "No".
* If the presence or absence of other light sources is unknown, select "Unknown".

Screen "Outlier track group" (repeat as required):

For each single outlier track, or groups of outlier tracks sharing a similar path (and bearing):

* Take a picture of the track or the group
* Measure bearing from nest to track 5 m away from nest or high water mark
* Count number of tracks in group (default: 1)
* Add comments only if deemed necessary

You have reached the end of protocol "Fan angles".
Circle nest with your foot to mark as observed.
Drag a line with your foot across the hatchling tracks above the high water mark.


.. _dct-stranding-report:

Marine Wildlife Incident (Turtle Stranding)
===========================================

Setup the device as described above and select the latest "Marine Wildlife Incident"
form in "Get blank forms".

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

**Important notice** Please **never** conduct training on a nesting beach. Instead:

* Collect as many records as you wish on any place outside the actual nesting beaches.
* Use the species "Hatchback turtle (Corolla corolla)" when training.

Training walk-through
---------------------
* Note on all forms: swipe right until done, leave "Mark as finalized" on, "Save and exit".
* Never save using the floppy symbol.
* Never back out with "back" key and "save form".
* The only valid way out of a form is to swipe right until "save and exit" is reached.
* Training data should be recorded either outside of nesting beaches, or use "Hatchback turtle".

0 Pre survey
^^^^^^^^^^^^
* Battery full?
* WiFi off (if saving battery)
* GPS on
* Set your ODK Collect username: ODK Settings > General Settings > User and device identity > Form metadata > Username > Your given name and surname, e.g. "Florian Mayer".

1 Site visit start
^^^^^^^^^^^^^^^^^^
* Form "Site Visit Start"
* Any reason you'd expect tracks to be non detectable, e.g. strong winds or rain? Photo, comment
* Mention in comment if this is a training run
* Field "Other data collectors in survey": add other data collectors apart from yourself with full name, separated by commas. (Make sure your own full name is entered into the ODK username through ODK settings.)
  Eg.: "Sarah McDonald, Marissa Speirs"

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
* Add new "Disturbance observation" group for each disturbance: A dialogue will pop up allowing to add a "Disturbance observation" until you decline, allowing to add as many disturbances as you wish.

Depending on whether your program records these events:

* Pretend we've excavated and counted eggs
* Pretend we've found nest tags
* Pretend we've found a data logger in the nest
* Pretend we've found and measured a few hatchlings

9 Signs of disturbance or predation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* Fox sake: human-made disturbance (e.g. vehicle tracks)

10 Dead turtle
^^^^^^^^^^^^^^
* Marine wildlife incident

11 A noteworthy find
^^^^^^^^^^^^^^^^^^^^
* Write on a whiteboard what we're looking at and include as label
* Include wooden folding ruler as length reference
* Take a photo, landscape, of your find, including length reference and label
* Photo will auto-upload to Google Photos where coordinators can access them
* Notify coordinators about noteworthy find
* "There should be a form for it, or it's not what we're looking for"

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