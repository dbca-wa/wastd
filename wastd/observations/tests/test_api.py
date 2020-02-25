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
# Get Auto token from profile
# curl  -H 'Authorization: Token XXX' -d "source=10&source_id=85464&permit_type=kermit&sample_type=blood-sample&sample_destination=department&sample_label=test&obstype=PhysicalSample" http://localhost:8220/api/1/occ-observation/


