# -*- coding: utf-8 -*-
"""Observation untilities."""
import csv
import json
import os

from confy import env
from datetime import datetime
from dateutil import parser
# from pprint import pprint
import requests
import shutil

from requests.auth import HTTPDigestAuth
from xml.etree import ElementTree

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import LineString
from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.utils.dateparse import parse_datetime
# from django.utils.timezone import get_fixed_timezone, utc

from wastd.observations.models import *
from wastd.users.models import User


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
    [s.claim_encounters for s in SiteVisit.objects.all()]
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


# -----------------------------------------------------------------------------#
# Data import from ODK Aggregate
# TODO create and use writable API
#
def guess_user(un, default_username="florianm"):
    """Find exact or fuzzy match of username, or create User.

    In order, return:

    * A user with username `un`, or
    * the first or only match of a user with username `icontain`ing the first
      five characters of `un`, or
    * a new user with username `un`.

    Arguments

    un A username
    default_username The default username if un is None

    Returns
    An instance of settings.AUTH_USER_MODEL
    """
    usermodel = get_user_model()

    if un is None:
        un = default_username

    print("Guessing User for {0}...".format(un))

    try:
        usr = usermodel.objects.get(username=un.replace(" ", "_"))
        msg = "   Username {0} found by exact match: returning {1}"

    except ObjectDoesNotExist:
        try:
            usrs = usermodel.objects.filter(username__icontains=un[0:4])

            if usrs.count() == 0:
                usr = usermodel.objects.create(username=un, name=un)
                msg = "  Username {0} not found: created {1}"

            elif usrs.count() == 1:
                usr = usrs[0]
                msg = "  Username {0} found by fuzzy match: only match is {1}"
                usr = usrs[0]

            else:
                usr = usrs[0]
                msg = "  [WARNING] Username {0} returned multiple matches, choosing {1}"

        except TypeError:
            usr = usermodel.objects.first()
            msg = "  [WARNING] Username not given, using admin {1}"

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


def keep_values(d):
    """Return a dict of WAStD:WAStD dropdown menu choices for a given choice dict.

    This is handy to generate a combined ODK and WAStD lookup.

    Arguments

    d The dict_name, e.g. NEST_TYPE_CHOICES

    Returns

    A dict of WAStD (keys) to WAStD (values) choices, e.g. NEST_TYPE_CHOICES
    {u'false-crawl': u'false-crawl',
     u'hatched-nest': u'hatched-nest',
     u'nest': u'nest',
     u'successful-crawl': u'successful-crawl',
     u'track-not-assessed': u'track-not-assessed',
     u'track-unsure': u'track-unsure'}
    """
    return {k: k for k in dict(d).keys()}


def map_and_keep(d):
    """Return the combined result of keep_values and map_values."""
    a = map_values(d)
    b = keep_values(d)
    a.update(b)
    return a


def read_odk_linestring(odk_str):
    """Convert an ODK LineString string to a Django LineString."""
    # in: "-31.99656982 115.88441855 0.0 0.0;-31.9965685 115.88441522 0.0 0.0;"
    # out: Line(Point(115.88441855 -31.99656982) Point(115.88441522 -31.9965685))
    return LineString(
        [Point(float(c[1]), float(c[0])) for c in
         [p.strip().split(" ")
          for p in odk_str.split(";")
          if len(p) > 0]
         ]
        )


def odk_linestring_as_point(odk_str):
    """Return the first point of an ODK LineString as Django Point."""
    point_str = odk_str.split(";")[0].split(" ")
    return Point(float(point_str[1]), float(point_str[0]))


def make_photo_foldername(photo_id):
    """Return a foldername for a given photo ID underneath MEDIA_ROOT."""
    return os.path.join(settings.MEDIA_ROOT, "photos", photo_id)


