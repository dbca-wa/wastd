# -*- coding: utf-8 -*-
"""Observation untilities."""
import csv
import json
import io
import os

from confy import env
from datetime import datetime, timedelta
from dateutil import parser
# from plogger.debug import plogger.debug
import logging
import requests
import shutil
import xmltodict
import pandas

from requests.auth import HTTPDigestAuth

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

logger = logging.getLogger(__name__)


def set_site(sites, encounter):
    """Set the site for an Encounter from a list of sites."""
    encounter.site = sites.filter(geom__contains=encounter.where).first() or None
    encounter.save(update_fields=["site"])
    logger.info("Found encounter {0} at site {1}".format(encounter, encounter.site))
    return enc


def set_sites():
    """Set the site where missing for all NEW Encounters."""
    sites = Area.objects.filter(area_type=Area.AREATYPE_SITE)
    enc = Encounter.objects.filter(status=Encounter.STATUS_NEW, site=None)
    logger.info("[wastd.observations.utils.set_sites] Found {0} encounters without site".format(enc.count()))
    return [set_site(sites, e) for e in enc]


def reconstruct_missing_surveys(buffer_mins=30):
    """Create missing surveys.

    Find TurtleNestEncounters with missing survey but existing site,
    group by date and site, aggregate datetime ("when") into earliest and latest record,
    buffer earliest and latest record by given minutes (default: 30),
    create a Survey with aggregated data.

    Crosstab: See pandas


    """
    logger.info("[QA][reconstruct_missing_surveys] Rounding up the orphans...")
    tne = TurtleNestEncounter.objects.exclude(site=None).filter(survey=None)
    logger.info("[QA][reconstruct_missing_surveys] Done. Found {0} orphans witout survey.".format(tne.count()))
    logger.info("[QA][reconstruct_missing_surveys] Inferring missing survey data...")
    tne_all = [[t.site.id, t.when.date(), t.when, t.reporter] for t in tne]
    tne_idx = [[t[0], t[1]] for t in tne_all]
    tne_data = [[t[2], t[3]] for t in tne_all]
    idx = pandas.MultiIndex.from_tuples(tne_idx, names=['site', 'date'])
    df = pandas.DataFrame(tne_data, index=idx, columns=['datetime', 'reporter'])
    missing_surveys = pandas.pivot_table(df,
                                         index=['date', 'site'],
                                         values=['datetime', 'reporter'],
                                         aggfunc={'datetime': [min, max], 'reporter': 'first'})
    logger.info("[QA][reconstruct_missing_surveys] Done. Creating {0} missing surveys...".format(len(missing_surveys)))

    bfr = timedelta(minutes=buffer_mins)
    for idx, row in missing_surveys.iterrows():
        logger.debug("Missing Survey on {0} at {1} by {2} from {3}-{4}".format(
            idx[0],
            idx[1],
            row['reporter']['first'],
            row['datetime']['min'] - bfr,
            row['datetime']['max'] + bfr
        ))
        s = Survey.objects.create(
            source="reconstructed",
            site=Area.objects.get(id=idx[1]),
            start_time=row['datetime']['min'] - bfr,
            end_time=row['datetime']['max'] + bfr,
            reporter=row['reporter']['first'],
            start_comments="[QA][AUTO] Reconstructed by WAStD from TurtleNestEncounters without surveys."
        )
        s.save()
    logger.info("[QA][reconstruct_missing_surveys] Done. Created {0} surveys to "
                "adopt {1} orphaned TurtleNestEncounters.".format(
                    len(missing_surveys), tne.count()))

    tne = TurtleNestEncounter.objects.exclude(site=None).filter(survey=None)
    logger.info("[QA][reconstruct_missing_surveys] Remaining orphans witout survey: {0}".format(tne.count()))

    return None


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
    ss = [s.save() for s in Survey.objects.all()]
    ae = [a.set_name_and_propagate(a.primary_flipper_tag.name)
          for a in AnimalEncounter.objects.all() if a.is_new_capture]
    le = [a.save() for a in LoggerEncounter.objects.all()]
    return [ss, ae, le]


def symlink_one_resource(t_dir, rj):
    """Symlink photographs of a resource JSON ``rj`` to a temp dir ``t_dir``."""
    if "photographs" in rj and len(rj["photographs"]) > 0:
        # Once per encounter, create temp_dir/media_path
        media_path = os.path.split(rj["photographs"][0]["attachment"])[0]
        logger.info("pre_latex symlinking {0}".format(media_path))
        dest_dir = os.path.join(t_dir, "tex", media_path)
        os.makedirs(dest_dir)
        logger.info("pre_latex created {0}".format(str(dest_dir)))

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
        logger.info("No photographs found.")


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
            logger.info("Symlinking photographs of a GeoJSON FeatureCollection")
            [symlink_one_resource(t_dir, f["properties"]) for f in d["features"]]

        elif d["type"] == "Feature":
            logger.info("Symlinking photographs of a GeoJSON Feature")
            symlink_one_resource(t_dir, d["properties"])

    elif "photographs" in d.keys():
        logger.info("Symlinking photographs of a JSON object")
        symlink_one_resource(t_dir, d)
    else:
        logger.info("Symlinking photographs of a list of JSON objects")
        [symlink_one_resource(t_dir, enc) for enc in d]


# -----------------------------------------------------------------------------#
# Data import from ODK Aggregate
# TODO create and use writable API
#
def lowersnake(unsafe_string):
    """Slugify an unsafe string, e.g. turn a full name into a username."""
    return unsafe_string.replace(" ", "_").replace(".", "_").lower()


def upperwhite(safe_string):
    """Return a username as full name."""
    return safe_string.replace("_", " ").title()


def make_user(d):
    """Get or create a user.

    Arguments:

    d A Dict with keys:

    name A human readable full name, required.
        The unique username will be inferred through lowersnake(name).
    email A valid email, optional.
    phone A phone number, optional.
    role A role description, optional.

    Usage:
    import sys; reload(sys); sys.setdefaultencoding('UTF8')
    from wastd.observations.utils import *; import csv
    with open("data/staff.csv") as df:
        [make_user(u) for u in csv.DictReader(df)]

    """
    usermodel = get_user_model()
    un = lowersnake(d["name"])

    usr, created = usermodel.objects.get_or_create(username=un)
    action = "created" if created else "found"
    msg = "[make_user] {0} {1} ({2})".format(action, d["name"], un)

    usr.name = d["name"]

    usr.phone = d["phone"].replace(" ", "")
    msg += ", phone updated"

    usr.email = d["email"]
    msg += ", email updated"

    usr.role = d["role"]
    msg += ", role updated"

    if created:
        usr.set_password(settings.DEFAULT_USER_PASSWORD)

    usr.save()
    logger.info(msg)
    return usr


def guess_user(un, default_username="FlorianM"):
    """Find exact or fuzzy match of username, or create User.

    Returns the first or only trigram match of username
    or a new user with username `un`.

    Arguments

    un A username
    default_username The default username if un is None

    Returns
    A dict of

    user: An instance of settings.AUTH_USER_MODEL
    message: The debug message
    """
    usermodel = get_user_model()
    username = default_username if not un else lowersnake(un)

    try:
        usr = usermodel.objects.get(username=username)
        msg = "[guess_user][OK] Exact match for {0} is {1}."
    except ObjectDoesNotExist:
        usrs = usermodel.objects.filter(username__trigram_similar=username)
        if usrs.count() == 0:
            usr = usermodel.objects.create(username=un, name=un)
            msg = "[guess_user][CREATED] {0} not found. Created {1}."
        elif usrs.count() == 1:
            usr = usrs[0]
            msg = "[guess_user][OK] Only match for {0} is {1}."
        else:
            usr = usrs[0]
            msg = "[guess_user][NEEDS QA] Best match for {0} is {1}."

    message = msg.format(username, usr)
    logger.info(message)
    return {'user': usr, 'message': message}


def map_values(d):
    """Return a dict of ODK:WAStD dropdown menu choices for a given choice dict.

    Arguments

    d The dict_name, e.g. NEST_TYPE_CHOICES

    Returns

    A dict of ODK (keys) to WAStD (values) choices, e.g. NEST_TYPE_CHOICES
    {u'falsecrawl': 'false-crawl',
     'hatchednest': 'hatched-nest',
     'nest': 'nest',
     'successfulcrawl': 'successful-crawl',
     'tracknotassessed': 'track-not-assessed',
     'trackunsure': 'track-unsure'}
    """
    return {k.replace("-", ""): k for k in dict(d).keys()}


def keep_values(d):
    """Return a dict of WAStD:WAStD dropdown menu choices for a given choice dict.

    This is handy to generate a combined ODK and WAStD lookup.

    Arguments

    d The dict_name, e.g. NEST_TYPE_CHOICES

    Returns

    A dict of WAStD (keys) to WAStD (values) choices, e.g. NEST_TYPE_CHOICES
    {u'false-crawl': 'false-crawl',
     'hatched-nest': 'hatched-nest',
     'nest': 'nest',
     'successful-crawl': 'successful-crawl',
     'track-not-assessed': 'track-not-assessed',
     'track-unsure': 'track-unsure'}
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


def odk_point_as_point(odk_str):
    """Return an ODK Point location as Django Point."""
    point_str = odk_str.split(" ")
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
    logger.debug("  Downloading photo...")
    pdir = make_photo_foldername(photo_id)
    if not os.path.exists(pdir):
        logger.debug("  Creating folder {0}".format(pdir))
        os.mkdir(pdir)
    else:
        logger.debug(("  Found folder {0}".format(pdir)))
    pname = os.path.join(pdir, photo_filename)

    if not os.path.exists(pname):
        logger.debug("  Downloading file {0}...".format(pname))
        response = requests.get(photo_url, stream=True)
        with open(pname, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
    else:
        logger.debug("  Found file {0}".format(pname))


def handle_photo(p, e, title="Track", enc=True):
    """Create a MediaAttachment of photo p to Encounter e with a given title.

    Arguments

    p The filepath of a locally accessible photograph
    e The related encounter (must exist)
    title The attachment's title (default: "Track")
    enc Whether to use Encounter / MediaAttachment (true, default) or
        Expedition / FieldMediaAttachment
    """
    # Does the file exist locally?
    logger.debug(
        "  Creating photo attachment at filepath"
        " {0} for encounter {1} with title {2}...".format(p, e.id, title))

    if os.path.exists(p):
        logger.debug("  File {0} exists".format(p))
        with open(p, 'rb') as photo:
            f = File(photo)
            # Is the file a dud?
            if f.size > 0:
                logger.debug("  File size is {0}".format(f.size))

                if enc:

                    # Does the MediaAttachment exist already?
                    if MediaAttachment.objects.filter(
                            encounter=e, title=title).exists():
                        m = MediaAttachment.objects.filter(
                            encounter=e, title=title)[0]
                        action = "updated"
                    else:
                        m = MediaAttachment(encounter=e, title=title)
                        action = "Created"
                else:
                    # Does the MediaAttachment exist already?
                    if FieldMediaAttachment.objects.filter(
                            expedition=e, title=title).exists():
                        m = FieldMediaAttachment.objects.filter(
                            expedition=e, title=title)[0]
                        action = "updated"
                    else:
                        m = FieldMediaAttachment(expedition=e, title=title)
                        action = "Created"

                # Update the file
                m.attachment.save(p, f, save=True)
                logger.debug("  Photo {0}: {1}".format(action, m))
            else:
                logger.debug("  [ERROR] zero size file {0}".format(p))
    else:
        logger.debug("  [ERROR] missing file {0}".format(p))


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
        logger.debug("  ODK collect photo not taken, skipping {0}".format(title))
        return

    pdir = make_photo_foldername(e.source_id)
    pname = os.path.join(pdir, photo_dict["filename"])
    logger.debug("  Photo dir is {0}".format(pdir))
    logger.debug("  Photo filepath is {0}".format(pname))

    dl_photo(
        e.source_id,
        photo_dict["url"],
        photo_dict["filename"])

    handle_photo(pname, e, title=title, enc=True)


def handle_fieldmedia_attachment(e, photo_dict, title="Photo"):
    """Download unless already done, then create or update a photo.

    Arguments:

    e A Survey with an attribute "source_id" (e.source_id)

    {
        "filename": "1485913363900.jpg",
        "type": "image/jpeg",
        "url": "https://dpaw-data.appspot.com/view/binaryData?blobKey=..."
    }
    """
    if photo_dict is None:
        logger.debug("  ODK collect photo not taken, skipping {0}".format(title))
        return

    pdir = make_photo_foldername(e.source_id)
    pname = os.path.join(pdir, photo_dict["filename"])
    logger.debug("  Photo dir is {0}".format(pdir))
    logger.debug("  Photo filepath is {0}".format(pname))

    dl_photo(
        e.source_id,
        photo_dict["url"],
        photo_dict["filename"])

    handle_photo(pname, e, title=title, enc=False)


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
    logger.debug("  Creating TurtleNestDisturbanceObservation...")
    dd, created = TurtleNestDisturbanceObservation.objects.get_or_create(
        encounter=e,
        disturbance_cause=d["disturbance_cause"],
        disturbance_cause_confidence=m["confidence"][d["disturbance_cause_confidence"]],
        disturbance_severity=d["disturbance_severity"],
        comments=d["comments"]
    )
    dd.save()
    action = "created" if created else "updated"
    logger.debug("  TurtleNestDisturbanceObservation {0}: {1}".format(action, dd))

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

    e The related (TurtleNest)Encounter (must exist)
    """
    logger.debug("  Creating TurtleNestDisturbanceObservation...")
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
    logger.debug("  TurtleNestDisturbanceObservation {0}: {1}".format(action, dd))

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
    logger.debug("  Creating TurtleNestObservation...")
    dd, created = TurtleNestObservation.objects.get_or_create(
        encounter=e,
        nest_position=m["habitat"][d["habitat"]],
        no_egg_shells=d["no_egg_shells"],
        no_live_hatchlings=d["no_live_hatchlings"],
        no_dead_hatchlings=d["no_dead_hatchlings"],
        no_undeveloped_eggs=d["no_undeveloped_eggs"],
        no_unhatched_eggs=d["no_unhatched_eggs"],
        no_unhatched_term=d["no_unhatched_term"],
        no_depredated_eggs=d["no_depredated_eggs"],
        nest_depth_top=d["nest_depth_top"],
        nest_depth_bottom=d["nest_depth_bottom"]
    )
    dd.save()
    action = "created" if created else "updated"
    logger.debug("  TurtleNestObservation {0}: {1}".format(action, dd))

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
    logger.debug("  Creating TurtleNestObservation...")
    dd, created = TurtleNestObservation.objects.get_or_create(
        encounter=e,
        nest_position=d["habitat"],
        no_egg_shells=int_or_none(d["no_egg_shells"]),
        no_live_hatchlings=int_or_none(d["no_live_hatchlings"]),
        no_dead_hatchlings=int_or_none(d["no_dead_hatchlings"]),
        no_undeveloped_eggs=int_or_none(d["no_undeveloped_eggs"]),
        no_unhatched_eggs=int_or_none(d["no_unhatched_eggs"]),
        no_unhatched_term=int_or_none(d["no_unhatched_term"]),
        no_depredated_eggs=int_or_none(d["no_depredated_eggs"]),
        nest_depth_top=int_or_none(d["nest_depth_top"]),
        nest_depth_bottom=int_or_none(d["nest_depth_bottom"])
    )
    dd.save()
    action = "created" if created else "updated"
    logger.debug("  TurtleNestObservation {0}: {1}".format(action, dd))

    if "egg_photos" in d:
        [handle_media_attachment(
            e, ep["photo_eggs"], title="Egg photo {0}".format(idx + 1))
            for idx, ep in enumerate(d["egg_photos"])]


