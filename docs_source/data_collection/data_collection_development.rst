.. _dc-dev:

===========================
Data collection development
===========================

This chapter provides information for developers of data collection forms and protocols.

Are you a volunteer or staff data collector?
All you need to know is written at :ref:`dc-training`,
but feel free to read more of this documentation.

Are you a data collection admin in charge of maintaining collection devices
(tablets), training data collectors, and uploading the data?
Read :ref:`dc-admin`.


Are you a solution architect, developer or business analyst? Then read on.

Solution architecture and infrastructure
========================================

This section provides a condensed overview of the information management infrastructure behind our digital data collection process.

* Forms are built using the form builder software
  `ODK Build <https://docs.getodk.org/form-design-intro/#drag-and-drop-form-creation>`_ 
  at `build.getodk.org <http://build.getodk.org/>`_.
* Forms are pushed from ODK Build to an instance of the data
  clearinghouse software
  `ODK Central <https://docs.getodk.org/central-intro/>`_ 
  at `odkc.dbca.wa.gov.au <https://odkc.dbca.wa.gov.au/>`_.
* Mobile Android devices (tablets, phablets, smartphones) running
  the data collection software
  `ODK Collect <https://docs.getodk.org/collect-intro/>`_
  are configured to load data collection forms from
  `DBCA's ODK Central server <https://odkc.dbca.wa.gov.au/>`_,
  collect data (offline capable), and submit collected data back to
  DBCA's ODK Central server.
* The data manager (Florian Mayer) uploads data from DBCA's
  ODK Central server to the WA Sea Turtle Database
  `WAStD <https://wastd.dpaw.wa.gov.au/>`_.
* Data anlysts access the WAStD API e.g. using the R package
  `wastdR <https://dbcawa.github.io/wastdr/>`_ to produce insight
  from the collected data.
* Insight is disseminated through the
  `DBCA data catalogue <https://data.dbca.wa.gov.au/>`_ and other internal or public platforms.

See also :ref:`business-process-turtle-tracks`.

The following diagram is also shown at :ref:`data-entry`.

.. image:: https://www.lucidchart.com/publicSegments/view/e903e543-e5b9-4b4e-b05f-035772f5bb36/image.png
    :target: https://www.lucidchart.com/publicSegments/view/e903e543-e5b9-4b4e-b05f-035772f5bb36/image.png
    :alt: Turtle data flow, ideal state


.. image:: https://www.lucidchart.com/publicSegments/view/d7ff2850-5ffc-4ccf-838e-d217ee39eca4/image.png
    :target: https://www.lucidchart.com/publicSegments/view/d7ff2850-5ffc-4ccf-838e-d217ee39eca4/image.png
    :alt: Turtle data flow, current state


.. _lessons-learnt-paper-based-data-capture:

Lessons learnt from paper-based field data collection
=====================================================

Scenario 1: Two tags applied, both tags recorded incorrectly
------------------------------------------------------------
One turtle is encountered in two subsequent nights by two separate teams.

Night 1
^^^^^^^
* Data entry operators "Tim" and "Natalie" were in a rush, tagged turtle with tag "WB7326", but
  recorded next tag "WB7330" on tag dispenser as "applied new".
* Operators grabbed a PIT tag "900006000144755" from bag and applied it to turtle,
  then went back to the bag, mistook another empty PIT package of tag
  "900006000143470" (hint: with a few missing ID stickers - missing means peeled
  off by sand, or stuck onto another datasheet when applied to a turtle)
  for the package of the just applied tag "...755" and recorded "...470" incorrectly
  as "applied new".
* Team 1 measure CCL

Night 2
^^^^^^^
* Second team "Spud" and "Coral" encounter the same turtle with left flipper tag "WB7326"
* They scan for PIT tag, find and record "...755"
* They apply and record another flipper tag "WB7384" on right flipper
* They measure CCL and CCW

The aftermath
^^^^^^^^^^^^^
* Team leader "Spud" wants to lookup tag history "WB7326", suspecting the turtle
  might originate from different nesting location, based on the fact that the
  turtle was already tagged. Most likely, seeing a tagged turtle this early in the
  tagging season means that the tag has been applied elswhere earlier.
* The tag is not in the tagging database. This is unexpected.
* Data curator realises that the tag is from the tag series allocated to the current
  field trip. This means that the tag must have been applied new within the past
  days, and the corresponding datasheet must be present in the field office.
