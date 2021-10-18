.. _dc-protocols:

**************************************
Data collection protocols and training
**************************************

This chapter provides the training resources for prospective data collectors.

Tasks covered:

* Prepare devices pre survey as a data collector
* Protocols for data capture, form by form
* Training beach: :ref:`dct-training-beach`


.. _dct-pre-survey:

Preparing a device pre survey
=============================
Run through this section every time before heading out to collect data.
Ideally, the admin handing out the Android device will double-check these settings
together with the data collector.

* Settings > General Settings > User and device identity > Form metadata > Username:
  * This username will be recorded during data collection -
    we need this so we can say "thank you" and improve training for users making repeated mistakes.
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
E.g., the username `Stephen King` is not correct if spelled `Stephen_King`,
`StephenK`, `stephen king`, `stephen-king` or `stephenking`.

Device checkout Broome - Cable Beach
------------------------------------
* There are six tablets (and one hotspot providing WiFi to the tablets) on a charger.
* Disconnect the tablets from the charger.
* Turn one on (to collect data), one off (as backup).
* Take the tablets and the collection backpack out.

Device checkin Broome - Cable Beach
-----------------------------------
* Deposit the collection backpack.
* Connect all tablets to the charger.
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

Devices Karratha WPTP
---------------------
* Maintained and stored at the DBCA Karratha office.
* Two devices in locked box at Yacht Club Wickham for Cape Lambert.
* Two devices in locked box at DBCA Karratha for Cleaverille.
* Two spares at DBCA Karratha.

Devices Rio Tinto Cape Lambert
------------------------------
* Two devices are maintained and stored at the DBCA Karratha office.

Devices Rosemary Island
-----------------------
* Six devices * Maintained and stored at the DBCA Karratha office and are taken on field trips to Rosemary Island.
* During turtle tagging, exactly one SVS (start of evening shift) and one SVE
  (end of morning or last shift) must be captured per beach and per night.
* Multiple tablets can capture data during that survey on that beach.
* Beach 3-5 (one site) must always be surveyed together. Exactly one SVS and SVE per visit to Beach 3-5 must be recorded.


Turtle Nesting Census
=====================

This section runs through all possible scenarios of using the form Turtle Track or Nest.
The data collector should already be trained to recognise species from tracks, as well as
identify turtle nests and body pits.

Data collection protocol overview
---------------------------------

Marine wildlife incidents, such as turtle strandings, are always recorded on a case-by-case basis.
Tracks can be recorded individually (preferred) or tallied over beach sections.

* Every device must be updated with the main data collector's name as username.
* All site visits are started with a ``Site Visit Start``
* *Nest* counts: walking in a straight line along the high water mark, each
  uptrack is followed to its apex, where the presence or absence of a nest
  determines the type of track (track without nest, track with nest, track with
  a possible nest).
  If evident, nest disturbance is recorded as well.
  Disturbed unhatched nests without tracks, as well as hatched nests (without
  tracks), if spotted, are recorded as well.

In extreme circumstances, such as boat-based surveys of remote Kimberley beaches
with a strict pick-up time (and survey time limit), the methodology of Nest/Track
counts can be modified:

* *Speed run* counts: walking in a straight line along the high water mark, only
  inbound tracks (uptracks) are counted as "tracks with success not assessed".
  The tracks are not followed. Except for the first day, only fresh (younger
  than 24h) tracks are recorded. Nests are recorded if spotted.
* *Track tallies* are recorded only under extreme time pressure, or on saturation
  beaches, where the geo-referencing of individual tracks is not possible within
  the available survey time. However, individual track counts (*nest* or *speed run*)
  are preferred.
* All site visits are ended with a ``Site Visit End``. You **should** take a photo.

Protocol Morning Track count
----------------------------
* Soundcheck before leaving camp and WiFi
* SVS once per site and day
* Track or Nest / Dist or Pred / MWI as encountered
* SVE once per site and day

Protocol Night Tagging
----------------------
* Soundcheck before leaving camp and WiFi, set tablets to night mode and dark ODK theme
* SVS once per site and day
* Track or Nest for each missed turtle
* Paper datasheet for each tagged turtle (THV/DEL: ODK form Turtle Tagging)
* SVE once per site and day


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

**If a supervisor regularly wants to proofread submissions pre-upload on the devices**
De-select "Mark form as finalized" and "Save Form and Exit".
This gives the field supervisors a chance to review and possibly determine species ID
(based on the photo taken) before uploading.

This form will take a trained operator about 13 taps and swipes over
about 15 seconds plus the time to take a photo.

Repeat for each track / nest.

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
* there was a temperature logger in the nest,
* hatchlings were found and measured, or
* fan angles were found and measured.

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


