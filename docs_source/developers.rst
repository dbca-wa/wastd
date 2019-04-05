=======================
Developer documentation
=======================

This chapter is targetted at developers and those who would like to understand
the underlying data model.

In this chapter, we will discuss:

* the data model - what data can TSC/ WAStD handle?
* the admin - manual data entry, validation, widgets
* the API - programmatic data retrieval and query
* the custom User app
* remaining modules of the observations app


.. _extend-app:
Extending the application
=========================

ObservationGroup
----------------

TFA, TFL, TEC paper forms contain further observation groups, which
are reviewed and evaluated for trustworthiness separately.

Each group becomes a model in TSC, inheriting from ``occurrences.models.ObservationGroup``.

* Model: add model to ``occurrences.models`` inheriting from ObservationGroup.
* Migration: create, run in dev.
* Form: create form for use in admin and views.
* Admin: add Inline and standalone admin.
* Views: CreateView, UpdateView. DetailView is that of related encounter.
* URLs: create and update URLs. Add ``update_url`` to model.
* Templates: card template for obsgroup model, add "create" link to either CAE/TAE detail template where applicable.
* Tests: Create sample instances, view on detail page. Call create and update urls.
* Docs: Migrate legacy docs on how to fill in the obsgroup sections.
* DevOps: git, docker, deploy, migrate.


.. _data-model:

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


:mod:`taxonomy.models` Module
---------------------------------------

.. automodule:: taxonomy.models
  :members:
  :undoc-members:
  :show-inheritance:



:mod:`conservation.models` Module
---------------------------------------

.. automodule:: conservation.models
  :members:
  :undoc-members:
  :show-inheritance:


:mod:`occurrence.models` Module
---------------------------------------

.. automodule:: occurrence.models
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


.. :mod:`wastd.api` Module
.. ---------------------------------------

.. .. automodule:: wastd.api
..     :members:
..     :undoc-members:
..     :show-inheritance:



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


:mod:`wastd.observations` app
-----------------------------
Remaining modules of the observations package are documented here.

:mod:`wastd.observations.views` Module
---------------------------------------

.. automodule:: wastd.observations.views
  :members:
  :undoc-members:
  :show-inheritance:


===================================
Project delivery: ticking the boxes
===================================
This chapter closes the development circle by pairing functional requirements with
corresponding functional, unit and view tests.
The tests are documented inline with the requirements they cover; the documentation
is extracted in the build process and shown below.

This chapter should read to business owners as a walk-through of their business processes.
Ideally, all requirements from the detailed requirements analysis find their counterpart in the following section.

Tests are structured into:

* Unit tests: the basics
    * data structure (model X must have field Y),
    * model functions (string representation of model X must include field Y)

* View tests: the boring bits
    * Do all pages load?
    * Do named URLs work?
    * Are all required page HTML templates in place?
    * Do all view functions work?

* Functional tests: the meat and potatoes
    * Business logic: following real-world scenarios
    * Permissions: which role can see / do what when?
    * Conditions: what needs to be done and present before a step can be executed?
    * Consequences: what will happen if I hit this button?

Threatened Species and Communities
==================================

Taxonomy
--------
:mod:`taxonomy.tests` Module

.. automodule:: taxonomy.tests.test_api
  :members:
  :undoc-members:

.. automodule:: taxonomy.tests.test_functional
  :members:
  :undoc-members:

.. automodule:: taxonomy.tests.test_unit
  :members:
  :undoc-members:

.. automodule:: taxonomy.tests.test_views
  :members:
  :undoc-members:


Conservation
------------
:mod:`conservation.tests` Module

.. automodule:: conservation.tests.test_functional
  :members:
  :undoc-members:

.. automodule:: conservation.tests.test_unit
  :members:
  :undoc-members:

.. automodule:: conservation.tests.test_views
  :members:
  :undoc-members:


Occurrences
-----------
:mod:`occurrence.tests` Module

.. automodule:: occurrence.tests.test_functional
  :members:
  :undoc-members:

.. automodule:: occurrence.tests.test_unit
  :members:
  :undoc-members:

.. automodule:: occurrence.tests.test_views
  :members:
  :undoc-members:

WA Strandings and WA Sea Turtles
================================

Observations
------------
:mod:`wastd.observations.tests` Module

.. automodule:: wastd.observations.tests
  :members:
  :undoc-members:

Users
-----
:mod:`wastd.users.tests` Module

.. automodule:: wastd.users.tests
  :members:
  :undoc-members:
