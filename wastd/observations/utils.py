# -*- coding: utf-8 -*-
"""Observation untilities."""
import os
import json
from pprint import pprint

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist
from django.utils.dateparse import parse_datetime

from wastd.observations.models import (
    Encounter, AnimalEncounter, LoggerEncounter, TurtleNestEncounter,
    TurtleNestDisturbanceObservation, MediaAttachment,
    NEST_AGE_CHOICES, NEST_TYPE_CHOICES, OBSERVATION_CHOICES
    )


def allocate_animal_names():
    """Reconstruct names of Animals from their first allocated Flipper Tag.

    Names are inferred as the first ever allocated flipper tag ID and written
    to each Encounter. Note this can include non-AnimalEncounters, such as
    incidents of tag returns, post-mortem necropsies and other incidentes related
    to an absent animal.

    Algorithm:

    * Find list of new captures (AnimalEncounters with at least one newly
      allocated FlipperTag and no other existing, resighted tags)
    * For each new capture, get the primary flipper tag name as animal name
    * Set the animal name of this and all related Encounters
    """
    ae = [a.set_name_and_propagate(a.primary_flipper_tag.name)
          for a in AnimalEncounter.objects.all() if a.is_new_capture]
    le = [a.save() for a in LoggerEncounter.objects.all()]
    return [ae, le]


def symlink_one_resource(t_dir, rj):
    """Symlink photographs of a resource JSON ``rj`` to a temp dir ``t_dir``."""
    if "photographs" in rj and len(rj["photographs"]) > 0:
        # Once per encounter, create temp_dir/media_path
        media_path = os.path.split(rj["photographs"][0]["attachment"])[0]
        print("pre_latex symlinking {0}".format(media_path))
        dest_dir = os.path.join(t_dir, "tex", media_path)
        os.makedirs(dest_dir)
        print("pre_latex created {0}".format(str(dest_dir)))

        for photo in rj["photographs"]:
            # Once per photo, symlink file to temp_dir
            src = photo["filepath"]
            rel_src = photo["attachment"]
            dest = os.path.join(t_dir, "tex", rel_src)
            if os.path.lexists(dest):
                # emulate ln -sf
                os.remove(dest)
            os.symlink(src, dest)
    else:
        print("No photographs found.")


def symlink_resources(t_dir, data):
    """Symlink photographs from an OrderedDict ``data`` of Encounters to a temp dir.

    ``data`` can be an OrderedDict of either:
    - a GeoJSON FeatureCollection of Encounters (rest_framework.gis serializer)
    - a GeoJSON Feature of one Encounter
    - a JSON list of Encounters (rest_framework model serializer)
    - a JSON dict of one Encounter
    """
    d = json.loads(json.dumps(data))
    if "type" in d.keys():

        if d["type"] == "FeatureCollection":
            print("Symlinking photographs of a GeoJSON FeatureCollection")
            [symlink_one_resource(t_dir, f["properties"]) for f in d["features"]]

        elif d["type"] == "Feature":
            print("Symlinking photographs of a GeoJSON Feature")
            symlink_one_resource(t_dir, d["properties"])

    elif "photographs" in d.keys():
        print("Symlinking photographs of a JSON object")
        symlink_one_resource(t_dir, d)
    else:
        print("Symlinking photographs of a list of JSON objects")
        [symlink_one_resource(t_dir, enc) for enc in d]


#------------------------------------------------------------------------------#
# Data import from ODK Aggregate
# TODO create and use writable API
#
def guess_user(un):
    """Find exact or fuzzy match of username, or create User.

    In order, return:

    * A user with username `un`, or
    * a user with username `icontain`ing the first five characters of `un`, or
    * a new user with username `un`.

    Arguments

    un A username

    Returns
    An instance of settings.AUTH_USER_MODEL
    """
    User = get_user_model()

    try:
        usr = User.objects.get(username=un)
        msg = "Username {0} found by exact match: returning {1}"
    except ObjectDoesNotExist:
        try:
            usr = User.objects.get(username__icontains=un[0:4])
            msg = "Username {0} found by fuzzy match: returning {1}"
        except ObjectDoesNotExist:
            msg = "Username {0} not found: created {1}"
            usr = User.objects.create(username=un, name=un)

    print(msg.format(un, usr))
    return usr


def map_values(d):
    """Return a dict of ODK:WAStD dropdown menu choices for a given choice dict.

    Arguments

    d The dict_name, e.g. NEST_TYPE_CHOICES

    Returns

    A dict of ODK (keys) to WAStD (values) choices, e.g. NEST_TYPE_CHOICES
    {u'falsecrawl': u'false-crawl',
     u'hatchednest': u'hatched-nest',
     u'nest': u'nest',
     u'successfulcrawl': u'successful-crawl',
     u'tracknotassessed': u'track-not-assessed',
     u'trackunsure': u'track-unsure'}
    """
    return {k.replace("-", ""): k for k in dict(d).keys()}


