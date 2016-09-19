==================
Data consumers
==================
This chapter addresses data consumers.

For humans: GUI
===============
This section will document the graphical user interface (GUI).

The GUI aims to give easy to digest insight to managers with
defined questions, and to allow the query and export of data.


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

    https://strandings-test.dpaw.wa.gov.au/api/1/animal-encounters/?format=csv

This API call will download all AnimalEncounters as flat CSV file.
Nested relationships (e.g. all Observation subgroups) are represented as prefix
to column names.

All stranding encounters (anything that's not "alive and healthy") as web page,
JSON, or CSV (will download)::

    https://strandings-test.dpaw.wa.gov.au/api/1/animal-encounters/?format=api&health!=alive
    https://strandings-test.dpaw.wa.gov.au/api/1/animal-encounters/?format=jsonp&health!=alive
    https://strandings-test.dpaw.wa.gov.au/api/1/animal-encounters/?format=csv&health!=alive

All tagging encounters (anything that's exactly "alive and healthy") as web page,
JSON, or CSV::

    https://strandings-test.dpaw.wa.gov.au/api/1/animal-encounters/?format=api&health=alive
    https://strandings-test.dpaw.wa.gov.au/api/1/animal-encounters/?format=jsonp&health=alive
    https://strandings-test.dpaw.wa.gov.au/api/1/animal-encounters/?format=csv&health=alive

The known history of a flipper tag::

    https://strandings-test.dpaw.wa.gov.au/api/1/tag-observations/?tag_type=flipper-tag&name=WA96394

All encounters with one animal ("WA96394")::

    https://strandings-test.dpaw.wa.gov.au/api/1/animal-encounters/?name=WA96394

All of these filter queries (anything after the "?") also work through the data curation portal::

    https://strandings-test.dpaw.wa.gov.au/admin/observations/animalencounter/?health__exact=alive
    https://strandings-test.dpaw.wa.gov.au/admin/observations/tagobservation/?tag_type=flipper-tag&name=WA96395

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
A working example is published
`here <https://github.com/parksandwildlife/ningaloo-turtle-etl/blob/master/wastd-api.Rmd>`_.
