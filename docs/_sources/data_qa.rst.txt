=======
Data QA
=======
This section addresses QA operators, who have two jobs:

* Proofreading: Sharp eyes compare data sheets to entered data and decide when a digital record is equivalent to the written paper datasheet.
* Curating: Subject matter experts make sense of the data and decide when a record is trustworthy.

Proofreading
============
A literate data QA operator can proofread data by simply comparing attached files
to the information present.
If errors are found, data can be updated - WAStD will retain the edit history.
Once the record is deemed "Proofread", the QA operator clicks the transition
"Proofread Encounter".
This step can be reverted by clicking the transition "Require Proofreading Encounter".
WAStD will keep track of each transition.

Curating data
=============
A subject matter expert can review records and e.g. confirm species identification.
Once the expert is satisfied that the record represents accurately the case as
evident from attached pictures, data sheet and communications records, the transition
"Curate Encounter" will mark the encounter as "curated".
The transition can be reversed with "Flag Encounter".

============
Data release
============
This section addresses data publishers, who authorise data release (mark records
as "publication ready") or embargo data (to prevent publication).

The transition "Publish Encounter" will mark the record as ready to be "published", but not
actually release information to the general public. The flag serves simply to
mark a record as "ready to publish".
This transition can be reversed with "Embargo Encounter", which will push the record
back to "curated".


Data QA for turtle track census
===============================
This section addresses the regional turtle monitoring program coordinators, who
conduct training and supervise volunteer data collection.

QA tracks with uncertain species
--------------------------------
Open WAStD's menu "Nests and Tracks" > QA shortlists > Tracks with uncertain species ID > https://wastd.dbca.wa.gov.au/observations/turtle-nest-encounters/?species=cheloniidae-fam
Then filter to your "Locality" Ningaloo (and hit "filter"): https://wastd.dbca.wa.gov.au/observations/turtle-nest-encounters/?area=56&species=cheloniidae-fam

Go through these ~80 records, expand details to reveal photos (if any were taken).
Where you can tell the species from the photos, hit the green QA pencil, change the species, leave a comment if you like, and directly "curate" the TurtleNestEncounter.
Where you can't tell the species, what would you like to do with the species? Leave species at "unknown turtle" and curate? (This way we could exclude those "confirmed unrecoverable" records from the QA shortlist.)
QA links open in new tabs to preserve your position in the track/nest record list.


Data flow of surveys
--------------------
WAStD creates or updates (if existing) one
`Survey <https://wastd.dbca.wa.gov.au/admin/observations/survey/>`_
for each recorded "Site Visit Start".
WAStD guesses the `Site <https://wastd.dbca.wa.gov.au/admin/observations/area/?area_type__exact=Site>`_
from the Site Visit Start's Geolocation.
WAStD tries to find a corresponding "Site Visit End", or else sets the end time to 6 hours
after the start time, and leaves a note in the "comments at finish".

If the data collectors forgot to record a "Site Visit Start", the QA operator has to create
a new Survey with start and end time before and after the recorded Encounters (Track or Treat, Fox Sake).

When a Survey is saved, it finds all Encounters within its start and end time at the given Site
and links them to itself. This link can be seen in the Encounters' field "survey".

Since data collection unavoidably lossy and incomplete due to human error,
QA operators (coordinators) have to:

* Flag training surveys (to exclude their corresponding Encounters from analysis)
* Double-check reporter names to QA WAStD's automated name matching
* Populate "team" from "comments at start" (to allow estimating volunteer hours)
* QA "survey end time" and set to a realistic time where guessed (to allow estimating volunteer hours)

Flag training surveys
---------------------
Surveys can be marked as training surveys by unticking the "production" checkbox.
This allows to exclude training data from analysis.

Remember to "Save and continue editing", "proofread" and "curate" the record to
protect it from being overwritten with the original data.