def dl_photo(photo_id, photo_url, photo_filename):
    """Download a photo if not already done.

    Arguments

    photo_id The WAStD source_id of the record, to which this photo belongs
    photo_url A URL to download the photo from
    """
    print("  Downloading photo...")
    pdir = make_photo_foldername(photo_id)
    if not os.path.exists(pdir):
        print("  Creating folder {0}".format(pdir))
        os.mkdir(pdir)
    else:
        print(("  Found folder {0}".format(pdir)))
    pname = os.path.join(pdir, photo_filename)

    if not os.path.exists(pname):
        print("  Downloading file {0}...".format(pname))
        response = requests.get(photo_url, stream=True)
        with open(pname, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
    else:
        print("  Found file {0}".format(pname))


def handle_photo(p, e, title="Track"):
    """Create a MediaAttachment of photo p to Encounter e with a given title.

    Arguments

    p The filepath of a locally accessible photograph
    e The related encounter (must exist)
    title The attachment's title (default: "Track")
    """
    # Does the file exist locally?
    print("  Creating photo attachment at filepath {0} for encounter {1} with title {2}...".format(p, e.id, title))
    if os.path.exists(p):
        print("  File {0} exists".format(p))
        with open(p, 'rb') as photo:
            f = File(photo)
            # Is the file a dud?
            if f.size > 0:
                print("  File size is {0}".format(f.size))

                # Does the MediaAttachment exist already?
                if MediaAttachment.objects.filter(
                        encounter=e, title=title).exists():
                    m = MediaAttachment.objects.filter(
                        encounter=e, title=title)[0]
                    action = "updated"
                else:
                    m = MediaAttachment(encounter=e, title=title)
                    action = "Created"

                # Update the file
                m.attachment.save(p, f, save=True)
                print("  Photo {0}: {1}".format(action, m))
            else:
                print("  [ERROR] zero size file {0}".format(p))
    else:
        print("  [ERROR] missing file {0}".format(p))


def handle_media_attachment(e, photo_dict, title="Photo"):
    """Download unless already done, then create or update a photo.

    Arguments:

    e An Encounter with an attribute "source_id" (e.source_id)

    {
        "filename": "1485913363900.jpg",
        "type": "image/jpeg",
        "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=..."
    }
    """
    if photo_dict is None:
        print("  ODK collect photo not taken, skipping {0}".format(title))
        return

    pdir = make_photo_foldername(e.source_id)
    pname = os.path.join(pdir, photo_dict["filename"])
    print("  Photo dir is {0}".format(pdir))
    print("  Photo filepath is {0}".format(pname))

    dl_photo(
        e.source_id,
        photo_dict["url"],
        photo_dict["filename"])

    handle_photo(pname, e, title=title)


def handle_turtlenestdistobs(d, e, m):
    """Get or create TurtleNestDisturbanceObservation.

    Arguments

    d A dictionary like
        {
            "disturbance_cause": "human",
            "disturbance_cause_confidence": "expertopinion",
            "disturbance_severity": "na",
            "photo_disturbance": {
                "filename": "1479173301849.jpg",
                "type": "image/jpeg",
                "url": "https://dpaw-data.appspot.com/view/..."
            },
            "comments": null
        }
    e The related TurtleNestEncounter (must exist)
    m The ODK_MAPPING
    """
    print("  Creating TurtleNestDisturbanceObservation...")
    dd, created = TurtleNestDisturbanceObservation.objects.get_or_create(
        encounter=e,
        disturbance_cause=d["disturbance_cause"],
        disturbance_cause_confidence=m["confidence"][d["disturbance_cause_confidence"]],
        disturbance_severity=d["disturbance_severity"],
        comments=d["comments"]
        )
    dd.save()
    action = "created" if created else "updated"
    print("  TurtleNestDisturbanceObservation {0}: {1}".format(action, dd))

    handle_media_attachment(
        e, d["photo_disturbance"], title="Disturbance {0}".format(dd.disturbance_cause))


def handle_turtlenestdistobs31(d, e):
    """Get or create TurtleNestDisturbanceObservation.

    Arguments

    d A dictionary like
        {
            "disturbance_cause": "human",
            "disturbance_cause_confidence": "expert-opinion",
            "disturbance_severity": "na",
            "photo_disturbance": {
                "filename": "1479173301849.jpg",
                "type": "image/jpeg",
                "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=..."
            },
            "comments": null
        }


    "disturbanceobservation": [
      {
        "photo_disturbance": null,
        "disturbance_cause": "pig",
        "disturbance_cause_confidence": "guess",
        "disturbance_severity": "partly",
        "comments": null
      }
    ],

    e The related TurtleNestEncounter (must exist)
    """
    print("  Creating TurtleNestDisturbanceObservation...")
    dd, created = TurtleNestDisturbanceObservation.objects.get_or_create(
        encounter=e,
        disturbance_cause=d["disturbance_cause"],
        disturbance_cause_confidence=d["disturbance_cause_confidence"],
        comments=d["comments"]
        )
    if "disturbance_severity" in d:
        dd.disturbance_severity = d["disturbance_severity"]
    dd.save()
    action = "created" if created else "updated"
    print("  TurtleNestDisturbanceObservation {0}: {1}".format(action, dd))

    handle_media_attachment(
        e, d["photo_disturbance"], title="Disturbance {0}".format(dd.disturbance_cause))


def handle_turtlenestobs(d, e, m):
    """Get or create a TurtleNestObservation and related MediaAttachments.

    Arguments

    d A dictionary containing at least:
    {
        "no_egg_shells": 120,
        "no_live_hatchlings": 13,
        "no_dead_hatchlings": 14,
        "no_undeveloped_eggs": 15,
        "no_unhatched_eggs": 16,
        "no_unhatched_term": 17,
        "no_depredated_eggs": 18,
        "nest_depth_top": 19,
        "nest_depth_bottom": 20,
        "egg_photos": [
            {
                "photo_eggs": {
                    "filename": "1485913363900.jpg",
                    "type": "image/jpeg",
                    "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=..."
                }
            },
            {
                "photo_eggs": {
                    "filename": "1485913376020.jpg",
                    "type": "image/jpeg",
                    "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=..."
                }
            }
        ],
    }

    e The related TurtleNestEncounter (must exist)
    m The ODK_MAPPING
    """
    print("  Creating TurtleNestObservation...")
    dd, created = TurtleNestObservation.objects.get_or_create(
        encounter=e,
        nest_position=m["habitat"][d["habitat"]],
        no_egg_shells=d["no_egg_shells"] or 0,
        no_live_hatchlings=d["no_live_hatchlings"] or 0,
        no_dead_hatchlings=d["no_dead_hatchlings"] or 0,
        no_undeveloped_eggs=d["no_undeveloped_eggs"] or 0,
        no_unhatched_eggs=d["no_unhatched_eggs"] or 0,
        no_unhatched_term=d["no_unhatched_term"] or 0,
        no_depredated_eggs=d["no_depredated_eggs"] or 0,
        nest_depth_top=d["nest_depth_top"] or 0,
        nest_depth_bottom=d["nest_depth_bottom"] or 0
        )
    dd.save()
    action = "created" if created else "updated"
    print("  TurtleNestObservation {0}: {1}".format(action, dd))

    for idx, ep in enumerate(d["egg_photos"]):
        handle_media_attachment(e, ep, title="Egg photo {0}".format(idx + 1))


def handle_turtlenestobs31(d, e):
    """Get or create a TurtleNestObservation and related MediaAttachments.

    Arguments

    d A dictionary containing at least:
    {
        "no_egg_shells": 120,
        "no_live_hatchlings": 13,
        "no_dead_hatchlings": 14,
        "no_undeveloped_eggs": 15,
        "no_unhatched_eggs": 16,
        "no_unhatched_term": 17,
        "no_depredated_eggs": 18,
        "nest_depth_top": 19,
        "nest_depth_bottom": 20,
        "egg_photos": [
            {
                "photo_eggs": {
                    "filename": "1485913363900.jpg",
                    "type": "image/jpeg",
                    "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey="
                }
            },
            {
                "photo_eggs": {
                    "filename": "1485913376020.jpg",
                    "type": "image/jpeg",
                    "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey="
                }
            }
        ],
    }

    e The related TurtleNestEncounter (must exist)
    """
    print("  Creating TurtleNestObservation...")
    dd, created = TurtleNestObservation.objects.get_or_create(
        encounter=e,
        nest_position=d["habitat"],
        no_egg_shells=d["no_egg_shells"] or 0,
        no_live_hatchlings=d["no_live_hatchlings"] or 0,
        no_dead_hatchlings=d["no_dead_hatchlings"] or 0,
        no_undeveloped_eggs=d["no_undeveloped_eggs"] or 0,
        no_unhatched_eggs=d["no_unhatched_eggs"] or 0,
        no_unhatched_term=d["no_unhatched_term"] or 0,
        no_depredated_eggs=d["no_depredated_eggs"] or 0,
        nest_depth_top=d["nest_depth_top"] or 0,
        nest_depth_bottom=d["nest_depth_bottom"] or 0
        )
    dd.save()
    action = "created" if created else "updated"
    print("  TurtleNestObservation {0}: {1}".format(action, dd))

    for idx, ep in enumerate(d["egg_photos"]):
        handle_media_attachment(
            e, ep["photo_eggs"], title="Egg photo {0}".format(idx + 1))


def handle_turtlenesttagobs(d, e, m):
    """Get or create a TagObservation and related MediaAttachments.

    Arguments

    d A dictionary containing at least:
    {
        "status": "resighted",
        "flipper_tag_id": "S1234",
        "date_nest_laid": "2017-02-01",
        "tag_label": "M1",
        "tag_comments": "test info",
        "photo_tag": {
            "filename": "1485913419914.jpg",
            "type": "image/jpeg",
            "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=..."
    },

    e The related TurtleNestEncounter (must exist)
    m The ODK_MAPPING
    """
    if (d["status"] is None and
            d["flipper_tag_id"] is None and
            d["date_nest_laid"] is None and
            d["tag_label"] is None):
        return
    else:
        dd, created = NestTagObservation.objects.get_or_create(
            encounter=e,
            status=m["tag_status"][d["status"]],
            flipper_tag_id=d["flipper_tag_id"],
            date_nest_laid=datetime.strptime(d["date_nest_laid"], '%Y-%m-%d') if d["date_nest_laid"] else None,
            tag_label=d["tag_label"])
        dd.save()
        action = "created" if created else "updated"
        print("  NestTagObservation {0}: {1}".format(action, dd))

    handle_media_attachment(e, d["photo_tag"], title="Nest tag photo")


def handle_hatchlingmorphometricobs(d, e):
    """Get or create a HatchlingMorphometricObservation.

    Arguments

    d A dictionary like
        {
            "straight_carapace_length_mm": 12,
            "straight_carapace_width_mm": 13,
            "body_weight_g": 14
        }
    e The related TurtleNestEncounter (must exist)
    """
    print("  Creating Hatchling Obs...")
    dd, created = HatchlingMorphometricObservation.objects.get_or_create(
        encounter=e,
        straight_carapace_length_mm=d["straight_carapace_length_mm"],
        straight_carapace_width_mm=d["straight_carapace_width_mm"],
        body_weight_g=d["body_weight_g"]
        )
    dd.save()
    action = "created" if created else "updated"
    print("  Hatchling Obs {0}: {1}".format(action, dd))


def handle_loggerenc(d, e):
    """Get or create a LoggerEncounter with photo and nest tag obs.

    If the related TurtleNestEncounter e has a NestTagObservation, an idential
    NTO will be created for the LoggerEncounter. This will allow to traverse
    the list of NestTagObservations by name to link related AnimalEncounters
    (when labelling a nest during a tagging), TurtleNestEncounters (when
    excavating a hatched nest) and LoggerEncounters (when retrieving loggers
    from the excavated, tagged nest).

    Arguments

    d A dictionary like
        {
            "logger_id": "S1235",
            "photo_logger": {
                "filename": "1485913441063.jpg",
                "type": "image/jpeg",
                "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=..."
            }
        }
    e The related TurtleNestEncounter (must exist)
    """
    print("  Creating LoggerEncounter...")
    dd, created = LoggerEncounter.objects.get_or_create(
        source=e.source,
        source_id="{0}-{1}".format(e.source_id, d["logger_id"]))

    dd.where = e.where
    dd.when = e.when
    dd.location_accuracy = e.location_accuracy
    dd.observer = e.observer
    dd.reporter = e.reporter
    dd.deployment_status = "retrieved"
    dd.logger_id = d["logger_id"]

    dd.save()
    action = "created" if created else "updated"
    print("  LoggerEncounter {0}: {1}".format(action, dd))

    handle_media_attachment(dd, d["photo_logger"], title="Logger ID")

    # If e has NestTagObservation, replicate NTO on LoggerEncounter
    if e.observation_set.instance_of(NestTagObservation).exists():
        print("  TurtleNestEncounter has nest tag, replicating nest tag observation on LoggerEncounter...")
        nto = e.observation_set.instance_of(NestTagObservation).first()
        NestTagObservation.objects.get_or_create(
            encounter=e,
            status=nto.status,
            flipper_tag_id=nto.flipper_tag_id,
            date_nest_laid=nto.date_nest_laid,
            tag_label=nto.tag_label,
            )
        nto.save()
        action = "created" if created else "updated"
        print("  NestTag Observation {0} for {1}".format(action, nto))


def handle_turtlenestdisttallyobs(d, e, m):
    """Get or create a TurtleNestDisturbanceObservation.

    Arguments

    d A dictionary like
        {
            "disturbance_cause": "cyclone",
            "no_nests_disturbed": 5,
            "no_tracks_encountered": 4,
            "disturbance_comments": "test"
        }
    e The related TurtleNestEncounter (must exist)
    m The ODK_MAPPING
    """
    print("  Found disturbance observation...")

    dd, created = TurtleNestDisturbanceTallyObservation.objects.get_or_create(
        encounter=e,
        disturbance_cause=d["disturbance_cause"],
        no_nests_disturbed=d["no_nests_disturbed"] or 0,
        no_tracks_encountered=d["no_tracks_encountered"] or 0,
        comments=d["disturbance_comments"]
        )
    dd.save()
    action = "created" if created else "updated"
    print("  Disturbance observation {0}: {1}".format(action, dd))
    e.save()  # cache distobs in HTML


def import_one_record_tt034(r, m):
    """Import one ODK Track or Treat 0.34 record into WAStD.

    The only change vs tt026 is that ODK now allows dashes in choice values.
    The following choices are now are identical to WAStD
    and do not require a mapping any longer:

    * species
    * nest_type
    * habitat
    * disturbance evident
    * disturbance_cause_confidence
    * status (tag status)

    Arguments

    r The record as dict

    m The mapping of ODK to WAStD choices

    Existing records will be overwritten.
    Make sure to skip existing records which should be retained.
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
        nest_age=r["nest_age"],
        nest_type=m["nest_type"][r["nest_type"]],
        species=m["species"][r["species"]],
        # comments
        )
    if r["nest_type"] in ["successfulcrawl", "nest", "hatchednest"]:
        new_data["habitat"] = m["habitat"][r["habitat"]]
        new_data["disturbance"] = r["disturbance"]

    if src_id in m["overwrite"]:
        print("Updating unchanged existing record {0}...".format(src_id))
        TurtleNestEncounter.objects.filter(source_id=src_id).update(**new_data)
        e = TurtleNestEncounter.objects.get(source_id=src_id)
    else:
        print("Creating new record {0}...".format(src_id))
        e = TurtleNestEncounter.objects.create(**new_data)

    e.save()

    handle_media_attachment(e, r["photo_track"], title="Track")
    handle_media_attachment(e, r["photo_nest"], title="Nest")

    # TurtleNestDisturbanceObservation, MediaAttachment "Photo of disturbance"
    [handle_turtlenestdistobs31(distobs, e)
     for distobs in r["disturbanceobservation"]
     if r["disturbance"] and len(r["disturbanceobservation"]) > 0]

    # TurtleNestObservation
    if r["eggs_counted"] == "yes":
        handle_turtlenestobs31(r, e)

    # NestTagObservation
    if r["nest_tagged"]:
        handle_turtlenesttagobs(r, e, m)

    # HatchlingMorphometricObservation
    [handle_hatchlingmorphometricobs(ho, e)
     for ho in r["hatchling_measurements"]
     if len(r["hatchling_measurements"]) > 0]

    # LoggerEncounter retrieved HOBO logger
    [handle_loggerenc(lg, e)
     for lg in r["logger_details"]
     if len(r["logger_details"]) > 0]

    print(" Saved {0}\n".format(e))
    e.save()
    return e


def import_one_record_tt036(r, m):
    """Import one ODK Track or Treat 0.35 or 0.36 record into WAStD.

    The only change vs tt026 is that ODK now allows dashes in choice values.
    The changes to tt034 are differently named track and nest photos.
    The following choices are now are identical to WAStD
    and do not require a mapping any longer:

    * species
    * nest_type
    * habitat
    * disturbance evident
    * disturbance_cause_confidence
    * status (tag status)

    Arguments

    r The record as dict

    m The mapping of ODK to WAStD choices

    Existing records will be overwritten.
    Make sure to skip existing records which should be retained.
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
        nest_age=r["nest_age"],
        nest_type=r["nest_type"],
        species=r["species"],
        # comments
        )
    if r["nest_type"] in ["successful-crawl", "nest", "hatched-nest"]:
        new_data["habitat"] = r["habitat"]
        new_data["disturbance"] = r["disturbance"]

    if src_id in m["overwrite"]:
        print("Updating unchanged existing record {0}...".format(src_id))
        TurtleNestEncounter.objects.filter(source_id=src_id).update(**new_data)
        e = TurtleNestEncounter.objects.get(source_id=src_id)
    else:
        print("Creating new record {0}...".format(src_id))
        e = TurtleNestEncounter.objects.create(**new_data)

    e.save()

    handle_media_attachment(e, r["photo_track_1"], title="Uptrack")
    handle_media_attachment(e, r["photo_track_2"], title="Downtrack")
    handle_media_attachment(e, r["photo_nest_1"], title="Nest 1")
    handle_media_attachment(e, r["photo_nest_2"], title="Nest 2")
    handle_media_attachment(e, r["photo_nest_3"], title="Nest 3")

    # TurtleNestDisturbanceObservation, MediaAttachment "Photo of disturbance"
    [handle_turtlenestdistobs31(distobs, e)
     for distobs in r["disturbanceobservation"]
     if r["disturbance"] and len(r["disturbanceobservation"]) > 0]

    # TurtleNestObservation
    if r["eggs_counted"] == "yes":
        handle_turtlenestobs31(r, e)

    # NestTagObservation
    if r["nest_tagged"]:
        handle_turtlenesttagobs(r, e, m)

    # HatchlingMorphometricObservation
    [handle_hatchlingmorphometricobs(ho, e)
     for ho in r["hatchling_measurements"]
     if len(r["hatchling_measurements"]) > 0]

    # LoggerEncounter retrieved HOBO logger
    [handle_loggerenc(lg, e)
     for lg in r["logger_details"]
     if len(r["logger_details"]) > 0]

    print(" Saved {0}\n".format(e))
    e.save()
    return e


def import_one_record_fs03(r, m):
    """Import one ODK Fox Sake 0.3 record into WAStD.

    The following choices are now are identical to WAStD
    and do not require a mapping any longer:

    * disturbance evident
    * disturbance_cause_confidence

    Arguments

    r The record as dict

    m The mapping of ODK to WAStD choices

    Existing records will be overwritten.
    Make sure to skip existing records which should be retained.
    """
    src_id = r["instanceID"]

    new_data = dict(
        source="odk",
        source_id=src_id,
        where=Point(r["location:Longitude"], r["location:Latitude"]),
        when=parse_datetime(r["observation_start_time"]),
        location_accuracy="10",
        observer=m["users"][r["reporter"]],
        reporter=m["users"][r["reporter"]]
        )

    if src_id in m["overwrite"]:
        print("Updating unchanged existing record {0}...".format(src_id))
        Encounter.objects.filter(source_id=src_id).update(**new_data)
        e = Encounter.objects.get(source_id=src_id)
    else:
        print("Creating new record {0}...".format(src_id))
        e = Encounter.objects.create(**new_data)

    e.save()

    handle_turtlenestdistobs31(r, e)

    print(" Saved {0}\n".format(e))
    e.save()
    return e


