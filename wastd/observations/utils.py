# -*- coding: utf-8 -*-
"""Observation untilities."""
import csv
from datetime import datetime
from dateutil import parser
import json
import os
from pprint import pprint
import requests
import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point, LineString
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.utils.dateparse import parse_datetime
from django.utils.timezone import get_fixed_timezone, utc

from wastd.observations.models import (
    Encounter, AnimalEncounter, LoggerEncounter, TurtleNestEncounter,
    LineTransectEncounter,
    MediaAttachment, TagObservation, NestTagObservation,
    TurtleNestObservation, TurtleNestDisturbanceObservation,
    TurtleNestDisturbanceTallyObservation, TrackTallyObservation,
    HatchlingMorphometricObservation,
    NEST_TYPE_CHOICES, TAG_STATUS_CHOICES, CETACEAN_SPECIES_CHOICES
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


# -----------------------------------------------------------------------------#
# Data import from ODK Aggregate
# TODO create and use writable API
#
def guess_user(un):
    """Find exact or fuzzy match of username, or create User.

    In order, return:

    * A user with username `un`, or
    * the first or only match of a user with username `icontain`ing the first
      five characters of `un`, or
    * a new user with username `un`.

    Arguments

    un A username

    Returns
    An instance of settings.AUTH_USER_MODEL
    """
    User = get_user_model()

    print("Guessing User for {0}...".format(un))

    try:
        usr = User.objects.get(username=un)
        msg = "   Username {0} found by exact match: returning {1}"

    except ObjectDoesNotExist:
        usrs = User.objects.filter(username__icontains=un[0:4])

        if usrs.count() == 0:
            usr = User.objects.create(username=un, name=un)
            msg = "  Username {0} not found: created {1}"

        elif usrs.count() == 1:
            usr = usrs[0]
            msg = "  Username {0} found by fuzzy match: returning only match {1}"
            usr = usrs[0]

        else:
            usr = usrs[0]
            msg = "  [WARNING] Username {0} returned multiple matches, choosing {1}"

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


def read_odk_linestring(odk_str):
    """Convert an ODK LineString string to a Django LineString."""
    # in: "-31.99656982 115.88441855 0.0 0.0;-31.9965685 115.88441522 0.0 0.0;"
    # out: Line(Point(115.88441855 -31.99656982) Point(115.88441522 -31.9965685))
    return LineString(
        [Point(float(c[1]), float(c[0])) for c in
         [p.split(" ") for p in odk_str.split(";") if len(p) > 0]
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
    print("  Creating photo attachment...")
    if os.path.exists(p):
        print("  File {0} exists".format(p))
        with open(p, 'rb') as photo:
            f = File(photo)
            # Is the file a dud?
            if f.size > 0:
                print("  File size is {0}".format(f.size))

                # Does the MediaAttachment exist already?
                if MediaAttachment.objects.filter(encounter=e, title=title).exists():
                    m = MediaAttachment.objects.filter(encounter=e, title=title)[0]
                    action = "updated"
                else:
                    m = MediaAttachment(encounter=e, title=title)
                    action = "Created"

                # Update the file
                m.attachment.save(title, f, save=True)
                print("  Photo {0}: {1}".format(action, m))
            else:
                print("  [ERROR] zero size file {0}".format(p))
    else:
        print("  [ERROR] missing file {0}".format(p))


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
                "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=build_TrackCount-0-10_1479172852%5B%40version%3Dnull+and+%40uiVersion%3Dnull%5D%2Fdata%5B%40key%3Duuid%3Af23177b3-2234-49be-917e-87b2096c921e%5D%2Fdisturbanceobservation%5B%40ordinal%3D1%5D%2Fphoto_disturbance"
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
        disturbance_cause_confidence=m["disturbance_cause_confidence"][d["disturbance_cause_confidence"]],
        disturbance_severity=d["disturbance_severity"],
        comments=d["comments"]
        )
    dd.save()
    action = "created" if created else "updated"
    print("  TurtleNestDisturbanceObservation {0}: {1}".format(action, dd))

    if d["photo_disturbance"] is not None:
        dl_photo(e.source_id,
                 d["photo_disturbance"]["url"],
                 d["photo_disturbance"]["filename"])
        pdir = make_photo_foldername(e.source_id)
        pname = os.path.join(pdir, d["photo_disturbance"]["filename"])
        handle_photo(pname, e, title="Disturbance {0}".format(dd.disturbance_cause))


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
                "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=build_TrackCount-0-10_1479172852%5B%40version%3Dnull+and+%40uiVersion%3Dnull%5D%2Fdata%5B%40key%3Duuid%3Af23177b3-2234-49be-917e-87b2096c921e%5D%2Fdisturbanceobservation%5B%40ordinal%3D1%5D%2Fphoto_disturbance"
            },
            "comments": null
        }
    e The related TurtleNestEncounter (must exist)
    """
    print("  Creating TurtleNestDisturbanceObservation...")
    dd, created = TurtleNestDisturbanceObservation.objects.get_or_create(
        encounter=e,
        disturbance_cause=d["disturbance_cause"],
        disturbance_cause_confidence=d["disturbance_cause_confidence"],
        disturbance_severity=d["disturbance_severity"],
        comments=d["comments"]
        )
    dd.save()
    action = "created" if created else "updated"
    print("  TurtleNestDisturbanceObservation {0}: {1}".format(action, dd))

    if d["photo_disturbance"] is not None:
        dl_photo(e.source_id,
                 d["photo_disturbance"]["url"],
                 d["photo_disturbance"]["filename"])
        pdir = make_photo_foldername(e.source_id)
        pname = os.path.join(pdir, d["photo_disturbance"]["filename"])
        handle_photo(pname, e, title="Disturbance {0}".format(dd.disturbance_cause))


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
                    "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=build_Track-or-Treat-0-26_1485851835%5B%40version%3Dnull+and+%40uiVersion%3Dnull%5D%2Fdata%5B%40key%3Duuid%3A22623d7c-ac39-46a1-9f99-741b7c668e58%5D%2Fegg_photos%5B%40ordinal%3D1%5D%2Fphoto_eggs"
                }
            },
            {
                "photo_eggs": {
                    "filename": "1485913376020.jpg",
                    "type": "image/jpeg",
                    "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=build_Track-or-Treat-0-26_1485851835%5B%40version%3Dnull+and+%40uiVersion%3Dnull%5D%2Fdata%5B%40key%3Duuid%3A22623d7c-ac39-46a1-9f99-741b7c668e58%5D%2Fegg_photos%5B%40ordinal%3D2%5D%2Fphoto_eggs"
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
        dl_photo(e.source_id,
                 ep["photo_eggs"]["url"],
                 ep["photo_eggs"]["filename"])
        pdir = make_photo_foldername(e.source_id)
        pname = os.path.join(pdir, ep["photo_eggs"]["filename"])
        handle_photo(pname, e, title="Egg photo {0}".format(idx + 1))


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
                    "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=build_Track-or-Treat-0-26_1485851835%5B%40version%3Dnull+and+%40uiVersion%3Dnull%5D%2Fdata%5B%40key%3Duuid%3A22623d7c-ac39-46a1-9f99-741b7c668e58%5D%2Fegg_photos%5B%40ordinal%3D1%5D%2Fphoto_eggs"
                }
            },
            {
                "photo_eggs": {
                    "filename": "1485913376020.jpg",
                    "type": "image/jpeg",
                    "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=build_Track-or-Treat-0-26_1485851835%5B%40version%3Dnull+and+%40uiVersion%3Dnull%5D%2Fdata%5B%40key%3Duuid%3A22623d7c-ac39-46a1-9f99-741b7c668e58%5D%2Fegg_photos%5B%40ordinal%3D2%5D%2Fphoto_eggs"
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
        dl_photo(e.source_id,
                 ep["photo_eggs"]["url"],
                 ep["photo_eggs"]["filename"])
        pdir = make_photo_foldername(e.source_id)
        pname = os.path.join(pdir, ep["photo_eggs"]["filename"])
        handle_photo(pname, e, title="Egg photo {0}".format(idx + 1))


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
            "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=build_Track-or-Treat-0-26_1485851835%5B%40version%3Dnull+and+%40uiVersion%3Dnull%5D%2Fdata%5B%40key%3Duuid%3A22623d7c-ac39-46a1-9f99-741b7c668e58%5D%2Fnest_tag%3Aphoto_tag"
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
            tag_label=d["tag_label"],
            )
        dd.save()
        action = "created" if created else "updated"
        print("  NestTagObservation {0}: {1}".format(action, dd))

    if d["photo_tag"]:
        dl_photo(e.source_id,
                 d["photo_tag"]["url"],
                 d["photo_tag"]["filename"])
        pdir = make_photo_foldername(e.source_id)
        pname = os.path.join(pdir, d["photo_tag"]["filename"])
        handle_photo(pname, e, title="Nest tag photo")


def handle_turtlenesttagobs31(d, e):
    """Get or create a TagObservation and related MediaAttachments.

    Arguments

    d A dictionary containing at least:
    {
        "status": "applied-new",
        "flipper_tag_id": "S1234",
        "date_nest_laid": "2017-02-01",
        "tag_label": "M1",
        "tag_comments": "test info",
        "photo_tag": {
            "filename": "1485913419914.jpg",
            "type": "image/jpeg",
            "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=build_Track-or-Treat-0-26_1485851835%5B%40version%3Dnull+and+%40uiVersion%3Dnull%5D%2Fdata%5B%40key%3Duuid%3A22623d7c-ac39-46a1-9f99-741b7c668e58%5D%2Fnest_tag%3Aphoto_tag"
    },

    e The related TurtleNestEncounter (must exist)
    """
    if (d["status"] is None and
            d["flipper_tag_id"] is None and
            d["date_nest_laid"] is None and
            d["tag_label"] is None):
        return
    else:
        dd, created = NestTagObservation.objects.get_or_create(
            encounter=e,
            status=d["status"],
            flipper_tag_id=d["flipper_tag_id"],
            date_nest_laid=datetime.strptime(
                d["date_nest_laid"], '%Y-%m-%d') if d["date_nest_laid"] else None,
            tag_label=d["tag_label"],
            )
        dd.save()
        action = "created" if created else "updated"
        print("  NestTagObservation {0}: {1}".format(action, dd))

    if d["photo_tag"]:
        dl_photo(e.source_id,
                 d["photo_tag"]["url"],
                 d["photo_tag"]["filename"])
        pdir = make_photo_foldername(e.source_id)
        pname = os.path.join(pdir, d["photo_tag"]["filename"])
        handle_photo(pname, e, title="Nest tag photo")


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
                "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=build_Track-or-Treat-0-26_1485851835%5B%40version%3Dnull+and+%40uiVersion%3Dnull%5D%2Fdata%5B%40key%3Duuid%3A22623d7c-ac39-46a1-9f99-741b7c668e58%5D%2Flogger_details%5B%40ordinal%3D1%5D%2Fphoto_logger"
            }
        }
    e The related TurtleNestEncounter (must exist)
    """
    print("  Creating LoggerEncounter...")
    dd, created = LoggerEncounter.objects.get_or_create(
        source=e.source,
        source_id="{0}-{1}".format(e.source_id, d["logger_id"]),
        where=e.where,
        when=e.when,
        location_accuracy=e.location_accuracy,
        observer=e.observer,
        reporter=e.reporter,
        deployment_status="retrieved",
        logger_id=d["logger_id"]
        )
    dd.save()
    action = "created" if created else "updated"
    print("  LoggerEncounter {0}: {1}".format(action, dd))

    if d["photo_logger"]:
        print("  Attaching photo to LoggerEncounter...")
        dl_photo(e.source_id,
                 d["photo_logger"]["url"],
                 d["photo_logger"]["filename"])
        pdir = make_photo_foldername(e.source_id)
        pname = os.path.join(pdir, d["photo_logger"]["filename"])
        handle_photo(pname, dd, title="Logger ID photo")
        # The logger encounter dd gets the photo, not the encounter e!

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


def import_one_record_tc010(r, m):
    """Import one ODK Track Count 0.10 record into WAStD.

    Arguments

    r The record as dict, e.g.
        {
            "instanceID": "uuid:f23177b3-2234-49be-917e-87b2096c921e",
            "observation_start_time": "2016-11-15T01:23:32.948Z",
            "reporter": "florianm",
            "nest_age": "fresh",
            "species": "flatback",
            "photo_track": {
                "filename": "1479173177551.jpg",
                "type": "image/jpeg",
                "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=build_TrackCount-0-10_1479172852%5B%40version%3Dnull+and+%40uiVersion%3Dnull%5D%2Fdata%5B%40key%3Duuid%3Af23177b3-2234-49be-917e-87b2096c921e%5D%2Fdetails%3Aphoto_track"
            },
            "nest_type": "successfulcrawl",
            "observed_at:Latitude": -32.05844863,
            "observed_at:Longitude": 115.77845847,
            "observed_at:Altitude": 19,
            "observed_at:Accuracy": 7,
            "habitat": "na",
            "photo_nest": {
                "filename": "1479173194012.jpg",
                "type": "image/jpeg",
                "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=build_TrackCount-0-10_1479172852%5B%40version%3Dnull+and+%40uiVersion%3Dnull%5D%2Fdata%5B%40key%3Duuid%3Af23177b3-2234-49be-917e-87b2096c921e%5D%2Fnest%3Aphoto_nest"
            },
            "disturbance": "present",
            "disturbanceobservation": [
                {
                    "disturbance_cause": "human",
                    "disturbance_cause_confidence": "expertopinion",
                    "disturbance_severity": "na",
                    "photo_disturbance": {
                        "filename": "1479173301849.jpg",
                        "type": "image/jpeg",
                        "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=build_TrackCount-0-10_1479172852%5B%40version%3Dnull+and+%40uiVersion%3Dnull%5D%2Fdata%5B%40key%3Duuid%3Af23177b3-2234-49be-917e-87b2096c921e%5D%2Fdisturbanceobservation%5B%40ordinal%3D1%5D%2Fphoto_disturbance"
                    },
                    "comments": null
                }
            ],
            "observation_end_time": "2016-11-15T01:29:59.935Z"
        },

    m The mapping of ODK to WAStD choices

    Returns

    The created Encounter instance.

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

    # MediaAttachment "Photo of track"
    if r["photo_track"] is not None:
        pdir = make_photo_foldername(src_id)
        pname = os.path.join(pdir, r["photo_track"]["filename"])
        handle_photo(pname, e, title="Track")

    # MediaAttachment "Photo of nest"
    if r["photo_nest"] is not None:
        pdir = make_photo_foldername(src_id)
        pname = os.path.join(pdir, r["photo_nest"]["filename"])
        handle_photo(pname, e, title="Nest")

    # TurtleNestDisturbanceObservation, MediaAttachment "Photo of disturbance"
    [handle_turtlenestdistobs(distobs, e, m)
     for distobs in r["disturbanceobservation"]
     if len(r["disturbanceobservation"]) > 0]

    print(" Saved {0}\n".format(e))
    e.save()
    return e


def import_one_record_tt026(r, m):
    """Import one ODK Track or Treat 0.16 record into WAStD.

    Arguments

    r The record as dict, e.g.

    {
        "instanceID": "uuid:22623d7c-ac39-46a1-9f99-741b7c668e58",
        "observation_start_time": "2017-02-01T01:37:11.947Z",
        "reporter": "florianm",
        "nest_age": "fresh",
        "species": "flatback",
        "photo_track": {
            "filename": "1485913222981.jpg",
            "type": "image/jpeg",
            "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=build_Track-or-Treat-0-26_1485851835%5B%40version%3Dnull+and+%40uiVersion%3Dnull%5D%2Fdata%5B%40key%3Duuid%3A22623d7c-ac39-46a1-9f99-741b7c668e58%5D%2Fdetails%3Aphoto_track"
        },
        "nest_type": "successfulcrawl",
        "observed_at:Latitude": -31.99673702,
        "observed_at:Longitude": 115.88434861,
        "observed_at:Altitude": -5,
        "observed_at:Accuracy": 8,
        "habitat": "edgeofvegetation",
        "photo_nest": {
            "filename": "1485913247467.jpg",
            "type": "image/jpeg",
            "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=build_Track-or-Treat-0-26_1485851835%5B%40version%3Dnull+and+%40uiVersion%3Dnull%5D%2Fdata%5B%40key%3Duuid%3A22623d7c-ac39-46a1-9f99-741b7c668e58%5D%2Fnest%3Aphoto_nest"
        },
        "disturbance": "yes",
        "eggs_counted": "yes",
        "nest_tagged": "yes",
        "logger_found": "yes",
        "hatchlings_measured": "yes",
        "disturbanceobservation": [
            {
                "photo_disturbance": {
                    "filename": "1485913281914.jpg",
                    "type": "image/jpeg",
                    "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=build_Track-or-Treat-0-26_1485851835%5B%40version%3Dnull+and+%40uiVersion%3Dnull%5D%2Fdata%5B%40key%3Duuid%3A22623d7c-ac39-46a1-9f99-741b7c668e58%5D%2Fdisturbanceobservation%5B%40ordinal%3D1%5D%2Fphoto_disturbance"
                },
                "disturbance_cause": "human",
                "disturbance_cause_confidence": "expertopinion",
                "disturbance_severity": "partly",
                "comments": "test"
            },
            {
                "photo_disturbance": {
                    "filename": "1485913310961.jpg",
                    "type": "image/jpeg",
                    "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=build_Track-or-Treat-0-26_1485851835%5B%40version%3Dnull+and+%40uiVersion%3Dnull%5D%2Fdata%5B%40key%3Duuid%3A22623d7c-ac39-46a1-9f99-741b7c668e58%5D%2Fdisturbanceobservation%5B%40ordinal%3D2%5D%2Fphoto_disturbance"
                },
                "disturbance_cause": "bird",
                "disturbance_cause_confidence": "expertopinion",
                "disturbance_severity": "partly",
                "comments": "test2"
            }
        ],
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
                    "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=build_Track-or-Treat-0-26_1485851835%5B%40version%3Dnull+and+%40uiVersion%3Dnull%5D%2Fdata%5B%40key%3Duuid%3A22623d7c-ac39-46a1-9f99-741b7c668e58%5D%2Fegg_photos%5B%40ordinal%3D1%5D%2Fphoto_eggs"
                }
            },
            {
                "photo_eggs": {
                    "filename": "1485913376020.jpg",
                    "type": "image/jpeg",
                    "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=build_Track-or-Treat-0-26_1485851835%5B%40version%3Dnull+and+%40uiVersion%3Dnull%5D%2Fdata%5B%40key%3Duuid%3A22623d7c-ac39-46a1-9f99-741b7c668e58%5D%2Fegg_photos%5B%40ordinal%3D2%5D%2Fphoto_eggs"
                }
            }
        ],
        "status": "resighted",
        "flipper_tag_id": "S1234",
        "date_nest_laid": "2017-02-01",
        "tag_label": "M1",
        "tag_comments": "test info",
        "photo_tag": {
            "filename": "1485913419914.jpg",
            "type": "image/jpeg",
            "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=build_Track-or-Treat-0-26_1485851835%5B%40version%3Dnull+and+%40uiVersion%3Dnull%5D%2Fdata%5B%40key%3Duuid%3A22623d7c-ac39-46a1-9f99-741b7c668e58%5D%2Fnest_tag%3Aphoto_tag"
        },
        "logger_details": [
            {
                "logger_id": "S1235",
                "photo_logger": {
                    "filename": "1485913441063.jpg",
                    "type": "image/jpeg",
                    "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=build_Track-or-Treat-0-26_1485851835%5B%40version%3Dnull+and+%40uiVersion%3Dnull%5D%2Fdata%5B%40key%3Duuid%3A22623d7c-ac39-46a1-9f99-741b7c668e58%5D%2Flogger_details%5B%40ordinal%3D1%5D%2Fphoto_logger"
                }
            },
            {
                "logger_id": "S1236",
                "photo_logger": {
                    "filename": "1485913471237.jpg",
                    "type": "image/jpeg",
                    "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=build_Track-or-Treat-0-26_1485851835%5B%40version%3Dnull+and+%40uiVersion%3Dnull%5D%2Fdata%5B%40key%3Duuid%3A22623d7c-ac39-46a1-9f99-741b7c668e58%5D%2Flogger_details%5B%40ordinal%3D2%5D%2Fphoto_logger"
                }
            }
        ],
        "hatchling_measurements": [
            {
                "straight_carapace_length_mm": 12,
                "straight_carapace_width_mm": 13,
                "body_weight_g": 14
            },
            {
                "straight_carapace_length_mm": 14,
                "straight_carapace_width_mm": 15,
                "body_weight_g": 16
            },
            {
                "straight_carapace_length_mm": 17,
                "straight_carapace_width_mm": 18,
                "body_weight_g": 19
            }
        ],
        "observation_end_time": "2017-02-01T01:44:59.504Z"
    }

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

    # MediaAttachment "Photo of track"
    if r["photo_track"] is not None:
        pdir = make_photo_foldername(src_id)
        pname = os.path.join(pdir, r["photo_track"]["filename"])
        handle_photo(pname, e, title="Track")

    # MediaAttachment "Photo of nest"
    if r["photo_nest"] is not None:
        pdir = make_photo_foldername(src_id)
        pname = os.path.join(pdir, r["photo_nest"]["filename"])
        handle_photo(pname, e, title="Nest")

    # TurtleNestDisturbanceObservation, MediaAttachment "Photo of disturbance"
    [handle_turtlenestdistobs(distobs, e, m)
     for distobs in r["disturbanceobservation"]
     if r["disturbance"] and len(r["disturbanceobservation"]) > 0]

    # TurtleNestObservation
    if r["eggs_counted"] == "yes":
        handle_turtlenestobs(r, e, m)

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