def handle_turtlenesttagobs(d, e, m=None):
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
    if (d["flipper_tag_id"] is None and
            d["date_nest_laid"] is None and
            d["tag_label"] is None):
        return None

    else:
        logger.info("[handle_turtlenesttagobs] looks like we have required fields")
        dd, created = NestTagObservation.objects.get_or_create(
            encounter=e,
            status=m["tag_status"][d["status"]] if m else d["status"],
            flipper_tag_id=d["flipper_tag_id"],
            date_nest_laid=datetime.strptime(d["date_nest_laid"], '%Y-%m-%d') if d["date_nest_laid"] else None,
            tag_label=d["tag_label"])
        logger.debug("[handle_turtlenesttagobs] created new NTO")
        dd.save()
        logger.debug("[handle_turtlenesttagobs] saved NTO")
        action = "created" if created else "updated"
        logger.debug("  NestTagObservation {0}: {1}".format(action, dd))

    logger.debug("[handle_turtlenesttagobs] handle photo")
    handle_media_attachment(e, d["photo_tag"], title="Nest tag photo")
    logger.debug("[handle_turtlenesttagobs] done!")
    return None


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
    logger.debug("  Creating Hatchling Obs...")
    scl = int(d["straight_carapace_length_mm"]) if d["straight_carapace_length_mm"] else None
    scw = int(d["straight_carapace_width_mm"]) if d["straight_carapace_width_mm"] else None
    bwg = int(d["body_weight_g"]) if d["body_weight_g"] else None

    dd, created = HatchlingMorphometricObservation.objects.get_or_create(
        encounter=e,
        straight_carapace_length_mm=scl,
        straight_carapace_width_mm=scw,
        body_weight_g=bwg
    )
    dd.save()
    action = "created" if created else "updated"
    logger.debug("  Hatchling Obs {0}: {1}".format(action, dd))


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
    logger.debug("  Creating LoggerEncounter...")
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
    logger.debug("  LoggerEncounter {0}: {1}".format(action, dd))

    handle_media_attachment(dd, d["photo_logger"], title="Logger ID")

    # If e has NestTagObservation, replicate NTO on LoggerEncounter
    if e.observation_set.instance_of(NestTagObservation).exists():
        logger.debug("  TurtleNestEncounter has nest tag, replicating nest tag observation on LoggerEncounter...")
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
        logger.debug("  NestTag Observation {0} for {1}".format(action, nto))


def handle_turtlenestdisttallyobs(d, e, m=None):
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
    logger.debug("  Found disturbance observation...")

    dd, created = TurtleNestDisturbanceTallyObservation.objects.get_or_create(
        encounter=e,
        disturbance_cause=d["disturbance_cause"],
        no_nests_disturbed=d["no_nests_disturbed"] or 0,
        no_tracks_encountered=d["no_tracks_encountered"] or 0,
        comments=d["disturbance_comments"]
    )
    dd.save()
    action = "created" if created else "updated"
    logger.debug("  Disturbance observation {0}: {1}".format(action, dd))
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
        logger.debug("Updating unchanged existing record {0}...".format(src_id))
        TurtleNestEncounter.objects.filter(source_id=src_id).update(**new_data)
        e = TurtleNestEncounter.objects.get(source_id=src_id)
    else:
        logger.debug("Creating new record {0}...".format(src_id))
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

    logger.debug(" Saved {0}\n".format(e))
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
        logger.debug("Updating unchanged existing record {0}...".format(src_id))
        TurtleNestEncounter.objects.filter(source_id=src_id).update(**new_data)
        e = TurtleNestEncounter.objects.get(source_id=src_id)
    else:
        logger.debug("Creating new record {0}...".format(src_id))
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

    logger.debug(" Saved {0}\n".format(e))
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
        logger.debug("Updating unchanged existing record {0}...".format(src_id))
        Encounter.objects.filter(source_id=src_id).update(**new_data)
        e = Encounter.objects.get(source_id=src_id)
    else:
        logger.debug("Creating new record {0}...".format(src_id))
        e = Encounter.objects.create(**new_data)

    e.save()

    handle_turtlenestdistobs31(r, e)

    logger.debug(" Saved {0}\n".format(e))
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
        logger.debug("Updating unchanged existing record {0}...".format(src_id))
        AnimalEncounter.objects.filter(source_id=src_id).update(**new_data)
        e = AnimalEncounter.objects.get(source_id=src_id)
    else:
        logger.debug("Creating new record {0}...".format(src_id))
        e = AnimalEncounter.objects.create(**new_data)

    e.save()

    if r["checked_for_injuries"]:
        logger.debug("  Damage seen - TODO")
        # "damage_observation": [],

    if r["samples_taken"]:
        logger.debug("  Samples taken - TODO")

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

    logger.debug(" Saved {0}\n".format(e))
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

    Creates a Survey, e.g.
    {
     'started_on': datetime.datetime(2017, 1, 31, 16, 0, tzinfo=<UTC>),
     'finished_on': datetime.datetime(2017, 2, 4, 16, 0, tzinfo=<UTC>),
     'site_id': 17,
     'source': 'direct',
     'source_id': None,
     'transect': None,
     'comments': '',
    }
    """
    src_id = r["instanceID"]

    new_data = dict(
        source="odk",
        source_id=src_id,
        site_id=17,  # TODO: reconstruct site on Survey if not given
        transect=read_odk_linestring(r["transect"]),
        started_on=parse_datetime(r["observation_start_time"]),
        finished_on=parse_datetime(r["observation_end_time"]),
        # m["users"][r["reporter"]],
        comments=r["comments"]
    )

    if Survey.objects.filter(source_id=src_id).exists():
        logger.debug("Updating unchanged existing record {0}...".format(src_id))
        Survey.objects.filter(source_id=src_id).update(**new_data)
        e = Survey.objects.get(source_id=src_id)
    else:
        logger.debug("Creating new record {0}...".format(src_id))
        e = Survey.objects.create(**new_data)

    e.save()

    # MediaAttachments
    handle_media_attachment(e, r["photo_start"], title="Site conditions at start of suvey")
    handle_media_attachment(e, r["photo_finish"], title="Site conditions at end of suvey")

    logger.debug(" Saved {0}\n".format(e))
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
    logger.debug('  Tally (created: {0}) {1}'.format(created, t))


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
        logger.debug("Updating unchanged existing record {0}...".format(src_id))
        LineTransectEncounter.objects.filter(source_id=src_id).update(**new_data)
        e = LineTransectEncounter.objects.get(source_id=src_id)
    else:
        logger.debug("Creating new record {0}...".format(src_id))
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
    logger.debug(" Saved {0}\n".format(e))
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
    {'activity': 'na',
    'behaviour': '',
    'cause_of_death': 'na',
    'cause_of_death_confidence': 'na',
    'checked_for_flipper_tags': 'na',
    'checked_for_injuries': 'na',
    'encounter_ptr_id': 2574,
    'encounter_type': 'stranding',
    'habitat': 'na',
    'health': 'dead-edible',
    'id': 2574,
    'location_accuracy': '1000',
    'maturity': 'adult',
    'name': None,
    'observer_id': 1,
    'polymorphic_ctype_id': 17,
    'reporter_id': 5,
    'scanned_for_pit_tags': 'na',
    'sex': 'na',
    'site_visit_id': None,
    'source': 'direct',
    'source_id': '2017-02-03-10-35-00-112-3242-25-5623-dead-edible-adult-na-dugong-dugon',
    'species': 'dugong-dugon',
    'status': 'new',
    'taxon': 'Sirenia',
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
        logger.debug("Updating unchanged existing record {0}...".format(src_id))
        AnimalEncounter.objects.filter(source_id=src_id).update(**new_data)
        e = AnimalEncounter.objects.get(source_id=src_id)
    else:
        logger.debug("Creating new record {0}...".format(src_id))
        e = AnimalEncounter.objects.create(**new_data)

    e.save()
    logger.debug(" Saved {0}\n".format(e))
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
    'tag_type': 'flipper-tag'
    'encounter_id': 80,
    'handler_id': 1,
    'recorder_id': 1,
    'name': 'WA1234',
    'status': 'resighted',
    'tag_location': 'whole',
    'comments': '',
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
        logger.debug("Updating existing tag obs {0}...".format(tag_name))
        e = TagObservation.objects.filter(
            encounter=enc, name=tag_name).update(**new_data)
        e = TagObservation.objects.get(encounter=enc, name=tag_name)

    else:
        logger.debug("Creating new tag obs {0}...".format(tag_name))
        e = TagObservation.objects.create(**new_data)

    e.save()
    logger.debug(" Saved {0}\n".format(e))
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

    'activity': 'na',
    'behaviour': '',
    'cause_of_death': 'na',
    'cause_of_death_confidence': 'na',
    'checked_for_flipper_tags': 'na',
    'checked_for_injuries': 'na',
    'habitat': 'na',
    'health': 'dead-edible',
    'location_accuracy': '1000',
    'maturity': 'adult',
    'name': None,
    'observer_id': 1,
    'reporter_id': 5,
    'scanned_for_pit_tags': 'na',
    'sex': 'na',
    'source': 'cet',
    'source_id': 'cet-1234',  # src_id
    'species': 'dugong-dugon',
    'taxon': 'Cetacea',
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
        'taxon': 'Cetacea',
        'species': species[fix_species_name(r["Scientific Name"] or '')],
        'activity': 'na',  # TODO
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
        'cause_of_death_confidence': 'na',  # TODO
        'checked_for_flipper_tags': 'na',  # TODO
        'checked_for_injuries': 'na',  # TODO
        'habitat': 'na',  # TODO
        'health': 'dead-edible',  # TODO
        'location_accuracy': '10',
        'maturity': 'adult',  # TODO
        # 'name': r["ID"] or None,
        'observer_id': 1,
        'reporter_id': 1,
        'scanned_for_pit_tags': 'na',  # TODO
        'sex': infer_cetacean_sex(r["F"], r["M"]),
        'source': 'cet',
        'source_id': src_id,
    }
    # check if src_id exists
    if src_id in m["overwrite"]:
        logger.debug("Updating unchanged existing record {0}...".format(src_id))
        AnimalEncounter.objects.filter(source_id=src_id).update(**new_data)
        e = AnimalEncounter.objects.get(source_id=src_id)
    else:
        logger.debug("Creating new record {0}...".format(src_id))
        e = AnimalEncounter.objects.create(**new_data)

    e.save()
    logger.debug(" Saved {0}\n".format(e))
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
    logger.debug("Got coords {0}".format(cstring))
    logger.debug("TODO: parse to point")
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
    logger.debug("User {0}: {1}".format("created" if created else "found", usr))

    # Update name
    if (usr.name is None or usr.name == "") and u["name"] != "NA" and u["name"] != "":
        usr.name = u["name"]
        logger.debug("  User name updated from name: {0}".format(usr.name))

    # Update email
    if (usr.email is None or usr.email == "") and u["EMAIL"] != "NA":
        usr.email = u["EMAIL"]
        logger.debug("  User email updated from EMAIL: {0}".format(usr.role))

    # If role is not set, or doesn't already contain SPECIALTY, add SPECIALTY
    if ((usr.role is None or usr.role == "" or u["SPECIALTY"] not in usr.role) and u["SPECIALTY"] != "NA"):
        usr.role = "{0} Specialty: {1}".format(usr.role or '', u["SPECIALTY"]).strip()
        logger.debug("  User role updated from SPECIALTY: {0}".format(usr.role))

    if ((usr.role is None or usr.role == "" or u["COMMENTS"] not in usr.role) and u["COMMENTS"] != "NA"):
        usr.role = "{0} Comments: {1}".format(usr.role or '', u["COMMENTS"]).strip()
        logger.debug("  User role updated from COMMENTS: {0}".format(usr.role))

    usr.save()
    logger.debug(" Saved User {0}".format(usr))
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
        # import_odk('data/Track_or_Treat_0_34_results.json', flavour="odk-tt034")
        import_odk('data/cetaceans.csv', flavour="cet")
        import_odk('data/wamtram_encounters.csv', flavour="wamtram", usercsv="data/wamtram_users.csv")
        import_odk('data/wamtram_tagobservations.csv', flavour="whambam")
        # import_odk('data/Site_Visit_0_1_results.json', flavour="sitevisit")

        import_odk("data/latest/tt05.json", flavour="odk-tally05")
        import_odk('data/latest/tt031.json', flavour="odk-tt031")
        import_odk('data/latest/tt034.json', flavour="odk-tt034")
        import_odk('data/latest/tt035.json', flavour="odk-tt036")
        import_odk('data/latest/tt036.json', flavour="odk-tt036")
        import_odk('data/latest/fs03.json', flavour="odk-fs03")
        import_odk('data/latest/mwi01.json', flavour="odk-mwi01")
    """
    if flavour == "odk-tt034":
        logger.info("Using flavour ODK Track or Treat 0.34...")
        with open(datafile) as df:
            d = json.load(df)
            logger.info("Loaded {0} records from {1}".format(len(d), datafile))
        mapping["users"] = {u: guess_user(u)["user"] for u in set([r["reporter"] for r in d])}
        mapping["keep"] = [t.source_id for t in Encounter.objects.exclude(
            status=Encounter.STATUS_NEW).filter(source="odk")]

        [import_one_record_tt034(r, mapping) for r in d
         if r["instanceID"] not in mapping["keep"]]     # retain local edits
        logger.info("Done!")

    elif flavour == "odk-tt036":
        logger.info("Using flavour ODK Track or Treat 0.35-0.36...")
        with open(datafile) as df:
            d = json.load(df)
            logger.info("Loaded {0} records from {1}".format(len(d), datafile))
        mapping["users"] = {u: guess_user(u)["user"] for u in set([r["reporter"] for r in d])}
        mapping["keep"] = [t.source_id for t in Encounter.objects.exclude(
            status=Encounter.STATUS_NEW).filter(source="odk")]

        [import_one_record_tt036(r, mapping) for r in d
         if r["instanceID"] not in mapping["keep"]]     # retain local edits
        logger.info("Done!")

    elif flavour == "odk-fs03":
        logger.info("Using flavour ODK Fox Sake 0.3...")
        with open(datafile) as df:
            d = json.load(df)
            logger.info("Loaded {0} records from {1}".format(len(d), datafile))
        mapping["users"] = {u: guess_user(u)["user"] for u in set([r["reporter"] for r in d])}
        mapping["keep"] = [t.source_id for t in Encounter.objects.exclude(
            status=Encounter.STATUS_NEW).filter(source="odk")]

        [import_one_record_fs03(r, mapping) for r in d
         if r["instanceID"] not in mapping["keep"]]     # retain local edits
        logger.info("Done!")

    elif flavour == "odk-mwi01":
        logger.info("Using flavour ODK Marine Wildlife Incident 0.1...")
        with open(datafile) as df:
            d = json.load(df)
            logger.info("Loaded {0} records from {1}".format(len(d), datafile))
        mapping["users"] = {u: guess_user(u)["user"] for u in set([r["reporter"] for r in d])}
        mapping["keep"] = [t.source_id for t in Encounter.objects.exclude(
            status=Encounter.STATUS_NEW).filter(source="odk")]

        [import_one_record_mwi01(r, mapping) for r in d
         if r["instanceID"] not in mapping["keep"]]     # retain local edits
        logger.info("Done!")

    elif flavour == "odk-tally05":
        logger.info("Using flavour ODK Track Tally 0.5...")
        with open(datafile) as df:
            d = json.load(df)
            logger.info("Loaded {0} records from {1}".format(len(d), datafile))
        mapping["users"] = {u: guess_user(u)["user"] for u in set([r["reporter"] for r in d])}
        mapping["keep"] = [t.source_id for t in Encounter.objects.exclude(
            status=Encounter.STATUS_NEW).filter(source="odk")]

        [import_one_record_tt05(r, mapping) for r in d
         if r["instanceID"] not in mapping["keep"]]     # retain local edits
        logger.info("Done!")

    elif flavour == "cet":
        logger.info("Using flavour Cetacean strandings...")
        # ODK_MAPPING["users"] = {u: guess_user(u)["user"] for u in set([r["reporter"] for r in d])}
        mapping["keep"] = [t.source_id for t in Encounter.objects.exclude(
            status=Encounter.STATUS_NEW).filter(source="cet")]
        mapping["overwrite"] = [t.source_id for t in Encounter.objects.filter(
            source="cet", status=Encounter.STATUS_NEW)]

        enc = csv.DictReader(open(datafile))

        [import_one_record_cet(e, mapping) for e in enc
         if e["Record No."] not in mapping["keep"]]

    elif flavour == "pin":
        logger.info("Using flavour Pinniped strandings...")
        # mapping["users"] = {u: guess_user(u)["user"] for u in set([r["reporter"] for r in d])}
        mapping["keep"] = [t.source_id for t in Encounter.objects.exclude(
            status=Encounter.STATUS_NEW).filter(source="pin")]
        enc = csv.DictReader(open(datafile))
        logger.info("not impemented yet")

    elif flavour == "wamtram":
        logger.info("ALL ABOARD THE WAMTRAM!!!")
        enc = csv.DictReader(open(datafile))
        wamtram_users = csv.DictReader(open(usercsv))

        # List of [WAStD User object (.id), WAMTRAM user dict (["PERSON_ID"])]
        users = {user["PERSON_ID"]: update_wastd_user(user)
                 for user in wamtram_users if user["name"] != ""}

        # mapping["users"] = {u: guess_user(u)["user"] for u in set([r["reporter"] for r in d])}
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
        logger.info("thank you ma'am")
        tags = csv.DictReader(open(datafile))

        logger.info("  Caching tagging encounters...")
        enc = [x["source_id"] for x in
               AnimalEncounter.objects.filter(source="wamtram").values("source_id")]

        [import_one_tag(x, mapping) for x in tags
         if make_wamtram_source_id(x["observation_id"]) in enc]

    elif flavour == "sitevisit":
        logger.info("Loading Site Visits...")
        with open(datafile) as df:
            d = json.load(df)
            logger.info("Loaded {0} records from {1}".format(len(d), datafile))
        mapping["users"] = {u: guess_user(u)["user"] for u in set(
            [r["reporter"] for r in d])}

        [import_one_record_sv01(r, mapping) for r in d]     # retain local edits
        logger.info("Done!")

    else:
        logger.info("Format {0} not recognized. Exiting.".format(flavour))


