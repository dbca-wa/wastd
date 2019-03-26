# -*- coding: utf-8 -*-
"""
Taxonomy functional test suite.

This test suite is a walk-through of the following taxonomy business processes:

* List, filter, export selection of species or communities
* Traverse phylogeny of a taxon
* Traverse name history of a taxon (older / newer names)
* [WACensus] Create new taxon
* [WACensus] Create xref
* [WACensus] Change xref
* [WACensus] View xref change history
* What if a taxon's phylogenic or name history sibling is conservation listed?
* [REQ 5] Include the following dashboard pages:
* Dashboard of all species included in the system
* Dashboard of all lists of threatened or priority species
* Dashboard of all occurrence reports (draft or approved) per species
* Filter the data shown on the dashboard pages by clicking a location on a map,
  on species file number or species group
* [REQ 19] Enable the user to choose authoritative names from WACensus. (= select from dropdowns).
  Allow for temporarily entering species names not yet been included in the
  species master list (WACensus) in use by the Department (i.e. informal or phrase names).
  This is to facilitate batch upload of data from sources that may not have authoritative names.
  Align entered species with the species master list once the species has been added to the master list.
"""