def import_one_record_tt031(r, m):
    """Import one ODK Track or Treat 0.31 record into WAStD.


    The only change vs tt026 is that ODK now allows dashes in choice values.
    The following choices are now are identical to WAStD
    and do not require a mapping any longer:

    * nest_type
    * habitat
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
        species=m["species"][r["species"]],
        # comments
        )
    if r["nest_type"] in ["successfulcrawl", "nest", "hatchednest"]:
        new_data["habitat"] = r["habitat"]
        new_data["disturbance"] = m["disturbance"][r["disturbance"]]

    if src_id in m["overwrite"]:
        print("Updating unchanged existing record {0}...".format(src_id))
        TurtleNestEncounter.objects.filter(source_id=src_id).update(**new_data)
        e = TurtleNestEncounter.objects.get(source_id=src_id)
    else:
        print("Creating new record {0}...".format(src_id))
        e = TurtleNestEncounter.objects.create(**new_data)

    e.save()

    # MediaAttachment "Photo of track"
    if r["photo_track"] is not None:
        pdir = make_photo_foldername(src_id)
        pname = os.path.join(pdir, r["photo_track"]["filename"])
        handle_photo(pname, e, title="Track")

    # MediaAttachment "Photo of nest"
    if r["photo_nest"] is not None:
        pdir = make_photo_foldername(src_id)
        pname = os.path.join(pdir, r["photo_nest"]["filename"])
        handle_photo(pname, e, title="Nest")

    # TurtleNestDisturbanceObservation, MediaAttachment "Photo of disturbance"
    [handle_turtlenestdistobs31(distobs, e)
     for distobs in r["disturbanceobservation"]
     if r["disturbance"] and len(r["disturbanceobservation"]) > 0]

    # TurtleNestObservation
    if r["eggs_counted"] == "yes":
        handle_turtlenestobs31(r, e)

    # NestTagObservation
    if r["nest_tagged"]:
        handle_turtlenesttagobs31(r, e)

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
        nest_type=r["nest_type"],
        species=r["species"],
        # comments
        )
    if r["nest_type"] in ["successfulcrawl", "nest", "hatchednest"]:
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

    # MediaAttachment "Photo of track"
    if r["photo_track"] is not None:
        pdir = make_photo_foldername(src_id)
        pname = os.path.join(pdir, r["photo_track"]["filename"])
        handle_photo(pname, e, title="Track")

    # MediaAttachment "Photo of nest"
    if r["photo_nest"] is not None:
        pdir = make_photo_foldername(src_id)
        pname = os.path.join(pdir, r["photo_nest"]["filename"])
        handle_photo(pname, e, title="Nest")

    # TurtleNestDisturbanceObservation, MediaAttachment "Photo of disturbance"
    [handle_turtlenestdistobs31(distobs, e)
     for distobs in r["disturbanceobservation"]
     if r["disturbance"] and len(r["disturbanceobservation"]) > 0]

    # TurtleNestObservation
    if r["eggs_counted"] == "yes":
        handle_turtlenestobs31(r, e)

    # NestTagObservation
    if r["nest_tagged"]:
        handle_turtlenesttagobs31(r, e)

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


def make_tallyobs(encounter, species, nest_age, nest_type, tally_number):
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
        [FB, "old",   "track-not-assessed", r["fb_no_old_tracks"] or 0],
        [FB, "fresh", "successful-crawl",   r["fb_no_fresh_successful_crawls"] or 0],
        [FB, "fresh", "false-crawl",        r["fb_no_fresh_false_crawls"] or 0],
        [FB, "fresh", "track-unsure",       r["fb_no_fresh_tracks_unsure"] or 0],
        [FB, "fresh", "track-not-assessed", r["fb_no_fresh_tracks_not_assessed"] or 0],
        [FB, "fresh", "hatched-nest",       r["fb_no_hatched_nests"] or 0],

        [GN, "old",   "track-not-assessed", r["gn_no_old_tracks"] or 0],
        [GN, "fresh", "successful-crawl",   r["gn_no_fresh_successful_crawls"] or 0],
        [GN, "fresh", "false-crawl",        r["gn_no_fresh_false_crawls"] or 0],
        [GN, "fresh", "track-unsure",       r["gn_no_fresh_tracks_unsure"] or 0],
        [GN, "fresh", "track-not-assessed", r["gn_no_fresh_tracks_not_assessed"] or 0],
        [GN, "fresh", "hatched-nest",       r["gn_no_hatched_nests"] or 0],

        [HB, "old", "track-not-assessed",   r["hb_no_old_tracks"] or 0],
        [HB, "fresh", "successful-crawl",   r["hb_no_fresh_successful_crawls"] or 0],
        [HB, "fresh", "false-crawl",        r["hb_no_fresh_false_crawls"] or 0],
        [HB, "fresh", "track-unsure",       r["hb_no_fresh_tracks_unsure"] or 0],
        [HB, "fresh", "track-not-assessed", r["hb_no_fresh_tracks_not_assessed"] or 0],
        [HB, "fresh", "hatched-nest",       r["hb_no_hatched_nests"] or 0],

        [LH, "old", "track-not-assessed",   r["lh_no_old_tracks"] or 0],
        [LH, "fresh", "successful-crawl",   r["lh_no_fresh_successful_crawls"] or 0],
        [LH, "fresh", "false-crawl",        r["lh_no_fresh_false_crawls"] or 0],
        [LH, "fresh", "track-unsure",       r["lh_no_fresh_tracks_unsure"] or 0],
        [LH, "fresh", "track-not-assessed", r["lh_no_fresh_tracks_not_assessed"] or 0],
        [LH, "fresh", "hatched-nest",       r["lh_no_hatched_nests"] or 0],

        [OR, "old", "track-not-assessed",   r["or_no_old_tracks"] or 0],
        [OR, "fresh", "successful-crawl",   r["or_no_fresh_successful_crawls"] or 0],
        [OR, "fresh", "false-crawl",        r["or_no_fresh_false_crawls"] or 0],
        [OR, "fresh", "track-unsure",       r["or_no_fresh_tracks_unsure"] or 0],
        [OR, "fresh", "track-not-assessed", r["or_no_fresh_tracks_not_assessed"] or 0],
        [OR, "fresh", "hatched-nest",       r["or_no_hatched_nests"] or 0],

        [UN, "old", "track-not-assessed",   r["unk_no_old_tracks"] or 0],
        [UN, "fresh", "successful-crawl",   r["unk_no_fresh_successful_crawls"] or 0],
        [UN, "fresh", "false-crawl",        r["unk_no_fresh_false_crawls"] or 0],
        [UN, "fresh", "track-unsure",       r["unk_no_fresh_tracks_unsure"] or 0],
        [UN, "fresh", "track-not-assessed", r["unk_no_fresh_tracks_not_assessed"] or 0],
        [UN, "fresh", "hatched-nest",       r["unk_no_hatched_nests"] or 0],
        ]

    [make_tallyobs(e, x[0], x[1], x[2], x[3]) for x in tally_mapping]

    e.save()
    print(" Saved {0}\n".format(e))
    return e


# -----------------------------------------------------------------------------#
# WAMTRAM
#
def import_one_encounter_wamtram(r, m):
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
    src_id = "wamtram-observation-id-{0}".format(r["OBSERVATION_ID"])
    new_data = dict(
        source="wamtram",
        source_id=src_id,
        where=Point(float(r["LONGITUDE"]), float(r["LATITUDE"])),
        when=parse_datetime("{0}+00".format(r["observation_datetime_utc"])),
        location_accuracy="10",
        observer_id=1,  # lookup_w2_user(r["REPORTER_PERSON_ID"]),
        reporter_id=1,
        taxon="Cheloniidae",
        species=m["species"][r["SPECIES_CODE"]],
        activity=m["activity"][r['activity_code']],
        sex="female",
        maturity="adult",
        health=m["health"][r['CONDITION_CODE']],
        )

    """
    TODO create mapping for:
    habitat = m["habitat"][r['BEACH_POSITION_CODE']],
    behaviour="", # all comments go here
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
    """Render a dict's field to text

    Return
        '<fieldname>: <dictobj["fieldname"]>' or ''
    """
    return "{0}: {1}\n\n".format(fieldname, dictobj[fieldname]) if \
        fieldname in dictobj and dictobj[fieldname] != "" else ""