# ---------------------------------------------------------------------------#
# ODK Aggregate API helpers
#
def odka_forms(url=env('ODKA_URL'),
               un=env('ODKA_UN'),
               pw=env('ODKA_PW')):
    """Return an OpenRosa xformsList XML response as list of dicts.

    See http://docs.opendatakit.org/openrosa-form-list/

    Arguments

    url The OpenRosa xformsList API endpoint of an ODK Aggregate instance,
        default: the value of environment variable "ODKA_URL".
    un A username that exists on the ODK-A instance.
        Default: the value of environment variable "ODKA_UN".
    pw The username's password.
        Default: the value of environment variable "ODKA_PW".

    Returns
    A list of dicts, each dict contains one xform:

    forms = odka_forms()
    logger.debug(json.dumps(forms, indent=4))


    The whole response parses to:
    res = {
    "xforms": {
        "@xmlns": "http://openrosa.org/xforms/xformsList",
        "xform": [
            {
                "formID": "build_Track-Tally-0-5_1502342159",
                "name": "Track Tally 0.5",
                "majorMinorVersion": null,
                "version": null,
                "hash": "md5:2607df5d22571e1e55e1b90e90157473",
                "downloadUrl": "https://dpaw-data.appspot.com/formXml?formId=build_Track-Tally-0-5_1502342159"
            },
            {... other form defs ...}
            ]
        }
    }

    This function returns res["xforms"]["xform"] and returns a list of dicts.
        [
            {
                "formID": "build_Track-Tally-0-5_1502342159",
                "name": "Track Tally 0.5",
                "majorMinorVersion": null,
                "version": null,
                "hash": "md5:2607df5d22571e1e55e1b90e90157473",
                "downloadUrl": "https://dpaw-data.appspot.com/formXml?formId=build_Track-Tally-0-5_1502342159"
            },
            {... other form defs ...}
        ]

    some_form_id = forms[0]["formID"]
    """
    api = "{0}/xformsList".format(url)
    au = HTTPDigestAuth(un, pw)
    logger.info("[odka_forms] Retrieving xformsList from {0}...".format(url))
    res = requests.get(api, auth=au)
    xforms = xmltodict.parse(res.content, xml_attribs=True)
    forms = xforms["xforms"]["xform"]
    logger.info("[odka_forms] Done, retrieved {0} forms.".format(len(forms)))
    return forms


def odka_submission_ids(form_id,
                        limit=10000,
                        url=env('ODKA_URL'),
                        un=env('ODKA_UN'),
                        pw=env('ODKA_PW'),
                        verbose=False):
    """Return a list of submission IDs for a given ODKA formID.

    See http://docs.opendatakit.org/aggregate-use/#briefcase-aggregate-api

    TODO: should lower numEntries and load in idChunks

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

    logger.info("[odka_submission_ids] Retrieving submission IDs for formID '{0}'...".format(form_id))
    logger.debug("[odka_submission_ids] Retrieving submission IDs from '{0}'...".format(api))

    res = requests.get(api, auth=au, params=pars)
    parsed = xmltodict.parse(res.content, xml_attribs=True)

    if not parsed["idChunk"]["idList"]:
        # No submissions.
        ids = []
    elif type(parsed["idChunk"]["idList"]["id"]) == unicode:
        # One submission.
        ids = [parsed["idChunk"]["idList"]["id"], ]
    else:
        # More than one submission.
        ids = parsed["idChunk"]["idList"]["id"]

    # resumption_cursor = parsed["idChunk"]["resumptionCursor"]

    logger.info("[odka_submission_ids] Done, retrieved {0} submission IDs.".format(len(ids)))
    return ids


def odka_submission(form_id,
                    submission_id,
                    url=env('ODKA_URL'),
                    un=env('ODKA_UN'),
                    pw=env('ODKA_PW'),
                    verbose=False):
    """Download one ODKA submission and return as dict.

    See http://docs.opendatakit.org/aggregate-use/#briefcase-aggregate-api

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
    verbose Whether to logger.debug verbose log messages, default: False.

    Returns
        A dict with key "submission" containing "data" and "mediaFile".

    Example
    d = odka_submission('build_Site-Visit-Start-0-1_1490753483',
        'uuid:a9772680-b6f9-45c0-8ed4-189f5e722a6c')
    logger.debug(json.dumps(d, indent=4))
    {
        "submission": {
            "@xmlns": "http://opendatakit.org/submissions",
            "@xmlns:orx": "http://openrosa.org/xforms",
            "data": {
                "data": {
                    "@id": "build_Site-Visit-Start-0-1_1490753483",
                    "@instanceID": "uuid:a9772680-b6f9-45c0-8ed4-189f5e722a6c",
                    "@submissionDate": "2017-11-05T23:37:49.829Z",
                    "@isComplete": "true",
                    "@markedAsCompleteDate": "2017-11-05T23:40:51.534Z",
                    "orx:meta": {
                        "orx:instanceID": "uuid:a9772680-b6f9-45c0-8ed4-189f5e722a6c"
                    },
                    "reporter": "ali_goss",
                    "survey_start_time": "2017-11-05T22:02:51.121Z",
                    "site_visit": {
                        "location": "-20.3136817000 118.6444200000 -2.1000000000 4.8000000000",
                        "site_conditions": "1509919398254.jpg",
                        "comments": null
                    }
                }
            },
            "mediaFile": {
                "filename": "1509919398254.jpg",
                "hash": "md5:4c112a49ab99aa6a5166741ff9ba2ea2",
                "downloadUrl": "https://dpaw-data.appspot.com/view/binaryData?blobKey=..."
            }
        }
    }

    d["submission"]["data"]["data"]["@id"]
    'build_Site-Visit-Start-0-1_1490753483'
    """
    api = ("{0}/view/downloadSubmission?formId={1}"
           "[@version=null%20and%20@uiVersion=null]/data[@key={2}]").format(
        url, form_id, submission_id)
    au = HTTPDigestAuth(un, pw)
    logger.info("[odka_submission] Retrieving {0}".format(submission_id))
    if verbose:
        logger.info("[odka_submission] URL {0}".format(api))
    res = requests.get(api, auth=au)
    return xmltodict.parse(res.content, xml_attribs=True)


def downloaded_data_filename(form_id, path):
    """Generate a filename for a form_id in format path/form_id.json."""
    return os.path.join(path, form_id) + ".json"


def downloaded_data_exists(form_id, path):
    """Whether data already was downloaded at path/form_id.json."""
    return os.path.exists(downloaded_data_filename(form_id, path))


def downloaded_data(form_id, path):
    """Return downloaded data for form_id stored at path as parsed JSON or an empty list."""
    if downloaded_data_exists(form_id, path):
        logger.info("[downloaded_data] Parsing {0}".format(downloaded_data_filename(form_id, path)))
        with io.open(downloaded_data_filename(form_id, path), mode="r", encoding="utf-8") as df:
            data = json.load(df)
    else:
        data = []
    return data


def odka_submissions(form_id,
                     path=".",
                     url=env('ODKA_URL'),
                     un=env('ODKA_UN'),
                     pw=env('ODKA_PW'),
                     verbose=False,
                     append=True
                     ):
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
    verbose Whether to logger.debug verbose log messages, default: False.
    append Whether to retain already downloaded data and append new data, or
        to overwrite all already downloaded data and download all data again.

    Example
    forms = odka_forms()
    data = odka_submissions(forms[6]["formID"])
    """
    logger.info("[odka_submissions] Retrieving submissions for formID {0}...".format(form_id))

    old_data = downloaded_data(form_id, path)
    logger.info("[odka_submissions] Found {0} already downloaded submissions.".format(len(old_data)))
    if append:
        old_ids = [make_data(x)["@instanceID"] for x in old_data]
        action = "retained"
    else:
        old_ids = []
        action = "overwrote"

    new_data = [odka_submission(form_id, x, url=url, un=un, pw=pw, verbose=verbose)
                for x in odka_submission_ids(form_id, url=url, un=un, pw=pw, verbose=verbose)
                if x not in old_ids]
    logger.info("[odka_submissions] Done, retrieved {0} new submissions, "
                "{1} {2} already downloaded submissions.".format(
                    len(new_data), action, len(old_data)))
    return old_data + new_data


