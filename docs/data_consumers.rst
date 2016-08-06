Accessing the data
==================
This chapter addresses data consumers.

For humans: GUI
---------------
This section will document the graphical user interface (GUI).

The GUI aims to give easy to digest insight to managers with
defined questions, and to allow the query and export of data.


For machines: API
-----------------
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

First code example::

    https://strandings-test.dpaw.wa.gov.au/api/1/animal-encounters/?format=csv

This API call will download all AnimalEncounters as flat CSV file.
Nested relationships (e.g. all Observation subgroups) are represented as prefix
to column names.

See the `Dynamic REST docs <http://dynamic-rest.readthedocs.io/en/latest/>`_ for
help with the query syntax.

Coming soon: working example of StrandNet style queries to the WAStD API.