.. dct-turtle-tagging:

Turtle Tagging
==============
Field coordinator tasks:

* Make sure tablets are set to not auto-upload.
* Have a volunteer number datasheets in consecutive numbers before handing them out into field packs.
* Make sure that paper datasheets are backfilled the next morning. Take photos of Biopsy sample IDs.
* Coordinate with WAStD maintainer on data/QA/form issues if needed daily.

Training focus:

* Handling of tablets: Only ever in your hand, in the neoprene sleeve, or on the charger. Mind sand and moisture. Keep the sleeve sand free.
* Explain: Form is squashed into minimal number of screens to streamline and make robust the data entry process at the cost of some repetition and some blank fields. Form handles both night time tagging and in-water turtle captures, the latter will have to suffer skipping some nest related fields in one screen.
* Data entry: voice to text works well for PIT and flipper tag numbers.
* Explain data capture modes. Practice backfilling. Point out guidance hint on data capture mode.
* Explain signed degrees.
* Explain: if no PIT tags, swipe past PIT screen.
* Explain: PIT/Flipper tag status only applies if a tag is recorded (in tag ID).
* If there are more tags or samples than the form provides for, there is a repeat group to add the rest coming later.
* Biopsy location provides identifiable mark (biopsy scar) to help reconstruct turtle identities.

Assumptions
-----------
1. Minimal ODK record is good enough if taken just before or right after tagging
  a. auto-time close enough
  b. location able to capture next to nest
2. Minimal ODK record links to datasheet via datasheet ID
  a. Datasheet ID can be hand-written on datasheet or pre-allocated and printed on sticker
  b. Datasheet ID is ephemeral and does not need to be unique beyond field team
3. Reasons for not backfilling form directly after tagging:
  a. other turtles need tagging right now
  b. dark night, preserve night vision
  c. rain, can't use tablet
4. Backfilling of paper datasheet happens in ODK Collect. The goal is to reproduce the written data on the paper datasheet faithfully.
5. QA happens after import into WAStD, assisted by dedicated QA reports.

Minimal viable record
----------------------
Both the ODK form "Turtle Tagging" and the paper datasheet allow to capture more data than needed to be
compatible with any detail level of data capture.
On busy nesting nights, there can be several turtles competing for the same tagging team's time.
In this case, the team needs to commit to one turtle for processing, and record the minimum viable record, then move on to the next turtle.

The minimal viable record includes:

* Location and time of nesting
* PIT tags
* Flipper tags
* Turtle details (species etc)

Even if other turtles are getting away without being processed,
the minimal record must to be taken for each processed turtle.

The nice-to-have record includes the above plus:

* One biopsy for already biopsied turtles (a wishlist of flipper tags to biopsy will be handed out)
* CCL
* Any significant damages which impact nesting success (e.g. flipper amputation impedes digging) or
  are recognizable (larger deformities, e.g. healed shark bites if carapace, sat tag harness scars).



Form workflow
-------------
Prepare devices for tagging
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Early in day
^^^^^^^^^^^^^^^^^^^^^^^^^^^
1. Ensure tablet is fully charged

Checking out tablets
^^^^^^^^^^^^^^^^^^^^^^^^^^^
2. Do a Soundcheck if willing - Update username at least
3. Verify auto-send is turned off for tagging. You can only edit finalized forms while they are not yet uploaded.

In situ: Tagging night
^^^^^^^^^^^^^^^^^^^^^^^^^^^
4. Site Visit Start when on site. Exactly one SVS per site and date. THV: two sites (north / south beach), DEL: one site (entire island).
5. Turtle Tagging for tagged turtles, Turtle Track or Nest for missed turtles. Backfill forms if time and brain space allow.
6. Site Visit End when finishing up for the night.

Tagging modes:

1. Turtle encountered while nesting.
  a. Hybrid Step 1 while egg laying (waiting phase).
  b. tagging on paper during hot phase.
  c. Backfill when possible via Hybrid Step 2. Don't bother with datasheet photo, leave for better light conditions in the morning.
  d. If backfilling during night, leave unfinalized.
2. Turtle encountered while returning to water.
  a. Tagging on paper (hot phase).
  b. capture Hybrid Step 1 record in situ once turtle is gone.
  c. backfill if time permits via Hybrid Step 2.
3. ODK unavailable.
  a. All data on paper. GPS in handheld.
  b. Backfill and choose data capture mode "New record".


Next morning
^^^^^^^^^^^^^^^^^^^^^^^^^^^
7. Return tablets to charger, place datasheets and biopsy samples with respective tablet.
   The coordinator clearly labels the drop-off area with a sign saying "Drop off for tablets, datasheets, biopsy samples".