def save_odka(form_id,
              path=".",
              url=env('ODKA_URL'),
              un=env('ODKA_UN'),
              pw=env('ODKA_PW'),
              verbose=False,
              append=True):
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
    verbose Whether to logger.debug verbose log messages, default: False.
    append Whether to retain already downloaded data and append new data, or
        to overwrite all already downloaded data and download all data again.
    """
    data = odka_submissions(
        form_id,
        path=path,
        url=url,
        un=un,
        pw=pw,
        verbose=verbose,
        append=append)
    with io.open(downloaded_data_filename(form_id, path), mode="w", encoding="utf-8") as outfile:
        data = json.dumps(data, indent=2, ensure_ascii=False, encoding="utf-8")
        outfile.write(unicode(data))


def save_all_odka(path=".",
                  url=env('ODKA_URL'),
                  un=env('ODKA_UN'),
                  pw=env('ODKA_PW'),
                  verbose=False,
                  append=True):
    """Save all submissions for all forms of an odka instance.

    Arguments:

    path A locally existing path, default: "."
    url The OpenRosa xformsList API endpoint of an ODK Aggregate instance,
        default: the value of environment variable "ODKA_URL".
    un A username that exists on the ODK-A instance.
        Default: the value of environment variable "ODKA_UN".
    pw The username's password.
        Default: the value of environment variable "ODKA_PW".
    verbose Whether to logger.debug verbose log messages, default: False.
    append Whether to retain already downloaded data and append new data, or
        to overwrite all already downloaded data and download all data again.

    Returns:
    At the specified location (path) for each form, a file will be written
    which contains all submissions (records) for that respective form.
    """
    [save_odka(
        xform['formID'],
        path=path,
        url=url,
        un=un,
        pw=pw,
        verbose=verbose,
        append=append)
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
    verbose Whether to logger.debug verbose log messages, default: False.
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
def make_data(odka_dict):
    """Return a dict of filename:downloadUrl of an ODK-A submission dict.

    Arguments:
    odka_dict An ODK-A submission parsed with xmltojson.

    Returns:
        The sub-node odka_dict["submission"]["data"]["data"]
    """
    return odka_dict["submission"]["data"]["data"]


def make_media(odka_dict):
    """Return a dict of filename:downloadUrl of an ODK-A submission dict.

    Arguments:
    odka_dict An ODK-A submission parsed with xmltojson.

    Returns:
        A dict with zero to many filename:downloadUrl key-value pairs.
    """
    if "mediaFile" in odka_dict["submission"]:
        mf = odka_dict["submission"]["mediaFile"]
        if "filename" in mf:
            logger.debug("[make_media] found single mediaFile")
            d = dict()
            d[mf["filename"]] = mf["downloadUrl"]
            return d
        elif len(mf) > 0 and "filename" in mf[0]:
            logger.debug("[make_media] found multiple mediaFiles")
            return {x["filename"]: x["downloadUrl"] for x in mf}
        else:
            logger.debug("[make_media] WARNING unknown data: {0}".format(
                json.dumps(mf, indent=2)))
            return dict()
    else:
        logger.debug("[make_media] no mediaFile found")
        return dict()


def make_photo_dict(filename, media):
    """Generate a photo dict (filename, url) as in the ODKA JSON export."""
    if filename and filename in media:
        return dict(filename=filename, url=media[filename])
    else:
        return None


def listify(x):
    """Wrap x in a list and return x if it already is a list or None.

    This re-instates the incorrectly flattened lists with one element from xmltojson,
    where repeating groups with only one element are flattened to a dict of the group.

    Returns:

    None > None
    {} > [{}, ]
    [] > []
    """
    if x:
        if type(x) == list:
            return x
        else:
            return [x, ]
    else:
        return None


# ---------------------------------------------------------------------------#
# Update logic for WAStD's custom QA django-fsm status
#
def create_update_skip(
        unique_data,
        extra_data=dict(),
        cls=Encounter,
        base_cls=Encounter,
        retain_qa=True):
    """Create, update or skip Encounter.

    From minimal required data, create (if not existing),
    update (if unchanged) or skip (if changed) an Encounter.


    Arguments:
    source An existing WAStD data source, e.g. "odk"
    source_id The unique source ID for a record, e.g. the instanceID of an ODK submission.
    unique_data A dict of arguments to base_cls.objects.filter(**unique_data), as
        defined in base_cls.meta.unique_together or as unique=true on fields.
    extra_data A dict of required fields to create a minimum new cls instance.
        Default: dict()
    cls The class to instantiate. Default: Encounter.
    base_cls The base class to filter for unique_data.
        This is required for polymorphic classes.
        Default: Encounter.
    retain_qa Whether to retain qa'd instances (proofread or higher Encounters).
        Default: True. Set to false for models without QA status.

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
    enc = base_cls.objects.filter(**unique_data)
    if enc.exists():
        if (not retain_qa) or (enc.first().status == Encounter.STATUS_NEW):
            action = "update"
            instantiated = cls.objects.filter(pk=enc.first().pk)
            instantiated.update(**extra_data)
            e = enc.first()
            msg = "[create_update_skip] Updating unchanged existing record {0}...".format(e.__str__())
            e.save()
        else:
            action = "skip"
            e = enc.first()
            msg = "[create_update_skip] Skipping existing curated record {0}...".format(e.__str__())
    else:
        action = "create"
        data = unique_data
        data.update(extra_data)
        e = cls.objects.create(**data)
        e.save()
        msg = "[create_update_skip] Created new record {0}".format(e.__str__())

    logger.debug(msg)
    logger.debug("[create_update_skip] Done, returning record.")
    return (e, action)


def int_or_none(value):
    """Return int(value) or None."""
    try:
        return int(value)
    except:
        return None


# ---------------------------------------------------------------------------#
# WAStD data import helpers
#
def handle_media_attachment_odka(enc, media, photo_filename, title="Photo"):
    """Handle MediaAttachment for ODKA data."""
    if not photo_filename:
        logger.debug("  [handle_media_attachment_odka] skipping empty photo {0}".format(title))
    else:
        handle_media_attachment(
            enc, dict(filename=photo_filename, url=media[photo_filename]), title=title)
    return None


def handle_fieldmedia_attachment_odka(exp, media, photo_filename, title="Photo"):
    """Handle MediaAttachment for ODKA data."""
    if not photo_filename:
        logger.debug("  [handle_fieldmedia_attachment_odka] skipping empty photo {0}".format(title))
    else:
        handle_fieldmedia_attachment(
            exp, dict(filename=photo_filename, url=media[photo_filename]), title=title)
    return None


def handle_odka_disturbanceobservation(enc, media, data):
    """Handle empty, one, or multiple TurtleNestDistObs.

    Arguments:

    enc A TurtleNestEncounter
    media A dict of photo filename:url
    data A "disturbance_observation" dict from ODK "Fox Sake 0.3" or "Track or Treat 0.36"

    Returns
    None
    """
    if "disturbanceobservation" in data:
        distobs = listify(data["disturbanceobservation"])
    elif "disturbance" in data:
        distobs = listify(data["disturbance"])
    else:
        logger.debug("  [handle_odka_disturbanceobservation] found no TurtleNestDisturbanceObservation")
        return None

    if distobs:
        logger.debug(
            "  [handle_odka_disturbanceobservation] found "
            "{0} TurtleNestDisturbanceObservation(s)".format(len(distobs)))
        [handle_turtlenestdistobs31(
            dict(
                disturbance_cause=x["disturbance_cause"],
                disturbance_cause_confidence=x["disturbance_cause_confidence"],
                disturbance_severity="na"
                if "disturbance_severity" not in x else x["disturbance_severity"],
                photo_disturbance=make_photo_dict(x["photo_disturbance"], media),
                comments=x["comments"]
            ),
            enc) for x in distobs]
    else:
        logger.debug("  [handle_odka_disturbanceobservation] found invalid data: {0}".format(
            json.dumps(distobs, indent=2)))
    return None


def handle_odka_nesttagobservation(enc, media, data):
    """Handle empty, one, or multiple NestTagObservations.

    Arguments:

        enc A TurtleNestEncounter
        media A dict of photo filename:url
        data A "data" dict from ODK "Track or Treat 0.36" or higher.

    Returns:

        None

    "nest_tag": {
        "status": "resighted",
        "flipper_tag_id": "WA1234",
        "date_nest_laid": "2017-11-10",
        "tag_label": "Test3",
        "tag_comments": "Jup",
        "photo_tag": "1510298358979.jpg"
    }
    """
    if "nest_tag" not in data:
        logger.debug("[handle_odka_nesttagobservation] found no TurtleNestTagObservation")
        return None

    obs = listify(data["nest_tag"])

    if obs:
        logger.debug("[handle_odka_nesttagobservation] found {0} TurtleNestTagObservation(s)".format(len(obs)))
        [handle_turtlenesttagobs(
            dict(
                encounter=enc,
                status=x["status"],
                flipper_tag_id=x["flipper_tag_id"],
                date_nest_laid=None if not x["date_nest_laid"] else x["date_nest_laid"],
                tag_label=x["tag_label"],
                photo_tag=make_photo_dict(x["photo_tag"], media)
            ),
            enc) for x in obs]
    else:
        logger.debug("[handle_odka_nesttagobservation] found invalid data:\n{0}".format(
            json.dumps(obs, indent=2)))

    return None


def handle_odka_tagsobs(enc, media, data):
    """Handle empty, one, or multiple TagObservations.

    Arguments:

        enc An AnimalEncounter
        media A dict of photo filename:url
        data A "data" dict from ODK "Marine Wildlife Incident 0.1" or higher, can contain

        No tagobs: key "tag_observation" missing from data.

        One tagobs:
        "tag_observation": {
            "photo_tag": "1511046895915.jpg",
            "name": "Wb6653",
            "tag_status": "resighted",
            "tag_comments": null,
            "tag_location": "flipper-front-left-1",
            "tag_type": "flipper-tag"
          }

        Multiple tagobs:
        "tag_observation": [
            {
              "photo_tag": "1511005364137.jpg",
              "name": "900119000520181",
              "tag_status": "resighted",
              "tag_comments": "applied-new",
              "tag_location": "neck",
              "tag_type": "pit-tag"
            },
            {
              "photo_tag": "1511005464946.jpg",
              "name": "wb14638",
              "tag_status": "resighted",
              "tag_comments": "applied-new",
              "tag_location": "flipper-front-right-1",
              "tag_type": "flipper-tag"
            },
            {
              "photo_tag": "1511005522216.jpg",
              "name": "f8904",
              "tag_status": "removed",
              "tag_comments": null,
              "tag_location": "flipper-rear-left",
              "tag_type": "biopsy-sample"
            }
          ]

    Returns:

        None
    """
    if "tag_observation" in data and data["tag_observation"]:

        tag_type_dict = map_and_keep(TAG_TYPE_CHOICES)
        tag_location_dict = map_and_keep(TURTLE_BODY_PART_CHOICES)
        tag_status_dict = map_and_keep(TAG_STATUS_CHOICES)

        for obs in listify(data["tag_observation"]):
            # 0. Lookups
            tag_name = sanitize_tag_name(obs["name"])
            tag_type = tag_type_dict[obs["tag_type"]]

            # 1. TagObservation
            new_data = dict(
                encounter_id=enc.id,
                tag_type=tag_type,
                handler_id=enc.observer_id,
                recorder_id=enc.reporter_id,
                name=tag_name,
                tag_location=tag_location_dict[obs["tag_location"]],
                status=tag_status_dict[obs["tag_status"]],
                comments=obs["tag_comments"]
            )

            criteria = dict(encounter=enc, tag_type=tag_type, name=tag_name)
            target = TagObservation.objects.filter(**criteria)
            if target.exists():
                logger.debug("  [handle_odka_tagsobs] Updating existing tag obs {0}...".format(tag_name))
                e = target.update(**new_data)
                e = TagObservation.objects.get(**criteria)

            else:
                logger.debug("  [handle_odka_tagsobs] Creating new tag obs {0}...".format(tag_name))
                e = TagObservation.objects.create(**new_data)

            # 2. Photo of tag
            if obs["photo_tag"]:
                handle_media_attachment_odka(
                    enc, media, obs["photo_tag"], title="Photo {0}".format(e.__str__()))

    else:
        logger.debug("  [handle_odka_tagsobs] found no TagObservation")

    return None


def handle_odka_turtlenestobservation(enc, media, data):
    """Handle empty, one, or multiple TurtleNestObservations.

    Arguments:

        enc A TurtleNestEncounter
        media A dict of photo filename:url
        data A "data" dict from ODK "Track or Treat 0.36" or higher, containing

        "nest": {
            "habitat": "in-dune-vegetation",
            "disturbance": "present",
            "nest_tagged": "yes",
            "logger_found": "yes",
            "eggs_counted": "yes",
            "hatchlings_measured": "yes",
            "fan_angles_measured": "yes"
        },
        "egg_count": {
            "no_egg_shells": "60",
            "no_live_hatchlings": "5",
            "no_dead_hatchlings": "14",
            "no_undeveloped_eggs": "15",
            "no_unhatched_eggs": "5",
            "no_unhatched_term": "6",
            "no_depredated_eggs": "2",
            "nest_depth_top": "25",
            "nest_depth_bottom": "89"
        },
        "egg_photos": {
            "photo_eggs": "1510298324400.jpg"
        },

    Returns:

        None
    """
    if "egg_count" not in data:
        logger.debug("  [handle_odka_turtlenestobservation] found no TurtleNestObservation")
        return None

    if data["nest"]["eggs_counted"] == "yes":
        nest_dict = data["egg_count"]
        nest_dict["habitat"] = data["nest"]["habitat"]
        handle_turtlenestobs31(nest_dict, enc)

        # Photos of excavated eggs
        if "egg_photos" in data and data["egg_photos"]:
            [handle_media_attachment_odka(
                enc, media, ep["photo_eggs"], title="Egg photo {0}".format(idx + 1))
                for idx, ep in enumerate(listify(data["egg_photos"]))]
    return None