* Data curator spends the next half hour manically trying to find the datasheet
  referencing the application of tag "WB7326".
* Data curator questions correctness of first datasheet's tag ID.
* Day 1's datasheet is the only potentially matching candidate with similarities
  to day 2's datasheet: CCL within 3mm, one tag on front left flipper.
* Data curator decides that at least one of two datasheets is incorrect.
* Data curator locates "WB7330" in one of the tagging backpacks. This means that
  datasheet 1's flipper tag ID must be incorrect.
* Data curator infers based on similar body length and position of single flipper
  tag, datasheet 1 and 2 refer to the same turtle, and corrects the tag ID on
  datasheet 1 to "WB7326".
* Data curator learns from "Natalie" that the empty PIT tag box had only two
  remaining stickers out of five left. This indicates that the recorded PIT tag ID
  on datasheet 1 is also incorrect. The curator therefore assumes that the PIT
  tag ID of datasheet 2 is correct and adjusts datasheet 1 to report PIT tag ID
  "...755".

Lessons learnt from mobile field data collection
================================================

The choice of methodology can be driven by time availability.

Example: Teams are dropped off on remote beaches and have too little time to
identify and individually record turtle tracks (on paper or on mobile).
In this case, a tally was kept on paper forms, as no specialised mobile app for
tally observations was available yet. Now such a form has been built.


.. _geolocation-and-wifi:

GPS location and WiFi
=====================
Android devices can set the location mode (System settings) to use WiFi + network + GPS, WiFi + network only, or GPS only.

A particularity of the guest WiFi network used for all tablets on DBCA campuses is that this WiFi network
does NOT provide a geolocation at all. If a tablet is therefore set to location mode "WiFi + GPS" and used
indoors (no GPS signal), the ODK Collect geolocation will time out on (not) getting a location estimate
from the guest WiFi at DBCA. This problem does not exist with other WiFi networks we tested.

Therefore, all training must happen outdoors. The location mode can be set to "WiFi + GPS" or "GPS only", but
tablets must have a clear view of the sky.

All devices get a good GPS signal on beaches outside of WiFi range, independent on location mode.

This insight was derived from testing devices in the field (beaches from Ningaloo, Karratha to Broome)
and DBCA offices (Exmouth, Karratha, Broome, Perth) and non-DBCA locations over seveal months.

.. _device-shootout:

Devices shoot-out
=================
Hands-on field testing at Thevenard and Barrow Islands Nov/Dec 2016.

General notes
-------------
* There are not many rugged cases available for low end, older or exotic devices
* $70 charger with 6 USB outlets replaces the Great Charger Kelp Forest
* $80 15Ah battery packs provide backup power
* $5 neoprene sleeves protect every device against bumps, scratches and sand
* $5 whiteboards plus whiteboard marker, placed in geotagged photo of any random
  observation are the best way to capture opportunistic observations

Samsung Galaxy S2 9.7"
----------------------
* $700 device, $150 rugged case, $50 64GB SD
* Office sleeves available in store, rugged cases only available online
* GPS fix ~ 10 sec to below 5m accuracy
* 64 GB internal storage is plenty for data collection
* Battery life excellent
* Screen excellent resolution and daylight readability
* System fast and snappy
* Android 6.0.1
* Large size is excellent to review visualisations and read
* (-) Larger size (A4 page) requires two hands to hold
* (-) too expensive to distribute widely or use in extreme conditions
* (-) compass bearing measurements vary wildly between four identical devices

Samsung Galaxy S2 8"
--------------------
* $550 device, $150 rugged case, $50 64GB SD
* Fits in 8" sleeve, can be balanced on one hand while operating with other.
* Same pros and cons as 9.7" version, plus:
* Size is on the border of one and two hand hold (depending on hand size).
* 32 GB internal storage is still plenty for data collection.
* (-) still too expensive to distribute widely or use in extreme conditions.

Samsung Galaxy Tab A 7"
-----------------------
* $160 device, $30 plastic shell, $50 64GB SD
* Fits in 7" sleeve, large trouser pocket, can be held securely in one hand.
* Rugged cases available in store at time of writing.
* Decidedly slower and laggier performance than flagship S2.
* (XXX) GPS unacceptably slow.
* (-) 8GB internal storage is too small to collect data.
* (-) Android 5.1.1 means external SD chip does not format as internal storage.

