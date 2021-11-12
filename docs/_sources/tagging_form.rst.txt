Turtle Tagging form design
==========================
Maintained by: Florian Mayer
Consulted: Ryan Douglas, James Gee

TODO merge comments and improvements from THV field testing and form development into this chapter.




Form design
-----------

Is there a nest?

Observed nesting success
nest-with-eggs - Nest with eggs - witnessed eggs drop
nest-without-eggs - Nest without eggs - witnessed aborted laying
nest-unsure-of-eggs - Nest unsure of eggs - found covered up nest mound
unsure-if-nest - Unsure if nest - can't tell whether nest mound present or not
no-nest - No nest - witnessed aborted nest or found track with no nest
na - Did not check

TagObs
- Securely fixed YN
- Barnacles

Field testing at Thevenard
--------------------------
TODO: distill the following field work log

Turtle Tagging 2020
Protocol
Form updates
Export forms from ODK Build to XForms XML.
Edit XML
Replace title <h:title>Turtle Tagging 1.3</h:title> with <h:title>Turtle Tagging</h:title>
Replace <data id="build_..."> with <data id="Turtle-Tagging" version="build_...">
Replace header with
content_copy
<h:html xmlns="http://www.w3.org/2002/xforms" xmlns:h="http://www.w3.org/1999/xhtml" xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  xmlns:jr="http://openrosa.org/javarosa" xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:odk="http://www.opendatakit.org/xforms">
Insert after
content_copy
<observation_start_time/>
<start_location/>
Insert after the <itext> nodes:
content_copy
<bind nodeset="/data/start_location" type="geopoint" /><odk:setgeopoint event="odk-instance-first-load" ref="/data/start_location" />
Data capture
Are we there yet?
ODK > Fill blank forms (e.g. Track or Nest) > Map symbol > offline map view plus saved forms and current position.
View coordinates in decimal degrees:
Go to hierarchy view > group in read-only mode is decimal degrees.
Data entry
Review each tablet:

Enter tagging data
Upload all finalized forms
Handle form upload errors: fix&finalize stuck forms
Prepare morning tablets: day mode; night tablets: night mode
Put back on charger
Fri 27 Nov
Arrived on airport 1700, on island 1900, unpacked, dinner, introduction talks, tagging 2200-0100.

Admin
[x] update tablets: mbtiles, QR, no autosend, nightmode, SVS map widget
[] ETL data

Tagging
[x] add r/o username
[x] location typo "rightshoulder"
[x] PIT location defaults PIT 1 left shoulder, PIT 2 right shoulder
[x] PIT status : add "applied, no read, assumed dud"
[x] Add tag scar to ft1 group
[x] Add nest tag to nesting event group
[x] damage type: add "scratches"
[x] Clean up labels and hints
[-] Cannot yet add start-geolocation - now can

Experience
11 taggers, 8 experienced, 3 new vollies
5 tagging forms filled while shadowing two teams, 7 more forms missed from two other teams.
There was enough staff to have a scribe per team handling the paper datasheet, plus one to two handlers to work on turtle.
The scribe could have handled the tablet and datasheet.

In some cases, there was often enough time to capture the initial record straight away.
In other cases, a snap decision was made to tag a turtle, and sometimes GPS was cold, so the form lagged.
Idea: add autolocation metadata to warm up GPS.

After tagging, there was enough time to backfill ODK from paper. This also utilises fresh memory, sparks some conversation about tagging details and events, keeps taggers engaged and awake.

The form can be navigated from the hierarchy view efficiently, so the flow of the form can be more tuned to the field data capture.

Sat 28 Nov
Morning walk. Up 0430, walk 0500-0830. Breakfast, shower, bed, sleep 1000-1400.
Finalized and uploaded 5 tagging forms.
Adjusted site bdy THV N/S to fish cleaning stn. Re-built and deployed mbtiles.
Updated form TurtleTagging 1900-2400. No beach testing, too tired and still working on forms.

Admin
[x] Update site boundaries
[x] Update all tablets with bg imagery
[x] Asked ODK team for help on start-geopoint via ODK Slack

Sun 29 Nov
[x] 0700-1100 Got solution from ODK team. Add start-geopoint to Turtle Tagging and Turtle Track or Nest, test, roll out, notify custodians
[-] Test tagging form with Sabrina
[x] Update tagging form / protocol
[x] 1900-2230 Test tagging form with teams

Experience
Team Anna Winkler, David Zaboj:

plenty of time to backfill ODK form from datasheet,
found readability of dimply backlit tablet (in full moon) superior to datasheet with head torch,
found range of display brightness adequate (currently full moon),
preferred entering numbers / tag IDs into tablet's keyboard over hand writing on paper.
Between 3 teams and ca 10 turtles processed, ca 1 minimal tagging form missed (pending team feedback).

Mon 30 Nov
1200-1500 Data entry test runs, feedback.

Experience
10 mins per form with discussions. 5 mins plain data entry.
Anna Winkler, David Zaboj: 20 mins to backfill 2 datasheets, plus photograph 2 more already backfilled sheets.
Christine Biesgen: 14:20-15:15, first backfilled form ever took 10 mins incl minimal instruction, second took 11 min.
Jenna Hounslow, Len Estrade: 20 mins, each one datasheet, feedback discussion.
Wrote up below change requests, in bed by 2100.