def handle_odka_managementaction(enc, media, data):
    """Handle empty, one, or multiple ManagementAction.

    Arguments:

        enc An AnimalEncounter
        media A dict of photo filename:url
        data A "data" dict from ODK "Marine Wildlife Incident 0.1" or higher, can contain

        data["animal_fate"]["animal_fate_comment"]

    Returns:

        None
    """
    if "animal_fate" not in data:
        msg = "  [handle_odka_managementaction] found no ManagementAction"
    else:
        new_data = dict(
            encounter_id=enc.id,
            management_actions=data["animal_fate"]["animal_fate_comment"]
        )

        criteria = dict(encounter=enc, management_actions=data["animal_fate"]["animal_fate_comment"])
        target = ManagementAction.objects.filter(**criteria)
        if target.exists():
            e = target.update(**new_data)
            e = ManagementAction.objects.get(**criteria)
            msg = "  [handle_odka_managementaction] Updated existing {0}".format(e)

        else:
            e = ManagementAction.objects.create(**new_data)
            msg = "  [handle_odka_managementaction] Created new {0}".format(e)

    logger.debug(msg)
    return None


def handle_odka_hatchlingmorphometricobservation(enc, media, data):
    """Handle empty, one, or multiple TurtleNestObservations.

    Arguments:

        enc A TurtleNestEncounter
        media A dict of photo filename:url
        data A "data" dict from ODK "Track or Treat 0.36" or higher, containing

        "nest": {
            "habitat": "in-dune-vegetation",
            "disturbance": "present",
            "nest_tagged": "yes",
            "logger_found": "yes",
            "eggs_counted": "yes",
            "hatchlings_measured": "yes",
            "fan_angles_measured": "yes"
        },
        "hatchling_measurements": [
            {
                "straight_carapace_length_mm": "125",
                "straight_carapace_width_mm": "56",
                "body_weight_g": "12"
            },
            {
                "straight_carapace_length_mm": "145",
                "straight_carapace_width_mm": "16",
                "body_weight_g": "15"
            }
        ],

    Returns:

        None
    """
    if data["nest"]["hatchlings_measured"] == "yes" and "hatchling_measurements" in data:
        [handle_hatchlingmorphometricobs(x, enc)
         for x in listify(data["hatchling_measurements"])]
    return None


def handle_odka_turtlemorph(enc, media, data):
    """Handle empty or one TurtleMorphometricObservation.

    ODK forms collect up to one TurtleMorphometricObservation.
    Records imported from ODK are assumed to be new.
    Therefore, there can be up to one TurtleMorphometricObservation per AnimalEncounter via ODK.

    Arguments:

        enc An AnimalEncounter
        media A dict of photo filename:url
        data A "data" dict from ODK "Marine Wildlife Incident 0.1" or higher, can contain

        "morphometrics": {
            "maximum_head_width_mm": "167",
            "curved_carapace_width_accuracy": "5",
            "curved_carapace_width_mm": "630",
            "curved_carapace_length_mm": "950",
            "curved_carapace_length_accuracy": "5",
            "tail_length_carapace_mm": "125",
            "maximum_head_width_accuracy": "1",
            "tail_length_carapace_accuracy": "1"
        },

    Returns:

        None
    """
    if "morphometrics" not in data:
        msg = "  [handle_odka_turtlemorph] found no TurtleMorphometricObservation"
    else:
        obs = data["morphometrics"]
        new_data = dict(
            encounter_id=enc.id,
            curved_carapace_length_mm=int_or_none(obs.get("curved_carapace_length_mm", None)),
            curved_carapace_length_accuracy=obs.get("curved_carapace_length_accuracy", None),
            curved_carapace_width_mm=int_or_none(obs.get("curved_carapace_width_mm", None)),
            curved_carapace_width_accuracy=obs.get("curved_carapace_width_accuracy", None),
            tail_length_carapace_mm=int_or_none(obs.get("tail_length_carapace_mm", None)),
            tail_length_carapace_accuracy=obs.get("tail_length_carapace_accuracy", None),
            maximum_head_width_mm=int_or_none(obs.get("maximum_head_width_mm", None)),
            maximum_head_width_accuracy=obs.get("maximum_head_width_accuracy", None),
            handler_id=enc.observer_id,
            recorder_id=enc.reporter_id,
        )

        criteria = dict(encounter=enc)
        target = TurtleMorphometricObservation.objects.filter(**criteria)
        if target.exists():
            e = target.update(**new_data)
            e = TurtleMorphometricObservation.objects.get(**criteria)
            msg = "  [handle_odka_turtlemorph] Updated existing {0}".format(e)

        else:
            e = TurtleMorphometricObservation.objects.create(**new_data)
            msg = "  [handle_odka_turtlemorph] Created new {0}".format(e)

    logger.debug(msg)
    return None


def handle_odka_turtledamageobs(enc, media, data):
    """Handle empty, one, or multiple TurtleDamageObservation.

    Arguments:

        enc An AnimalEncounter
        media A dict of photo filename:url
        data A "data" dict from ODK "Marine Wildlife Incident 0.1" or higher, can contain

        No tagobs: key "damage_observation" missing from data.

        One damageobs:
        "damage_observation":
          {
            "photo_damage": "1510473605661.jpg",
            "body_part": "neck",
            "description": "damage comments",
            "damage_type": "amputatedentirely",
            "damage_age": "healed-partially"
          },

        Multiple damageobs:

        "damage_observation": [
          {
            "photo_damage": "1510473605661.jpg",
            "body_part": "neck",
            "description": "damage comments",
            "damage_type": "amputatedentirely",
            "damage_age": "healed-partially"
          },
          {
            "photo_damage": "1510473630318.jpg",
            "body_part": "eyes",
            "description": "another comment",
            "damage_type": "algal-growth",
            "damage_age": "healed-entirely"
          }
        ],

    Returns:

        None
    """
    if "damage_observation" in data and data["damage_observation"]:

        body_part_dict = map_and_keep(TURTLE_BODY_PART_CHOICES)
        damage_type_dict = map_and_keep(DAMAGE_TYPE_CHOICES)
        damage_age_dict = map_and_keep(DAMAGE_AGE_CHOICES)

        for obs in listify(data["damage_observation"]):

            # 1. DamageObservation
            new_data = dict(
                encounter_id=enc.id,
                body_part=body_part_dict[obs["body_part"]],
                damage_type=damage_type_dict[obs["damage_type"]],
                damage_age=damage_age_dict[obs["damage_age"]],
                description=obs["description"]
            )

            criteria = new_data
            target = TurtleDamageObservation.objects.filter(**criteria)
            if target.exists():
                e = target.update(**new_data)
                e = TurtleDamageObservation.objects.get(**criteria)
                logger.debug("  [handle_odka_turtledamageobs] Updated existing {0}...".format(e.__str__()))

            else:
                e = TurtleDamageObservation.objects.create(**new_data)
                logger.debug("  [handle_odka_turtledamageobs] Created new {0}...".format(e.__str__()))

            # 2. Photo
            if obs["photo_damage"]:
                handle_media_attachment_odka(
                    enc, media, obs["photo_damage"], title="Photo {0}".format(e.__str__()))

    else:
        logger.debug("  [handle_odka_turtledamageobs] found no TurtleDamageObservation")

    return None


# ---------------------------------------------------------------------------#
# Site Visit Start 0.1-0.2
#
def import_odka_svs02(r):
    """Import one ODK Site Visit Start 0.1 or 0.2 record from the OKA-A API into WAStD.

    The start point becomes a Survey, the end point can be matched to the
    corresponding Survey (containing start point) later.

    Arguments

    r The submission record as dict, e.g.

    save_all_odka(path="data/odka")
    with open("data/odka/build_Site-Visit-Start-0-1_1490753483.json") as df:
        d = json.load(df)
    r = d[1]

    r

    {
    "submission": {
      "@xmlns": "http://opendatakit.org/submissions",
      "@xmlns:orx": "http://openrosa.org/xforms",
      "data": {
        "data": {
          "reporter": null,
          "@instanceID": "uuid:d8decc72-a789-411a-b071-aabc871965a5",
          "orx:meta": {
            "orx:instanceID": "uuid:d8decc72-a789-411a-b071-aabc871965a5"
          },
          "@submissionDate": "2017-08-23T03:46:26.706Z",
          "survey_start_time": "2017-08-15T03:40:57.512Z",
          "@isComplete": "true",
          "@markedAsCompleteDate": "2017-08-23T03:46:26.706Z",
          "site_visit": {
            "location": "-15.7113833333 124.3992633333 8.5000000000 4.9000000000",
            "comments": null,
            "site_conditions": "1502768495317.jpg"
          },
          "@id": "build_Site-Visit-Start-0-1_1490753483"
            }
          },
      "mediaFile": {
        "downloadUrl": "https://dpaw-data.appspot.com/view/binaryData?blobKey=...",
        "hash": "md5:9fcf6ae0ffb8676c933ee43027b45dae",
        "filename": "1502768495317.jpg"
        }
      }
    }


    with open("data/odka/build_Site-Visit-Start-0-2_1510716686.json") as df:
        d = json.load(df)
    r = d[1]

    r

    {
    "submission": {
      "@xmlns": "http://opendatakit.org/submissions",
      "@xmlns:orx": "http://openrosa.org/xforms",
      "data": {
        "data": {
          "reporter": "sam_pegg",
          "@instanceID": "uuid:c58fe0d6-179a-47b6-af1d-508555fbd1b9",
          "@isComplete": "true",
          "@submissionDate": "2017-11-15T11:42:52.444Z",
          "survey_start_time": "2017-11-15T11:41:27.652Z",
          "orx:meta": {
            "orx:instanceID": "uuid:c58fe0d6-179a-47b6-af1d-508555fbd1b9"
          },
          "@markedAsCompleteDate": "2017-11-15T11:42:52.444Z",
          "site_visit": {
            "location": "-17.9711817000 122.2323750000 17.4000000000 11.2000000000",
            "comments": "Training with tash and matt",
            "site_conditions": "1510746110532.jpg"
          },
          "@id": "build_Site-Visit-Start-0-2_1510716686",
          "device_id": "febd1d3515c97a61"
        }
      },
      "mediaFile": {
        "downloadUrl": "https://dpaw-data.appspot.com/view/binaryData?blobKey=b...",
        "hash": "md5:6f60589b2d3fd5bb118c0287382ee734",
        "filename": "1510746110532.jpg"
          }
        }
      },

    Existing records will be overwritten unless marked in WAStD as "proofread"
    or higher levels of QA.

    Returns:
        The WAStD Survey object.
    """
    logger.info("Found Site Visit Start...")
    data = make_data(r)
    media = make_media(r)
    reporter_match = guess_user(data["reporter"])

    unique_data = dict(
        source="odk",
        source_id=data["@instanceID"])
    extra_data = dict(
        start_location=odk_point_as_point(data["site_visit"]["location"]),
        start_time=parse_datetime(data["survey_start_time"]),
        start_comments="{0}\n\n\n{1}".format(reporter_match["message"], data["site_visit"]["comments"]),
        reporter=reporter_match["user"],
        device_id=None if "device_id" not in data else data["device_id"],
        # TODO team if present
    )

    enc, action = create_update_skip(
        unique_data,
        extra_data,
        cls=Survey,
        base_cls=Survey,
        retain_qa=True)

    if action in ["update", "create"]:
        enc.save()

        fname = data["site_visit"]["site_conditions"]
        if fname:
            logger.debug(" Found start_photo.")
            pdir = make_photo_foldername(enc.source_id)
            pname = os.path.join(pdir, fname)
            logger.debug("  Photo dir is {0}".format(pdir))
            logger.debug("  Photo filepath is {0}".format(pname))

            dl_photo(enc.source_id, media[fname], fname)
            logger.debug("  Downloaded start_photo.")

            if os.path.exists(pname):
                logger.debug("  File {0} exists".format(pname))
                with open(pname, 'rb') as photo:
                    f = File(photo)
                    if f.size > 0:
                        enc.start_photo.save(pname, f, save=True)
                        logger.debug("  Attached start_photo.")
                    else:
                        logger.debug("  [ERROR] zero size file {0}".format(p))
            else:
                logger.debug("  [ERROR] missing file {0}".format(p))

            enc.save()

    logger.info("Done: {0}\n".format(enc))
    return enc