Lenovo Tab 3 7" TB3-730F
------------------------
* $100 device, $50 64GB SD
* No cover in store, but device is splash-resistant.
* Fits in 7" sleeve, trouser pocket, can be held securely in one hand.
* Very fast GPS fix, faster than Samsung S2, slower than a Moto G4+ phone.
* Best cost-benefit for handing out in bulk.
* (-) Being phased out as of early 2018, replaced by TB-7304F.

Lenovo Tab 7 Essential TB-7304F
-------------------------------
* Successor to the TB3-730F.
* Beautiful performance, low price.
* Lives longer with silicone shell and screen protector.
* Cheap rugged case options available on eBay.
* (-) Being phased out as of late 2018, replaced by (GPS-less = useless) TB7104F.

Lenovo Tab E7
-------------
* Successor to the TB-7304F.
* (XXX) Does not have a GPS chip. Does not advertise lack of GPS anywhere on packaging.
* Cannot use for ODK Collect.

Moto G4 Plus phone
------------------
* $400 device, $4 plastic shell, $50 SD
* Cheap rugged case options available on eBay.
* Very good mid-range 5" Android phone
* Fast GPS fix (~4-5 sec outdoors)
* Dual SIM
* Data collection works nicely
* Good option for work phone for front-line staff at time of writing (Dec 2016)

Moto G6 phone
-------------
* $388 in 2018.
* Successor to Moto G4/G4+.
* Cheap rugged case options available on eBay.
* Works perfectly fine with ODK Collect.


Samsung Galaxy Tab A 8" 2019
----------------------------
* Our winner and mainstay of our current device fleet.
* Fast GPS.
* Good battery life.
* Good size.
* Affordable: AUD 250 with AUD 30 Poetic silicone case and AUD 10 screen protector.
* Night mode and sufficient display dimming for use at night.

General observations
--------------------
* All devices were daylight-readable.
* Screen protectors, especially the non-sticky plastic sheets from rugged cases,
  tend to decrease the contrast a bit.
* Polarising sunglasses and (polarised) device screens cancel each other out
  at certain angles, so that the display appears to blacken.
* All devices had sufficient battery life to support hours of data collection.
* Operation in harsh environments was against expectations no problem:
  walking along sandy beaches in daylight, sweaty fingers, flying sand.
* Large devices in rugged cases in full sun can overheat to the point of auto-shutdown.
  Hold them in your own shade when operating and out of the sun when not.
* External battery packs extend time between wall power charging.
* Best low-cost field device: Lenovo Tab 3. Runner-up: Samsung S2 8".
* Strong case against Galaxy Tab A (slow GPS, low internal storage,
  old OS version) and of course devices without GPS chip.

.. _cost-benefit-analysis-digital-data-capture:

Cost-benefit analysis for digital data collection
=================================================
Digital data collection provides systematic advantages over paper-based
data collection, as it skips several work-intensive, error-prone steps
in the data life cycle.

Paper-based data collection
---------------------------

Filling in a paper data sheet
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* Error sources: typos, illegible or rushed handwriting, invalid values, fields
  incorrectly filled or skipped.
* Breaking the analog-digital barrier multiple times is costly and error prone:
  GPS, PIT tag reader, barcodes for samples etc.
* Associating media to records is labourious and error-prone

Digitising a paper data sheet
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Data collected on paper has to be read (interpreting handwriting correctly),
mentally mapped from datasheet to electronic form, and typed off (correctly) by
the data entry operator.

Proof-reading a digital record against paper data sheet
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
A second person, acting as proofreader, has to reproduce the same mental effort
to map the paper data sheet to the electronic form and correct any errors they find.


Digital data collection
-----------------------
Digital forms can offer dropdown menus with pre-defined values to reduce sources
of error.

Digital data capture devices can reliably and easily record and associate
location and take photos. Compare pressing a "record location" button to taking
a GPS point, reading, understanding, typing, and confirming 15 digits under time
pressure, sleep deprivation and harsh environmental conditions.

Data collected digitally enters the system as "proofread", eliminating two laborious
and error-prone steps requiring human interaction.
In addition, the data is available to QA straight away, possibly creating a
tighter error-checking loop.

Re-thinking datasheets
----------------------
Each field in the data sheets has been, and should continue to be questioned:

* Is this information used in any of the analytical outputs?
* Does this information serve any QA purpose?
* Is this information used to derive other information, e.g. deformities being
  used to identify a resighted, untagged animal?
* Will anyone in the foreseeable future require this information?