Feedback
Should re-order paper datasheet to follow tagging protocol (Meta, PIT, FT, Biopsy, Meas, Dmg, Nest)
Consider cutting down both sheet and form to skip unused fields
Damage known last, when turtle is returning to water
Tasks
Bigger tasks
[] Make it somehow easier to fill in PIT Left, PIT Right, FT {1.3}{L1..R3}
[] Update paper datasheet to follow tagging workflow and ODK form
[] Add egg count datasheet to turtle tagging
[] Annotate flatback schematic photo as image widget at dmg

XML editing
[] Turn verbose hints into "guidance" https://github.com/getodk/build/issues/238

content_copy


Minimal record
[x] ODK Reporter = ODK username = Datasheet data captured by = person entering data into the tablet.
Handler = defaults to reporter, but edit to the person measuring and tagging. ODK form default "measured by" and "tag handled by" to Handler.
[x] Re-ordered fields

Screen PIT/Flipper tags
Named to include default positions "PIT 1 - Left", "PIT 2 - Right", "PIT 3 - Extra". This should capture the 99% use case including one dud.
[x] Tag status: renamed "tag resighted" to include "tag" in the status to prevent confusion with "this is a resighted turtle".
We don't want to use "old" and "new" tags as this could be confused with the age and condition of tags. A shiny, freshly applied tag, resighed a week later could be interpreted as "hey that looks pretty new".
[x] Tag scars: add "none" to prevent confusion.
[] Enforce 15 character length PIT tag ID.

Nesting event
[x] Nest tag date: full date, defaults to start date. This prevents confusion at data entry and shows the date as already captured.
[x] Nest tag ID hint: Do no include date here. The date shown just above will make this very obvious.

Biopsy
[x] Biopsy sample photo: typo fixed.
[x] Biopsy sample location default to rear left flipper. Completely irrelevant.

Additional sample
[x] Additional sample photo of (delete biopsy) sample - deleted additional sample screen. We have "add tag or sample", but don't expect any extra taken.

[x] Simplify nesting success - dropped superfluous option
[x] add sample, status: add "dud"
[x] turtle morph: simplify accuracy (drop 10cm? drop 1cm?) - removed altogether, import as accuracy nearest 5 mm.
[x] species should toggle "flatback measurements" vs "hawksbill measurements" - not needed after taking out accuracy and being sorted by prio of measurements
[x] PIT never goes into neck, remove option neck? - Could migrate into neck, therefore keep option.
[x] Tag ID hint: capitalisation and whitespace don't matter
[x] dmg type: prefix with category, re-order alphabetically
[x] turtle morph: add "plastron to tail tip", "vent to tail tip", "carapace to tail tip"
[x] dataset image: force portrait? - Mentioned in hint but no way to force camera orientation.

XPath wizardry
[] Update form name to include whether nest or not, whether new or not

Reporting
[] Add summary to report: daily number of nests from tagging = animal encounters and missed tracks = tracks and morning tracks
[] Expand in report: number of missed tracks at start of tagging, number of missed tracks during tagging. Bar chart y=no missed tracks, x=time of day, group=date. Map missed tracks, animation step per day, over sites, popups, marker label time, marker colour species.
[] Create report for Hannah to go on website.

Tue Dec 1
Wrote up use cases start-geopoint and
instanceName.
Form updates.

Use case Turtle Tagging in foraging grounds (Roebuck bay):

Form "Turtle Sighting" > turtle tagged > unlocks "Turtle Tagging" screens (with Roebuck flavour and extras).
Wed Dec 2
1000-1500 Implemented ODK Build issues

Quick wins
Add guidance to Minimal Record: your current location is fine, you will backfill the actual nest location from your own records into the next screen,
Guidance on minus sign at longitude
Change option label "reclinched" to include "tag"
Sort damage types alphabetically, make all category - kind
Datasheet photo: hint: take in daylight next day
Add to flipper tag screen option "seen but couldn't read" with options from tag scars
Barnacles - add field to flipper tag screen

Later basket
Improve workflow "enter manual coordinates"
Make nest_location conditionally required: optional if capture_mode = manual.
Tag status conflates tag lifecycle transition (before vs after) and actions taken on tag (reclinched)
Font size of screen title is too small and the colour is too muted - should be better readable
Can we update a media file to supply volunteer names to TT.xslx while keeping the same form version?
Add pictorial images to options?
Damage type - remove body part from damage type to simplify dmg type

Training
Explain how to enter the minus sign on the android keyboard on Samsung STM280
Explain that for testing, made up data is fine. Only PIT tag numbers
Explain that when backfilling manual location, your recorded location is still required to capture but will not be used.

Feedback
Paper datasheet in the howling wind is a massive hassle. Tablet is as fast as paper.

Thu Dec 3
Last day, last updates, confirmed that forms and methodology work.

Fri Dec 4
0500-0700 Morning walk to cross off tracks. Luke and Flo South, David Z North.
0800 Pack and leave
1000-1100 Ferry
1100-1500 Onslow resport, migraine attack
1500-2000 Flight back
2100 Home
