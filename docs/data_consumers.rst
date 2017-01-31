==================
Data consumers
==================
This chapter addresses data consumers.

For humans: GUI
===============
This section documents the graphical user interface (GUI).

The GUI aims to give easy to digest insight to managers with
defined questions, and to allow the query and export of data.

There are four ways of viewing data: on a map, as a data table, (only with special
privileges:) through the admin interface ("backstage"), and through the API preview.

Map
---
**Getting there** https://strandings.dpaw.wa.gov.au/
or click on "WA Strandings Database WAStD"

**Accessible to** all Parks & Wildlife staff

WAStD's homepage displays (currently all) records on a map.

Encounters of any kind are displayed as place markers.
Click on any record to see a popup with a summary and links to view- more details.

The "edit" button indicates the record's QA status and allows data entry operators
to view and update details.

Named animals displayed a link (e.g. ``WA1234``) to their known life history,
which consists of all recorded encounters with this animal.

Furthermore, each tag on the animal features a link to a list to the full tag
history.

Data
----
**Getting there** https://strandings.dpaw.wa.gov.au/animal-encounters/ or click on "Data"

**Accessible to** all Parks & Wildlife staff

The "Data" tab offers the capacity to filter and view data.
Currently, this part is in devlopment and does not offer all commodities yet.

Backstage
---------
**Getting there** https://strandings.dpaw.wa.gov.au/admin/ or click on "Backstage"

**Accessible to** authorised Parks & Wildlife staff of group "data entry"

Authorised users belonging to WAStD's "data entry" group can access the admin
interface under the "backstage" tab.

Strandings and tagging encounters are located under
`Animal Encounters <https://strandings.dpaw.wa.gov.au/admin/observations/animalencounter/>`_.

Many questions can be answered with a simple combination of filter criteria, e.g.:

* How many strandings were there in 2015? Select year 2015 in the date facet (top
  left), and "Observation type" stranding in the Filter dropdown (top right).
  https://strandings.dpaw.wa.gov.au/admin/observations/animalencounter/?encounter_type__exact=stranding&when__year=2016
* How many strandings were suspected boat strikes?
  https://strandings.dpaw.wa.gov.au/admin/observations/animalencounter/?cause_of_death__exact=boat-strike&encounter_type__exact=stranding
* How many Flatback turtles were stranded in 2016?
  https://strandings.dpaw.wa.gov.au/admin/observations/animalencounter/?encounter_type__exact=stranding&species__exact=Natator+depressus&when__year=2016

The result of any combination of filter criteria is a list of Animal Encounters,
which can be exported to XLS or CSV:

* Select all (checkbox in table header)
* Admin actions (bottom left): Export to XLS / CSV (choose) > Go
* Options: header (includes header row), use display (uses human-readable labels
  instead of terse yet legible database values), columns (deselect the voluminous
  HTML representation) > Export > XLS / CSV is downloaded.

API preview
-----------
**Getting there** https://strandings.dpaw.wa.gov.au/api/1/ or click on "API"

**Accessible to** DPaW intranet

Data analysts will likely want to cut out the manual filter and download process described
above, and consume (filtered) data programmatically. This can be done with the API.
WAStD's API features a human-readable preview with the same filters as the "backstage"
admin interface. This facilitates a user-friendly, trial-and-error way of quickly
building the desired API query. To learn more about the API, read on.


For machines: API
=================
This section will document the application programming interface (API).

The API aims to serve programmers to batch-upload data,
and to serve analysts to query and read data from analytical
frameworks like R or Python.

Talking points:

* django-rest-framework
* API docs
* coreapi and its command line interface
* authentication

Working examples:

* Reading all Animal Observations into a data.frame in R
* Uploading one Animal Observation from R and Python

The following examples will only work for DPaW staff, as the API sits behind
the Departmental Single-Sign-On authentication.

First code example::

    https://strandings.dpaw.wa.gov.au/api/1/animal-encounters/?format=csv

This API call will download all AnimalEncounters as flat CSV file.
Nested relationships (e.g. all Observation subgroups) are represented as prefix
to column names.

All stranding encounters (anything that's not "alive and healthy") as web page,
JSON, or CSV (will download)::

    https://strandings.dpaw.wa.gov.au/api/1/animal-encounters/?format=api&health!=alive
    https://strandings.dpaw.wa.gov.au/api/1/animal-encounters/?format=jsonp&health!=alive
    https://strandings.dpaw.wa.gov.au/api/1/animal-encounters/?format=csv&health!=alive

All tagging encounters (anything that's exactly "alive and healthy") as web page,
JSON, or CSV::

    https://strandings.dpaw.wa.gov.au/api/1/animal-encounters/?format=api&health=alive
    https://strandings.dpaw.wa.gov.au/api/1/animal-encounters/?format=jsonp&health=alive
    https://strandings.dpaw.wa.gov.au/api/1/animal-encounters/?format=csv&health=alive

The known history of a flipper tag::

    https://strandings.dpaw.wa.gov.au/api/1/tag-observations/?tag_type=flipper-tag&name=WA96394

All encounters with one animal ("WA96394")::

    https://strandings.dpaw.wa.gov.au/api/1/animal-encounters/?name=WA96394

All encounters with animals which names start with "WA9" (note the ``__startswith``
has to be inserted manually)::

    https://strandings.dpaw.wa.gov.au/api/1/encounters/?name__startswith=WA9*

All of these filter queries (anything after the "?") also work through the data curation portal::

    https://strandings.dpaw.wa.gov.au/admin/observations/animalencounter/?health__exact=alive
    https://strandings.dpaw.wa.gov.au/admin/observations/tagobservation/?tag_type=flipper-tag&name=WA96395

Any filter combination, if found useful, can be bookmarked.


Data Analysis
=============

Tag life cycle
--------------
The life cycle of one tag (e.g. a flipper tag) is captured through recorded
encounters along its life cycle stages::

    https://strandings-test.dpaw.wa.gov.au/api/1/tag-observations/?tag_type=flipper-tag&name=WA96394


Animal life cycle
-----------------
An animal's identity can be reconstructed from overlapping sightings of a set of tags.
The following table demonstrates the connection between encounters and tag
observations. Tag orders, nesting / tagging encounters, stranding observations
and tag returns (and possibly encounters from other occations) form the complete
picture of one animal and all related identifying tags.

As an important difference to the existing WAMTRAM tagging database, the life
cycle of tags and animals is reconstructed from *reports of observations*.

Thus, all data about one animal could look like this:

================== ========= ============== ============== ========================
Encounters         Occasion  Tag WA001      Tag WA002      Tag WA003
================== ========= ============== ============== ========================
Encounter        7 order     ordered
Encounter        8 order                    ordered
Encounter        9 order                                   ordered
AnimalEncounter 11 nesting   attached
AnimalEncounter 12 nesting   recaptured     attached
AnimalEncounter 13 nesting   tag scar       recaptured     attached
AnimalEncounter 14 nesting   tag scar       not observed   recaptured
AnimalEncounter 15 stranding tag scar       recaptured     removed from dead animal
Encounter       16 return                                  returned
================== ========= ============== ============== ========================

WAStD will reconstruct the fact that these encounters happened with the same
animal from shared tags (following rows) and their tag history (following columns).

The first ever applied flipper tag name will be used as the animal's name, and
saved on each encounter. This allows to quickly retrieve or search encounters
of a particular animal.

Pressing "Update Names" will reconstruct names for all animals.

Three simple lines of R code will consume Animal Encounters from the WAStD API
and transform them into the format required for e.g. program MARK.
A working example is published `here <http://rpubs.com/florian_mayer/wastd-mark>`_.