Double-check reporter names
---------------------------
Filter the Survey list to each of your sites, compare "reported by" with "comments at start".
WAStD leaves QA messages. Surveys requiring QA will have a "NEEDS QA" remark.

QA Survey end time
------------------
The end time can be incorrect for two reasons:

* If the data collector forgot to capture a Site Visit End, WAStD will guess the end time.
* If WAStD's heuristic picked the wrong Site Visit End (likely in absence of the right one),
  the Survey's "end" fields will be populated, but likely wrong.

In the first case, WAStD leaves a "Needs QA" remark in the "Comments at finish" regarding "Survey end guessed",
try to set the end time to a more realistic time.

Where a Survey's ``device_id`` differs from ``end_device_id``, the data collectors either have
switched to the backup device, or WAStD has mismatched the Site Visit End.
Similarly, a different ``[guess_user]`` comment in the Survey's ``start_comments`` and ``end_comments``
can indicate a mismatch.

In the case of a mismatched Site Visit End, simply delete the incorrect information from the Survey's
``end_comments``, save and proofread. Set ``end time`` to a sensible time, ignore the end point.

Populate team
-------------
From "Comments at start" beginning after the [guess_user] QA message, the team is listed.
Excluding the "reporter", add all team members to the "team" field.

This in combination with an accurate Survey end time assists to accurately estimate
the volunteer hours (hours on ground times number of volunteers)
and survey effort (hours on ground).

**Note** Remember to "curate" each updated record to protect it from being overwritten with the original data.
It is not necessary to "proofread" and "curate" unchanged records.

Add missing surveys
-------------------
This currently is a job for the admin: Pivot Encounters without a survey by site and date
and extract earliest and latest Encounter. Buffer by a few minutes, extract Encounter's reporter,
and create missing surveys.

Add missing users
-----------------
If a person is not listed in the dropdown menus, you might need to
`add a User <https://wastd.dbca.wa.gov.au/admin/users/user/add/>`_ for that person.
Use their ``firstname_lastname`` as username, select a password, save, then add the details.

WAStD will create a new user profile at first login for each DBCA staff member, but
the profile will miss the details

Curate records from training days
---------------------------------



For CBB on Oct 25:
All Tracks/Nests:
Open TurtleNestEncounters, filter to area and date.
https://wastd.dbca.wa.gov.au/admin/observations/turtlenestencounter/?area__id__exact=19&when__month=10&when__year=2020
For each record, set species to Hatchback, set any affiliated TurtleNestDisturbanceObservations to "test record" and curate.

All Dist/Pred:
ODK form "Dist/Pred" becomes a WAStD Encounter plus TurtleNestDisturbanceObservation.
ODK form "Track or Nest" becomes a WAStD TurtleNestEncounter plus TurtleNestDisturbanceObservation.

Open TurtleNestDisturbanceObservations, filter to area and date.
https://wastd.dbca.wa.gov.au/admin/observations/turtlenestdisturbanceobservation/?encounter__area__id__exact=19&encounter__when__month=10&encounter__when__year=2020
This list will contain the (now curated and hatchbacked) TurtleNestEncounters from Track or Nest, as well as Dist/Pred forms.
For any record that shows as status "new" or cause not "training": open the link to the Encounter (column "encounter" on the right)
Set species to Hatchback (if it's a TNE), set disturbance cause to "training" and curate Encounter

All MWI:
Open AnimalEncounters, filter to area and date.
https://wastd.dbca.wa.gov.au/admin/observations/animalencounter/?area__id__exact=19&when__year=2020 (no records for CBB Oct 25).
Set species to hatchback and curate.

Productivity tips:
Open individual records in new tabs (middle-click links or Ctrl+click). You can work on the next tab while another tab is still saving. Close tabs by middle-click on tab header or Ctrl+w.
Collapse WAStD form sections by clicking on the blue header, e.g. collapse "Encounter".
"Curate" includes saving the record. No need to "Save and continue editing".

