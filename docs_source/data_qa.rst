=======
Data QA
=======
This section addresses the following steps:

Proofreading
------------
A literate data QA operator can proofread data by simply comparing attached files
to the information present.
If errors are found, data can be updated - WAStD will retain the edit history.
Once the record is deemed "Proofread", the QA operator clicks the transition
"Proofread Encounter".
This step can be reverted by clicking the transition "Require Proofreading Encounter".
WAStD will keep an audit log of each transition.

Curating data
-------------
A subject matter expert can review records and e.g. confirm species identification.
Once the expert is satisfied that the record represents accurately the case as
evident from attached pictures, data sheet and communications records, the transition
"Curate Encounter" will mark the encounter as "curated".
The transition can be reversed with "Flag Encounter".

Data release
------------
A qualified operator can authorise data release (mark records
as "publication ready") or embargo data (to prevent publication).

The transition "Publish Encounter" will mark the record as ready to be "published", but not
actually release information to the general public. The flag serves simply to
mark a record as "ready to publish".
This transition can be reversed with "Embargo Encounter", which will push the record
back to "curated".

QA levels
==========
What does "new", "proofread", and "curated" mean and do? Two things: It primarily protects human edits to records from repeated data imports, which may skip or update existing but unchanged ("new") records. It furthermore shows the confidence we have in the record's completeness, correctness, and consistency.

However, the majority of records don't require any QA edits, and for now remain "new".
We could but do not yet batch-curate existing records (per season and locality) after QA by the respective data custodian.
Reports currently include records of all QA levels.
A log of QA is kept on the `Confluence Wiki <https://dbcawa.atlassian.net/wiki/spaces/TG/pages/932184080/Turtle+Nesting+Data+QA+log>`_.

Productivity tips
=================
* Open individual records in new tabs (middle-click links or Ctrl+click). You can work on the next tab while another tab is still saving. * Close tabs by middle-click on tab header or Ctrl+w.
* Collapse WAStD form sections by clicking on the blue header, e.g. collapse "Encounter".
* "Curate" includes saving the record. No need to "Save and continue editing".

Users
=====

Double-check reporter names
---------------------------
Filter the Survey list to each of your sites, compare "reported by" with "comments at start".
WAStD leaves QA messages. Surveys requiring QA will have a "NEEDS QA" remark.

In addition, review the "QA Users" report, which lists all non-exact matches of username vs WAStD accounts.
Follow instructions within to add any misspellings of existing WAStD Users as their alias.
The next reporting run will pick up User aliases and match them better.

Merge duplicate User profiles
-----------------------------
The data in WAStD has been imported from many different sources.
Import routines have seen improvements, but have in the past created duplicate User profiles,
or faithfully imported duplicate profiles from legacy sources.

Users can be listed and viewed through the front end or the Data Curation Portal.
The front end User detail pages contain linked Surveys and Encounters.
Duplicate User profiles can be merged from Users > Merge Profiles, or from the shortcut on each User's detail card.

Merging profiles will transfer all data linked against the old profile into the new profile, update the new profile (contact details if empty in new and populated on old profile), and add the old profile's username, name, and aliases to the new profile's aliases. This ensures that user matching will match the new profile against records named after the old profile.
Finally, the old profile is marked as "not active", but is retained.

Add missing users
-----------------
At the beginning of the field season, send a spreadsheet of new data enumerators to the admin as per the "QA users" report.
The spreadsheet must contain the following columns:
* name: The full given and surname, as they will write it in the "Username". E.g. "Florian Mayer".
  Roberts and Josephs have to decide whether they're Bob and Joe once and stick with it. Longer is often better.
* email: A valid email address without any further markup. E.g. "Florian.Mayer@email.com".
* phone: A valid phone number, formatted as text, and with the international prefix. E.g. "+61414123456".

If a person is not listed in the dropdown menus, you might need to
`add a User <https://wastd.dbca.wa.gov.au/admin/users/user/add/>`_ for that person.
Use their ``firstname_lastname`` as username, select a password, save, then add the details.

WAStD will create a new user profile at first login for each DBCA staff member, but
the profile will miss the details.

Surveys
=======
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

* Flag training surveys (to exclude their corresponding Encounters from analysis).
* Double-check reporter names to QA WAStD's automated name matching.
* Populate "team" from "comments at start" (to allow estimating volunteer hours).
* QA "survey end time" and set to a realistic time where guessed (to allow estimating volunteer hours).

Flag training surveys
---------------------
Surveys can be marked as training surveys by unticking the "production" checkbox.
This allows to exclude training data from analysis.

Remember to "curate" an edited record to protect it from being overwritten with the original data.

Populate team
-------------
This section describes the field "Team" in a Survey.
From "Comments at start" beginning after the [guess_user] QA message, the team is listed.
Excluding the "reporter", add all team members to the "team" field.

This in combination with an accurate Survey end time assists to accurately estimate
the volunteer hours (hours on ground times number of volunteers)
and survey effort (hours on ground).

**Note** Remember to "curate" each updated record to protect it from being overwritten with the original data.
It is not necessary to "proofread" and "curate" unchanged records.

QA Survey end time
------------------
The end time can be incorrect for two reasons:

* If the data collector forgot to capture a Site Visit End, WAStD will guess the end time
  as 30 minutes after the last Encounter.
* If WAStD's heuristic picked the wrong Site Visit End (likely in absence of the right one),
  the Survey's "end" fields will be populated, but likely wrong.

In the first case, WAStD labels Surveys with "End time reconstructed".

Where a Survey's ``device_id`` differs from ``end_device_id``, the data collectors either have
switched to the backup device, or WAStD has mismatched the Site Visit End.
Similarly, a different ``[guess_user]`` comment in the Survey's ``start_comments`` and ``end_comments``
can indicate a mismatch.

In the case of a mismatched Site Visit End, simply delete the incorrect information from the Survey's
``end_comments``, save and proofread. Set ``end time`` to a sensible time, ignore the end point.


Add missing surveys
-------------------
An admin can re-save all Surveys in batch to adopt any stray Encounters.

An admin can then run "Curators > Reconstruct missing Surveys".
This will create surveys for bundles of Encounters at known sites.

Close duplicate Surveys
-----------------------
Find the "QA duplicate Surveys" table in the report.
This table lists all combinations of site and dates on which more than one Survey exist.
Open each link, decide on which Survey to make production, then hit "make production".
If duplicate Surveys are missed, make sure their duration overlaps.
Adjust start or end time of the missed duplicated, then mark the "good" one as the production Survey again.


Encounters
==========

QA tracks with uncertain species
--------------------------------
* Nests and Tracks > Tracks with `uncertain species ID <https://wastd.dbca.wa.gov.au/observations/turtle-nest-encounters/?species=cheloniidae-fam)>`_, filter to your location, bookmark.
* Review each record, update from photos as far as possible, curate.
* Take notes on systematic errors by individual users or entire programs. Provide these as feedback and re-train as appropriate.

Unsure if nest
--------------
* Nests and Tracks > `Nests with uncertain nesting success <https://wastd.dbca.wa.gov.au/observations/turtle-nest-encounters/?nest_type=track-unsure>`_ > filter to your location, bookmark.
* Review each record, update from photos as far as possible, curate.
* Take notes on systematic errors by individual users or entire programs. Provide these as feedback and re-train as appropriate.


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



