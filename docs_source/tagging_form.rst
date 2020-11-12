Turtle Tagging form design
==========================
Built by: Florian Mayer
Consulted: Ryan Douglas

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


Form workflow
-------------
Prepare devices for tagging
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Early in day
^^^^^^^^^^^^^^^^^^^^^^^^^^^
1. Ensure tablet is fully charged

Checking out tablets
^^^^^^^^^^^^^^^^^^^^^^^^^^^
2. Update username
3. Turn off auto-send for tagging. You can only edit finalized forms while they are not yet uploaded.

In situ: Tagging night
^^^^^^^^^^^^^^^^^^^^^^^^^^^
4. Site Visit Start when on site
5. Turtle Tagging for tagged turtles, Turtle Track or Nest for missed turtles. Backfill forms if bored.
6. Site Visit End when finishing up for the night

Tagging modes:
1. Turtle encountered while nesting.
  a. MinODK while egg laying (waiting phase)
  b. tagging on paper during hot phase.
  c. Backfill when possible. Don't bother with datasheet photo.
  d. If backfilling during night, leave unfinalized.
2. Turtle encountered while returning to water.
  a. Tagging on paper (hot phase)
  b. capture MinODK record in situ once turtle is gone
  c. backfill if time permits
3. ODK unavailable.
  a. All data on paper. GPS in handheld.
  b. Backfill and choose data capture mode "New record".


Next morning
^^^^^^^^^^^^^^^^^^^^^^^^^^^
7. Backfill ODK: Go through "Edit saved forms", open each, find corresponding datasheet, backfill remaining forms, proofread, photograph datasheets (needs daylight).
8. Send finalized forms. Leave tablets in "manual upload mode".
9. Enter data into WAMTRAM.

After import and QA
^^^^^^^^^^^^^^^^^^^^^^^^^^^
9. WAStD: QA typos. Mark changed records as "curated" to prevent data loss. QA reports will assist finding records that need review. We will learn from QA and improve QA helpers this season.




Minimum ODK record
^^^^^^^^^^^^^^^^^^
Minimum record in ODK form "Turtle Tagging" with a nest location, timestamp, the username, and datasheet ID.
Save form as "non finalized" and name after datasheet ID.

Backfill paper to ODK
^^^^^^^^^^^^^^^^^^^^^
Backfill the ODK record from the paper datasheet.
Find record in "Edit saved forms", choose data capture mode "continue here", once light allows photograph paper datasheet, save as finalized. Let record upload.



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