def tx_odk(k, m):
    """
    """
    return m[k]

def import_one_record_tc010(r, m):
    """Import one ODK Track Count 0.10 record into WAStD.

    Arguments

    r The record as dict
    m The mapping of ODK to WAStD choices
    """

    src_id = r["instanceID"]

    new_data = dict(
        source="odk",
        source_id=src_id,
        where=Point(r["observed_at:Longitude"], r["observed_at:Latitude"]),
        when=parse_datetime(r["observation_start_time"]),
        location_accuracy="10",
        observer=m["users"][r["reporter"]],
        reporter=m["users"][r["reporter"]],
        nest_age=m["nest_age"][r["nest_age"]],
        nest_type=m["nest_type"][r["nest_type"]],
        species=m["species"][r["species"]],
        # habitat=,
        # disturbance
        # comments
        )
    if r["nest_type"] in ["successfulcrawl", "nest", "hatchednest"]:
        new_data["habitat"] = m["habitat"][r["habitat"]]
        new_data["disturbance"] = m["disturbance"][r["disturbance"]]

    if src_id in m["overwrite"]:
        print("Found record {0}, updating...".format(src_id))
        TurtleNestEncounter.objects.filter(source_id=src_id).update(**new_data)
        e = TurtleNestEncounter.objects.get(source_id=src_id)
        # update disturbance observation, photos
    else:
        print("New record {0}, creating...".format(src_id))
        e = TurtleNestEncounter.objects.create(**new_data)
        # create disturbance observation, photos

    e.save()
    pprint(e)

    # TODO download photographs, attach as MediaAttachment
    # TODO TurtleNestDisturbanceObservation


def import_odk(jsonfile, flavour="odk-trackcount-010"):
    """Import ODK Track Count 0.10 data.

    Arguments

    jsonfile A filepath to the JSON exported from ODK Aggregate
    flavour The ODK form with version

    Preparation:

    * https://dpaw-data.appspot.com/ > Submissions > Form "TrackCount 0.10"
    * Export > JSON > Export
    * Submissions > Exported Submissions > download JSON

    Behaviour:

    * Records in JSON that are not in db will be created in db
    * Records in JSON that are in db, but have status NEW (not QA'd yet) will
      be created in db
    * Records in JSON that are in db, but have status **above** NEW (QA'd and
      possibly locally changed) will be ignored

    Example:

        >>> from django.conf import settings
        >>> json_file = os.path.join(settings.STATIC_ROOT, 'data', 'TrackCount_0_10_results.json')
        >>> import_odk(json_file)
    """

    with open(jsonfile) as df:
        d = json.load(df)
        print("Loaded {0} records from {1}".format(len(d), jsonfile))

    # generate a fresh mapping... once
    ODK_MAPPING = {
        # some values can be derived
        "nest_age": map_values(NEST_AGE_CHOICES),
        "nest_type": map_values(NEST_TYPE_CHOICES),

        # some are custom
        "species": {
            'flatback': 'Natator depressus',
            'green': 'Chelonia mydas',
            'hawksbill': 'Eretmochelys imbricata',
            'loggerhead': 'Caretta caretta',
            'oliveridley': 'Lepidochelys olivacea',
            'leatherback': 'Dermochelys coriacea',
            'turtle': 'Cheloniidae fam.'
            },

        "habitat": {
            'abovehwm': 'beach-above-high-water',
            'belowhwm': 'beach-below-high-water',
            'edgeofvegetation': 'beach-edge-of-vegetation',
            'vegetation': 'in-dune-vegetation',
            'na': 'na',
            },
        "disturbance": map_values(OBSERVATION_CHOICES),

        # some have to be guessed
        "users": {u: guess_user(u) for u in set([r["reporter"] for r in d])},
        "keep":  [t.source_id for t in TurtleNestEncounter.objects.exclude(
            status=Encounter.STATUS_NEW).filter(source="odk")],
        "overwrite": [t.source_id for t in TurtleNestEncounter.objects.filter(
            source="odk", status=Encounter.STATUS_NEW)]
        }
    print("\n\nMapping:\n\n")
    pprint(ODK_MAPPING)

    if flavour == "odk-trackcount-010":
        print("Using flavour ODK Track Count 0.10...")
        [import_one_record_tc010(r, ODK_MAPPING) for r in d[0:100]
         if r["instanceID"] not in ODK_MAPPING["keep"]]
        print("Done!")
