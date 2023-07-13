.. _data-consumers:

**************
Data consumers
**************

This chapter addresses data consumers.

There are four principal ways to access data and derived data products from WAStD:

* Data export from GUI: filter to taste, hit "CSV" or "XLS" on the top right.
* Data export from Data Curation Portal: filter to location and date, select all, bottom left menu "export to CSV", export.
* Data export from API: see wastdr vignette `Accessing WAStD Data <https://dbca-wa.github.io/wastdr/articles/access.html>`_.
* Automated reporting: Latest date-stamped `folder on SharePoint <https://dpaw.sharepoint.com/sites/theturtles/Shared%20Documents/Forms/AllItems.aspx?viewid=b34c0a22%2Da086%2D4a61%2D9506%2D1e8b66ceccd0&id=%2Fsites%2Ftheturtles%2FShared%20Documents%2F10%20Turtle%20data%20exports>`_ or as shared with you through MS Teams.

Additional data export pathways for admins:
* Shell: Rancher > pod > shell > fab shell > iPython session.
* Database: Rancher > pod > shell > ./manage.py db_shell > psql session.

The main avenue for data consumers are the value-added and well documented reports.
The reports contain an up to date explanation of all exported data products, as well as maps and summary tables.
Most of the insights and summaries a data consumer might want will be in the reports.

The remainder of this page is the older documentation, pending an update of links.

For humans: GUI
===============
This section documents the graphical user interface (GUI).

The GUI aims to give easy to digest insight to managers with
defined questions, and to allow the query and export of data.

Map
---
**Getting there** https://wastd.dbca.wa.gov.au/

**Accessible to** all DBCA staff

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
**Getting there** https://wastd.dpaw.wa.gov.au/animal-encounters/ or click on "Data"

**Accessible to** all DBCA staff

The "Data" tab offers the capacity to filter and view data.
Currently, this part is in devlopment and does not offer all commodities yet.

Data Curation Portal
--------------------
**Getting there** https://wastd.dpaw.wa.gov.au/admin/ or click on "Data Curation Portal"

**Accessible to** authorised Parks & Wildlife staff of group "data entry"

Authorised users (those belonging to WAStD's "data entry" User group)
can access the Data Curation Portal interface under the "Data Curators" tab.

Strandings and tagging encounters are located under
`Animal Encounters <https://wastd.dpaw.wa.gov.au/admin/observations/animalencounter/>`_.

Many questions can be answered with a simple combination of filter criteria, e.g.:

Examples:
* AnimalEncounters https://wastd.dbca.wa.gov.au/admin/observations/animalencounter/
* Filter to Locality and date
* E.g. AE at Caravan Park https://wastd.dbca.wa.gov.au/admin/observations/animalencounter/?area__id__exact=142
* Encounters added before areas/sites were changed/added need to be re-saved to pick up the area/site they're now in
* How many strandings were there in 2015? Select year 2015 in the date facet (top
  left), and "Observation type" stranding in the Filter dropdown (top right).
  https://wastd.dpaw.wa.gov.au/admin/observations/animalencounter/?encounter_type__exact=stranding&when__year=2016
* How many strandings were suspected boat strikes?
  https://wastd.dpaw.wa.gov.au/admin/observations/animalencounter/?cause_of_death__exact=boat-strike&encounter_type__exact=stranding
* How many Flatback turtles were stranded in 2016?
  https://wastd.dpaw.wa.gov.au/admin/observations/animalencounter/?encounter_type__exact=stranding&species__exact=Natator+depressus&when__year=2016

Download filtered list of enc/AE/TNE etc:
* Select all (if more filtered than the initial 100 records that fit on one page, hit "Select all XXX records")
* Bottom menu: export to CSV > Go
* Settings: see <https://django-adminactions.readthedocs.io/en/latest/actions.html#export-as-csv>.
  * Alternative: Export to XLS, Header yes, Use display (whether to export human-readable displayed labels or URL-safe database values).

API preview
-----------
**Getting there** https://wastd.dpaw.wa.gov.au/api/1/ or click on "API"

**Accessible to** DBCA intranet

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

See the R package `wastdr <https://dbca-wa.github.io/wastdr/>`_ for working examples.

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
---------------------------
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
  Save `https://wastd.dpaw.wa.gov.au/api/1/turtle-nest-encounters/?area=19&format=json <https://wastd.dpaw.wa.gov.au/api/1/turtle-nest-encounters/?area=19&format=json>`_
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

Accessing the data in GIS
-------------------------
Selected tables and views of WAStD are published through a GeoServer run by the Office for Information Management, DBCA.
The KMI GeoServer's website `https://kmi.dbca.wa.gov.au/geoserver/web/ <https://kmi.dbca.wa.gov.au/geoserver/web/>`_
sits behind DBCA's SSO, the endpoints support basicauth (username / password).

You can open the endpoints as listed on the KMI's website in any standard-compliant GIS like `Quantum GIS <https://qgis.org/en/site/>`_
or vendor-locked GIS like ESRI ArcGIS.

KMI offers in addition to WAStD's layers a range of all spatial DBCA datasets (CDDP and others) as well as datasets from other agencies (BOM, Landgate and others).

To view WAStD's data offline, the spatial API endpoints offer GeoJSON FeatureCollections (format "json") which can be viewed
directly in standard-compliant GIS like Quantum GIS, and can be exported into vendor-specific formats (e.g. shapefile for ESRI products).

Open WAStD/TSC data in QGIS 3.0.1
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* Layer > Add Layer > WFS
* Create a new connection with settings:
  * Name KMI (or as you please)
  * URL ``https://kmi.dbca.wa.gov.au/geoserver/ows``
  * Authentication: Create configuration with your DBCA username and password, protect with master password
  * WFS options: Version 2 is buggy, use version 1
* Connect
* Search for ``wastd`` to finc WAStD/TSC data layers
* Select and Add layers
* Adjust layer style and save style to file
* Save project (contains layers and styles)

Add other layers as WFS or WMS (choose jpeg for faster rendering) as suitable. Warning: WMS layers slow down project startup.

See the `QGIS docs <https://docs.qgis.org/>`_ on how to
`load a web mapping (WFS, WMS) layer <https://docs.qgis.org/testing/en/docs/training_manual/online_resources/index.html>`_.