def import_one_record_mwi01(r, m):
    """Import one ODK Marine wildlife Incident 0.1 record into WAStD.

    Arguments

    r The record as dict

    m The mapping of ODK to WAStD choices

    Existing records will be overwritten.
    Make sure to skip existing records which should be retained.

    Input: a dict like

    {
    "instanceID": "uuid:2273f52a-276a-4972-bc45-034626a3c278",
    "observation_start_time": "2017-08-15T04:17:31.194Z",
    "reporter": null,
    "observed_at:Latitude": -15.7072566667,
    "observed_at:Longitude": 124.4008183333,
    "observed_at:Altitude": -7.6,
    "observed_at:Accuracy": 5.8,
    "location_comment": null,
    "incident_time": "2017-08-15T04:17:00.000Z",
    "habitat": "beach",
    "photo_habitat": {
      "filename": "1502770702714.jpg",
      "type": "image/jpeg",
      "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=..."
    },
    "species": "turtle",
    "maturity": "na",
    "sex": "na",
    "photo_carapace_top": null,
    "photo_head_top": null,
    "photo_head_side": null,
    "photo_head_front": null,
    "activity": "beachwashed",
    "health": "na",
    "behaviour": null,
    "cause_of_death": "na",
    "cause_of_death_confidence": "na",
    "checked_for_injuries": "na",
    "scanned_for_pit_tags": "na",
    "checked_for_flipper_tags": "na",
    "samples_taken": "na",
    "damage_observation": [],
    "tag_observation": [],
    "curved_carapace_length_mm": null,
    "curved_carapace_length_accuracy": "10",
    "curved_carapace_width_mm": null,
    "curved_carapace_width_accuracy": "10",
    "tail_length_carapace_mm": null,
    "tail_length_carapace_accuracy": "10",
    "maximum_head_width_mm": null,
    "maximum_head_width_accuracy": "10",
    "photo_habitat_2": null,
    "photo_habitat_3": null,
    "photo_habitat_4": null,
    "observation_end_time": "2017-08-15T04:18:55.033Z"
    },
    {
    "instanceID": "uuid:87fcedb9-05ba-476e-90c0-9bfa40faf7f2",
    "observation_start_time": "2017-10-24T23:26:00.396Z",
    "reporter": "florianm",
    "observed_at:Latitude": -31.9413368,
    "observed_at:Longitude": 115.9716166,
    "observed_at:Altitude": 0e-10,
    "observed_at:Accuracy": 22.092,
    "location_comment": null,
    "incident_time": "2017-10-24T23:26:00.000Z",
    "habitat": "harbour",
    "photo_habitat": {
      "filename": "1508887643518.jpg",
      "type": "image/jpeg",
      "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=..."
    },
    "species": "flatback",
    "maturity": "adult",
    "sex": "female",
    "photo_carapace_top": {
      "filename": "1508887669660.jpg",
      "type": "image/jpeg",
      "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=..."
    },
    "photo_head_top": {
      "filename": "1508887683511.jpg",
      "type": "image/jpeg",
      "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=..."
    },
    "photo_head_side": {
      "filename": "1508887698795.jpg",
      "type": "image/jpeg",
      "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=..."
    },
    "photo_head_front": {
      "filename": "1508887714082.jpg",
      "type": "image/jpeg",
      "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=..."
    },
    "activity": "beachwashed",
    "health": "deadedible",
    "behaviour": "condition comments",
    "cause_of_death": "poisoned",
    "cause_of_death_confidence": "expertopinion",
    "checked_for_injuries": "present",
    "scanned_for_pit_tags": "present",
    "checked_for_flipper_tags": "present",
    "samples_taken": "present",
    "damage_observation": [
      {
        "photo_damage": {
          "filename": "1508887793593.jpg",
          "type": "image/jpeg",
          "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=..."
        },
        "body_part": "flipperfrontright",
        "damage_type": "other",
        "damage_age": "fresh",
        "description": null
      }
    ],
    "tag_observation": [
      {
        "photo_tag": {
          "filename": "1508887828938.jpg",
          "type": "image/jpeg",
          "url":
            "https://dpaw-data.appspot.com/view/binaryData?blobKey=..."
        },
        "name": "wa1234",
        "tag_type": "flippertag",
        "tag_location": "flipperfrontright1",
        "tag_status": "resighted",
        "tag_comments": null
      }
    ],
    "curved_carapace_length_mm": 890,
    "curved_carapace_length_accuracy": "10",
    "curved_carapace_width_mm": 560,
    "curved_carapace_width_accuracy": "10",
    "tail_length_carapace_mm": 210,
    "tail_length_carapace_accuracy": "10",
    "maximum_head_width_mm": 125,
    "maximum_head_width_accuracy": "10",
    "photo_habitat_2": {
      "filename": "1508887910356.jpg",
      "type": "image/jpeg",
      "url":
        "https://dpaw-data.appspot.com/view/binaryData?blobKey=..."
    },
    "photo_habitat_3": {
      "filename": "1508887919139.jpg",
      "type": "image/jpeg",
      "url":
        "https://dpaw-data.appspot.com/view/binaryData?blobKey=..."
    },
    "photo_habitat_4": {
      "filename": "1508887930269.jpg",
      "type": "image/jpeg",
      "url":
        "https://dpaw-data.appspot.com/view/binaryData?blobKey=..."
    },
    "observation_end_time": "2017-10-24T23:32:20.630Z"
    }
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
        species=m["species"][r["species"]],
        habitat=m["habitat"][r["habitat"]],
        maturity=m["maturity"][r["maturity"]],
        sex=r["sex"],
        activity=m["activity"][r["activity"]],
        health=m["health"][r["health"]],
        cause_of_death=m["cause_of_death"][r["cause_of_death"]],
        cause_of_death_confidence=m["confidence"][r["cause_of_death_confidence"]],
        behaviour=r["behaviour"],
        checked_for_injuries=m["yes_no"][r["checked_for_injuries"]],
        scanned_for_pit_tags=m["yes_no"][r["scanned_for_pit_tags"]],
        checked_for_flipper_tags=m["yes_no"][r["checked_for_flipper_tags"]],
        # comments
        )

    if src_id in m["overwrite"]:
        print("Updating unchanged existing record {0}...".format(src_id))
        AnimalEncounter.objects.filter(source_id=src_id).update(**new_data)
        e = AnimalEncounter.objects.get(source_id=src_id)
    else:
        print("Creating new record {0}...".format(src_id))
        e = AnimalEncounter.objects.create(**new_data)

    e.save()

    if r["checked_for_injuries"]:
        print("  Damage seen - TODO")
        # "damage_observation": [],

    if r["samples_taken"]:
        print("  Samples taken - TODO")

    # "tag_observation": [],

    # #TurtleMorphometricObservation
    # "curved_carapace_length_mm": null,
    # "curved_carapace_length_accuracy": "10",
    # "curved_carapace_width_mm": null,
    # "curved_carapace_width_accuracy": "10",
    # "tail_length_carapace_mm": null,
    # "tail_length_carapace_accuracy": "10",
    # "maximum_head_width_mm": null,
    # "maximum_head_width_accuracy": "10",

    handle_media_attachment(e, r["photo_habitat"], title="Habitat")
    handle_media_attachment(e, r["photo_habitat_2"], title="Habitat 2")
    handle_media_attachment(e, r["photo_habitat_3"], title="Habitat 3")
    handle_media_attachment(e, r["photo_habitat_4"], title="Habitat 4")
    handle_media_attachment(e, r["photo_carapace_top"], title="Carapace top")
    handle_media_attachment(e, r["photo_head_top"], title="Head top")
    handle_media_attachment(e, r["photo_head_side"], title="Head side")
    handle_media_attachment(e, r["photo_head_front"], title="Head front")

    print(" Saved {0}\n".format(e))
    e.save()
    return e


def import_one_record_sv01(r, m):
    """Import one ODK Site Visit 0.1 record into WAStD.

    Arguments

    r The record as dict, e.g.
    {
        "instanceID": "uuid:cc7224d7-f40f-4368-a937-1eb655e0203a",
        "observation_start_time": "2017-03-08T07:10:43.378Z",
        "reporter": "florianm",
        "photo_start": {
            "filename": "1488957113670.jpg",
            "type": "image/jpeg",
            "url": "https://..."
        },
        "transect": "-31.9966142 115.88456594 0.0 0.0;",
        "photo_finish": {
            "filename": "1488957172832.jpg",
            "type": "image/jpeg",
            "url": "https://..."
        },
        "comments": null,
        "observation_end_time": "2017-03-08T07:13:23.317Z"
    }

    m The mapping of ODK to WAStD choices

    All existing records will be updated.
    Make sure to skip existing records which should be retained unchanged.

    Creates a SiteVisit, e.g.
    {
     'started_on': datetime.datetime(2017, 1, 31, 16, 0, tzinfo=<UTC>),
     'finished_on': datetime.datetime(2017, 2, 4, 16, 0, tzinfo=<UTC>),
     'site_id': 17,
     'source': u'direct',
     'source_id': None,
     'transect': None,
     'comments': u'',
    }
    """
    src_id = r["instanceID"]

    new_data = dict(
        source="odk",
        source_id=src_id,
        site_id=17,  # TODO: reconstruct site on SiteVisit if not given
        transect=read_odk_linestring(r["transect"]),
        started_on=parse_datetime(r["observation_start_time"]),
        finished_on=parse_datetime(r["observation_end_time"]),
        # m["users"][r["reporter"]],  # add to team
        comments=r["comments"]
        )

    if SiteVisit.objects.filter(source_id=src_id).exists():
        print("Updating unchanged existing record {0}...".format(src_id))
        SiteVisit.objects.filter(source_id=src_id).update(**new_data)
        e = SiteVisit.objects.get(source_id=src_id)
    else:
        print("Creating new record {0}...".format(src_id))
        e = SiteVisit.objects.create(**new_data)

    e.save()

    # MediaAttachments
    handle_media_attachment(e, r["photo_start"], title="Site conditions at start of suvey")
    handle_media_attachment(e, r["photo_finish"], title="Site conditions at end of suvey")

    print(" Saved {0}\n".format(e))
    e.save()
    return e


def make_tallyobs(encounter, species, nest_age, nest_type, tally_number):
    """Create a TrackTallyObservation."""
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=encounter,
        species=species,
        nest_age=nest_age,
        nest_type=nest_type,
        tally=tally_number
        )
    print('  Tally (created: {0}) {1}'.format(created, t))


def import_one_record_tt05(r, m):
    """Import one ODK Track Tally 0.5 record into WAStD.

    Notably, counts of "None" are true absences and will be converted to "0".

    Arguments

    r The record as dict, e.g.
        {
            "instanceID": "uuid:29204c9c-3170-4dd1-b355-1d84d11e70e8",
            "observation_start_time": "2017-01-19T04:42:41.195Z",
            "reporter": "florianm",
            "location": "-31.99656982 115.88441855 0.0 0.0;-31.9965685 115.88441522 0.0 0.0;",
            "fb_evidence": "present",
            "gn_evidence": "absent",
            "hb_evidence": "absent",
            "lh_evidence": "absent",
            "or_evidence": "absent",
            "unk_evidence": "present",
            "predation_evidence": "present",
            "fb_no_old_tracks": 10,
            "fb_no_fresh_successful_crawls": 26,
            "fb_no_fresh_false_crawls": 21,
            "fb_no_fresh_tracks_unsure": 5,
            "fb_no_fresh_tracks_not_assessed": 9,
            "fb_no_hatched_nests": 2,
            "gn_no_old_tracks": null,
            "gn_no_fresh_successful_crawls": null,
            "gn_no_fresh_false_crawls": null,
            "gn_no_fresh_tracks_unsure": null,
            "gn_no_fresh_tracks_not_assessed": null,
            "gn_no_hatched_nests": null,
            "hb_no_old_tracks": null,
            "hb_no_fresh_successful_crawls": null,
            "hb_no_fresh_false_crawls": null,
            "hb_no_fresh_tracks_unsure": null,
            "hb_no_fresh_tracks_not_assessed": null,
            "hb_no_hatched_nests": null,
            "lh_no_old_tracks": null,
            "lh_no_fresh_successful_crawls": null,
            "lh_no_fresh_false_crawls": null,
            "lh_no_fresh_tracks_unsure": null,
            "lh_no_fresh_tracks_not_assessed": null,
            "lh_no_hatched_nests": null,
            "or_no_old_tracks": null,
            "or_no_fresh_successful_crawls": null,
            "or_no_fresh_false_crawls": null,
            "or_no_fresh_tracks_unsure": null,
            "or_no_fresh_tracks_not_assessed": null,
            "or_no_hatched_nests": null,
            "unk_no_old_tracks": 10,
            "unk_no_fresh_successful_crawls": 2,
            "unk_no_fresh_false_crawls": 91,
            "unk_no_fresh_tracks_unsure": 5,
            "unk_no_fresh_tracks_not_assessed": 2,
            "unk_no_hatched_nests": 5,
            "disturbance": [
                {
                    "disturbance_cause": "cyclone",
                    "no_nests_disturbed": 5,
                    "no_tracks_encountered": 4,
                    "disturbance_comments": "test"
                }
            ],
            "observation_end_time": "2017-01-19T05:02:04.577Z"
        }

    m The mapping of ODK to WAStD choices

    Existing records will be overwritten.
    Make sure to skip existing records which should be retained.
    """
    src_id = r["instanceID"]

    new_data = dict(
        source="odk",
        source_id=src_id,
        where=odk_linestring_as_point(r["location"]),
        transect=read_odk_linestring(r["location"]),
        when=parse_datetime(r["observation_start_time"]),
        location_accuracy="10",
        observer=m["users"][r["reporter"]],
        reporter=m["users"][r["reporter"]],
        )

    if src_id in m["overwrite"]:
        print("Updating unchanged existing record {0}...".format(src_id))
        LineTransectEncounter.objects.filter(source_id=src_id).update(**new_data)
        e = LineTransectEncounter.objects.get(source_id=src_id)
    else:
        print("Creating new record {0}...".format(src_id))
        e = LineTransectEncounter.objects.create(**new_data)

    e.save()

    # TurtleNestDisturbanceTallyObservation
    [handle_turtlenestdisttallyobs(distobs, e, m)
     for distobs in r["disturbance"] if len(r["disturbance"]) > 0]

    #  TrackTallyObservations
    FB = "natator-depressus"
    GN = "chelonia-mydas"
    HB = "eretmochelys-imbricata"
    LH = "caretta-caretta"
    OR = "lepidochelys-olivacea"
    UN = "cheloniidae-fam"

    tally_mapping = [
        [FB, "old",   "track-not-assessed",     r["fb_no_old_tracks"] or 0],
        [FB, "fresh", "successful-crawl",       r["fb_no_fresh_successful_crawls"] or 0],
        [FB, "fresh", "false-crawl",            r["fb_no_fresh_false_crawls"] or 0],
        [FB, "fresh", "track-unsure",           r["fb_no_fresh_tracks_unsure"] or 0],
        [FB, "fresh", "track-not-assessed",     r["fb_no_fresh_tracks_not_assessed"] or 0],
        [FB, "fresh", "hatched-nest",           r["fb_no_hatched_nests"] or 0],

        [GN, "old",     "track-not-assessed",   r["gn_no_old_tracks"] or 0],
        [GN, "fresh",   "successful-crawl",     r["gn_no_fresh_successful_crawls"] or 0],
        [GN, "fresh",   "false-crawl",          r["gn_no_fresh_false_crawls"] or 0],
        [GN, "fresh",   "track-unsure",         r["gn_no_fresh_tracks_unsure"] or 0],
        [GN, "fresh",   "track-not-assessed",   r["gn_no_fresh_tracks_not_assessed"] or 0],
        [GN, "fresh",   "hatched-nest",         r["gn_no_hatched_nests"] or 0],

        [HB, "old",     "track-not-assessed",   r["hb_no_old_tracks"] or 0],
        [HB, "fresh",   "successful-crawl",     r["hb_no_fresh_successful_crawls"] or 0],
        [HB, "fresh",   "false-crawl",          r["hb_no_fresh_false_crawls"] or 0],
        [HB, "fresh",   "track-unsure",         r["hb_no_fresh_tracks_unsure"] or 0],
        [HB, "fresh",   "track-not-assessed",   r["hb_no_fresh_tracks_not_assessed"] or 0],
        [HB, "fresh",   "hatched-nest",         r["hb_no_hatched_nests"] or 0],

        [LH, "old",     "track-not-assessed",   r["lh_no_old_tracks"] or 0],
        [LH, "fresh",   "successful-crawl",     r["lh_no_fresh_successful_crawls"] or 0],
        [LH, "fresh",   "false-crawl",          r["lh_no_fresh_false_crawls"] or 0],
        [LH, "fresh",   "track-unsure",         r["lh_no_fresh_tracks_unsure"] or 0],
        [LH, "fresh",   "track-not-assessed",   r["lh_no_fresh_tracks_not_assessed"] or 0],
        [LH, "fresh",   "hatched-nest",         r["lh_no_hatched_nests"] or 0],

        [OR, "old",     "track-not-assessed",   r["or_no_old_tracks"] or 0],
        [OR, "fresh",   "successful-crawl",     r["or_no_fresh_successful_crawls"] or 0],
        [OR, "fresh",   "false-crawl",          r["or_no_fresh_false_crawls"] or 0],
        [OR, "fresh",   "track-unsure",         r["or_no_fresh_tracks_unsure"] or 0],
        [OR, "fresh",   "track-not-assessed",   r["or_no_fresh_tracks_not_assessed"] or 0],
        [OR, "fresh",   "hatched-nest",         r["or_no_hatched_nests"] or 0],

        [UN, "old",     "track-not-assessed",   r["unk_no_old_tracks"] or 0],
        [UN, "fresh",   "successful-crawl",     r["unk_no_fresh_successful_crawls"] or 0],
        [UN, "fresh",   "false-crawl",          r["unk_no_fresh_false_crawls"] or 0],
        [UN, "fresh",   "track-unsure",         r["unk_no_fresh_tracks_unsure"] or 0],
        [UN, "fresh",   "track-not-assessed",   r["unk_no_fresh_tracks_not_assessed"] or 0],
        [UN, "fresh",   "hatched-nest",         r["unk_no_hatched_nests"] or 0],
        ]

    [make_tallyobs(e, x[0], x[1], x[2], x[3]) for x in tally_mapping]

    e.save()
    print(" Saved {0}\n".format(e))
    return e


# -----------------------------------------------------------------------------#
# WAMTRAM
#
def make_wamtram_source_id(original_id):
    """Generate the source_id for WAMTRAM records."""
    return "wamtram-observation-id-{0}".format(original_id)


def import_one_encounter_wamtram(r, m, u):
    """Import one WAMTRAM 2 tagging record into WAStD.

    Arguments

    r The record as dict, e.g.

    {'ACTION_TAKEN': 'NA',
    'ALIVE': 'Y',
    'BEACH_POSITION_CODE': 'A',
    'CC_LENGTH_Not_Measured': '0',
    'CC_NOTCH_LENGTH_Not_Measured': '1',
    'CC_WIDTH_Not_Measured': '0',
    'CLUTCH_COMPLETED': 'N',
    'COMMENTS': 'PTT: #103225-11858',
    'COMMENT_FROMRECORDEDTAGSTABLE': 'PTT',
    'CONDITION_CODE': 'NA',
    'DATE_ENTERED': '2010-12-20 00:00:00',
    'DATUM_CODE': 'WGS84',
    'DidNotCheckForInjury': '0',
    'EASTING': 'NA',
    'EGG_COUNT_METHOD': 'NA',
    'ENTERED_BY': 'NA',
    'ENTERED_BY_PERSON_ID': '3537',
    'ENTRY_BATCH_ID': '301',
    'LATITUDE': '-21.46315',
    'LATITUDE_DEGREES': 'NA',
    'LATITUDE_MINUTES': 'NA',
    'LATITUDE_SECONDS': 'NA',
    'LONGITUDE': '115.01963',
    'LONGITUDE': '115.01963',
    'LONGITUDE_DEGREES': 'NA',
    'LONGITUDE_MINUTES': 'NA',
    'LONGITUDE_SECONDS': 'NA',
    'MEASUREMENTS': 'Y',
    'MEASURER_PERSON_ID': '623',
    'MEASURER_REPORTER_PERSON_ID': '3826',
    'Mund': '0',
    'NESTING': 'Y',
    'NORTHING': 'NA',
    'NUMBER_OF_EGGS': 'NA',
    'OBSERVATION_ID': '211465',
    'OBSERVATION_STATUS': 'Initial Nesting',
    'ORIGINAL_OBSERVATION_ID': 'NA',
    'OTHER_TAGS': '103225-11858  PENV URS',
    'OTHER_TAGS_IDENTIFICATION_TYPE': 'PTT',
    'PLACE_CODE': 'THEE',
    'PLACE_DESCRIPTION': 'NA',
    'REPORTER_PERSON_ID': '3826',
    'SCARS_LEFT': '0',
    'SCARS_LEFT_SCALE_1': '0',
    'SCARS_LEFT_SCALE_2': '0',
    'SCARS_LEFT_SCALE_3': '0',
    'SCARS_RIGHT': '0',
    'SCARS_RIGHT_SCALE_1': '0',
    'SCARS_RIGHT_SCALE_2': '0',
    'SCARS_RIGHT_SCALE_3': '0',
    'TAGGER_PERSON_ID': '623',
    'TURTLE_ID': '55742',
    'TagScarNotChecked': '0',
    'TransferID': 'NA',
    'ZONE': 'NA',
    'activity_code': 'I',
    'activity_description': 'Returning to water - Nesting',
    'activity_is_nesting': 'Y',
    'activity_label': 'Returning To Water',
    'display_this_observation': '1',
    'observation_datetime_gmt08': '2010-12-12 00:55:00',
    'observation_datetime_utc': '2010-12-11 16:55:00'}

    m The ODK_MAPPING

    u a dict of WAMTRAM PERSON_ID: WAStD User object

    Returns

    The created encounter, e.g.
    {'activity': u'na',
    'behaviour': u'',
    'cause_of_death': u'na',
    'cause_of_death_confidence': u'na',
    'checked_for_flipper_tags': u'na',
    'checked_for_injuries': u'na',
    'encounter_ptr_id': 2574,
    'encounter_type': u'stranding',
    'habitat': u'na',
    'health': u'dead-edible',
    'id': 2574,
    'location_accuracy': u'1000',
    'maturity': u'adult',
    'name': None,
    'observer_id': 1,
    'polymorphic_ctype_id': 17,
    'reporter_id': 5,
    'scanned_for_pit_tags': u'na',
    'sex': u'na',
    'site_visit_id': None,
    'source': u'direct',
    'source_id': u'2017-02-03-10-35-00-112-3242-25-5623-dead-edible-adult-na-dugong-dugon',
    'species': u'dugong-dugon',
    'status': u'new',
    'taxon': u'Sirenia',
    'when': datetime.datetime(2017, 2, 3, 2, 35, tzinfo=<UTC>),
    'where': <Point object at 0x7f16854fb400>}

    TODO
    Tags
    'COMMENT_FROMRECORDEDTAGSTABLE': 'PTT',
    'COMMENTS': 'PTT: #103225-11858',
    'OTHER_TAGS_IDENTIFICATION_TYPE': 'PTT',
    'OTHER_TAGS': '103225-11858  PENV URS',
    'SCARS_LEFT': '0',
    'SCARS_LEFT_SCALE_1': '0',
    'SCARS_LEFT_SCALE_2': '0',
    'SCARS_LEFT_SCALE_3': '0',
    'SCARS_RIGHT': '0',
    'SCARS_RIGHT_SCALE_1': '0',
    'SCARS_RIGHT_SCALE_2': '0',
    'SCARS_RIGHT_SCALE_3': '0',
    'TagScarNotChecked': '0',
    'TransferID': 'NA',

    Measurements
    'DidNotCheckForInjury': '0',
    'Mund': '0',
    'ALIVE': 'Y',
    'CONDITION_CODE': 'NA',
    'MEASUREMENTS': 'Y',
    'NUMBER_OF_EGGS': 'NA',
    'EGG_COUNT_METHOD': 'NA',
    'CLUTCH_COMPLETED': 'N',
    'MEASURER_PERSON_ID': '623',
    'MEASURER_REPORTER_PERSON_ID': '3826',
    'CC_LENGTH_Not_Measured': '0',
    'CC_NOTCH_LENGTH_Not_Measured': '1',
    'CC_WIDTH_Not_Measured': '0',


    Personnel
    'REPORTER_PERSON_ID': '3826',
    'TAGGER_PERSON_ID': '623',

    Event
    'ACTION_TAKEN': 'NA',
    'NESTING': 'Y',
    'OBSERVATION_STATUS': 'Initial Nesting',

    Comments
    'display_this_observation': '1' # mention if "0"

    Turtle
    'OBSERVATION_ID': '211465',
    'ORIGINAL_OBSERVATION_ID': 'NA',
    'TURTLE_ID': '55742',

    Audit trail
    'DATE_ENTERED': '2010-12-20 00:00:00',
    'ENTERED_BY': 'NA',
    'ENTERED_BY_PERSON_ID': '3537',
    'ENTRY_BATCH_ID': '301',
    """
    src_id = make_wamtram_source_id(r["OBSERVATION_ID"])

    # Personnel: Get WAStD User from u if PERSON_ID present, default to 1
    observer_id = u[r["TAGGER_PERSON_ID"]] if r["TAGGER_PERSON_ID"] in u else 1
    reporter_id = u[r["REPORTER_PERSON_ID"]] if r["REPORTER_PERSON_ID"] in u else 1
    # meas_observer_id = u[r["MEASURER_PERSON_ID"]] if r["MEASURER_PERSON_ID"] in u else 1
    # meas_reporter_id = u[r["MEASURER_REPORTER_PERSON_ID"]] if r["MEASURER_REPORTER_PERSON_ID"] in u else 1

    new_data = dict(
        source="wamtram",
        source_id=src_id,
        where=Point(float(r["LONGITUDE"]), float(r["LATITUDE"])),
        when=parse_datetime("{0}+00".format(r["observation_datetime_utc"])),
        location_accuracy="10",
        observer_id=observer_id,  # lookup_w2_user(r["REPORTER_PERSON_ID"]),
        reporter_id=reporter_id,
        taxon="Cheloniidae",
        species=m["species"][r["SPECIES_CODE"]],
        activity=m["activity"][r['activity_code']],
        sex="female",
        maturity="adult",
        health=m["health"][r['CONDITION_CODE']],
        habitat=m["habitat"][r["BEACH_POSITION_CODE"]],
        nesting_event=m["nesting"][r["CLUTCH_COMPLETED"]],
        )

    """
    TODO create mapping for:
    behaviour="", # all comments go here
    r["NESTING"] Y/N/U = nesting success
    """

    if src_id in m["overwrite"]:
        print("Updating unchanged existing record {0}...".format(src_id))
        AnimalEncounter.objects.filter(source_id=src_id).update(**new_data)
        e = AnimalEncounter.objects.get(source_id=src_id)
    else:
        print("Creating new record {0}...".format(src_id))
        e = AnimalEncounter.objects.create(**new_data)

    e.save()
    print(" Saved {0}\n".format(e))
    return e


def sanitize_tag_name(name):
    """Return a string capitalised and stripped of all whitespace."""
    return name.upper().replace(" ", "")


def make_tag_side(side, position):
    """Return the WAStD tag_position from WAMTRAM side and position.

    Arguments:

    side The WAMTRAM tag side, values: NA L R
    position The WAMTRAM tag position, values: NA 1 2 3

    Return
    The WAStD tag_position, e.g. flipper-front-left-1 or flipper-front-right-3
    """
    side_dict = {
        "NA": "left",
        "L": "left",
        "R": "right"
        }
    pos_dict = {
        "NA": "1",
        "1": "1",
        "2": "2",
        "3": "3"
        }
    return "flipper-front-{0}-{1}".format(side_dict[side], pos_dict[position])


def import_one_tag(t, m):
    """Import one WAMTRAM 2 tag observation record into WAStD.

    Arguments

    t The record as dict, e.g.

    {
     'observation_id': '267425',
     'recorded_tag_id': '394783',
     'tag_name': 'WB 9239',
     'tag_state': 'A1',
     'attached_on_side': 'R',
     'tag_position': 'NA',
     'comments': 'NA',
     'tag_label': 'NA',
     }

    m The ODK_MAPPING

    Return a TabObservation e.g.

    {
    'tag_type': u'flipper-tag'
    'encounter_id': 80,
    'handler_id': 1,
    'recorder_id': 1,
    'name': u'WA1234',
    'status': u'resighted',
    'tag_location': u'whole',
    'comments': u'',
    }
    """
    tag_name = sanitize_tag_name(t["tag_name"])
    enc = AnimalEncounter.objects.get(
        source_id=make_wamtram_source_id(t["observation_id"]))

    new_data = dict(
        encounter_id=enc.id,
        tag_type='flipper-tag',
        handler_id=enc.observer_id,
        recorder_id=enc.reporter_id,
        name=tag_name,
        tag_location=make_tag_side(t["attached_on_side"], t["tag_position"]),
        status=m["tag_status"][t["tag_state"]],
        comments='{0}{1}'.format(t["comments"], t["tag_label"]),
        )

    if TagObservation.objects.filter(encounter=enc, name=tag_name).exists():
        print("Updating existing tag obs {0}...".format(tag_name))
        e = TagObservation.objects.filter(
            encounter=enc, name=tag_name).update(**new_data)
        e = TagObservation.objects.get(encounter=enc, name=tag_name)

    else:
        print("Creating new tag obs {0}...".format(tag_name))
        e = TagObservation.objects.create(**new_data)

    e.save()
    print(" Saved {0}\n".format(e))
    return e


# -----------------------------------------------------------------------------#
# Cetacean strandings database (Filemaker Pro)
def infer_cetacean_sex(f, m):
    """Infer WAStD sex from Cetacean db values.

    Arguments

    f String The db value of column "is female". Females are '1'.
    m String The db value of column "is male". Males are '1'.

    Return
    String One of WAStD SEX_CHOICES "na" (unknown sex), "female" or "male"
    """
    if f == "1":
        return "female"
    elif m == "1":
        return "male"
    else:
        return "na"


def fix_species_name(spname):
    """Return one species name lowercase-dashseparated."""
    return spname.replace(".", "").replace("? ", "").replace(
        "(?)", "").replace("?", "").strip().replace(" ", "-").lower()


def make_comment(dictobj, fieldname):
    """Render a dict's field to text.

    Return
        '<fieldname>: <dictobj["fieldname"]>' or ''
    """
    return "{0}: {1}\n\n".format(fieldname, dictobj[fieldname]) if \
        fieldname in dictobj and dictobj[fieldname] != "" else ""


def import_one_record_cet(r, m):
    r"""Import one Cetacean strandings database record into WAStD.

    The Filemaker Pro db is exported to CSV, and read here as csv.DictReader.
    This method imports one DictReader.next() record.

    Arguments

    r The record as dict, e.g.

    {'A': '',
    'Admin comment': '',
    'Age': one of:
    {'', '1', '1-2', '1-3', '11 years old', '2-3', '2-3 years old', '3 month',
    '3-4 months', '4 months', '6 yrs ', 'A', 'A, C', 'AC', 'AMC', 'C', 'J',
    'Juvenile', 'MC', 'Neonate', 'Possibly yearling', 'SA', 'Still born',
    'X', 'Yearing', 'Yearling', 'Young', 'x', '~35', '~8-10 years'},
    'Ailment_injury comment': '',
    'Attachment': '',
    'Boat_Ship Strike': '',
    'C': '1',
    'Carcass Location_Fate': 'Buried 300m NE of Doungup Park cut in dunes. See map on file.',
    'Cause of Death _drop down_': 'Euthanasia - firearm',
    'Comments': '',
    'Common Name': 'Minke Whale',
    'Condition comments': '',
    'Condition when found': 'Live',
    'Cow_calf pair Stranding': '',
    'DPaW Attended': '',
    'Date': '27/07/82',
    'Dead Stranding': '',
    'Demographic comment': '',
    'El Nino': '',
    'Entanglement': '',
    'Entanglement gear': '',
    'Entanglement gear details': '',
    'Event': 'Single Stranding\nLive Stranding',
    'F': '1',
    'Fate': '',
    'File Number': '025298F3803',
    'Floating carcass': '',
    'Heavy Metals': '',
    'ID': '',
    'Lat': '-33.4886',
    'Length _m_': '3.98',
    'Live Stranding': 'Yes',
    'Location': 'Doungup Park',
    'Long': '115.5406 ',
    'M': '',
    'Mass Stranding': '',
    'Moon Phase': '',
    'Near River': '',
    'Number of animals': '1',
    'Outcome': 'Euthanased',
    'PCB': '',
    'PM Report location': '',
    'Photos taken': 'Yes',
    'Post Mortem': 'Yes',
    'Post mortem report summary': 'Cause of death - Haemorrhagic gastroenteritis',
    'Record No.': '1',
    'Rescue info': '',
    'SA': '',
    'Sampling comments': '',
    'Scientific Name': 'Balaenoptera acutorostrata',
    'Single Stranding': 'Yes',
    'Site': 'Doungup Park beach, 20km SW of Bunbury, 8 km from Capel.',
    'U': '',
    'Weight _kg_': '',
    '_U': '',
    'latdeg': '33',
    'latmin': '29',
    'latsec': '19',
    'longdeg': '115',
    'longmin': '32',
    'longsec': '26'}

    m The ODK_MAPPING

    Returns AnimalEncounter e.g.

    'activity': u'na',
    'behaviour': u'',
    'cause_of_death': u'na',
    'cause_of_death_confidence': u'na',
    'checked_for_flipper_tags': u'na',
    'checked_for_injuries': u'na',
    'habitat': u'na',
    'health': u'dead-edible',
    'location_accuracy': u'1000',
    'maturity': u'adult',
    'name': None,
    'observer_id': 1,
    'reporter_id': 5,
    'scanned_for_pit_tags': u'na',
    'sex': u'na',
    'source': u'cet',
    'source_id': u'cet-1234',  # src_id
    'species': u'dugong-dugon',
    'taxon': u'Cetacea',
    'when': datetime.datetime(2017, 2, 3, 2, 35, tzinfo=<UTC>),
    'where': <Point object at 0x7fdede584b50>

    The species name mapping is created from names found with:

    from wastd.observations.utils import *
    legacy_strandings = csv.DictReader(open("data/cetaceans.csv"))
    wastd_cet_species = [d[0] for d in CETACEAN_SPECIES_CHOICES]]
    set([fix_species_name(x["Scientific Name"])
         for x in legacy_strandings
         if fix_species_name(x["Scientific Name"]) not in wastd_cet_species)


    """
    species = map_and_keep(CETACEAN_SPECIES_CHOICES)
    # TODO this mapping needs QA (add species to CETACEAN_SPECIES_CHOICES)
    happy_little_mistakes = {
        '': 'cetacea',
        'balaenopter-musculus-brevicauda': "balaenoptera-musculus-brevicauda",
        'balaenopters-cf-b-omurai': "balaenoptera-omurai",
        'kogia-simus': "kogia-sima",
        'sousa-chinensis': 'sousa-sahulensis',
        'orcaella-heinsohni-x': "orcaella-heinsohni",
        'stenella--sp-(coeruleoalba)': "stenella-sp",
        }
    species.update(happy_little_mistakes)

    cod = {
        'Birthing': "birthing",
        'Boat/ship strike': "boat-strike",
        'Complications from stranding': "stranded",
        'Disease/health': "natural",
        'Drowning/misadventure': "drowned-other",
        'Entanglement': "drowned-entangled",
        'Euthanasia': "euthanasia",
        'Euthanasia - firearm': "euthanasia-firearm",
        'Euthanasia - firearm - SOP 17(1)': "euthanasia-firearm",
        'Euthanasia - implosion': "euthanasia-implosion",
        'Euthanasia - injection': "euthanasia-injection",
        'Failure to thrive/dependant calf': "calf-failure-to-thrive",
        'Failure to thrive/dependent calf': "calf-failure-to-thrive",
        'Live stranding': "na",  # not a cause of death then
        'Misadventure': "natural",
        'Misadventure 13 died during event': "natural",
        'Mixed fate group': "na",  # split into individual strandings
        'Old age': "natural",
        'Predatory attack': "predation",
        'PM report pending': "na",  # set COD once necropsy done
        'Predatory attack - Orca': "predation",
        'Predatory attack - shark': "predation",
        'Remote stranding - died': "stranded",  # remoteness is not COD
        'SEE Necropsy Report': "na",  # and transcribe here
        'Spear/gunshot': "trauma-human-induced",
        'Starvation': "starved",
        'Still born': "still-born",
        'Stingray barb': "trauma-animal-induced",
        'Stranding': "stranded",
        'Trauma': "trauma",
        'Under nourished': "starved",  # if COD, else physical condition
        'Unknown': "na",
        'Unkown': "na",
        '': "na",
        'Weapon (gun, spear etc)': "trauma-human-induced",
        }

    src_id = "cet-{0}".format(r["Record No."])

    """
    Map:
    'SA', # subadult?
    'C': '1',
    Attachments:
    'Attachment': '',
    'Photos taken': 'Yes',
    'Post Mortem': 'Yes',
    """

    new_data = {
        'when': parser.parse('{0} 12:00:00 +0800'.format(r["Date"])),
        'where': Point(float(r["Long"] or 120), float(r["Lat"] or -35)),
        'taxon': u'Cetacea',
        'species': species[fix_species_name(r["Scientific Name"] or '')],
        'activity': u'na',  # TODO
        'behaviour': "".join([make_comment(r, x) for x in [
            "File Number",
            "Name",
            "Age",

            "Comments",
            "Admin comment",

            "Event",

            'Boat_Ship Strike',
            "Entanglement",
            "Entanglement gear",
            "Entanglement gear details",
            "Floating carcass",
            "Single Stranding",
            "Cow_calf pair Stranding",
            "Mass Stranding",
            "Number of animals",
            "Demographic comment",
            'Live Stranding',
            'Dead Stranding',

            "DPaW Attended",
            'Rescue info',
            "Outcome",
            "Fate",
            "Carcass Location_Fate",

            "El Nino",
            "Heavy Metals",
            'PCB',
            "Moon Phase",
            "Near River",

            'Condition when found',
            "Condition comments",
            "Ailment_injury comment",
            "PM Report location",
            "Post mortem report summary",
            'Sampling comments',
            "Length _m_",
            'Weight _kg_',

            'Site',
            'Location',
            ]]),
        'cause_of_death': cod[r["Cause of Death _drop down_"]],
        'cause_of_death_confidence': u'na',  # TODO
        'checked_for_flipper_tags': u'na',  # TODO
        'checked_for_injuries': u'na',  # TODO
        'habitat': u'na',  # TODO
        'health': u'dead-edible',  # TODO
        'location_accuracy': u'10',
        'maturity': u'adult',  # TODO
        # 'name': r["ID"] or None,
        'observer_id': 1,
        'reporter_id': 1,
        'scanned_for_pit_tags': u'na',  # TODO
        'sex': infer_cetacean_sex(r["F"], r["M"]),
        'source': u'cet',
        'source_id': src_id,
        }
    # check if src_id exists
    if src_id in m["overwrite"]:
        print("Updating unchanged existing record {0}...".format(src_id))
        AnimalEncounter.objects.filter(source_id=src_id).update(**new_data)
        e = AnimalEncounter.objects.get(source_id=src_id)
    else:
        print("Creating new record {0}...".format(src_id))
        e = AnimalEncounter.objects.create(**new_data)

    e.save()
    print(" Saved {0}\n".format(e))
    return e


def pinniped_coords_as_point(cstring):
    r"""Convert the pinniped strandings coordinate format into a Point.

    Arguments:

    cstring, a string of coordinates in the following formats:

    example_formats = [
    '',
    '-32.943382; 115.659916',  # Lat Lon   D.D; D.D
    '121:56.04; 33:49.53',     # Lon Lat   D:M.M; D:M.M
    '28:44.528; 114:37.096',   # Lat Lon   D:M.M; D:M.M
    '29:56:39.6; 114:58:41.1', # Lat Lon   D:M:S.S; D:M:S.S
    '28:46114:37',             # Lat Lon   D:MD:M
    '28:46;114:36',            # Lat Lon   D:M;D:M
    '30 29.955; 155 03.621',   # Lat Lon   D M.M; D M.M
    '30:07:47;114:56:40',      # Lat Lon   D:M:S; D:M:S
    '314394.595; 6237428.999', # UTM
    '33 27 0.73s 115 34 35.00e',# Lat Lon  D M S.S"s" D M S"s"
    '35:2 :11.198; 116:44:21.536',# weird space
    '416247E; 6143585',        # UTM E N
    'Hauled out, resting, good body condition.',  # column mismatch?
    'Lat 6240557; Long 0236825', # UTM N E
    '`31:00;115:19']           # Stray "`"

    Returns
    Point in WGS84 or None
    """
    print("Got coords {0}".format(cstring))
    print("TODO: parse to point")
    return None


def import_one_record_pin(r, m):
    r"""Import one Pinniped strandings database record into WAStD.

    The Filemaker Pro db is exported to CSV, and read here as csv.DictReader.
    This method imports one DictReader.next() record.

    Arguments

    r The record as dict, e.g.
        {'Attachment': '',
        'Comment': '',
        'Common Name': 'Australian Sea Lion',
        'Condition': 'Fish hooks ',
        'Date': '30/01/80',
        'Day': '30',
        'ID No.': '1',
        'Lat_Long': '30:08;114:57',
        'Location': 'Fisherman\xe2\x80\x99s Island',
        'Man Influenced': 'Yes',
        'Month': 'January',
        'Number': '1',
        'Scientific Name': 'Neophoca cinerea',
        'Sex': 'Female',
        'Special': '',
        'Year': '1980'}

    Species:
        {'': 'pinnipedia',
        '1': 'pinnipedia',
        'Female': 'pinnipedia',
        'Arctocephalus forsteri': "arctocephalus-forsteri",
        'Arctocephalus forsterii': "arctocephalus-forsteri",
        'Arctocephalus tropicalis': "arctocephalus-tropicalis",
        'Hydrurga leptonyx': "hydrurga-leptonyx",
        'Lobodon carcinophagus': "lobodon-carcinophagus",
        'Mirounga leonina': "mirounga-leonina",
        'Neophoca cinerea': "neophoca-cinerea"}
    """
    pass


def update_wastd_user(u):
    """Create or update a WAStD user from a dict.

    Arguments

    u   A dict with name, email, role (SPECIALTY) and WAMTRAM PERSON_ID, e.g.

    {'ADDRESS_LINE_1': 'NA',
    'ADDRESS_LINE_2': 'NA',
    'COMMENTS': 'MSP Thevenard 2016-17',
    'COUNTRY': 'NA',
    'EMAIL': 'NA',
    'FAX': 'NA',
    'FIRST_NAME': 'Joel',
    'MIDDLE_NAME': 'NA',
    'MOBILE': 'NA',
    'PERSON_ID': '4725',
    'POST_CODE': 'NA',
    'Recorder': '0',
    'SPECIALTY': 'NA',
    'STATE': 'NA',
    'SURNAME': 'Kerbey',
    'TELEPHONE': 'NA',
    'TOWN': 'NA',
    'Transfer': 'NA',
    'email': 'NA',
    'name': 'Joel Kerbey'}

    Return

    The updated or created WAStD User ID
    """
    usr, created = User.objects.get_or_create(
        username=u["name"].lower().replace(" ", "_"))
    print("User {0}: {1}".format("created" if created else "found", usr))

    # Update name
    if (usr.name is None or usr.name == "") and u["name"] != "NA" and u["name"] != "":
        usr.name = u["name"]
        print("  User name updated from name: {0}".format(usr.name))

    # Update email
    if (usr.email is None or usr.email == "") and u["EMAIL"] != "NA":
        usr.email = u["EMAIL"]
        print("  User email updated from EMAIL: {0}".format(usr.role))

    # If role is not set, or doesn't already contain SPECIALTY, add SPECIALTY
    if ((usr.role is None or usr.role == "" or u["SPECIALTY"] not in usr.role) and u["SPECIALTY"] != "NA"):
        usr.role = "{0} Specialty: {1}".format(usr.role or '', u["SPECIALTY"]).strip()
        print("  User role updated from SPECIALTY: {0}".format(usr.role))

    if ((usr.role is None or usr.role == "" or u["COMMENTS"] not in usr.role) and u["COMMENTS"] != "NA"):
        usr.role = "{0} Comments: {1}".format(usr.role or '', u["COMMENTS"]).strip()
        print("  User role updated from COMMENTS: {0}".format(usr.role))

    usr.save()
    print(" Saved User {0}".format(usr))
    return usr.id


# -----------------------------------------------------------------------------#
# Mapping
#
def make_mapping():
    """Generate a mapping of ODK to WAStD keys."""
    species = map_and_keep(SPECIES_CHOICES)
    species.update({
        # MWI < 0.4
        'flatback': 'natator-depressus',
        'green': 'chelonia-mydas',
        'hawksbill': 'eretmochelys-imbricata',
        'loggerhead': 'caretta-caretta',
        'oliveridley': 'lepidochelys-olivacea',
        'leatherback': 'dermochelys-coriacea',
        'turtle': 'cheloniidae-fam',

        # WAMTRAM
        'FB': 'natator-depressus',
        'GN': 'chelonia-mydas',
        'HK': 'eretmochelys-imbricata',
        'LO': 'caretta-caretta',
        'OR': 'lepidochelys-olivacea',
        'LB': 'dermochelys-coriacea',
        '?': 'cheloniidae-fam',
        '0': 'cheloniidae-fam',
        })

    habitat = map_and_keep(HABITAT_CHOICES)
    habitat.update({
        'abovehwm': 'beach-above-high-water',
        'belowhwm': 'beach-below-high-water',
        'edgeofvegetation': 'beach-edge-of-vegetation',
        'vegetation': 'in-dune-vegetation',
        'na': 'na',

        # WAMTRAM BEACH_POSITION_CODE
        'NA': 'na',
        "?": "na",
        "A": "beach-above-high-water",
        "B": "beach-above-high-water",
        "C": "beach-below-high-water",
        "D": "beach-edge-of-vegetation",
        "E": "in-dune-vegetation",
    })

    health = map_and_keep(HEALTH_CHOICES)
    health.update({
        "F": "dead-edible",     # Carcase - fresh
        "G": "alive",           # Good - fat
        "H": "alive",           # Live & fit
        "I": "alive",           # Injured but OK
        "M": "alive",           # Moribund
        "P": "alive",           # Poor - thin
        "NA": "na",
    })

    activity = map_and_keep(ACTIVITY_CHOICES)
    activity.update({
        "&": "captivity",       # Captive animal
        "A": "arriving",        # Resting at waters edge - Nesting
        "B": "arriving",        # Leaving water - Nesting
        "C": "approaching",     # Climbing beach slope - Nesting
        "D": "approaching",     # Moving over bare sand (=beach) - Nesting
        "E": "digging-body-pit",  # Digging body hole - Nesting
        "F": "excavating-egg-chamber",  # Excavating egg chamber - Nesting
        "G": "laying-eggs",     # Laying eggs - confirmed observation - Nesting
        "H": "filling-in-egg-chamber",  # Covering nest (filling in) - Nesting
        "I": "returning-to-water",  # Returning to water - Nesting
        # "J": "",              # Check/?edit these: only on VA records
        "K": "non-breeding",    # Basking - on beach above waterline
        "L": "arriving",        # Arriving - Nesting
        "M": "other",           # Mating
        "N": "other",           # Courting
        "O": "non-breeding",    # Free at sea
        "Q": "na",              # Not recorded in field
        "R": "non-breeding",    # Released to wild
        "S": "non-breeding",    # Rescued from stranding
        "V": "non-breeding",    # Caught in fishing gear - Decd
        "W": "non-breeding",    # Captured in water (reef or sea)
        "X": "floating",        # Turtle dead
        "Y": "floating",        # Caught in fishing gear - Relsd
        "Z": "other",           # Hunted for food by Ab & others
        })

    yes_no = map_and_keep(OBSERVATION_CHOICES)
    yes_no.update({
        'Y': 'present',
        'N': 'absent',
        'U': 'na',
        'NA': 'na',
        'yes': 'present',
        'no': 'absent',
    })

    confidence = map_and_keep(CONFIDENCE_CHOICES)
    confidence.update({
        "validate": "validated",
    })

    tag_status = map_and_keep(TAG_STATUS_CHOICES)
    tag_status.update({
        "#": 'resighted',
        "OX": 'resighted',
        "P": 'resighted',
        "P_OK": 'resighted',
        "RQ": 'resighted',
        "P_ED": 'resighted',
        "A1": 'applied-new',
        "AE": 'applied-new',
        "RC": 'reclinched',
        "OO": 'removed',
        "R": 'removed',
        "Q": 'resighted',
        'resighted': 'resighted'
    })

    return {
        "nest_type": map_and_keep(NEST_TYPE_CHOICES),

        "tag_status": map_and_keep(TAG_STATUS_CHOICES),
        "maturity": map_and_keep(MATURITY_CHOICES),
        "cause_of_death": map_and_keep(CAUSE_OF_DEATH_CHOICES),
        "confidence": confidence,
        "yes_no": yes_no,
        "species": species,
        "activity": activity,
        "habitat": habitat,
        "health": health,
        "tag_status": tag_status,
        "disturbance": yes_no,
        "nesting": yes_no,

        "overwrite": [t.source_id for t in Encounter.objects.filter(
            source="odk", status=Encounter.STATUS_NEW)]
        }


# -----------------------------------------------------------------------------#
# Main import call
#
def import_odk(datafile,
               flavour="odk-tt036",
               extradata=None,
               usercsv=None,
               mapping=make_mapping()):
    """Import ODK data.

    Arguments

    datafile A filepath to the JSON exported from ODK Aggregate
    flavour The ODK form with version

    flavour A string indicating the type of input, see examples.

    extradata A second datafile (tags for WAMTRAM)

    usercsv A CSV file with columns "name" and "PERSON_ID"

    mapping A dict mapping dropdown values from ODK to WAStD, default: ODK_MAPPING

    Preparation:

    * https://dpaw-data.appspot.com/ > Submissions > Form e.g. "Track or Treat 0.31"
    * Export > JSON > Export
    * Submissions > Exported Submissions > download JSON

    Behaviour:

    * Records not in WAStD will be created
    * Records in WAStD of status NEW (unchanged since import) will be updated
    * Records in WAStD of status **above** NEW (QA'd and possibly locally changed) will be skipped

    Example:

        from wastd.observations.utils import *
        #import_odk('data/Track_or_Treat_0_34_results.json', flavour="odk-tt034")
        import_odk('data/cetaceans.csv', flavour="cet")
        import_odk('data/wamtram_encounters.csv', flavour="wamtram", usercsv="data/wamtram_users.csv")
        import_odk('data/wamtram_tagobservations.csv', flavour="whambam")
        #import_odk('data/Site_Visit_0_1_results.json', flavour="sitevisit")

        import_odk("data/latest/tt05.json", flavour="odk-tally05")
        import_odk('data/latest/tt031.json', flavour="odk-tt031")
        import_odk('data/latest/tt034.json', flavour="odk-tt034")
        import_odk('data/latest/tt035.json', flavour="odk-tt036")
        import_odk('data/latest/tt036.json', flavour="odk-tt036")
        import_odk('data/latest/fs03.json', flavour="odk-fs03")
        import_odk('data/latest/mwi01.json', flavour="odk-mwi01")
    """
    if flavour == "odk-tt034":
        print("Using flavour ODK Track or Treat 0.34...")
        with open(datafile) as df:
            d = json.load(df)
            print("Loaded {0} records from {1}".format(len(d), datafile))
        mapping["users"] = {u: guess_user(u) for u in set([r["reporter"] for r in d])}
        mapping["keep"] = [t.source_id for t in Encounter.objects.exclude(
            status=Encounter.STATUS_NEW).filter(source="odk")]

        [import_one_record_tt034(r, mapping) for r in d
         if r["instanceID"] not in mapping["keep"]]     # retain local edits
        print("Done!")

    elif flavour == "odk-tt036":
        print("Using flavour ODK Track or Treat 0.35-0.36...")
        with open(datafile) as df:
            d = json.load(df)
            print("Loaded {0} records from {1}".format(len(d), datafile))
        mapping["users"] = {u: guess_user(u) for u in set([r["reporter"] for r in d])}
        mapping["keep"] = [t.source_id for t in Encounter.objects.exclude(
            status=Encounter.STATUS_NEW).filter(source="odk")]

        [import_one_record_tt036(r, mapping) for r in d
         if r["instanceID"] not in mapping["keep"]]     # retain local edits
        print("Done!")

    elif flavour == "odk-fs03":
        print("Using flavour ODK Fox Sake 0.3...")
        with open(datafile) as df:
            d = json.load(df)
            print("Loaded {0} records from {1}".format(len(d), datafile))
        mapping["users"] = {u: guess_user(u) for u in set([r["reporter"] for r in d])}
        mapping["keep"] = [t.source_id for t in Encounter.objects.exclude(
            status=Encounter.STATUS_NEW).filter(source="odk")]

        [import_one_record_fs03(r, mapping) for r in d
         if r["instanceID"] not in mapping["keep"]]     # retain local edits
        print("Done!")

    elif flavour == "odk-mwi01":
        print("Using flavour ODK Marine Wildlife Incident 0.1...")
        with open(datafile) as df:
            d = json.load(df)
            print("Loaded {0} records from {1}".format(len(d), datafile))
        mapping["users"] = {u: guess_user(u) for u in set([r["reporter"] for r in d])}
        mapping["keep"] = [t.source_id for t in Encounter.objects.exclude(
            status=Encounter.STATUS_NEW).filter(source="odk")]

        [import_one_record_mwi01(r, mapping) for r in d
         if r["instanceID"] not in mapping["keep"]]     # retain local edits
        print("Done!")

    elif flavour == "odk-tally05":
        print("Using flavour ODK Track Tally 0.5...")
        with open(datafile) as df:
            d = json.load(df)
            print("Loaded {0} records from {1}".format(len(d), datafile))
        mapping["users"] = {u: guess_user(u) for u in set([r["reporter"] for r in d])}
        mapping["keep"] = [t.source_id for t in Encounter.objects.exclude(
            status=Encounter.STATUS_NEW).filter(source="odk")]

        [import_one_record_tt05(r, mapping) for r in d
         if r["instanceID"] not in mapping["keep"]]     # retain local edits
        print("Done!")

    elif flavour == "cet":
        print("Using flavour Cetacean strandings...")
        # ODK_MAPPING["users"] = {u: guess_user(u) for u in set([r["reporter"] for r in d])}
        mapping["keep"] = [t.source_id for t in Encounter.objects.exclude(
            status=Encounter.STATUS_NEW).filter(source="cet")]
        mapping["overwrite"] = [t.source_id for t in Encounter.objects.filter(
            source="cet", status=Encounter.STATUS_NEW)]

        enc = csv.DictReader(open(datafile))

        [import_one_record_cet(e, mapping) for e in enc
         if e["Record No."] not in mapping["keep"]]

    elif flavour == "pin":
        print("Using flavour Pinniped strandings...")
        # mapping["users"] = {u: guess_user(u) for u in set([r["reporter"] for r in d])}
        mapping["keep"] = [t.source_id for t in Encounter.objects.exclude(
            status=Encounter.STATUS_NEW).filter(source="pin")]
        enc = csv.DictReader(open(datafile))
        print("not impemented yet")

    elif flavour == "wamtram":
        print("ALL ABOARD THE WAMTRAM!!!")
        enc = csv.DictReader(open(datafile))
        wamtram_users = csv.DictReader(open(usercsv))

        # List of [WAStD User object (.id), WAMTRAM user dict (["PERSON_ID"])]
        users = {user["PERSON_ID"]: update_wastd_user(user)
                 for user in wamtram_users if user["name"] != ""}

        # mapping["users"] = {u: guess_user(u) for u in set([r["reporter"] for r in d])}
        mapping["keep"] = [t.source_id for t in Encounter.objects.exclude(
            status=Encounter.STATUS_NEW).filter(source="wamtram")]
        mapping["overwrite"] = [t.source_id for t in Encounter.objects.filter(
            source="wamtram", status=Encounter.STATUS_NEW)]

        [import_one_encounter_wamtram(e, mapping, users) for e in enc
         if e["OBSERVATION_ID"] not in mapping["keep"]]

        # if extradata:
        #   tags = csv.DictReader(open(extradata))
        # [import_one_tag_wamtram(t, ODK_MAPPING) for t in tags]

    elif flavour == "whambam":
        print("thank you ma'am")
        tags = csv.DictReader(open(datafile))

        print("  Caching tagging encounters...")
        enc = [x["source_id"] for x in
               AnimalEncounter.objects.filter(source="wamtram").values("source_id")]

        [import_one_tag(x, mapping) for x in tags
         if make_wamtram_source_id(x["observation_id"]) in enc]

    elif flavour == "sitevisit":
        print("Loading Site Visits...")
        with open(datafile) as df:
            d = json.load(df)
            print("Loaded {0} records from {1}".format(len(d), datafile))
        mapping["users"] = {u: guess_user(u) for u in set(
            [r["reporter"] for r in d])}

        [import_one_record_sv01(r, mapping) for r in d]     # retain local edits
        print("Done!")

    else:
        print("Format {0} not recognized. Exiting.".format(flavour))


# ---------------------------------------------------------------------------#
# ODK Aggregate API helpers
#
def xmlelem_to_dict(t):
    """Convert a potentially nested XML Element to a dict, strip namespace.

    Source: https://stackoverflow.com/a/19557036/2813717
    Credit: https://stackoverflow.com/users/489638/s29

    Note: creates some superfluous dicts and lists.
    """
    return {t.tag.split("}")[-1]: map(xmlelem_to_dict, list(t)) or t.text}


def odka_forms(url=env('ODKA_URL'),
               un=env('ODKA_UN'),
               pw=env('ODKA_PW')):
    """Return an OpenRosa xformsList XML response as list of dicts.

    See https://groups.google.com/forum/#!topic/opendatakit-developers/rfjN1nwYRFY

    Arguments

    url The OpenRosa xformsList API endpoint of an ODK Aggregate instance,
        default: the value of environment variable "ODKA_URL".
    un A username that exists on the ODK-A instance.
        Default: the value of environment variable "ODKA_UN".
    pw The username's password.
        Default: the value of environment variable "ODKA_PW".

    Returns
    A list of dicts, each dict contains one xform:

    [
      {'downloadUrl': 'https://dpaw-data.appspot.com/formXml?formId=build_Site-Visit-Start-0-1_1490753483',
       'formID': 'build_Site-Visit-Start-0-1_1490753483',
       'hash': 'md5:c18c69c713c648bac240cbac9eee2d8a',
       'majorMinorVersion': None,
       'name': 'Site Visit Start 0.1',
       'version': None},
      {...repeat for each form...},
    ]
    """
    api = "{0}/xformsList".format(url)
    au = HTTPDigestAuth(un, pw)
    print("[odka_forms] Retrieving xformsList from {0}...".format(url))
    res = requests.get(api, auth=au)
    ns = "{http://openrosa.org/xforms/xformsList}"
    xforms = ElementTree.fromstring(res.content)
    forms = [{x.tag.replace(ns, ""): xform.find(x.tag).text for x in xform}
             for xform in list(xforms)]
    # not quite right:
    # xforms_dict = [xmlelem_to_dict(xform, ns=ns) for xform in list(xforms)]
    print("[odka_forms] Done, retrieved {0} forms.".format(len(forms)))
    return forms


def odka_submission_ids(form_id,
                        limit=10000,
                        url=env('ODKA_URL'),
                        un=env('ODKA_UN'),
                        pw=env('ODKA_PW')):
    """Return a list of submission IDs for a given ODKA formID.

    TODO: should lower numEntries

    Arguments:

    form_id An existing xform formID,
        e.g. 'build_Site-Visit-End-0-1_1490756971'.
    limit The maximum number of submission IDs to retrieve, default: 10000.
    url The OpenRosa xformsList API endpoint of an ODK Aggregate instance,
        default: the value of environment variable "ODKA_URL".
    un A username that exists on the ODK-A instance.
        Default: the value of environment variable "ODKA_UN".
    pw The username's password.
        Default: the value of environment variable "ODKA_PW".


    Returns
    A list of submission IDs. Each ID can be used as input for odka_submission().

    Example:

    forms = odka_forms()
    ids = odka_submission_ids(forms[6]["formID"])

    ['uuid:c439fb45-3a1f-4127-be49-571af79a2c63',
     'uuid:13f06748-54a4-4aac-9dc2-e547c80a1c37',
     'uuid:fdde19ad-cc80-48d6-a0fd-adebfa3c5e02',
     'uuid:ce83e6cf-df9f-4705-8cfc-5fc413e22c43',
     'uuid:5d4b2bb6-21c0-4ec9-801a-f13b74a78add',
     'uuid:a9772680-b6f9-45c0-8ed4-189f5e722a6c',
     ...
    ]
    """
    pars = {'formId': form_id, 'numEntries': limit}
    api = "{0}/view/submissionList".format(url)
    au = HTTPDigestAuth(un, pw)
    print("[odka_submission_ids] Retrieving submission IDs for formID '{0}'...".format(form_id))
    res = requests.get(api, auth=au, params=pars)
    el = ElementTree.fromstring(res.content)
    ids = [e.text for e in el.find('{http://opendatakit.org/submissions}idList')]
    print("[odka_submission_ids] Done, retrieved {0} submission IDs.".format(len(ids)))
    return ids


def odka_submission(form_id,
                    submission_id,
                    url=env('ODKA_URL'),
                    un=env('ODKA_UN'),
                    pw=env('ODKA_PW'),
                    verbose=False):
    """Download one ODKA submission and return as ElementTree (goal: dict).

    Arguments:

    form_id An existing xform formID,
        e.g. 'build_Site-Visit-Start-0-1_1490753483'.
    submission_id An existing opendatakit submission ID,
        e.g. 'uuid:a9772680-b6f9-45c0-8ed4-189f5e722a6c'.
    limit The maximum number of submission IDs to retrieve, default: 10000.
    url The OpenRosa xformsList API endpoint of an ODK Aggregate instance,
        default: the value of environment variable "ODKA_URL".
    un A username that exists on the ODK-A instance.
        Default: the value of environment variable "ODKA_UN".
    pw The username's password.
        Default: the value of environment variable "ODKA_PW".
    verbose Whether to print verbose log messages, default: False.

    Returns
    WIP - currently the submission as XML Element.

    Example
    d = odka_submission('build_Site-Visit-Start-0-1_1490753483',
        'uuid:a9772680-b6f9-45c0-8ed4-189f5e722a6c')
    list(d)
    """
    api = ("{0}/view/downloadSubmission?formId={1}"
           "[@version=null%20and%20@uiVersion=null]/data[@key={2}]").format(
        url, form_id, submission_id)
    au = HTTPDigestAuth(un, pw)
    print("[odka_submission] Retrieving {0}".format(submission_id))
    if verbose:
        print("[odka_submission] URL {0}".format(api))
    res = requests.get(api, auth=au)
    el = ElementTree.fromstring(res.content)
    return xmlelem_to_dict(el)


def odka_submissions(form_id,
                     url=env('ODKA_URL'),
                     un=env('ODKA_UN'),
                     pw=env('ODKA_PW'),
                     verbose=False):
    """Retrieve a list of all submissions for a given formID.

    Arguments:

    form_id An existing xform formID,
        e.g. 'build_Site-Visit-Start-0-1_1490753483'.
    url The OpenRosa xformsList API endpoint of an ODK Aggregate instance,
        default: the value of environment variable "ODKA_URL".
    un A username that exists on the ODK-A instance.
        Default: the value of environment variable "ODKA_UN".
    pw The username's password.
        Default: the value of environment variable "ODKA_PW".
    verbose Whether to print verbose log messages, default: False.

    Example
    forms = odka_forms()
    data = odka_submissions(forms[6]["formID"])
    """
    print("[odka_submissions] Retrieving submissions for formID {0}...".format(form_id))
    d = [odka_submission(form_id, x, url=url, un=un, pw=pw, verbose=verbose)
         for x in odka_submission_ids(form_id, url=url, un=un, pw=pw)]
    print("[odka_submissions] Done, retrieved {0} submissions.".format(len(d)))
    return d


def save_odka(form_id,
              path=".",
              url=env('ODKA_URL'),
              un=env('ODKA_UN'),
              pw=env('ODKA_PW'),
              verbose=False):
    """Save all submissions for a given form_id as JSON to a given path.

    Arguments:

    form_id An existing form_id
    path A locally existing path, default: "."
    url The OpenRosa xformsList API endpoint of an ODK Aggregate instance,
        default: the value of environment variable "ODKA_URL".
    un A username that exists on the ODK-A instance.
        Default: the value of environment variable "ODKA_UN".
    pw The username's password.
        Default: the value of environment variable "ODKA_PW".
    verbose Whether to print verbose log messages, default: False.
    """
    with open('{0}/{1}.json'.format(path, form_id), 'w') as outfile:
        json.dump(
            odka_submissions(
                form_id,
                url=url,
                un=un,
                pw=pw,
                verbose=verbose),
            outfile
        )


def save_all_odka(path=".",
                  url=env('ODKA_URL'),
                  un=env('ODKA_UN'),
                  pw=env('ODKA_PW'),
                  verbose=False):
    """Save all submissions for all forms of an odka instance.

    Arguments:

    path A locally existing path, default: "."
    url The OpenRosa xformsList API endpoint of an ODK Aggregate instance,
        default: the value of environment variable "ODKA_URL".
    un A username that exists on the ODK-A instance.
        Default: the value of environment variable "ODKA_UN".
    pw The username's password.
        Default: the value of environment variable "ODKA_PW".
    verbose Whether to print verbose log messages, default: False.

    Returns:
    At the specified location (path) for each form, a file will be written
    which containis all submissions (records) for that respective form.
    """
    [save_odka(
        xform['formID'],
        path=path,
        url=url,
        un=un,
        pw=pw,
        verbose=verbose)
     for xform in odka_forms()]


def make_datapackage_json(xform,
                          path=".",
                          url=env('ODKA_URL'),
                          un=env('ODKA_UN'),
                          pw=env('ODKA_PW'),
                          verbose=False,
                          download_submissions=False,
                          download_config=False):
    """Generate a datapacke.json config for a given xform dict.

    Arguments:

    xform An xform dict as produced by odka_forms()
    path The local path to the downloaded submission JSON as produced by save_odka()
    url The OpenRosa xformsList API endpoint of an ODK Aggregate instance,
        default: the value of environment variable "ODKA_URL".
    un A username that exists on the ODK-A instance.
        Default: the value of environment variable "ODKA_UN".
    pw The username's password.
        Default: the value of environment variable "ODKA_PW".
    verbose Whether to print verbose log messages, default: False.
    download_submissions Whether to download submissions
    download_config Whether to write the returned config to a local file

    Returns:
    A dict
    """
    fid = xform["formID"].lower()
    datapackage_path = os.path.join(path, fid)

    if not os.path.exists(datapackage_path):
        os.makedirs(datapackage_path)

    if download_submissions:
        save_odka(
            xform["formID"],
            path=datapackage_path,
            url=url,
            un=un,
            pw=pw,
            verbose=verbose)

    datapackage_config = {
        "name": fid,
        "title": xform["name"],
        "description": "Hash: {0}\nversion: {1}\nmajorMinorVersion: {2}\ndownload URL: {3}".format(
            xform["hash"], xform["version"], xform["majorMinorVersion"], xform["downloadUrl"]),
        "licenses": [
            {
                "id": "odc-pddl",
                "name": "Public Domain Dedication and License",
                "version": "1.0",
                "url": "http://opendatacommons.org/licenses/pddl/1.0/"
            }
        ],
        "resources": [
                {'encoding': 'utf-8',
                 'format': 'json',
                 'mediatype': 'text/json',
                 'name': fid,
                 'path': "{0}/{1}.json".format(datapackage_path, fid),
                 'profile': 'data-resource'}
        ]
        }

    if download_config:
        with open('{0}/datapackage.json'.format(datapackage_path), 'w') as outfile:
            json.dump(datapackage_config, outfile)

    return datapackage_config


# ---------------------------------------------------------------------------#
# Munging JSON output from odka_*
#
def gimme_data(submission_dict):
    """Return the data part of an ODKA submission."""
    return submission_dict["submission"][0]["data"][0]["data"]


def gimme_all(my_iterable, my_key):
    """Return a list of all elements having at least my_key in a given iterable.

    E.g.
    r = {
        "submission": [
          {
            "data": [
              {
                "data": [
                  {
                    "meta": [
                      { "instanceID": "uuid:d7f96001-a126-410c-b33d-407decf068d1" }
                    ]
                  },
                  { "observation_start_time": "2017-10-25T09:39:18.532Z" },
                  { "reporter": "david_porteous" },
                  {
                    "disturbanceobservation": [
                      {
                        "location":
                          "-20.7768750000 116.8622416667 -3.4000000000 4.9000000000"
                      },
                      { "photo_disturbance": "1508924412065.jpg" },
                      { "disturbance_cause": "fox" },
                      { "disturbance_cause_confidence": "expert-opinion" },
                      { "comments": null }
                    ]
                  },
                  { "observation_end_time": "2017-10-25T09:40:37.327Z" }
                ]
              }
            ]
          },
          {
            "mediaFile": [
              { "filename": "1508924412065.jpg" },
              { "hash": "md5:f4f0b5dea646865c27ca0c8c832c5800" },
              {
                "downloadUrl":
                  "https://dpaw-data.appspot.com/view/binaryData?blobKey=..."
              }
            ]
          }
        ]
      }

    gimme_all(gimme_data(r), "reporter")
    ["david_porteous"]
    """
    return [element[my_key] for element in my_iterable if my_key in element]


def gimme(my_iterable, my_key):
    """Return the first match of gimme_all.

    {
        "submission": [
          {
            "data": [
              {
                "data": [
                  {
                    "meta": [
                      { "instanceID": "uuid:d7f96001-a126-410c-b33d-407decf068d1" }
                    ]
                  },
                  { "observation_start_time": "2017-10-25T09:39:18.532Z" },
                  { "reporter": "david_porteous" },
                  {
                    "disturbanceobservation": [
                      {
                        "location":
                          "-20.7768750000 116.8622416667 -3.4000000000 4.9000000000"
                      },
                      { "photo_disturbance": "1508924412065.jpg" },
                      { "disturbance_cause": "fox" },
                      { "disturbance_cause_confidence": "expert-opinion" },
                      { "comments": null }
                    ]
                  },
                  { "observation_end_time": "2017-10-25T09:40:37.327Z" }
                ]
              }
            ]
          },
          {
            "mediaFile": [
              { "filename": "1508924412065.jpg" },
              { "hash": "md5:f4f0b5dea646865c27ca0c8c832c5800" },
              {
                "downloadUrl":
                  "https://dpaw-data.appspot.com/view/binaryData?blobKey=..."
              }
            ]
          }
        ]
      }

    gimme(d, "reporter")
    "david_porteous"
    """
    return gimme_all(my_iterable, my_key)[0]


def gimme_src_id(r):
    """Return the instanceID from an odka_submission."""
    return gimme(r, "meta")[0]["instanceID"]


def gimme_media(r):
    """Return a list of {filename: downloadUrl} for all mediaFiles."""
    return [{gimme(x["mediaFile"], "filename"): gimme(x["mediaFile"], "downloadUrl")}
            for x in r["submission"]
            if "mediaFile" in x]


def create_update_skip(
        source,
        source_id,
        lon,
        lat,
        acc,
        when,
        observer,
        reporter):
    """Create, update or skip Encounter.

    From minimal required data, create (if not existing),
    update (if unchanged) or skip (if changed) an Encounter.


    Arguments:
    source An existing WAStD data source, e.g. "odk"
    source_id The unique source ID for a record, e.g. the instanceID of an ODK submission.
    lon, lat, acc Coordinates (will be forced to float)
    when observed_od, will be parsed to date
    observer,
    reporter: username for observer and reporter.

    Returns:

    If Encounter exists with STATUS_NEW, it already has been imported, but no
    QA actions have updated the data, so the original data before import is
    deemed the point of truth. The Encounter can safely be overwritten.
    Returns updated Encounter and action verb "overwrite".

    If Encounter exists with a status other than STATUS_NEW, this means that QA operators
    have deemed this record the point of truth.
    Returns the skipped Encounter and action verb "skip".

    If the Encounter does not exist, it needs to be created.
    Returns newly created Encounter and action verb "create".
    """
    new_data = dict(
        source=source,
        source_id=source_id,
        where=Point(float(lon), float(lat)),
        when=parse_datetime(when),
        location_accuracy=acc,
        observer=guess_user(observer),
        reporter=guess_user(reporter)
    )

    enc = Encounter.objects.filter(source=source, source_id=source_id)
    if enc.exists():
        if enc.first().status == Encounter.STATUS_NEW:
            msg = "Updating unchanged existing record {0}...".format(source_id)
            action = "update"
            enc.update(**new_data)
            e = enc.first()
            e.save()
        else:
            msg = "Skipping existing curated record {0}...".format(source_id)
            action = "skip"
            e = enc.first()
    else:
        msg = "Creating new record {0}...".format(source_id)
        action = "create"
        e = Encounter.objects.create(**new_data)
        e.save()

    print(msg)
    return (e, action)


# ---------------------------------------------------------------------------#
# Fox Sake 0.3
#
def import_odka_fs03(r):
    """Import one ODK Fox Sake 0.3 record from the OKA-A API into WAStD.

    The following choices are now are identical to WAStD
    and do not require a mapping any longer:

    * disturbance evident
    * disturbance_cause_confidence

    Arguments

    r The submission record as dict, e.g.

      {
        "submission": [
          {
            "data": [
              {
                "data": [
                  {
                    "meta": [
                      { "instanceID": "uuid:d7f96001-a126-410c-b33d-407decf068d1" }
                    ]
                  },
                  { "observation_start_time": "2017-10-25T09:39:18.532Z" },
                  { "reporter": "david_porteous" },
                  {
                    "disturbanceobservation": [
                      {
                        "location":
                          "-20.7768750000 116.8622416667 -3.4000000000 4.9000000000"
                      },
                      { "photo_disturbance": "1508924412065.jpg" },
                      { "disturbance_cause": "fox" },
                      { "disturbance_cause_confidence": "expert-opinion" },
                      { "comments": null }
                    ]
                  },
                  { "observation_end_time": "2017-10-25T09:40:37.327Z" }
                ]
              }
            ]
          },
          {
            "mediaFile": [
              { "filename": "1508924412065.jpg" },
              { "hash": "md5:f4f0b5dea646865c27ca0c8c832c5800" },
              {
                "downloadUrl":
                  "https://dpaw-data.appspot.com/view/binaryData?blobKey=..."
              }
            ]
          }
        ]
      }

    m The mapping of ODK to WAStD choices

    Existing records will be overwritten.
    Make sure to skip existing records which should be retained.
    """
    data = gimme_data(r)
    media = gimme_media(r)
    lat, lon, alt, acc = gimme(data, "disturbanceobservation")[0]["location"].split(" ")

    enc, action = create_update_skip(
        "odk",
        gimme_src_id(data),
        lon,
        lat,
        "10",
        gimme(data, "observation_start_time"),
        gimme(data, "reporter"),
        gimme(data, "reporter"))

    if action in ["overwrite", "create"]:
        distobs = gimme(data, "disturbanceobservation")
        photo = gimme(distobs, "photo_disturbance")

        if photo:
            photo_dict = dict(filename=photo, url=gimme(media, photo))
        else:
            photo_dict = None

        handle_turtlenestdistobs31(
            dict(
                disturbance_cause=gimme(distobs, "disturbance_cause"),
                disturbance_cause_confidence=gimme(distobs, "disturbance_cause_confidence"),
                disturbance_severity="na",
                photo_disturbance=photo_dict,
                comments=gimme(distobs, "comments")
            ),
            enc)

        enc.save()

    print(" Done: {0}\n".format(enc))
    return enc
