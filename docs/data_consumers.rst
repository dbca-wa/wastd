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


All of these filter queries (anything after the "?") also work through the data curation portal::

    https://strandings-test.dpaw.wa.gov.au/admin/observations/animalencounter/?health__exact=alive
    https://strandings-test.dpaw.wa.gov.au/admin/observations/tagobservation/?tag_type=flipper-tag&name=WA96395

Any filter combination, if found useful, can be bookmarked.