def import_one_record_cet(r, m):
    """Import one Cetacean strandings database record into WAStD.

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
    SPECIES = dict([[d[0], d[0]] for d in CETACEAN_SPECIES_CHOICES])
    # TODO this mapping needs QA (add species to CETACEAN_SPECIES_CHOICES)
    SPECIES.update({
        '': 'cetacea',
        'balaenopter-musculus-brevicauda': "balaenoptera-musculus-brevicauda",
        'balaenopters-cf-b-omurai': "balaenoptera-omurai",
        'kogia-simus': "kogia-sima",
        'sousa-chinensis': 'sousa-sahulensis',
        'orcaella-heinsohni-x': "orcaella-heinsohni",
        'stenella--sp-(coeruleoalba)': "stenella-sp",
        })

    COD = {
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
        'species': SPECIES[fix_species_name(r["Scientific Name"] or '')],
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
        'cause_of_death': COD[r["Cause of Death _drop down_"]],
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
    """Convert the pinniped strandings coordinate format into a Point.

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
    """Import one Pinniped strandings database record into WAStD.

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


# -----------------------------------------------------------------------------#
# Main import call
#
def import_odk(datafile, flavour="odk-tt031", extradata=None):
    """Import ODK Track Count 0.10 data.

    Arguments

    datafile A filepath to the JSON exported from ODK Aggregate
    flavour The ODK form with version

    flavour A string indicating the type of input

    extradata A second datafile (tags for WAMTRAM)

    Preparation:

    * https://dpaw-data.appspot.com/ > Submissions > Form e.g. "Track or Treat 0.31"
    * Export > JSON > Export
    * Submissions > Exported Submissions > download JSON

    Behaviour:

    * Records not in WAStD will be created
    * Records in WAStD of status NEW (unchanged since import) will be updated
    * Records in WAStD of status **above** NEW (QA'd and possibly locally changed) will be skipped

    Example:

        >>> from wastd.observations.utils import *
        >>> import_odk('data/TrackCount_0_10_results.json', flavour="odk-tc010")
        >>> import_odk('data/Track_or_Treat_0_26_results.json', flavour="odk-tt026")
        >>> import_odk('data/Track_or_Treat_0_31_results.json', flavour="odk-tt031")
        >>> import_odk('data/Track_or_Treat_0_34_results.json', flavour="odk-tt034")
        >>> import_odk('data/cetaceans.csv', flavour="cet")

    """
    # Older ODK forms don't support dashes for choice fields and require mapping
    ODK_MAPPING = {
        # some values can be derived
        "nest_type": map_values(NEST_TYPE_CHOICES),
        "tag_status": map_values(TAG_STATUS_CHOICES),

        "species": {
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
            },
        "activity": {
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
            },
        "health": {
            "F": "dead-edible",     # Carcase - fresh
            "G": "alive",           # Good - fat
            "H": "alive",           # Live & fit
            "I": "alive",           # Injured but OK
            "M": "alive",           # Moribund
            "P": "alive",           # Poor - thin
            "NA": "na",
            },

        # tag status 0L A1 A2 ae AE M M1 N OO OX p P P_ED P_OK PX Q R RC RQ

        "habitat": {
            'abovehwm': 'beach-above-high-water',
            'belowhwm': 'beach-below-high-water',
            'edgeofvegetation': 'beach-edge-of-vegetation',
            'vegetation': 'in-dune-vegetation',
            'na': 'na',
            },
        "disturbance": {
            'yes': 'present',
            'no': 'absent',
            },
        # typo in Track or Treat 0.26: validate (missing "d")
        "disturbance_cause_confidence": {
            "na": "guess",
            "guess": "guess",
            "expertopinion": "expert-opinion",
            "validated": "validated",
            "validate": "validated",
            },
        "overwrite": [t.source_id for t in Encounter.objects.filter(
            source="odk", status=Encounter.STATUS_NEW)]
        }

    if flavour == "odk-tc010":
        print("Using flavour ODK Track Count 0.10...")
        with open(datafile) as df:
            d = json.load(df)
            print("Loaded {0} records from {1}".format(len(d), datafile))
        ODK_MAPPING["users"] = {u: guess_user(u) for u in set([r["reporter"] for r in d])}
        ODK_MAPPING["keep"] = [t.source_id for t in Encounter.objects.exclude(
            status=Encounter.STATUS_NEW).filter(source="odk")]

        [import_one_record_tc010(r, ODK_MAPPING) for r in d
         if r["instanceID"] not in ODK_MAPPING["keep"]]     # retain local edits
        print("Done!")

    elif flavour == "odk-tt026":
        print("Using flavour ODK Track or Treat 0.26...")
        with open(datafile) as df:
            d = json.load(df)
            print("Loaded {0} records from {1}".format(len(d), datafile))
        ODK_MAPPING["users"] = {u: guess_user(u) for u in set([r["reporter"] for r in d])}
        ODK_MAPPING["keep"] = [t.source_id for t in Encounter.objects.exclude(
            status=Encounter.STATUS_NEW).filter(source="odk")]

        [import_one_record_tt026(r, ODK_MAPPING) for r in d
         if r["instanceID"] not in ODK_MAPPING["keep"]]     # retain local edits
        print("Done!")

    elif flavour == "odk-tt031":
        print("Using flavour ODK Track or Treat 0.31...")
        with open(datafile) as df:
            d = json.load(df)
            print("Loaded {0} records from {1}".format(len(d), datafile))
        ODK_MAPPING["users"] = {u: guess_user(u) for u in set([r["reporter"] for r in d])}
        ODK_MAPPING["keep"] = [t.source_id for t in Encounter.objects.exclude(
            status=Encounter.STATUS_NEW).filter(source="odk")]

        [import_one_record_tt031(r, ODK_MAPPING) for r in d
         if r["instanceID"] not in ODK_MAPPING["keep"]]     # retain local edits
        print("Done!")

    elif flavour == "odk-tt034":
            print("Using flavour ODK Track or Treat 0.34...")
            with open(datafile) as df:
                d = json.load(df)
                print("Loaded {0} records from {1}".format(len(d), datafile))
            ODK_MAPPING["users"] = {u: guess_user(u) for u in set([r["reporter"] for r in d])}
            ODK_MAPPING["keep"] = [t.source_id for t in Encounter.objects.exclude(
                status=Encounter.STATUS_NEW).filter(source="odk")]

            [import_one_record_tt034(r, ODK_MAPPING) for r in d
             if r["instanceID"] not in ODK_MAPPING["keep"]]     # retain local edits
            print("Done!")

    elif flavour == "odk-tally05":
        print("Using flavour ODK Track Tally 0.5...")
        with open(datafile) as df:
            d = json.load(df)
            print("Loaded {0} records from {1}".format(len(d), datafile))
        ODK_MAPPING["users"] = {u: guess_user(u) for u in set([r["reporter"] for r in d])}
        ODK_MAPPING["keep"] = [t.source_id for t in Encounter.objects.exclude(
            status=Encounter.STATUS_NEW).filter(source="odk")]

        [import_one_record_tt05(r, ODK_MAPPING) for r in d
         if r["instanceID"] not in ODK_MAPPING["keep"]]     # retain local edits
        print("Done!")

    elif flavour == "cet":
        print("Using flavour Cetacean strandings...")
        # ODK_MAPPING["users"] = {u: guess_user(u) for u in set([r["reporter"] for r in d])}
        ODK_MAPPING["keep"] = [t.source_id for t in Encounter.objects.exclude(
            status=Encounter.STATUS_NEW).filter(source="cet")]
        ODK_MAPPING["overwrite"] = [t.source_id for t in Encounter.objects.filter(
            source="cet", status=Encounter.STATUS_NEW)]

        enc = csv.DictReader(open(datafile))

        [import_one_record_cet(e, ODK_MAPPING) for e in enc
         if e["Record No."] not in ODK_MAPPING["keep"]]

    elif flavour == "pin":
        print("Using flavour Pinniped strandings...")
        # ODK_MAPPING["users"] = {u: guess_user(u) for u in set([r["reporter"] for r in d])}
        ODK_MAPPING["keep"] = [t.source_id for t in Encounter.objects.exclude(
            status=Encounter.STATUS_NEW).filter(source="pin")]
        enc = csv.DictReader(open(datafile))
        print("not impemented yet")

    elif flavour == "w2":
        print("ALL ABOARD THE WAMTRAM!!!")
        enc = csv.DictReader(open(datafile))

        # ODK_MAPPING["users"] = {u: guess_user(u) for u in set([r["reporter"] for r in d])}
        ODK_MAPPING["keep"] = [t.source_id for t in Encounter.objects.exclude(
            status=Encounter.STATUS_NEW).filter(source="wamtram")]
        ODK_MAPPING["overwrite"] = [t.source_id for t in Encounter.objects.filter(
            source="wamtram", status=Encounter.STATUS_NEW)]

        [import_one_encounter_wamtram(e, ODK_MAPPING) for e in enc
         if e["OBSERVATION_ID"] not in ODK_MAPPING["keep"]]

        # if extradata:
        #   tags = csv.DictReader(open(extradata))
        # [import_one_tag_wamtram(t, ODK_MAPPING) for t in tags]

    else:
        print("Format not recognized. Exiting.")
