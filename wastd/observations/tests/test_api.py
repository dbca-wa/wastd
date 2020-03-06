# -*- coding: utf-8 -*-
"""wastd.observations API test suite."""
from __future__ import unicode_literals

from django.utils import timezone  # noqa

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry
from django.test import TestCase
from django.urls import reverse  # noqa
from model_mommy import mommy  # noqa
from mommy_spatial_generators import MOMMY_SPATIAL_FIELDS  # noqa

from wastd.observations.models import (  # noqa
    NA,
    TAXON_CHOICES_DEFAULT,
    AnimalEncounter,
    Area,
    DispatchRecord,
    DugongMorphometricObservation,
    Encounter,
    Expedition,
    FieldMediaAttachment,
    HatchlingMorphometricObservation,
    LineTransectEncounter,
    LoggerEncounter,
    ManagementAction,
    MediaAttachment,
    NestTagObservation,
    SiteVisit,
    Survey,
    TagObservation,
    TemperatureLoggerDeployment,
    TemperatureLoggerSettings,
    TrackTallyObservation,
    TurtleDamageObservation,
    TurtleMorphometricObservation,
    TurtleNestDisturbanceObservation,
    TurtleNestDisturbanceTallyObservation,
    TurtleNestEncounter,
    TurtleNestObservation,
    PathToSea,
    TurtleHatchlingEmergenceObservation,
    TurtleHatchlingEmergenceOutlierObservation,
    LightSourceObservation
)

# Create an AnimalEncounter from MWI 0.6 data
# Create a TurtleNestEncounter from Track or Nest 1.0 (with TNdist, HatchlingEm, HEoutlier, LightSource, TurtleNestEnc eggs, HatchlingMorph)
# Pred or Dist > Enc with Distobs
# SVE > SiteVisitEnd
# SVS > Survey
# Users


# TSC: AreaEncounter (Taxon/CommunityAE) > ObsGroup (polymorphic)
# enc = AreaEncounter.objects.last() # for source and source_id
# {'source': 10, 'source_id': '94654', 'sample_type': 'blood-sample', 'sample_destination': '', 'sample_label': '[]', 'obstype': 'PhysicalSample'}
# Get Auth token from profile
# curl  -H 'Authorization: Token XXX' -d
# "format=json&source=10&source_id=85464&permit_type=kermit&sample_type=blood-sample&sample_destination=department&sample_label=test&obstype=PhysicalSample"
# http://localhost:8220/api/1/occ-observation/

# curl -X POST -H "Authorization: Token XXX"
# "http://localhost:8220/api/1/occ-observation/?format=json" -d
# "obstype=AssociatedSpecies&source=10&source_id=85464&taxon=26599"

# curl -X POST -H "Authorization: Token XXX"
# "http://localhost:8220/api/1/occ-observation/?format=json" -d
# "obstype=AssociatedSpecies&source=10&source_id=85464&taxon=26599"

# M2M:
# curl -X POST -H "Authorization: Token XXX"
# "http://localhost:8211/api/1/occ-observation/?format=json" -d
# "obstype=AnimalObservation&source=10&source_id=85464&secondary_signs=7&secondary_signs=13"

# File attachments:
# curl -X POST -H "Authorization: Token XXX"
# "http://localhost:8211/api/1/occ-observation/?format=json" -F
# "obstype=FileAttachment" -F "source=10" -F "source_id=85464" -F
# "attachment=@/path/to/file"


# TODO test that occ-observation request parameter filter obsgroup works
# create three separate ObsGroup models, e.g. one each of PhysicalSample, AssociatedSpecies, AnimalObservation.
# Test http://localhost:8220/api/1/occ-observation/ returns all three existing ObsGroup models
# Test
# http://localhost:8220/api/1/occ-observation/?obstype=AssociatedSpecies
# returns only obstype AssociatedSpecies - repeat for other two ObsGroup
# models

# TODO test that ObsGroup Serializers allow empty/missing/NA in R = None in Python non-required fields
# e.g. permit_type is NA in R, arrives as None in Python
# {'source': 10, 'source_id': '4', 'sample_type': 'frozen-carcass', 'sample_destination': 'wa-museum', 'sample_label': '[WA Museum]kmd091', 'permit_type': None, 'obstype': 'PhysicalSample'}
# After adding "required=False" to serializer fields, we can omit a field, e.g. the following request has no permit_type
# [INFO] [API][ObservationGroupPolymorphicSerializer] called with data {'source': 10, 'source_id': '4', 'sample_type': 'frozen-carcass', 'sample_destination': 'wa-museum', 'sample_label': '[WA Museum]kmd091', 'obstype': 'PhysicalSample'}
# [INFO] <class 'occurrence.models.PhysicalSample'>Serializer.create after enc with data {'sample_type': <SampleType: Frozen carcass>, 'sample_destination': <SampleDestination: WA Museum>, 'sample_label': '[WA Museum]kmd091', 'encounter': <TaxonAreaEncounter: Encounter of [24098][PHACAL] (Species) Phascogale calura (Gould) at [Fauna Site] (south-glencoe) South Glencoe on 1991-07-11 16:00:00+00:00 by TSC Admin>}
# [INFO] "POST /api/1/occ-observation/ HTTP/1.1" 201 4214

# BUG however, adding 'permit_type': None fails (but shouldn't - reason, we pipe an entire table from R into API, individual rows could have missing value anywhere)
# [INFO] [API][ObservationGroupPolymorphicSerializer] called with data {'source': 10, 'source_id': '4', 'sample_type': 'frozen-carcass', 'sample_destination': 'wa-museum', 'sample_label': '[WA Museum]kmd091', 'permit_type': None, 'obstype': 'PhysicalSample'}
# [WARNING] Bad Request: /api/1/occ-observation/
# [WARNING] Bad Request: /api/1/occ-observation/
# [WARNING] "POST /api/1/occ-observation/ HTTP/1.1" 400 47


# TurtleNestEncounter
# [{"source": "odk", "source_id": "uuid:673f1150-4d60-4cc5-846a-ebca5a98d4eb", "reporter": 4, "observer": 4, "comments": "Device ID 2856338745efba86",
#     "where": "POINT (114.052963333333 -21.8359983333333)", "location_accuracy": "gps", "when": "2020-02-22 22:36:26", "nest_age": "fresh", "nest_type": "false-crawl", "species": "chelonia-mydas"}]

# Florian to add expected test data for Ash