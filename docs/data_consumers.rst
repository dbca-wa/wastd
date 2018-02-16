.. _data-consumers:

==============
Data consumers
==============

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


.. _data-consumers-api:

For machines: API
=================
**Note** This section is being re-written, as the API is being fine-tuned.

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

The following examples will only work on the DPaW intranet, as the API sits behind
the Departmental firewall (intranet only) until the Single-Sign-On authentication
will work without browsers.

API > JSON > table
------------------
To get started, clone the turtle script `Github repo
<https://github.com/parksandwildlife/turtle-scripts>`_ in your
`RStudio Server <https://rstudio.dpaw.wa.gov.au/>`_.

The workbooks show real-life use cases of downloading data as JSON from the API,
transforming the nested document structure into flat table structures.



.. First code example::
..
..     https://strandings.dpaw.wa.gov.au/api/1/animal-encounters/?format=csv
..
.. This API call will download all AnimalEncounters as flat CSV file. Currently,
.. that CSV file is really weird. We've got a team of highly trained monkeys working
.. on a fix.
.. Nested relationships (e.g. all Observation subgroups) are represented as prefix
.. to column names.


API parameters
--------------
This section shows examples of filtering data server-side through URL parameters.

All stranding encounters (anything that's not "alive and healthy") as web page,
JSON::

    https://strandings.dpaw.wa.gov.au/api/1/animal-encounters/?format=api&health!=alive
    https://strandings.dpaw.wa.gov.au/api/1/animal-encounters/?format=jsonp&health!=alive

All tagging encounters (anything that's exactly "alive and healthy") as web page,
JSON, or CSV::

    https://strandings.dpaw.wa.gov.au/api/1/animal-encounters/?format=api&health=alive
    https://strandings.dpaw.wa.gov.au/api/1/animal-encounters/?format=jsonp&health=alive

The known history of a flipper tag::

    https://strandings.dpaw.wa.gov.au/api/1/tag-observations/?tag_type=flipper-tag&name=WA67541

All encounters with one animal ("WA96394")::

    https://strandings.dpaw.wa.gov.au/api/1/animal-encounters/?name=WA67541

All encounters with animals which names start with "WA9" (note the ``__startswith``
has to be inserted manually)::

    https://strandings.dpaw.wa.gov.au/api/1/encounters/?name__startswith=WA6*

All of these filter queries (anything after the "?") also work through the data curation portal::

    https://strandings.dpaw.wa.gov.au/admin/observations/animalencounter/?health__exact=alive
    https://strandings.dpaw.wa.gov.au/admin/observations/tagobservation/?tag_type=flipper-tag&name=WA67541

Any filter combination, if found useful, can be bookmarked.


Data Analysis
=============

Tag life cycle
--------------
The life cycle of one tag (e.g. a flipper tag) is captured through recorded
encounters along its life cycle stages::

    https://strandings-test.dpaw.wa.gov.au/api/1/tag-observations/?tag_type=flipper-tag&name=WA96394


.. _data-analysis-animal-life-cycle:

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

Re-visiting existing points
===========================
This is the rough-and-ready process to re-visit existing encounters, e.g. tagged nests.

Before we start, let's clarify some terms:

Let's call your **home directory** (Windows - read `Windows home directory <https://en.wikipedia.org/wiki/Home_directory>`_) or **home folder** (Linux) ``HOME``.

If you install Dropbox, it will create a directory/folder in your ``HOME``. We'll refer to this path ``HOME/Dropbox``.

* Install the app `MapIt <https://play.google.com/store/apps/dev?id=9214118068832022925&hl=en>`_ to a tablet.
* Install the app `Dropbox <https://play.google.com/store/apps/details?id=com.dropbox.android&hl=en>`_
  to the same tablet and login with your account.
* Open MapIt and visit all areas of interest to cache the offline maps.

On a desktop computer or on the tablet:

* Download the data from WAStD: e.g. Tracks and nests at Cable Beach Broome:
  Save `https://strandings.dpaw.wa.gov.au/api/1/turtle-nest-encounters/?area=19&format=json <https://strandings.dpaw.wa.gov.au/api/1/turtle-nest-encounters/?area=19&format=json>`_
  as a file called ``nests.geojson``.
  If you have WAStD open in your browser (and are authenticated), the API should not ask for authentication.
* Create the subfolders ``HOME/Dropbox/Apps/MapIt`` and move ``nests.geojson`` there.
* The file **must** now be in ``HOME/Dropbox/Apps/MapIt/nests.geojson``
* The file **must** have the file extension ``.geojson`` (not ``.json`` as WAStD saves).
* The filename (``nests``) is arbitrary.
* Let Dropbox sync the file to the cloud, then you'll see a green tick indicating that the file is synced to your Dropbox cloud storage.

On your tablet:

* Open Dropbox while online. You should find ``Apps/MapIt/nests.geojson`` in your Dropbox app when synced from the Dropbox cloud storage to your tablet's local Dropbox folder.
* Open MapIt on your tablet while online.
* Menu (cheeseburger icon top left) >
  Manage layers >
  Add layer (icon with red plus sign on bottom right) >
  Name the layer as you like ("Nests" or so).
* Tap on the new layer ("Nests"),
  then the "add data" icon (down arrow icon top right),
  tap "Dropbox",
  tap "Geojson files" to expand the files,
  tap on the ``nests.geojson`` file saved from WAStD.
* Use back arrow to go back from the "add layers" screen to MapIt's main map screen.

Now the map (the areas you have visited while online at the respective zoom level)
should be saved for offline use, and the layer "Nests" should show turtle tracks and nests.
Nest tags are shown as labels on the map where given.
The map has a live mode where it follows the current position.

To re-run the process with fresher data:

* Download the data again and save over the file ``Dropbox/Apps/MapIt/nests.geojson``. You can do this directly on the tablet.
* On the tablet, open MapIt, Manage layers, select the "Nests" layer, in options (three vertical dots top right) select "clear" and confirm to remove existing records from the layer, then "import" the fresher data from Dropbox again.