# ---------------------------------------------------------------------------#
# Site Visit End 0.1-0.2
#
def import_odka_sve02(r):
    """Import one ODK Site Visit End 0.1 or 0.2 record from the OKA-A API into WAStD.

    Arguments

    r The submission record as dict, e.g.

    save_all_odka(path="data/odka")
    with open("data/odka/build_Site-Visit-Start-0-1_1490753483.json") as df:
        d = json.load(df)
    r = d[1]

    r

    { # SVE01
        "submission": {
          "@xmlns": "http://opendatakit.org/submissions",
          "@xmlns:orx": "http://openrosa.org/xforms",
          "data": {
            "data": {
              "@id": "build_Site-Visit-End-0-1_1490756971",
              "@instanceID": "uuid:bd16c5b0-dcf2-4ef2-b3bf-ccf0ac7f9a4b",
              "@submissionDate": "2017-08-23T03:46:20.663Z",
              "@isComplete": "true",
              "@markedAsCompleteDate": "2017-08-23T03:46:20.663Z",
              "orx:meta": {
                "orx:instanceID": "uuid:bd16c5b0-dcf2-4ef2-b3bf-ccf0ac7f9a4b"
              },
              "reporter": null,
              "survey_end_time": "2017-08-15T03:17:22.024Z",
              "site_visit": {
                "location": "-15.7593433333 124.4011133333 50.0000000000 5.0000000000",
                "site_conditions": "1502767093482.jpg",
                "comments": null
              }
            }
          },
          "mediaFile": {
            "filename": "1502767093482.jpg",
            "hash": "md5:5c837c90b20bf3cc49c43c32605fdb62",
            "downloadUrl": "https://dpaw-data.appspot.com/view/binaryData?blobKey=..."
          }
        }
      },
        { #SVE02
        "submission": {
          "@xmlns": "http://opendatakit.org/submissions",
          "@xmlns:orx": "http://openrosa.org/xforms",
          "data": {
            "data": {
              "@id": "build_Site-Visit-End-0-2_1510716716",
              "@instanceID": "uuid:d6ca6ab9-e4ed-461f-9449-e52248c05ff0",
              "@submissionDate": "2017-11-15T11:49:31.694Z",
              "@isComplete": "true",
              "@markedAsCompleteDate": "2017-11-15T11:49:31.694Z",
              "orx:meta": {
                "orx:instanceID": "uuid:d6ca6ab9-e4ed-461f-9449-e52248c05ff0"
              },
              "reporter": "jessamy_ham",
              "survey_end_time": "2017-11-15T09:33:05.370Z",
              "device_id": "febd1d3515c97a61",
              "site_visit": {
                "location": "-17.9711717000 122.2326200000 1.2000000000 4.7000000000",
                "site_conditions": "1510746532962.jpg",
                "comments": "Training"
              }
            }
          },
          "mediaFile": {
            "filename": "1510746532962.jpg",
            "hash": "md5:b3320f6a4425d711c6c0546d740ae07c",
            "downloadUrl": "https://dpaw-data.appspot.com/view/binaryData?blobKey=..."
          }
        }
      },


    with open("data/odka/build_Site-Visit-Start-0-2_1510716686.json") as df:
        d = json.load(df)
    r = d[1]

    r

    {
    "submission": {
      "@xmlns": "http://opendatakit.org/submissions",
      "@xmlns:orx": "http://openrosa.org/xforms",
      "data": {
        "data": {
          "reporter": "sam_pegg",
          "@instanceID": "uuid:c58fe0d6-179a-47b6-af1d-508555fbd1b9",
          "@isComplete": "true",
          "@submissionDate": "2017-11-15T11:42:52.444Z",
          "survey_start_time": "2017-11-15T11:41:27.652Z",
          "orx:meta": {
            "orx:instanceID": "uuid:c58fe0d6-179a-47b6-af1d-508555fbd1b9"
          },
          "@markedAsCompleteDate": "2017-11-15T11:42:52.444Z",
          "site_visit": {
            "location": "-17.9711817000 122.2323750000 17.4000000000 11.2000000000",
            "comments": "Training with tash and matt",
            "site_conditions": "1510746110532.jpg"
          },
          "@id": "build_Site-Visit-Start-0-2_1510716686",
          "device_id": "febd1d3515c97a61"
        }
      },
      "mediaFile": {
        "downloadUrl": "https://dpaw-data.appspot.com/view/binaryData?blobKey=b...",
        "hash": "md5:6f60589b2d3fd5bb118c0287382ee734",
        "filename": "1510746110532.jpg"
          }
        }
      },

    Existing records will be overwritten unless marked in WAStD as "proofread"
    or higher levels of QA.

    Returns:
        The WAStD SurveyEnd object.
    """
    logger.info("Found Site Visit End...")
    data = make_data(r)
    media = make_media(r)
    reporter_match = guess_user(data["reporter"])

    unique_data = dict(
        source="odk",
        source_id=data["@instanceID"])
    extra_data = dict(
        end_location=odk_point_as_point(data["site_visit"]["location"]),
        end_time=parse_datetime(data["survey_end_time"]),
        end_comments="{0}\n\n\n{1}".format(reporter_match["message"], data["site_visit"]["comments"]),
        reporter=reporter_match["user"],
        device_id=None if "device_id" not in data else data["device_id"],
    )

    enc, action = create_update_skip(
        unique_data,
        extra_data,
        cls=SurveyEnd,
        base_cls=SurveyEnd,
        retain_qa=False)

    if action in ["update", "create"]:
        enc.save()

        fname = data["site_visit"]["site_conditions"]
        if fname:
            logger.debug(" Found end_photo.")
            pdir = make_photo_foldername(enc.source_id)
            pname = os.path.join(pdir, fname)
            logger.debug("  Photo dir is {0}".format(pdir))
            logger.debug("  Photo filepath is {0}".format(pname))

            dl_photo(enc.source_id, media[fname], fname)
            logger.debug("  Downloaded end_photo.")

            if os.path.exists(pname):
                logger.debug("  File {0} exists".format(pname))
                with open(pname, 'rb') as photo:
                    f = File(photo)
                    if f.size > 0:
                        enc.end_photo.save(pname, f, save=True)
                        logger.debug("  Attached end_photo.")
                    else:
                        logger.debug("  [ERROR] zero size file {0}".format(p))
            else:
                logger.debug("  [ERROR] missing file {0}".format(p))

            enc.save()

    logger.info("Done: {0}\n".format(enc))
    return enc


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

    save_all_odka(path="data/odka")
    with open("data/odka/build_Fox-Sake-0-3_1490757423.json") as df:
        d = json.load(df)
    r = d[1]

    r

    {
      "submission": {
        "@xmlns": "http://opendatakit.org/submissions",
        "mediaFile": {
          "downloadUrl": "https://dpaw-data.appspot.com/view/binaryData?blobKey=...",
          "hash": "md5:ed81ee17661c5abd50d1afcd8e286df1",
          "filename": "1502766687358.jpg"
        },
        "data": {
          "data": {
            "@id": "build_Fox-Sake-0-3_1490757423",
            "observation_end_time": "2017-08-15T03:12:40.171Z",
            "reporter": null,
            "@instanceID": "uuid:01c1d466-d759-4bea-a740-1dbf29031060",
            "orx:meta": {
              "orx:instanceID": "uuid:01c1d466-d759-4bea-a740-1dbf29031060"
            },
            "@submissionDate": "2017-08-23T03:45:56.782Z",
            "disturbanceobservation": {
              "disturbance_cause": "unknown",
              "photo_disturbance": "1502766687358.jpg",
              "location": "-15.7594300000 124.4009683333 57.1000000000 5.0000000000",
              "comments": "Fire pits X 6",
              "disturbance_cause_confidence": "expert-opinion"
            },
            "@isComplete": "true",
            "observation_start_time": "2017-08-15T03:10:41.862Z",
            "@markedAsCompleteDate": "2017-08-23T03:45:56.782Z"
          }
        },
        "@xmlns:orx": "http://openrosa.org/xforms"
      }
    }

    Existing records will be overwritten unless marked in WAStD as "proofread"
    or higher levels of QA.

    Returns:
        The WAStD Encounter object.
    """
    logger.info("Found Fox Sake...")
    data = make_data(r)
    media = make_media(r)
    reporter_match = guess_user(data["reporter"])

    unique_data = dict(
        source="odk",
        source_id=data["@instanceID"])
    extra_data = dict(
        where=odk_point_as_point(data["disturbanceobservation"]["location"]),
        when=parse_datetime(data["observation_start_time"]),
        location_accuracy="10",
        observer=reporter_match["user"],
        reporter=reporter_match["user"],
        comments=reporter_match["message"],
    )

    # if cls == LineTransectEncounter:
    #     extra_data["transect"] = read_odk_linestring(where)

    enc, action = create_update_skip(
        unique_data,
        extra_data,
        cls=Encounter,
        base_cls=Encounter)

    if action in ["update", "create"]:
        handle_odka_disturbanceobservation(enc, media, data)
        enc.save()

    logger.info("Done: {0}\n".format(enc))
    return enc


# ---------------------------------------------------------------------------#
# Track or Treat 0.36-0.44
#
def import_odka_tt044(r):
    """Import one ODK Track or Treat 0.44 record from the OKA-A API into WAStD.

    This should work for versions 0.36, 0.44 and up.

    Arguments

    r The submission record as dict, e.g.

    save_all_odka(path="data/odka")
    from wastd.observations.utils import *

    with open("data/odka/build_Track-or-Treat-0-44_1509422138.json") as df:
        d = json.load(df)

    logger.debug(json.dumps(d[0], indent=4))

    {
        "submission": {
            "@xmlns": "http://opendatakit.org/submissions",
            "@xmlns:orx": "http://openrosa.org/xforms",
            "data": {
                "data": {
                    "@id": "build_Track-or-Treat-0-44_1509422138",
                    "@instanceID": "uuid:e4106979-e2d8-4020-9bd7-49f47579dfb5",
                    "@submissionDate": "2017-11-10T07:22:40.265Z",
                    "@isComplete": "true",
                    "@markedAsCompleteDate": "2017-11-10T07:22:40.265Z",
                    "orx:meta": {
                        "orx:instanceID": "uuid:e4106979-e2d8-4020-9bd7-49f47579dfb5"
                    },
                    "observation_start_time": "2017-11-10T07:15:43.160Z",
                    "reporter": "Thevenard3",
                    "device_id": "d0:f8:8c:78:f5:f0",
                    "details": {
                        "nest_age": "fresh",
                        "species": "natator-depressus",
                        "nest_type": "successful-crawl",
                        "observed_at": "-31.9965742000 115.8842839000 0E-10 50.0000000000"
                    },
                    "track_photos": {
                        "photo_track_1": null,
                        "photo_track_2": null
                    },
                    "nest_photos": {
                        "photo_nest_1": null,
                        "photo_nest_2": null,
                        "photo_nest_3": null
                    },
                    "nest": {
                        "habitat": "in-dune-vegetation",
                        "disturbance": "present",
                        "nest_tagged": "yes",
                        "logger_found": "yes",
                        "eggs_counted": "yes",
                        "hatchlings_measured": "yes",
                        "fan_angles_measured": "yes"
                    },
                    "disturbanceobservation": [
                        {
                            "photo_disturbance": "1510298200138.jpg",
                            "disturbance_cause": "vehicle",
                            "disturbance_cause_confidence": "guess",
                            "disturbance_severity": "completely",
                            "comments": "Yeah"
                        },
                        {
                            "photo_disturbance": "1510298254227.jpg",
                            "disturbance_cause": "goanna",
                            "disturbance_cause_confidence": "guess",
                            "disturbance_severity": "partly",
                            "comments": "Jup"
                        }
                    ],
                    "egg_count": {
                        "no_egg_shells": "60",
                        "no_live_hatchlings": "5",
                        "no_dead_hatchlings": "14",
                        "no_undeveloped_eggs": "15",
                        "no_unhatched_eggs": "5",
                        "no_unhatched_term": "6",
                        "no_depredated_eggs": "2",
                        "nest_depth_top": "25",
                        "nest_depth_bottom": "89"
                    },
                    "egg_photos": {
                        "photo_eggs": "1510298324400.jpg"
                    },
                    "nest_tag": {
                        "status": "resighted",
                        "flipper_tag_id": "WA1234",
                        "date_nest_laid": "2017-11-10",
                        "tag_label": "Test3",
                        "tag_comments": "Jup",
                        "photo_tag": "1510298358979.jpg"
                    },
                    "hatchling_measurements": [
                        {
                            "straight_carapace_length_mm": "125",
                            "straight_carapace_width_mm": "56",
                            "body_weight_g": "12"
                        },
                        {
                            "straight_carapace_length_mm": "145",
                            "straight_carapace_width_mm": "16",
                            "body_weight_g": "15"
                        }
                    ],
                    "fan_angles": {
                        "leftmost_track_auto": null,
                        "rightmost_track_auto": null,
                        "bearing_to_water_auto": null,
                        "device_compass_present": "no",
                        "no_tracks_main_group": "20",
                        "outlier_tracks_present": "yes",
                        "light_sources_present": "yes",
                        "hatchling_emergence_time_known": "yes"
                    },
                    "hatchling_emergence_time_group": {
                        "hatchling_emergence_time": "2017-11-10T07:21:00.000Z"
                    },
                    "fan_angles_manual": {
                        "leftmost_track_manual": "230",
                        "rightmost_track_manual": "356",
                        "bearing_to_water_manual": "270"
                    },
                    "outlier_track": [
                        {
                            "track_bearing_auto": null,
                            "track_bearing_manual": "53"
                        },
                        {
                            "track_bearing_auto": null,
                            "track_bearing_manual": "52"
                        }
                    ],
                    "light_source": {
                        "light_bearing_auto": null,
                        "bearing_manual": "23",
                        "light_source_type": "artificial",
                        "light_source_description": "That's no moon!"
                    },
                    "observation_end_time": "2017-11-10T07:21:50.211Z"
                }
            },
            "mediaFile": [
                {
                    "filename": "1510298200138.jpg",
                    "hash": "md5:c4e49a94ba76623160fd2dbebf34eff2",
                    "downloadUrl": "https://dpaw-data.appspot.com/view/binaryData?blobKey="
                },
                {
                    "filename": "1510298254227.jpg",
                    "hash": "md5:0da51be6b4e6fb3f0210d473c979d85c",
                    "downloadUrl": "https://dpaw-data.appspot.com/view/binaryData?blobKey="
                },
                {
                    "filename": "1510298324400.jpg",
                    "hash": "md5:351d1043a5cc49c2fbf093e8d60508a1",
                    "downloadUrl": "https://dpaw-data.appspot.com/view/binaryData?blobKey="
                },
                {
                    "filename": "1510298358979.jpg",
                    "hash": "md5:16b72612f5297b04846f4cba73bf0988",
                    "downloadUrl": "https://dpaw-data.appspot.com/view/binaryData?blobKey="
                }
            ]
        }
    }


    Existing records will be overwritten unless marked in WAStD as "proofread"
    or higher levels of QA.

    Important note: repeating groups with only one element are flattened into
    a simple dict consisting of the element's keys.
    Repeating groups with multiple elements consist of lists of dicts.
    This is an artifact of the XML parser.

    Returns:
        The WAStD Encounter object.
    """
    logger.info("Found Track or Treat...")
    data = make_data(r)
    media = make_media(r)
    usr = guess_user(data["reporter"])

    unique_data = dict(
        source="odk",
        source_id=data["@instanceID"])
    extra_data = dict(
        where=odk_point_as_point(data["details"]["observed_at"]),
        when=parse_datetime(data["observation_start_time"]),
        location_accuracy="10",
        observer=usr["user"],
        reporter=usr["user"],
        comments=usr["message"],
    )

    enc, action = create_update_skip(
        unique_data,
        extra_data,
        cls=TurtleNestEncounter,
        base_cls=Encounter)

    if action in ["update", "create"]:
        enc.nest_age = data["details"]["nest_age"]
        enc.species = data["details"]["species"]
        enc.nest_type = data["details"]["nest_type"]
        enc.habitat = data["nest"]["habitat"] or "na"
        enc.disturbance = data["nest"]["disturbance"] or "na"
        enc.save()
        handle_media_attachment_odka(enc, media, data["track_photos"]["photo_track_1"], title="Uptrack")
        handle_media_attachment_odka(enc, media, data["track_photos"]["photo_track_2"], title="Downtrack")
        handle_media_attachment_odka(enc, media, data["nest_photos"]["photo_nest_1"], title="Nest 1")
        handle_media_attachment_odka(enc, media, data["nest_photos"]["photo_nest_2"], title="Nest 2")
        handle_media_attachment_odka(enc, media, data["nest_photos"]["photo_nest_3"], title="Nest 3")
        handle_odka_disturbanceobservation(enc, media, data)
        handle_odka_nesttagobservation(enc, media, data)
        handle_odka_turtlenestobservation(enc, media, data)
        handle_odka_hatchlingmorphometricobservation(enc, media, data)
        # handle_odka_fanangles(enc, media, data)

        if "photo_hatchling_tracks_seawards" in data["fan_angles"]:
            handle_media_attachment_odka(
                enc, media,
                data["fan_angles"]["photo_hatchling_tracks_seawards"],
                title="Hatchling tracks seawards")
        if "photo_hatchling_tracks_relief" in data["fan_angles"]:
            handle_media_attachment_odka(
                enc, media,
                data["fan_angles"]["photo_hatchling_tracks_relief"],
                title="Hatchling tracks relief")

        # TT0.44
        # "hatchling_emergence_time_group": {
        #     "hatchling_emergence_time": null
        #   },
        # "fan_angles_manual": {
        #     "bearing_to_water_manual": "6",
        #     "rightmost_track_manual": null,
        #     "leftmost_track_manual": null
        #   },
        # "fan_angles": {
        #     "no_tracks_main_group": "1",
        #     "device_compass_present": "no",
        #     "light_sources_present": "na",
        #     "rightmost_track_auto": null,
        #     "hatchling_emergence_time_known": "no",
        #     "bearing_to_water_auto": null,
        #     "leftmost_track_auto": null,
        #     "outlier_tracks_present": "no"
        #   },

        # "outlier_track": [
        #     {
        #       "track_bearing_auto": null,
        #       "track_bearing_manual": "347"
        #     },
        #     {
        #       "track_bearing_auto": null,
        #       "track_bearing_manual": "21"
        #     }
        #   ],

        # TT0.45
        # "fan_angles_manual": {
        #    "bearing_to_water_manual": null,
        #    "rightmost_track_manual": null,
        #    "leftmost_track_manual": null
        #  },
        #  "fan_angles": {
        #    "no_tracks_main_group": "35",
        #    "device_compass_present": "yes",
        #    "light_sources_present": "no",
        #    "rightmost_track_auto": "296.2910000000",
        #    "hatchling_emergence_time_known": "no",
        #    "bearing_to_water_auto": "296.7820000000",
        #    "leftmost_track_auto": "296.6340000000",
        #    "outlier_tracks_present": "yes"
        #  },
        #  "outlier_track": {
        #    "track_bearing_auto": "296.9590000000",
        #    "track_bearing_manual": null
        #  },

        # TT0.46
        # "fan_angles": {
        #     "no_tracks_main_group": "8",
        #     "device_compass_present": "no",
        #     "light_sources_present": "no",
        #     "rightmost_track_auto": null,
        #     "hatchling_emergence_time_known": "no",
        #     "bearing_to_water_auto": null,
        #     "leftmost_track_auto": null,
        #     "outlier_tracks_present": "yes"
        #   },

        # TT0.47
        # "fan_angles": {
        #     "leftmost_track_auto": null,
        #     "rightmost_track_auto": null,
        #     "bearing_to_water_auto": null,
        #     "device_compass_present": "no",
        #     "no_tracks_main_group": "25",
        #     "outlier_tracks_present": "no",
        #     "light_sources_present": "no",
        #     "hatchling_emergence_time_known": "no"
        #   },
        #   "fan_angles_manual": {
        #     "leftmost_track_manual": "307",
        #     "rightmost_track_manual": "29",
        #     "bearing_to_water_manual": "342"
        #   },
        #   "hatchling_emergence_time_group": {
        #     "hatchling_emergence_time": null,
        #     "hatchling_emergence_time_source": null
        #   },

        # # TT0.51
        # "fan_angles": {
        #     "photo_hatchling_tracks_seawards": "1517444725383.jpg",
        #     "photo_hatchling_tracks_relief": "1517444761289.jpg",
        #     "bearing_to_water_manual": "255.0000000000",
        #     "leftmost_track_manual": "190.0000000000",
        #     "rightmost_track_manual": "251.0000000000",
        #     "no_tracks_main_group": "12",
        #     "no_tracks_main_group_min": "12",
        #     "no_tracks_main_group_max": "13",
        #     "outlier_tracks_present": "present",
        #     "hatchling_path_to_sea": "uneven-ground",
        #     "path_to_sea_comments": "Climbing out of goanna diggings",
        #     "hatchling_emergence_time_known": "no",
        #     "cloud_cover_at_emergence_known": "no",
        #     "light_sources_present": "present"
        #   },
        #   "hatchling_emergence_time_group": {
        #     "hatchling_emergence_time": null,
        #     "hatchling_emergence_time_source": null
        #   },
        #   "emergence_climate": {
        #     "cloud_cover_at_emergence": null
        #   },
        #   "light_source": {
        #     "light_source_photo": "1517444993845.jpg",
        #     "light_bearing_manual": "164.0000000000",
        #     "light_source_type": "artificial",
        #     "light_source_description": "Industry"
        #   },
        #   "other_light_sources": {
        #     "other_light_sources_present": "na"
        #   },
        #   "outlier_track": {
        #     "outlier_track_photo": "1517445093780.jpg",
        #     "outlier_track_bearing_manual": "135.0000000000",
        #     "outlier_group_size": "1",
        #     "outlier_track_comment": null
        #   },

        enc.save()

    logger.info("Done: {0}\n".format(enc))
    return enc


# ---------------------------------------------------------------------------#
# Track Tally 0.5
#
def import_odka_tal05(r):
    """Import one ODK Track or Treat 0.44 record from the OKA-A API into WAStD.

    This should work for versions 0.36, 0.44 and up.

    Arguments

    r The submission record as dict, e.g.

    save_all_odka(path="data/odka")
    from wastd.observations.utils import *

    with open("data/odka/build_Track-Tally-0-5_1502342159.json") as df:
        tal05 = json.load(df)

    logger.debug(json.dumps(tal05[0], indent=4))

    {
        "submission": {
            "@xmlns": "http://opendatakit.org/submissions",
            "@xmlns:orx": "http://openrosa.org/xforms",
            "data": {
                "data": {
                    "@id": "build_Track-Tally-0-5_1502342159",
                    "@instanceID": "uuid:a0954e6a-14ff-4099-9bae-0b1bdc466675",
                    "@submissionDate": "2017-10-12T08:20:06.257Z",
                    "@isComplete": "true",
                    "@markedAsCompleteDate": "2017-10-12T08:20:06.257Z",
                    "orx:meta": {
                        "orx:instanceID": "uuid:a0954e6a-14ff-4099-9bae-0b1bdc466675"
                    },
                    "observation_start_time": "2017-10-12T08:13:41.990Z",
                    "reporter": "SarahM",
                    "overview": {
                        "location": "-17.97119 122.23269499999999 0.0 0.0;
                        -17.971113333333335 122.23275333333335 0.0 0.0;
                        -17.970951666666668 122.23281166666666 0.0 0.0;
                        -17.970821666666666 122.232755 0.0 0.0;
                        -17.970818333333334 122.23259166666666 0.0 0.0;
                        -17.970824999999998 122.23257666666665",
                        "fb_evidence": "present",
                        "gn_evidence": "absent",
                        "hb_evidence": "absent",
                        "lh_evidence": "absent",
                        "or_evidence": "absent",
                        "unk_evidence": "absent",
                        "predation_evidence": "present"
                    },
                    "fb": {
                        "fb_no_old_tracks": "0",
                        "fb_no_fresh_successful_crawls": "1",
                        "fb_no_fresh_false_crawls": "0",
                        "fb_no_fresh_tracks_unsure": "0",
                        "fb_no_fresh_tracks_not_assessed": "0",
                        "fb_no_hatched_nests": "2"
                    },
                    "gn": {
                        "gn_no_old_tracks": null,
                        "gn_no_fresh_successful_crawls": null,
                        "gn_no_fresh_false_crawls": null,
                        "gn_no_fresh_tracks_unsure": null,
                        "gn_no_fresh_tracks_not_assessed": null,
                        "gn_no_hatched_nests": null
                    },
                    "hb": {
                        "hb_no_old_tracks": null,
                        "hb_no_fresh_successful_crawls": null,
                        "hb_no_fresh_false_crawls": null,
                        "hb_no_fresh_tracks_unsure": null,
                        "hb_no_fresh_tracks_not_assessed": null,
                        "hb_no_hatched_nests": null
                    },
                    "lh": {
                        "lh_no_old_tracks": null,
                        "lh_no_fresh_successful_crawls": null,
                        "lh_no_fresh_false_crawls": null,
                        "lh_no_fresh_tracks_unsure": null,
                        "lh_no_fresh_tracks_not_assessed": null,
                        "lh_no_hatched_nests": null
                    },
                    "or": {
                        "or_no_old_tracks": null,
                        "or_no_fresh_successful_crawls": null,
                        "or_no_fresh_false_crawls": null,
                        "or_no_fresh_tracks_unsure": null,
                        "or_no_fresh_tracks_not_assessed": null,
                        "or_no_hatched_nests": null
                    },
                    "unk": {
                        "unk_no_old_tracks": null,
                        "unk_no_fresh_successful_crawls": null,
                        "unk_no_fresh_false_crawls": null,
                        "unk_no_fresh_tracks_unsure": null,
                        "unk_no_fresh_tracks_not_assessed": null,
                        "unk_no_hatched_nests": null
                    },
                    "disturbance": {
                        "disturbance_cause": "vehicle",
                        "no_nests_disturbed": "1",
                        "no_tracks_encountered": null,
                        "disturbance_comments": null
                    },
                    "observation_end_time": "2017-10-12T08:20:04.296Z"
                }
            }
        }
    }
    Existing records will be overwritten unless marked in WAStD as "proofread"
    or higher levels of QA.

    Important note: repeating groups with only one element are flattened into
    a simple dict consisting of the element's keys.
    Repeating groups with multiple elements consist of lists of dicts.
    This is an artifact of the XML parser.

    Returns:
        The WAStD Encounter object.
    """
    logger.info("Found Track Tally...")
    data = make_data(r)
    # media = make_media(r)
    usr = guess_user(data["reporter"])

    unique_data = dict(
        source="odk",
        source_id=data["@instanceID"])
    extra_data = dict(
        where=odk_point_as_point(data["overview"]["location"]),
        transect=read_odk_linestring(data["overview"]["location"]),
        when=parse_datetime(data["observation_start_time"]),
        location_accuracy="10",
        observer=usr["user"],
        reporter=usr["user"],
        comments=usr["message"],
    )

    enc, action = create_update_skip(
        unique_data,
        extra_data,
        cls=LineTransectEncounter,
        base_cls=Encounter)

    if action in ["update", "create"]:

        # TurtleNestDisturbanceTallyObservation
        [handle_turtlenestdisttallyobs(distobs, enc)
         for distobs in listify(data["disturbance"])
         if len(listify(data["disturbance"])) > 0]

        #  TrackTallyObservations
        FB = "natator-depressus"
        GN = "chelonia-mydas"
        HB = "eretmochelys-imbricata"
        LH = "caretta-caretta"
        OR = "lepidochelys-olivacea"
        UN = "cheloniidae-fam"

        tally_mapping = [
            [FB, "old",   "track-not-assessed",     data["fb"]["fb_no_old_tracks"] or 0],
            [FB, "fresh", "successful-crawl",       data["fb"]["fb_no_fresh_successful_crawls"] or 0],
            [FB, "fresh", "false-crawl",            data["fb"]["fb_no_fresh_false_crawls"] or 0],
            [FB, "fresh", "track-unsure",           data["fb"]["fb_no_fresh_tracks_unsure"] or 0],
            [FB, "fresh", "track-not-assessed",     data["fb"]["fb_no_fresh_tracks_not_assessed"] or 0],
            [FB, "fresh", "hatched-nest",           data["fb"]["fb_no_hatched_nests"] or 0],

            [GN, "old",     "track-not-assessed",   data["gn"]["gn_no_old_tracks"] or 0],
            [GN, "fresh",   "successful-crawl",     data["gn"]["gn_no_fresh_successful_crawls"] or 0],
            [GN, "fresh",   "false-crawl",          data["gn"]["gn_no_fresh_false_crawls"] or 0],
            [GN, "fresh",   "track-unsure",         data["gn"]["gn_no_fresh_tracks_unsure"] or 0],
            [GN, "fresh",   "track-not-assessed",   data["gn"]["gn_no_fresh_tracks_not_assessed"] or 0],
            [GN, "fresh",   "hatched-nest",         data["gn"]["gn_no_hatched_nests"] or 0],

            [HB, "old",     "track-not-assessed",   data["hb"]["hb_no_old_tracks"] or 0],
            [HB, "fresh",   "successful-crawl",     data["hb"]["hb_no_fresh_successful_crawls"] or 0],
            [HB, "fresh",   "false-crawl",          data["hb"]["hb_no_fresh_false_crawls"] or 0],
            [HB, "fresh",   "track-unsure",         data["hb"]["hb_no_fresh_tracks_unsure"] or 0],
            [HB, "fresh",   "track-not-assessed",   data["hb"]["hb_no_fresh_tracks_not_assessed"] or 0],
            [HB, "fresh",   "hatched-nest",         data["hb"]["hb_no_hatched_nests"] or 0],

            [LH, "old",     "track-not-assessed",   data["lh"]["lh_no_old_tracks"] or 0],
            [LH, "fresh",   "successful-crawl",     data["lh"]["lh_no_fresh_successful_crawls"] or 0],
            [LH, "fresh",   "false-crawl",          data["lh"]["lh_no_fresh_false_crawls"] or 0],
            [LH, "fresh",   "track-unsure",         data["lh"]["lh_no_fresh_tracks_unsure"] or 0],
            [LH, "fresh",   "track-not-assessed",   data["lh"]["lh_no_fresh_tracks_not_assessed"] or 0],
            [LH, "fresh",   "hatched-nest",         data["lh"]["lh_no_hatched_nests"] or 0],

            [OR, "old",     "track-not-assessed",   data["or"]["or_no_old_tracks"] or 0],
            [OR, "fresh",   "successful-crawl",     data["or"]["or_no_fresh_successful_crawls"] or 0],
            [OR, "fresh",   "false-crawl",          data["or"]["or_no_fresh_false_crawls"] or 0],
            [OR, "fresh",   "track-unsure",         data["or"]["or_no_fresh_tracks_unsure"] or 0],
            [OR, "fresh",   "track-not-assessed",   data["or"]["or_no_fresh_tracks_not_assessed"] or 0],
            [OR, "fresh",   "hatched-nest",         data["or"]["or_no_hatched_nests"] or 0],

            [UN, "old",     "track-not-assessed",   data["unk"]["unk_no_old_tracks"] or 0],
            [UN, "fresh",   "successful-crawl",     data["unk"]["unk_no_fresh_successful_crawls"] or 0],
            [UN, "fresh",   "false-crawl",          data["unk"]["unk_no_fresh_false_crawls"] or 0],
            [UN, "fresh",   "track-unsure",         data["unk"]["unk_no_fresh_tracks_unsure"] or 0],
            [UN, "fresh",   "track-not-assessed",   data["unk"]["unk_no_fresh_tracks_not_assessed"] or 0],
            [UN, "fresh",   "hatched-nest",         data["unk"]["unk_no_hatched_nests"] or 0],
        ]

        [make_tallyobs(enc, x[0], x[1], x[2], x[3]) for x in tally_mapping]

        enc.save()

    logger.info("Done: {0}\n".format(enc))
    return enc


# ---------------------------------------------------------------------------#
# Marine Wildlife Incident 0.5
#
def import_odka_mwi05(r):
    """
    Import one ODK Marine Wildlife Incident 0.5 record from the OKA-A API into WAStD.

    This should work for versions 0.4 and up.

    Arguments

    r The submission record as dict, e.g.

    save_all_odka(path="data/odka")
    from wastd.observations.utils import *

    with open("data/odka/build_Marine-Wildlife-Incident-0-4_1509605702.json") as df:
        d = json.load(df)

    logger.debug(json.dumps(d[0], indent=4))

    {
        "submission": {
          "@xmlns": "http://opendatakit.org/submissions",
          "@xmlns:orx": "http://openrosa.org/xforms",
          "data": {
            "data": {
              "@id": "build_Marine-Wildlife-Incident-0-5_1510547403",
              "@instanceID": "uuid:a9cf803b-174f-44a9-a0e9-5dff96ddc3c3",
              "@submissionDate": "2017-11-13T04:33:07.558Z",
              "@isComplete": "true",
              "@markedAsCompleteDate": "2017-11-13T04:33:07.558Z",
              "orx:meta": {
                "orx:instanceID": "uuid:a9cf803b-174f-44a9-a0e9-5dff96ddc3c3"
              },
              "observation_start_time": "2017-11-13T04:30:32.482Z",
              "reporter": "Thevenard3",
              "device_id": "d0:f8:8c:78:f5:f0",
              "phone_number": null,
              "incident": {
                "observed_at": "-31.9966218000 115.8843043000 0E-10 50.0000000000",
                "location_comment": null,
                "incident_time": "2017-11-13T04:30:00.000Z",
                "habitat": "below-mshwm",
                "photo_habitat": "1510547487217.jpg"
              },
              "details": {
                "taxon": "Cheloniidae",
                "species": "caretta-caretta",
                "maturity": "na",
                "sex": "na"
              },
              "photos_turtle": {
                "photo_carapace_top": null,
                "photo_head_top": null,
                "photo_head_side": null,
                "photo_head_front": null
              },
              "status": {
                "activity": "beach-washed",
                "health": "dead-advanced",
                "behaviour": null
              },
              "death": {
                "cause_of_death": "drowned-entangled-infrastructure",
                "cause_of_death_confidence": "expert-opinion"
              },
              "checks": {
                "checked_for_injuries": "na",
                "scanned_for_pit_tags": "na",
                "checked_for_flipper_tags": "na",
                "samples_taken": "na"
              },
              "morphometrics": {
                "curved_carapace_length_mm": null,
                "curved_carapace_length_accuracy": "10",
                "curved_carapace_width_mm": null,
                "curved_carapace_width_accuracy": "10",
                "tail_length_carapace_mm": null,
                "tail_length_carapace_accuracy": "10",
                "maximum_head_width_mm": null,
                "maximum_head_width_accuracy": "10"
              },
              "habitat_photos": {
                "photo_habitat_2": null,
                "photo_habitat_3": null,
                "photo_habitat_4": null
              },
              "animal_fate": {
                "animal_fate_comment": "Detonation"
              },
              "observation_end_time": "2017-11-13T04:33:01.780Z"
            }
          },
          "mediaFile": {
            "filename": "1510547487217.jpg",
            "hash": "md5:3fc23a100c0767bcff56420648d9ecc7",
            "downloadUrl": "https://dpaw-data.appspot.com/view/binaryData?blobKey=..."
          }
        }
      }


    Existing records will be overwritten unless marked in WAStD as "proofread"
    or higher levels of QA.

    Important note: repeating groups with only one element are flattened into
    a simple dict consisting of the element's keys.
    Repeating groups with multiple elements consist of lists of dicts.
    This is an artifact of the XML parser.

    Returns:
    The WAStD Encounter object.
    """
    logger.info("Found Marine Wildlife Incident...")
    data = make_data(r)
    media = make_media(r)
    usr = guess_user(data["reporter"])

    # Older versions of this form use the dashless, pardon, dash-less keys
    # required for older versions of ODK Collect.
    # We'll build lookup dicts with current and dash-less keys,
    # but we'll do so programmatically because we're not savages.
    health_dict = map_and_keep(HEALTH_CHOICES)
    habitat_dict = map_and_keep(HABITAT_CHOICES)
    activity_dict = map_and_keep(ACTIVITY_CHOICES)
    maturity_dict = map_and_keep(MATURITY_CHOICES)
    species_dict = map_and_keep(SPECIES_CHOICES)
    species_dict.update({
        'turtle': 'cheloniidae-fam',
        'flatback': 'natator-depressus',
        'green': 'chelonia-mydas',
        'hawksbill': 'eretmochelys-imbricata',
        'loggerhead': 'caretta-caretta',
        'oliveridley': 'lepidochelys-olivacea',
        'leatherback': 'dermochelys-coriacea'
    })

    unique_data = dict(
        source="odk",
        source_id=data["@instanceID"])
    extra_data = dict(
        where=odk_point_as_point(data["incident"]["observed_at"]),
        when=parse_datetime(data["incident"]["incident_time"]),
        location_accuracy="10",
        observer=usr["user"],
        reporter=usr["user"],
        comments=usr["message"]
    )

    enc, action = create_update_skip(
        unique_data,
        extra_data,
        cls=AnimalEncounter,
        base_cls=Encounter)

    if action in ["update", "create"]:

        enc.taxon = data["details"].get("taxon", "Cheloniidae")
        enc.species = species_dict[data["details"]["species"]]
        enc.maturity = maturity_dict[data["details"]["maturity"]]
        enc.sex = data["details"]["sex"]
        enc.health = health_dict[data["status"]["health"]]
        enc.activity = activity_dict[data["status"]["activity"]]
        enc.behaviour = "Behaviour: {0}\nLocation: {1}".format(
            data["status"]["behaviour"] or "",
            data["incident"]["location_comment"] or "")
        enc.habitat = habitat_dict[data["incident"]["habitat"]]
        enc.nesting_event = "absent"
        enc.checked_for_injuries = data["checks"]["checked_for_injuries"]
        enc.scanned_for_pit_tags = data["checks"]["scanned_for_pit_tags"]
        enc.checked_for_flipper_tags = data["checks"]["checked_for_flipper_tags"]
        enc.cause_of_death = data["death"]["cause_of_death"] or 'na'
        enc.cause_of_death_confidence = data["death"]["cause_of_death_confidence"] or 'na'

        #  "checks": {
        #   "samples_taken": "present",

        enc.save()

        # Photos
        handle_media_attachment_odka(enc, media, data["incident"]["photo_habitat"], title="Initial photo of habitat")
        handle_media_attachment_odka(enc, media, data["habitat_photos"]["photo_habitat_2"], title="Habitat 2")
        handle_media_attachment_odka(enc, media, data["habitat_photos"]["photo_habitat_3"], title="Habitat 3")
        handle_media_attachment_odka(enc, media, data["habitat_photos"]["photo_habitat_4"], title="Habitat 4")
        handle_media_attachment_odka(enc, media, data["photos_turtle"]["photo_head_top"], title="Turtle head top")
        handle_media_attachment_odka(enc, media, data["photos_turtle"]["photo_head_front"], title="Turtle head front")
        handle_media_attachment_odka(enc, media, data["photos_turtle"]["photo_head_side"], title="Turtle head side")
        handle_media_attachment_odka(
            enc, media, data["photos_turtle"]["photo_carapace_top"], title="Turtle carapace top")

        handle_odka_tagsobs(enc, media, data)
        handle_odka_managementaction(enc, media, data)
        handle_odka_turtlemorph(enc, media, data)
        handle_odka_turtledamageobs(enc, media, data)

        enc.save()

    logger.info("Done: {0}\n".format(enc))
    return enc


# ---------------------------------------------------------------------------#
# Turtle Tagging
# Turtle Encounter
# TODO

def import_all_odka(path="."):
    """Import all known ODKA data.

    Example usage on shell_plus:

    import sys; reload(sys); sys.setdefaultencoding('UTF8'); path="data/odka"; from wastd.observations.utils import *
    save_all_odka(path="data/odka")
    enc = import_all_odka(path="data/odka")

    TODO: disable deprecated forms after adding fan angles etc to import
    """
    logger.info("[import_all_odka] Starting import of all downloaded ODKA data...")
    results = dict(
        tal05=[import_odka_tal05(x) for x in downloaded_data("build_Track-Tally-0-5_1502342159", path)],
        fs03=[import_odka_fs03(x) for x in downloaded_data("build_Fox-Sake-0-3_1490757423", path)],
        fs04=[import_odka_fs03(x) for x in downloaded_data("build_Fox-Sake-0-4_1534140913", path)],

        tt35=[import_odka_tt044(x) for x in downloaded_data("build_Track-or-Treat-0-35_1507882361", path)],
        tt36=[import_odka_tt044(x) for x in downloaded_data("build_Track-or-Treat-0-36_1508561995", path)],
        tt44=[import_odka_tt044(x) for x in downloaded_data("build_Track-or-Treat-0-44_1509422138", path)],
        tt45=[import_odka_tt044(x) for x in downloaded_data("build_Track-or-Treat-0-45_1511079712", path)],
        tt46=[import_odka_tt044(x) for x in downloaded_data("build_Track-or-Treat-0-46_1512095567", path)],
        tt47=[import_odka_tt044(x) for x in downloaded_data("build_Track-or-Treat-0-47_1512461621", path)],
        tt50=[import_odka_tt044(x) for x in downloaded_data("build_Track-or-Treat-0-50_1516929392", path)],
        tt51=[import_odka_tt044(x) for x in downloaded_data("build_Track-or-Treat-0-51_1517196378", path)],
        tt52=[import_odka_tt044(x) for x in downloaded_data("build_Track-or-Treat-0-52_1518683842", path)],
        tt53=[import_odka_tt044(x) for x in downloaded_data("build_Track-or-Treat-0-53_1535702040", path)],

        mwi01=[import_odka_mwi05(x) for x in downloaded_data("build_Marine-Wildlife-Incident-0-1_1502342347", path)],
        mwi04=[import_odka_mwi05(x) for x in downloaded_data("build_Marine-Wildlife-Incident-0-4_1509605702", path)],
        mwi05=[import_odka_mwi05(x) for x in downloaded_data("build_Marine-Wildlife-Incident-0-5_1510547403", path)],
        mwi06=[import_odka_mwi05(x) for x in downloaded_data("build_Marine-Wildlife-Incident-0-6_1517197224", path)],

        sve01=[import_odka_sve02(x) for x in downloaded_data("build_Site-Visit-End-0-1_1490756971", path)],
        sve02=[import_odka_sve02(x) for x in downloaded_data("build_Site-Visit-End-0-2_1510716716", path)],
        svs01=[import_odka_svs02(x) for x in downloaded_data("build_Site-Visit-Start-0-1_1490753483", path)],
        svs02=[import_odka_svs02(x) for x in downloaded_data("build_Site-Visit-Start-0-2_1510716686", path)],
        svs03=[import_odka_svs02(x) for x in downloaded_data("build_Site-Visit-Start-0-3_1535694081", path)],

        # turtle tagging 0.3
        # turtle encounter 0.4
    )
    logger.info("[import_all_odka] Finished import. Stats:")
    logger.info("\n".join(["[import_all_odka]  Imported {0} {1}".format(len(results[x]), x.upper()) for x in results]))
    return results
