# -*- coding: utf-8 -*-
"""Observation untilities."""
import csv
from datetime import datetime
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

from wastd.observations.models import (
    Encounter, AnimalEncounter, LoggerEncounter, TurtleNestEncounter,
    LineTransectEncounter,
    MediaAttachment, TagObservation, NestTagObservation,
    TurtleNestObservation, TurtleNestDisturbanceObservation,
    TurtleNestDisturbanceTallyObservation, TrackTallyObservation,
    HatchlingMorphometricObservation,
    NEST_AGE_CHOICES, NEST_TYPE_CHOICES, OBSERVATION_CHOICES,
    NEST_DAMAGE_CHOICES, CONFIDENCE_CHOICES, TAG_STATUS_CHOICES
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
        msg = "Username {0} found by exact match: returning {1}"

    except ObjectDoesNotExist:
        usrs = User.objects.filter(username__icontains=un[0:4])

        if usrs.count() == 0:
            usr = User.objects.create(username=un, name=un)
            msg = "Username {0} not found: created {1}"

        elif usrs.count() == 1:
            usr = usrs[0]
            msg = "Username {0} found by fuzzy match: returning only match {1}"
            usr = usrs[0]

        else:
            usr = usrs[0]
            msg = "[WARNING] Username {0} returned multiple matches, choosing {1}"

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
    return os.path.join(settings.MEDIA_ROOT, "photos", photo_id)


def dl_photo(photo_id, photo_url, photo_filename):
    """Download a photo if not already done.

    Arguments

    photo_id The WAStD source_id of the record, to which this photo belongs
    photo_url A URL to download the photo from
    """
    pdir = make_photo_foldername(photo_id)
    if not os.path.exists(pdir):
        print("Creating folder {0}".format(pdir))
        os.mkdir(pdir)
    else:
        print(("Found folder {0}".format(pdir)))
    pname = os.path.join(pdir, photo_filename)

    if not os.path.exists(pname):
        print("Downloading file {0}...".format(pname))
        response = requests.get(photo_url, stream=True)
        with open(pname, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
    else:
        print("Found file {0}".format(pname))


def handle_photo(p, e, title="Track"):
    """Create a MediaAttachment of photo p to Encounter e with a given title.

    Arguments

    p The filepath of a locally accessible photograph
    e The related encounter (must exist)
    title The attachment's title (default: "Track")
    """
    # Does the file exist locally?
    if os.path.exists(p):
        print("File {0} exists".format(p))
        with open(p, 'rb') as photo:
            f = File(photo)
            # Is the file a dud?
            if f.size > 0:
                print("File size is {0}".format(f.size))

                # Does the MediaAttachment exist already?
                if MediaAttachment.objects.filter(encounter=e, title=title).exists():
                    m = MediaAttachment.objects.filter(encounter=e, title=title)[0]
                    action = "updated"
                else:
                    m = MediaAttachment(encounter=e, title=title)
                    action = "Created"

                # Update the file
                m.attachment.save(title, f, save=True)
                print("Photo {0}: {1}".format(action, m))
            else:
                print("[ERROR] zero size file {0}".format(p))
    else:
        print("[ERROR] missing file {0}".format(p))


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


    dd, created = TurtleNestDisturbanceObservation.objects.get_or_create(
        encounter=e,
        disturbance_cause=m["disturbance_cause"][d["disturbance_cause"]],
        disturbance_cause_confidence=m["disturbance_cause_confidence"][d["disturbance_cause_confidence"]],
        disturbance_severity=m["disturbance_severity"][d["disturbance_severity"]],
        comments=d["comments"]
        )
    dd.save()
    print("Turtle Nest Disturbance Obs {0}".format("created" if created else "found"))
    pprint(dd)

    if d["photo_disturbance"] is not None:
        dl_photo(e.source_id,
                 d["photo_disturbance"]["url"],
                 d["photo_disturbance"]["filename"])
        pdir = make_photo_foldername(e.source_id)
        pname = os.path.join(pdir, d["photo_disturbance"]["filename"])
        handle_photo(pname, e, title="Disturbance {0}".format(dd.disturbance_cause))
    pprint(dd)

    e.save()  # cache distobs in HTML

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
    dd, created = TurtleNestDisturbanceObservation.objects.get_or_create(
        encounter=e,
        disturbance_cause=d["disturbance_cause"],
        disturbance_cause_confidence=d["disturbance_cause_confidence"],
        disturbance_severity=d["disturbance_severity"],
        comments=d["comments"]
        )
    dd.save()
    print("Turtle Nest Disturbance Obs {0}".format("created" if created else "found"))
    pprint(dd)

    if d["photo_disturbance"] is not None:
        dl_photo(e.source_id,
                 d["photo_disturbance"]["url"],
                 d["photo_disturbance"]["filename"])
        pdir = make_photo_foldername(e.source_id)
        pname = os.path.join(pdir, d["photo_disturbance"]["filename"])
        handle_photo(pname, e, title="Disturbance {0}".format(dd.disturbance_cause))
    pprint(dd)

    e.save()  # cache distobs in HTML


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
    print("TurtleNestObservation {0}".format("created" if created else "found"))
    pprint(dd)

    for idx, ep in enumerate(d["egg_photos"]):
        dl_photo(e.source_id,
                 ep["photo_eggs"]["url"],
                 ep["photo_eggs"]["filename"])
        pdir = make_photo_foldername(e.source_id)
        pname = os.path.join(pdir, ep["photo_eggs"]["filename"])
        handle_photo(pname, e, title="Egg photo {0}".format(idx + 1))

    e.save()

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
    print("TurtleNestObservation {0}".format("created" if created else "found"))
    pprint(dd)

    for idx, ep in enumerate(d["egg_photos"]):
        dl_photo(e.source_id,
                 ep["photo_eggs"]["url"],
                 ep["photo_eggs"]["filename"])
        pdir = make_photo_foldername(e.source_id)
        pname = os.path.join(pdir, ep["photo_eggs"]["filename"])
        handle_photo(pname, e, title="Egg photo {0}".format(idx + 1))

    e.save()


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
    print(d)
    if (d["status"] is None and
            d["flipper_tag_id"] is None and
            d["date_nest_laid"] is None and
            d["tag_label"] is None):
        print("No TurtleNestObs found, skipping.")
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
        print("NestTagObservation {0}".format("created" if created else "found"))
        pprint(dd)

    if d["photo_tag"]:
        dl_photo(e.source_id,
                 d["photo_tag"]["url"],
                 d["photo_tag"]["filename"])
        pdir = make_photo_foldername(e.source_id)
        pname = os.path.join(pdir, d["photo_tag"]["filename"])
        handle_photo(pname, e, title="Nest tag photo")

    e.save()

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
    print(d)
    if (d["status"] is None and
            d["flipper_tag_id"] is None and
            d["date_nest_laid"] is None and
            d["tag_label"] is None):
        print("No TurtleNestObs found, skipping.")
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
        print("NestTagObservation {0}".format("created" if created else "found"))
        pprint(dd)

    if d["photo_tag"]:
        dl_photo(e.source_id,
                 d["photo_tag"]["url"],
                 d["photo_tag"]["filename"])
        pdir = make_photo_foldername(e.source_id)
        pname = os.path.join(pdir, d["photo_tag"]["filename"])
        handle_photo(pname, e, title="Nest tag photo")

    e.save()


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
    dd, created = HatchlingMorphometricObservation.objects.get_or_create(
        encounter=e,
        straight_carapace_length_mm=d["straight_carapace_length_mm"],
        straight_carapace_width_mm=d["straight_carapace_width_mm"],
        body_weight_g=d["body_weight_g"]
        )
    dd.save()
    print("HatchlingMorphometricObservation {0}".format("created" if created else "found"))
    pprint(dd)

    e.save()


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
    print("LoggerEncounter {0}".format("created" if created else "found"))
    pprint(dd)

    if d["photo_logger"]:
        dl_photo(e.source_id,
                 d["photo_logger"]["url"],
                 d["photo_logger"]["filename"])
        pdir = make_photo_foldername(e.source_id)
        pname = os.path.join(pdir, d["photo_logger"]["filename"])
        handle_photo(pname, dd, title="Logger ID photo")
        # The logger encounter dd gets the photo, not the encounter e!

    # If e has NestTagObservation, replicate NTO on LoggerEncounter
    if e.observation_set.instance_of(NestTagObservation).exists():
        nto = e.observation_set.instance_of(NestTagObservation).first()
        NestTagObservation.objects.get_or_create(
            encounter=e,
            status=nto.status,
            flipper_tag_id=nto.flipper_tag_id,
            date_nest_laid=nto.date_nest_laid,
            tag_label=nto.tag_label,
            )
        nto.save()
        print("NestTagObservation {0}".format("created" if created else "found"))
        pprint(nto)

    e.save()


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
    print("Found disturbance obs")
    pprint(d)

    dd, created = TurtleNestDisturbanceTallyObservation.objects.get_or_create(
        encounter=e,
        disturbance_cause=m["disturbance_cause"][d["disturbance_cause"]],
        no_nests_disturbed=d["no_nests_disturbed"] or 0,
        no_tracks_encountered=d["no_tracks_encountered"] or 0,
        comments=d["disturbance_comments"]
        )
    dd.save()
    e.save()  # cache distobs in HTML
    pprint(dd)


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
        nest_age=m["nest_age"][r["nest_age"]],
        nest_type=m["nest_type"][r["nest_type"]],
        species=m["species"][r["species"]],
        # comments
        )
    if r["nest_type"] in ["successfulcrawl", "nest", "hatchednest"]:
        new_data["habitat"] = m["habitat"][r["habitat"]]
        new_data["disturbance"] = m["disturbance"][r["disturbance"]]

    if src_id in m["overwrite"]:
        print("Updating unchanged existing record {0}...".format(src_id))
        TurtleNestEncounter.objects.filter(source_id=src_id).update(**new_data)
        e = TurtleNestEncounter.objects.get(source_id=src_id)
    else:
        print("Creating new record {0}...".format(src_id))
        e = TurtleNestEncounter.objects.create(**new_data)

    e.save()
    pprint(e)

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
        nest_age=m["nest_age"][r["nest_age"]],
        nest_type=m["nest_type"][r["nest_type"]],
        species=m["species"][r["species"]],
        # comments
        )
    if r["nest_type"] in ["successfulcrawl", "nest", "hatchednest"]:
        new_data["habitat"] = m["habitat"][r["habitat"]]
        new_data["disturbance"] = m["disturbance26"][r["disturbance"]]

    if src_id in m["overwrite"]:
        print("Updating unchanged existing record {0}...".format(src_id))
        TurtleNestEncounter.objects.filter(source_id=src_id).update(**new_data)
        e = TurtleNestEncounter.objects.get(source_id=src_id)
    else:
        print("Creating new record {0}...".format(src_id))
        e = TurtleNestEncounter.objects.create(**new_data)

    e.save()
    pprint(e)

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

    # TODO if both nest tag and logger enc present:
    # create nest tag obs on logger enc
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
        new_data["disturbance"] = m["disturbance26"][r["disturbance"]]

    if src_id in m["overwrite"]:
        print("Updating unchanged existing record {0}...".format(src_id))
        TurtleNestEncounter.objects.filter(source_id=src_id).update(**new_data)
        e = TurtleNestEncounter.objects.get(source_id=src_id)
    else:
        print("Creating new record {0}...".format(src_id))
        e = TurtleNestEncounter.objects.create(**new_data)

    e.save()
    pprint(e)

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

    return e


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
        # nest_age=m["nest_age"][r["nest_age"]],
        # nest_type=m["nest_type"][r["nest_type"]],
        # species=m["species"][r["species"]],
        # comments
        )

    if src_id in m["overwrite"]:
        print("Updating unchanged existing record {0}...".format(src_id))
        LineTransectEncounter.objects.filter(source_id=src_id).update(**new_data)
        e = LineTransectEncounter.objects.get(source_id=src_id)
    else:
        print("Creating new record {0}...".format(src_id))
        e = LineTransectEncounter.objects.create(**new_data)

    e.save()
    pprint(e)

    # TurtleNestDisturbanceTallyObservation
    [handle_turtlenestdisttallyobs(distobs, e, m)
     for distobs in r["disturbance"] if len(r["disturbance"]) > 0]

    # TrackTallyObservations
    # Flatbacks
    msg = 'Tally (created: {0}) {1}'
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["flatback"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="old",  # old fresh
        nest_type="track-not-assessed",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["fb_no_old_tracks"] or 0
        )
    print(msg.format(created, t))

    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["flatback"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="successful-crawl",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["fb_no_fresh_successful_crawls"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["flatback"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="false-crawl",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["fb_no_fresh_false_crawls"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["flatback"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="track-unsure",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["fb_no_fresh_tracks_unsure"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["flatback"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="track-not-assessed",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["fb_no_fresh_tracks_not_assessed"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["flatback"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="hatched-nest",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["fb_no_hatched_nests"] or 0
        )
    print(msg.format(created, t))

    # Greens
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["green"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="old",  # old fresh
        nest_type="track-not-assessed",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["gn_no_old_tracks"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["green"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="successful-crawl",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["gn_no_fresh_successful_crawls"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["green"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="false-crawl",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["gn_no_fresh_false_crawls"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["green"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="track-unsure",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["gn_no_fresh_tracks_unsure"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["green"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="track-not-assessed",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["gn_no_fresh_tracks_not_assessed"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["green"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="hatched-nest",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["gn_no_hatched_nests"] or 0
        )
    print(msg.format(created, t))

    # Hawksbills
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["hawksbill"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="old",  # old fresh
        nest_type="track-not-assessed",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["hb_no_old_tracks"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["hawksbill"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="successful-crawl",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["hb_no_fresh_successful_crawls"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["hawksbill"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="false-crawl",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["hb_no_fresh_false_crawls"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["hawksbill"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="track-unsure",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["hb_no_fresh_tracks_unsure"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["hawksbill"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="track-not-assessed",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["hb_no_fresh_tracks_not_assessed"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["hawksbill"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="hatched-nest",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["hb_no_hatched_nests"] or 0
        )
    print(msg.format(created, t))

    # Loggerheads
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["loggerhead"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="old",  # old fresh
        nest_type="track-not-assessed",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["lh_no_old_tracks"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["loggerhead"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="successful-crawl",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["lh_no_fresh_successful_crawls"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["loggerhead"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="false-crawl",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["lh_no_fresh_false_crawls"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["loggerhead"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="track-unsure",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["lh_no_fresh_tracks_unsure"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["loggerhead"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="track-not-assessed",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["lh_no_fresh_tracks_not_assessed"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["loggerhead"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="hatched-nest",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["lh_no_hatched_nests"] or 0
        )
    print(msg.format(created, t))

    # Olive Ridley
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["oliveridley"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="old",  # old fresh
        nest_type="track-not-assessed",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["or_no_old_tracks"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["oliveridley"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="successful-crawl",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["or_no_fresh_successful_crawls"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["oliveridley"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="false-crawl",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["or_no_fresh_false_crawls"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["oliveridley"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="track-unsure",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["or_no_fresh_tracks_unsure"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["oliveridley"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="track-not-assessed",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["or_no_fresh_tracks_not_assessed"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["oliveridley"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="hatched-nest",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["or_no_hatched_nests"] or 0
        )
    print(msg.format(created, t))

    # Unknown turtle
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["turtle"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="old",  # old fresh
        nest_type="track-not-assessed",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["unk_no_old_tracks"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["turtle"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="successful-crawl",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["unk_no_fresh_successful_crawls"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["turtle"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="false-crawl",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["unk_no_fresh_false_crawls"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["turtle"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="track-unsure",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["unk_no_fresh_tracks_unsure"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["turtle"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="track-not-assessed",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["unk_no_fresh_tracks_not_assessed"] or 0
        )
    print(msg.format(created, t))
    t, created = TrackTallyObservation.objects.get_or_create(
        encounter=e,
        species=m["species"]["turtle"],  # flatback green hawksbill loggerhead oliveridley turtle
        nest_age="fresh",  # old fresh
        nest_type="hatched-nest",  # false-crawl successful-crawl track-unsure track-not-assessed hatched-nest
        tally=r["unk_no_hatched_nests"] or 0
        )
    print(msg.format(created, t))


#------------------------------------------------------------------------------#
# WAMTRAM
#
def import_one_encounter_wamtram(r, m):
    """Import one ODK Track Tally 0.5 record into WAStD.

    Notably, counts of "None" are true absences and will be converted to "0".

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

    Point(float(r["LONGITUDE"]), float(r["LATITUDE"]))
    """
    print("Import one WAMTRAM...")
    pprint(r)

    print("Done.")


#------------------------------------------------------------------------------#
# Main import call
#
def import_odk(datafile, flavour="odk-trackortreat-026", extradata=None):
    """Import ODK Track Count 0.10 data.

    Arguments

    datafile A filepath to the JSON exported from ODK Aggregate
    flavour The ODK form with version

    flavour A string indicating the type of input

    extradata A second datafile (tags for WAMTRAM)

    Preparation:

    * https://dpaw-data.appspot.com/ > Submissions > Form e.g. "TrackCount 0.10"
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

    # generate a fresh mapping... once
    ODK_MAPPING = {
        # some values can be derived
        "nest_age": map_values(NEST_AGE_CHOICES),
        "nest_type": map_values(NEST_TYPE_CHOICES),
        "tag_status": map_values(TAG_STATUS_CHOICES),

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
        "disturbance26": {
            'yes': 'present',
            'no': 'absent',
            },
        "disturbance_cause": map_values(NEST_DAMAGE_CHOICES),
        # "disturbance_cause_confidence": map_values(CONFIDENCE_CHOICES),
        "disturbance_cause_confidence": {
            "na": "guess",
            "guess": "guess",
            "expertopinion": "expert-opinion",
            "validated": "validated",
            "validate": "validated",
            },
        "disturbance_severity": map_values(
            TurtleNestDisturbanceObservation.NEST_VIABILITY_CHOICES),

        "overwrite": [t.source_id for t in Encounter.objects.filter(
            source="odk", status=Encounter.STATUS_NEW)]
        }

    # typo in Track or Treat 0.26
    # ODK_MAPPING["disturbance_cause_confidence"]["validate"] = "validated"

    print("\n\nMapping:\n\n")
    pprint(ODK_MAPPING)

    if flavour == "odk-tc010":
        print("Using flavour ODK Track Count 0.10...")
        with open(datafile) as df:
            d = json.load(df)
            print("Loaded {0} records from {1}".format(len(d), datafile))
        ODK_MAPPING["users"] = {u: guess_user(u) for u in set([r["reporter"] for r in d])}
        ODK_MAPPING["keep"] = [t.source_id for t in Encounter.objects.exclude(
            status=Encounter.STATUS_NEW).filter(source="odk")]

        # Download photos
        pt = [[r["instanceID"],
               r["photo_track"]["url"],
               r["photo_track"]["filename"]]
              for r in d
              if r["photo_track"] is not None]
        pn = [[r["instanceID"],
               r["photo_nest"]["url"],
               r["photo_nest"]["filename"]]
              for r in d
              if r["photo_nest"] is not None]
        print("Downloading photos of {0} tracks and {1} nests".format(
            len(pt), len(pn)))
        all_photos = pt + pn
        [dl_photo(p[0], p[1], p[2]) for p in all_photos]

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

        # Download photos
        ptr = [[r["instanceID"],
                r["photo_track"]["url"],
                r["photo_track"]["filename"]]
               for r in d
               if r["photo_track"] is not None]

        pne = [[r["instanceID"],
                r["photo_nest"]["url"],
                r["photo_nest"]["filename"]]
               for r in d
               if r["photo_nest"] is not None]

        pta = [[r["instanceID"],
                r["photo_nest"]["url"],
                r["photo_nest"]["filename"]]
               for r in d
               if r["photo_nest"] is not None]

        print("Downloading photos of {0} tracks, {1} nests, {2} tags".format(
            len(ptr), len(pne), len(pta)))
        all_photos = ptr + pne + pta
        [dl_photo(p[0], p[1], p[2]) for p in all_photos]

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

        # Download photos
        ptr = [[r["instanceID"],
                r["photo_track"]["url"],
                r["photo_track"]["filename"]]
               for r in d
               if r["photo_track"] is not None]

        pne = [[r["instanceID"],
                r["photo_nest"]["url"],
                r["photo_nest"]["filename"]]
               for r in d
               if r["photo_nest"] is not None]

        pta = [[r["instanceID"],
                r["photo_nest"]["url"],
                r["photo_nest"]["filename"]]
               for r in d
               if r["photo_nest"] is not None]

        print("Downloading photos of {0} tracks, {1} nests, {2} tags".format(
            len(ptr), len(pne), len(pta)))
        all_photos = ptr + pne + pta
        [dl_photo(p[0], p[1], p[2]) for p in all_photos]

        [import_one_record_tt031(r, ODK_MAPPING) for r in d
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

        print("not impemented yet")

    elif flavour == "wamtram":
        print("Using flavour WAMTRAM...")
        enc = csv.DictReader(open(datafile))

        # ODK_MAPPING["users"] = {u: guess_user(u) for u in set([r["reporter"] for r in d])}
        ODK_MAPPING["keep"] = [t.source_id for t in Encounter.objects.exclude(
            status=Encounter.STATUS_NEW).filter(source="wamtram")]

        print("not impemented yet")
        [import_one_encounter_wamtram(e, ODK_MAPPING) for e in enc]

        # if extradata:
        #   tags = csv.DictReader(open(extradata))
        # [import_one_tag_wamtram(t, ODK_MAPPING) for t in tags]

    else:
        print("Format not recognized. Exiting.")
