=======================
Developer documentation
=======================

This chapter is targetted at developers and those who would like to understand
the underlying data model.

In this chapter, we will discuss:

* the data model - what data can WAStD handle?
* the admin - manual data entry, validation, widgets
* the API - programmatic data retrieval and query
* the custom User app
* remaining modules of the observations app

Data model
==========
WAStD is designed to handle biological
observations of any kind which happen during an encounter.

Both Encounters and Observations are polymorphic (database table inheritance)
and share one primary key, while allowing for different fields for child models.

E.g., AnimalEncounters are Encounters (where, when, observed by, recorded by)
with an Animal (species, sex, maturity, health). The combination of Animal
attributes can determine which subsequent Observations are required.

Following this "mix&match" approach, e.g. an AnimalEncounter with a dead turtle
will be a "Turtle Stranding" encounter, requiring TurtleMorphometricObesrvations,
DistinguishingFeatureObservations, TurtleDamageObservations etc.

An AnimalEncounter with a nesting (= female, mature) turle will be a "Turtle
Tagging" encounter, which requires a TurtleNestObservation, plus the above
types of observations.

Both encounters will share MediaAttachments (photos, scanned field data sheet)
and (if appropriate) TagObservations (flipper / PIT / satellite tags, biopsy
samples etc.).

.. image:: datamodel.png
     :alt: WAStD data model

:mod:`wastd.observations.models` Module
---------------------------------------

.. automodule:: wastd.observations.models
 :members:
 :undoc-members:
 :show-inheritance:


Admin
=====
We're using a nicely styled admin to let trained data entry operators and
curators add and update data.

Also, data analysts can search, filter, and export data from here.


:mod:`wastd.observations.admin` Module
---------------------------------------

.. automodule:: wastd.observations.admin
    :members:
    :undoc-members:
    :show-inheritance:


API
===
The API is intended for programmatic access to data, mainly to batch-import
and batch-export.


:mod:`wastd.api` Module
---------------------------------------

.. automodule:: wastd.api
    :members:
    :undoc-members:
    :show-inheritance:


The rest
========
This concludes the documentation of the key features.
The following sections document the remaining modules for completeness' sake.

:mod:`wastd.users` app
----------------------
WAStD's custom user package, courtesy of pydanny's django project template.

:mod:`wastd.users.admin` Module
---------------------------------------

.. automodule:: wastd.users.admin
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`wastd.users.views` Module
---------------------------------------

.. automodule:: wastd.users.views
    :members:
    :undoc-members:
    :show-inheritance:


:mod:`wastd.users.tests` Module
---------------------------------------

.. automodule:: wastd.users.tests
    :members:
    :undoc-members:
    :show-inheritance:


:mod:`wastd.observations` app
-----------------------------
Remaining modules of the observations package are documented here.

:mod:`wastd.observations.views` Module
---------------------------------------

.. automodule:: wastd.observations.views
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`wastd.observations.tests` Module
---------------------------------------

.. automodule:: wastd.observations.tests
    :members:
    :undoc-members:
    :show-inheritance:
