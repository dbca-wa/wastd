# -*- coding: utf-8 -*-
"""
Occurrence functional test suite.

This test suite is a walk-through of the following occurrence business processes:

* [REQ 9] Report a new occurrence: Allow for the recording of occurrence data for each
  species recorded in the system, including textual
  attributes relating to locality, habitat, associated species,
  population, biology, and management context (e.g.
  threats, tenure). Data must be able to be visualised
  spatially, as well as textually, so that outliers can be detected.
* [REQ 10] Allow for Department and non-Department users to submit an occurrence
  report including contextual details described in REQ 9.
  Include spatial data in occurrence reports. Allow for the upload of
  occurrence data recorded in a spreadsheet.
* Spatial mapping of occurrences
* Critical habitat of a species or community: see Taxonomy
* [REQ 7][REQ 17] List, filter, export selection of species or communities, and
  species or community occurrences as spreadsheet and in spatial formats.
  Support the creation of various types of reports in various formats -
  Word, PDF and Excel (and/or shapefile), including:
  * species by various location types
  * species file numbers by category and species group
  * report on any species (not just threatened)
  * report on occurrences/populations/communities using a variety of search criteria
    (e.g. species name, conservation status, Vesting, Region etc.).
* [REQ 11] Allow for the assessment of a submitted occurrence report.
  Only upon approval, the draft report is to be accepted as approved occurrence report.
  Assessing the submitted occurrence reports includes the
  QA and possibly adjustment of the submitted spatial data.
* [REQ 12] Primary storage for species occurrence data is BioSys - won't have. TSC is primary.
* [REQ 14] Admin user able to add/incorporate additional attributes that may be relevant
  to only specific species (e.g. Malleefowl) - won't have. TSC is for common attributes only.
  Malleefowls and friends go to BioSys.
* [REQ 24] Upload shapefiles population boundaries or occurrences or critical habitat
  from regions or external consultants.
  Run through API example, see OCC ETL workbooks.
"""