8. Backfill ODK via Hybrid Step 2: Go through "Edit saved forms", open each, find corresponding datasheet, backfill remaining forms, proofread, photograph datasheets (needs daylight).
9. Send finalized forms. Leave tablets in "manual upload mode".
10. Enter data into WAMTRAM.

After import and QA
^^^^^^^^^^^^^^^^^^^^^^^^^^^
11. WAStD: QA typos. Mark changed records as "curated" to prevent data loss. QA reports will assist finding records that need review. We will learn from QA and improve QA helpers this season.

Minimum ODK record
^^^^^^^^^^^^^^^^^^
Minimum record in ODK form "Turtle Tagging" via Hybrid Step 1 with a nest location, timestamp, the username, and datasheet ID.
Save form as "non finalized" and name after datasheet ID.

Backfill paper to ODK
^^^^^^^^^^^^^^^^^^^^^
Backfill the ODK record from the paper datasheet via Hybrid Step 2.
Find record in "Edit saved forms", choose data capture mode "continue here", once light allows photograph paper datasheet, save as finalized. Let record upload.


.. _dct-training-beach:

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


* Collect as many records as you wish on any place outside the actual nesting beaches.
* Use the species "Hatchback turtle (Corolla corolla)" and any available options indicating training/testing when conducting training on an actual nesting beach.

Training walk-through
---------------------
* Note on all forms: swipe right until done, leave "Mark as finalized" on, "Save and exit".
* Never save using the floppy symbol.
* Never back out with "back" key and "save form".
* The only valid way out of a form is to swipe right until "save and exit" is reached.
* Training data should be recorded either outside of nesting beaches, or use "Hatchback turtle", or with tablets set to not auto-upload and the trainer deleting the submissions before sending.

0 Pre survey
^^^^^^^^^^^^
* Battery full?
* WiFi off (if saving battery)
* GPS on
* Set your **ODK Collect username**:
  ODK Settings > General Settings > User and device identity > Form metadata > Username > Your given name and surname, e.g. "Florian Mayer".

1 Site visit start
^^^^^^^^^^^^^^^^^^
* Form "Site Visit Start" when "feet in the sand, eyes open".
* Location: can be done anywhere on beach - feet in the sand.
* Time: **must** be done before any other record is created.
* Photo: **should** always be taken.
  May be valuable later on - high opportunity cost not to take a photo!
  The photo can show environmental conditions (wind, past rain) which may lead
  to under-detection of tracks. The photo also could show anything that might be
  relevant to other questions in the future.
* Field "Other data collectors in survey": add other data collectors apart from
  yourself with full name, separated by commas.
  Eg.: "Sarah McDonald, Marissa Speirs"
  Omit your own name, as it already is recorded through the ODK username.
* Mention in comment if this is a training run, or if there were any
  unusal environmental conditions.

2 Fox track
^^^^^^^^^^^
Any disturbance or sign of predation.

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
* Pretend we've found and measured hatchling tracks (fan angles)

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
* Take a photo in landscape orientation of your find, including length reference and label
* Photo will auto-upload to Google Photos where coordinators can access them
* Notify coordinators about noteworthy find
* "There should be a form for it, or it's not what we're looking for"



12 Turtle (nesting)
^^^^^^^^^^^^^^^^^^^
TODO: add tranining scenarios here for Turtle Tagging 3.0

* One turtle, enough time: full digital mode.
* One turtle, rushed, hybrid: Min ODK, paper, backfill.
* Pure paper. Backfill.
* Many turtles. What's the minimal viable record?

Training turtles:

* A minimal turtle - just minimal PIT and flipper tags.
* A turtle with one extra (biopsy, nest tag, damage, nest logger, etc.) - explain details for each group.
* A turtle "the works".


12 Survey end
^^^^^^^^^^^^^
* Site visit end: "feet in the sand, eyes off".
* Take a photo facing back towards surveyed area.
* Any new reasons impacting data collection? Photo, comment.
* Location: The end point can be taken anywhere on the just surveyed beach - "feet in the sand".
* Time: **must** be taken when survey effort is ended - "eyes off".

13 Return device
^^^^^^^^^^^^^^^^
Returning to an office (WiFi and wall power):

* GPS can stay on
* WiFi on

Returning to a deposit box (no WiFi, portable battery):

* GPS off
* Device off
* Plugin battery to charge device

Returning to a deposit box (WiFi, portable battery):

* GPS off
* WiFi on
* Device stays on (so it can auto-upload data)

Returning after tagging (THV, DEL: WiFi hotspot, wall power):

* Leave tablets at "no auto-upload"
* Backfill datasheets, proofread until happy
* "Send finalized forms"
* Await ingest to WAStD
* Review QA reports
