from datetime import datetime, timedelta
from dateutil import parser
from django.conf import settings
import logging

from users.models import User
from wastd.odk import (
    get_auth_headers,
    get_form_submission_data,
    parse_geopoint,
    parse_geopoint_accuracy,
    get_submission_attachment,
)
from wastd.utils import LegacySourceMixin
from .lookups import NA_VALUE, TURTLE_INTERACTION_CHOICES
from .models import (
    Area,
    Survey,
    SurveyMediaAttachment,
    MediaAttachment,
    Encounter,
    TurtleNestEncounter,
    TurtleNestObservation,
    TurtleNestDisturbanceObservation,
    TurtleTrackObservation,
    NestTagObservation,
    HatchlingMorphometricObservation,
    TurtleHatchlingEmergenceObservation,
    TurtleHatchlingEmergenceOutlierObservation,
    LightSourceObservation,
    LoggerObservation,
    AnimalEncounter,
    TurtleMorphometricObservation,
    TurtleDamageObservation,
    TagObservation,
    DisturbanceObservation,
)

LOGGER = logging.getLogger("turtles")


def create_new_user(name):
    """Creates and returns a new User based on the passed-in name value.
    """
    username = name.lower().replace(" ", "_")
    # Guarantee a unique username value by appending an underscore to the string.
    while User.objects.filter(username=username).exists():
        username += "_"
    user = User.objects.create(name=name, username=username)
    user.set_unusable_password()
    return user


def get_user(reporter):
    """Try to match the reporter to an existing user. If not, return 'Unknown user'.
    """
    if reporter:
        reporter = reporter.strip()
        if User.objects.filter(is_active=True, name=reporter).exists():
            user = User.objects.filter(is_active=True, name=reporter).first()
        else:  # Create a new user.
            user = create_new_user(reporter)
            LOGGER.info(f"Created new user {user}")
    else:  # The form has been submitted without a user name recorded.
        user = User.objects.get_or_create(name='Unknown user', username='unknown_user')[0]
        LOGGER.warning(f"No reporter recorded, returning {user}")

    return user


def import_turtle_track_or_nest(form_id="turtle_track_or_nest", auth_headers=None):
    """Import submissions to the Turtle Track or Nest ODK form.
    Each submission should create:
        1 TurtleNestEncounter
        0-1 TurtleNestObservation (egg count)
        0-1 TurtleTrackObservation (unidentified species track)
        0-1 NestTagObservation (nest tag seen/deployed)
        0-1 TurtleHatchlingEmergenceObservation (fan angles, hatchling emergence time)
        0+ TurtleNestDisturbanceObservation (disturbance/predation observations)
        0+ LoggerObservation (loggers seen/deployed)
        0+ HatchlingMorphometricObservation (hatchling measurements)
        0+ TurtleHatchlingEmergenceOutlierObservation (outlier measurements measured in fan angles)
        0+ LightSourceObservation (measured in fan angles)
    """
    if not auth_headers:
        LOGGER.info("Downloading auth headers")
        auth_headers = get_auth_headers()
    project_id = settings.ODK_API_PROJECTID
    LOGGER.info(f"Downloading {form_id} submission data")
    submissions = get_form_submission_data(auth_headers, project_id, form_id)
    LOGGER.info(f"Downloaded {form_id} submission data")
    for submission in submissions:
        try:
            instance_id = submission["meta"]["instanceID"]
            if TurtleNestEncounter.objects.filter(source="odk", source_id=instance_id):
                continue  # Skip records already imported.

            # Try to match the reporter to an existing user. If not, create a new one.
            reporter = submission["reporter"]
            user = get_user(reporter)

            #check for new forms
            if "survey_start_time" in submission["details"]:
                start_time = parser.isoparse(submission["details"]["survey_start_time"])  # New forms allow editing of time in case submitted after the fact
            else:
                start_time = parser.isoparse(submission["start_time"])  # Old forms

            # Confusingly, TurtleNestEncounter objects cover nest, track and nest & track encounters.
            encounter = TurtleNestEncounter(
                status="imported",
                source="odk",
                source_id=instance_id,
                where=parse_geopoint(submission["details"]["observed_at"]),
                when=start_time,
                observer=user,
                reporter=user,
                comments=f"Device ID {submission['device_id']}",
                nest_age=submission["details"]["nest_age"],
                nest_type=submission["details"]["nest_type"],
                species=submission["details"]["species"],
            )
            encounter.encounter_type = encounter.get_encounter_type()

            if "nest" in submission:
                encounter.habitat = submission["nest"]["habitat"]
                encounter.disturbance = submission["nest"]["disturbance"]
                encounter.nest_tagged = submission["nest"]["nest_tagged"]
                encounter.logger_found = submission["nest"]["logger_found"]
                encounter.eggs_counted = submission["nest"]["eggs_counted"]
                encounter.hatchlings_measured = submission["nest"]["hatchlings_measured"]

            # Try to determine the encounter site & area.
            encounter.area = encounter.guess_area
            encounter.site = encounter.guess_site

            encounter.save()
            LOGGER.info(f"Created TurtleNestEncounter: {encounter}")

            #get any nest photos
            if "nest_photos" in submission:
                nest_photos = submission["nest_photos"]
                if nest_photos["photo_nest_1"]:
                        filename = nest_photos["photo_nest_1"]
                        LOGGER.info(f"Downloading {filename}")
                        attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                        photo = MediaAttachment(
                            encounter=encounter,
                            source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                            media_type="photograph",
                            title=f"Photo of nest {filename}",
                            attachment=attachment,
                        )
                        photo.save()
                        LOGGER.info(f"Created MediaAttachment {photo}")

                if nest_photos["photo_nest_2"]:
                        filename = nest_photos["photo_nest_2"]
                        LOGGER.info(f"Downloading {filename}")
                        attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                        photo = MediaAttachment(
                            encounter=encounter,
                            source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                            media_type="photograph",
                            title=f"Photo of nest {filename}",
                            attachment=attachment,
                        )
                        photo.save()
                        LOGGER.info(f"Created MediaAttachment {photo}")

                if nest_photos["photo_nest_3"]:
                        filename = nest_photos["photo_nest_3"]
                        LOGGER.info(f"Downloading {filename}")
                        attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                        photo = MediaAttachment(
                            encounter=encounter,
                            source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                            media_type="photograph",
                            title=f"Photo of nest {filename}",
                            attachment=attachment,
                        )
                        photo.save()
                        LOGGER.info(f"Created MediaAttachment {photo}")

            # TurtleNestObservation object
            if "egg_count" in submission:
                observation = submission["egg_count"]
                nest_observation = TurtleNestObservation(
                    encounter=encounter,
                    source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                    no_egg_shells=int(observation["no_egg_shells"]),
                    no_live_hatchlings=int(observation["no_live_hatchlings"]),
                    no_dead_hatchlings=int(observation["no_dead_hatchlings"]),
                    no_undeveloped_eggs=int(observation["no_undeveloped_eggs"]),
                    no_unhatched_eggs=int(observation["no_unhatched_eggs"]),
                    no_unhatched_term=int(observation["no_unhatched_term"]),
                    no_depredated_eggs=int(observation["no_depredated_eggs"]),
                    nest_depth_top=int(observation["nest_depth_top"]) if observation["nest_depth_top"] else None,
                    nest_depth_bottom=int(observation["nest_depth_bottom"]) if observation["nest_depth_bottom"] else None,
                    comments=observation["nest_excavation_comments"],
                )
                nest_observation.egg_count = nest_observation.no_egg_shells + nest_observation.no_undeveloped_eggs + nest_observation.no_unhatched_eggs + nest_observation.no_unhatched_term
                nest_observation.eggs_laid = nest_observation.egg_count and nest_observation.egg_count > 0
                nest_observation.save()
                LOGGER.info(f"Created TurtleNestObservation {nest_observation}")

                # Photo of eggs.
                filename = observation["photo_eggs"]
                LOGGER.info(f"Downloading {filename}")
                attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                photo = MediaAttachment(
                    encounter=encounter,
                    source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                    media_type="photograph",
                    title=f"Photo of nest eggs {filename}",
                    attachment=attachment,
                )
                photo.save()
                LOGGER.info(f"Created MediaAttachment {photo}")

            # TurtleNestDisturbanceObservation objects
            if "disturbance_observations" in submission:
                # Might be a list or a single object :|
                if not isinstance(submission["disturbance_observations"]["disturbance_observation"], list):
                    observations = [submission["disturbance_observations"]["disturbance_observation"]]
                else:
                    observations = submission["disturbance_observations"]["disturbance_observation"]

                for observation in observations:
                    disturbance = TurtleNestDisturbanceObservation(
                        encounter=encounter,
                        source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                        disturbance_cause=observation["disturbance_cause"],
                        disturbance_cause_confidence=observation["disturbance_cause_confidence"],
                        disturbance_severity=observation["disturbance_severity"],
                        comments=observation["comments"],
                    )
                    disturbance.save()
                    LOGGER.info(f"Created TurtleNestDisturbanceObservation: {disturbance}")

                    # All photos are associated with the parent Encounter, as another Observation subclass.
                    filename = observation["photo_disturbance"]
                    LOGGER.info(f"Downloading {filename}")
                    attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                    photo = MediaAttachment(
                        encounter=encounter,
                        source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                        media_type="photograph",
                        title=f"Photo of nest disturbance {filename}",
                        attachment=attachment,
                    )
                    photo.save()
                    LOGGER.info(f"Created MediaAttachment {photo}")

            # TurtleTrackObservation object.
            if "track_photos" in submission:
                track_observation = submission["track_photos"]
                if track_observation["photo_track_1"]:
                    filename = track_observation["photo_track_1"]
                    LOGGER.info(f"Downloading {filename}")
                    attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                    photo = MediaAttachment(
                        encounter=encounter,
                        source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                        media_type="photograph",
                        title=f"Photo of track {filename}",
                        attachment=attachment,
                    )
                    photo.save()
                    LOGGER.info(f"Created MediaAttachment {photo}")
                if track_observation["photo_track_2"]:
                    filename = track_observation["photo_track_2"]
                    LOGGER.info(f"Downloading {filename}")
                    attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                    photo = MediaAttachment(
                        encounter=encounter,
                        source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                        media_type="photograph",
                        title=f"Photo of track {filename}",
                        attachment=attachment,
                    )
                    photo.save()
                    LOGGER.info(f"Created MediaAttachment {photo}")
                if any([
                    track_observation["max_track_width_front"],
                    track_observation["max_track_width_rear"],
                    track_observation["carapace_drag_width"],
                    track_observation["step_length"],
                    track_observation["tail_pokes"],
                ]):
                    track_observation = TurtleTrackObservation(
                        encounter=encounter,
                        source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                        max_track_width_front=int(track_observation["max_track_width_front"]) if track_observation["max_track_width_front"] else None,
                        max_track_width_rear=int(track_observation["max_track_width_rear"]) if track_observation["max_track_width_rear"] else None,
                        carapace_drag_width=int(track_observation["carapace_drag_width"]) if track_observation["carapace_drag_width"] else None,
                        step_length=int(track_observation["step_length"]) if track_observation["step_length"] else None,
                        tail_pokes=track_observation["tail_pokes"],
                    )
                    track_observation.save()
                    LOGGER.info(f"Created TurtleTrackObservation {track_observation}")

            # NestTagObservation object.
            if "nest_tag" in submission:
                tag_observation = NestTagObservation(
                    encounter=encounter,
                    source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                    status=submission["nest_tag"]["tag_status"],
                    flipper_tag_id=submission["nest_tag"]["flipper_tag_id"],
                    date_nest_laid=datetime.strptime(submission["nest_tag"]["date_nest_laid"], "%Y-%m-%d").date() if submission["nest_tag"]["date_nest_laid"] else None,
                    tag_label=submission["nest_tag"]["tag_label"],
                    comments=submission["nest_tag"]["tag_comments"],
                )
                tag_observation.save()
                LOGGER.info(f"Created NestTagObservation {tag_observation}")
                # Tag photo
                if submission["nest_tag"]["photo_tag"]:
                    filename = submission["nest_tag"]["photo_tag"]
                    LOGGER.info(f"Downloading {filename}")
                    attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                    photo = MediaAttachment(
                        encounter=encounter,
                        source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                        media_type="photograph",
                        title=f"Photo of nest tag {filename}",
                        attachment=attachment,
                    )
                    photo.save()
                    LOGGER.info(f"Created MediaAttachment {photo}")

            # LoggerObservation objects
            if "loggers" in submission:
                loggers = submission["loggers"]["logger_details"]
                # Might be a list or a single object :|
                if not isinstance(loggers, list):
                    loggers = [loggers]

                for logger in loggers:
                    logger_observation = LoggerObservation(
                        encounter=encounter,
                        source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                        logger_type=logger["logger_type"],
                        deployment_status=logger["logger_status"],
                        logger_id=logger["logger_id"],
                        comments=logger["logger_comments"],
                    )
                    logger_observation.save()
                    LOGGER.info(f"Created LoggerObservation: {logger_observation}")

                    if logger["photo_logger"]:
                        filename = logger["photo_logger"]
                        LOGGER.info(f"Downloading {filename}")
                        attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                        photo = MediaAttachment(
                            encounter=encounter,
                            source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                            media_type="photograph",
                            title=f"Photo of logger {filename}",
                            attachment=attachment,
                        )
                        photo.save()
                        LOGGER.info(f"Created MediaAttachment {photo}")

            # HatchlingMorphometricObservation objects
            if "hatchling_measurements" in submission:
                hatchlings = submission["hatchling_measurements"]["hatchling_measurement"]
                # Might be a list or a single object :|
                if not isinstance(hatchlings, list):
                    hatchlings = [hatchlings]

                for hatchling in hatchlings:
                    hatchling_measurement = HatchlingMorphometricObservation(
                        encounter=encounter,
                        source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                        straight_carapace_length_mm=int(hatchling["straight_carapace_length_mm"]) if hatchling["straight_carapace_length_mm"] else None,
                        straight_carapace_width_mm=int(hatchling["straight_carapace_width_mm"]) if hatchling["straight_carapace_width_mm"] else None,
                        body_weight_g=int(hatchling["body_weight_g"]) if hatchling["body_weight_g"] else None,
                    )
                    hatchling_measurement.save()
                    LOGGER.info(f"Created HatchlingMorphometricObservation: {hatchling_measurement}")

            # TurtleHatchlingEmergenceObservation objects
            if "fan_angles" in submission:
                fan = submission["fan_angles"]

                # Seawards photo
                filename = fan["photo_hatchling_tracks_seawards"]
                LOGGER.info(f"Downloading {filename}")
                attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                photo = MediaAttachment(
                    encounter=encounter,
                    source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                    media_type="photograph",
                    title=f"Seawards photo of fan angles {filename}",
                    attachment=attachment,
                )
                photo.save()
                LOGGER.info(f"Created MediaAttachment {photo}")

                # Relief photo
                filename = fan["photo_hatchling_tracks_relief"]
                LOGGER.info(f"Downloading {filename}")
                attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                photo = MediaAttachment(
                    encounter=encounter,
                    source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                    media_type="photograph",
                    title=f"Relief photo of fan angles {filename}",
                    attachment=attachment,
                )
                photo.save()
                LOGGER.info(f"Created MediaAttachment {photo}")

                emergence_obs = TurtleHatchlingEmergenceObservation(
                    encounter=encounter,
                    source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                    bearing_to_water_degrees=float(fan["bearing_to_water_manual"]) if fan["bearing_to_water_manual"] else None,
                    bearing_leftmost_track_degrees=float(fan["leftmost_track_manual"]) if fan["leftmost_track_manual"] else None,
                    bearing_rightmost_track_degrees=float(fan["rightmost_track_manual"]) if fan["rightmost_track_manual"] else None,
                    no_tracks_main_group=int(fan["no_tracks_main_group"]) if fan["no_tracks_main_group"] else None,
                    no_tracks_main_group_min=int(fan["no_tracks_main_group_min"]) if fan["no_tracks_main_group_min"] else None,
                    no_tracks_main_group_max=int(fan["no_tracks_main_group_max"]) if fan["no_tracks_main_group_max"] else None,
                    outlier_tracks_present=fan["outlier_tracks_present"],
                    path_to_sea_comments=fan["path_to_sea_comments"],
                    hatchling_emergence_time_known=fan["hatchling_emergence_time_known"],
                    light_sources_present=fan["light_sources_present"],
                    cloud_cover_at_emergence=int(fan["cloud_cover_at_emergence"]) if fan["cloud_cover_at_emergence"] else None,
                )

                if "hatchling_emergence_time_group" in submission:
                    emergence = submission["hatchling_emergence_time_group"]
                    emergence_obs.hatchling_emergence_time = parser.isoparse(emergence["hatchling_emergence_time"])
                    emergence_obs.hatchling_emergence_time_accuracy = emergence["hatchling_emergence_time_source"]

                # TODO: path to sea record.
                emergence_obs.save()
                LOGGER.info(f"Created TurtleHatchlingEmergenceObservation {emergence_obs}")

                if "outlier_tracks" in submission:
                    # Might be a list or a single object :|
                    outliers = submission["outlier_tracks"]["outlier_track"]
                    if not isinstance(outliers, list):
                        outliers = [outliers]

                    for outlier in outliers:
                        outlier_obs = TurtleHatchlingEmergenceOutlierObservation(
                            encounter=encounter,
                            source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                            bearing_outlier_track_degrees=float(outlier["outlier_track_bearing_manual"]) if outlier["outlier_track_bearing_manual"] else None,
                            outlier_group_size=int(outlier["outlier_group_size"]) if outlier["outlier_group_size"] else None,
                            outlier_track_comment=outlier["outlier_track_comment"],
                        )
                        outlier_obs.save()
                        LOGGER.info(f"Created TurtleHatchlingEmergenceOutlierObservation {outlier_obs}")
                        # Outlier photo
                        filename = outlier["outlier_track_photo"]
                        LOGGER.info(f"Downloading {filename}")
                        attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                        photo = MediaAttachment(
                            encounter=encounter,
                            source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                            media_type="photograph",
                            title=f"Outlier track of fan angles {filename}",
                            attachment=attachment,
                        )
                        photo.save()
                        LOGGER.info(f"Created MediaAttachment {photo}")

                if "light_sources" in submission:
                    # Might be a list or a single object :|
                    light_sources = submission["light_sources"]["light_source"]
                    if not isinstance(light_sources, list):
                        light_sources = [light_sources]

                    for source in light_sources:
                        source_obs = LightSourceObservation(
                            encounter=encounter,
                            source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                            bearing_light_degrees=int(source["light_bearing_manual"]) if source["light_bearing_manual"] else None,
                            light_source_type=source["light_source_type"],
                            light_source_description=source["light_source_description"],
                        )
                        source_obs.save()
                        LOGGER.info(f"Created LightSourceObservation {source_obs}")

                        # Light source photo
                        filename = source["light_source_photo"]
                        LOGGER.info(f"Downloading {filename}")
                        attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                        photo = MediaAttachment(
                            encounter=encounter,
                            source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                            media_type="photograph",
                            title=f"Light source photo {filename}",
                            attachment=attachment,
                        )
                        photo.save()
                        LOGGER.info(f"Created MediaAttachment {photo}")
        except:
            LOGGER.exception(f"Exception during import of ODK {form_id} submission {instance_id}")


def import_turtle_track_or_nest_simple(form_id="beach_tracks_nest_simple", auth_headers=None):
    """Import submissions to the Simple turtle Track or Nest ODK form.
    Each submission should create:
    1 TurtleNestEncounter
    0-1 TurtleTrackObservation (unidentified species track)
    0+ TurtleNestDisturbanceObservation (disturbance/predation observations)
    """
    if not auth_headers:
        LOGGER.info("Downloading auth headers")
        auth_headers = get_auth_headers()
    project_id = settings.ODK_API_PROJECTID
    LOGGER.info(f"Downloading {form_id} submission data")
    submissions = get_form_submission_data(auth_headers, project_id, form_id)

    for submission in submissions:
        try:
            instance_id = submission['meta']['instanceID']
            if TurtleNestEncounter.objects.filter(source='odk', source_id=instance_id):
                continue  # Skip records already imported.

            # Try to match the reporter to an existing user. If not, create a new one.
            reporter = submission['reporter']
            user = get_user(reporter)

            #check for new forms
            if 'survey_start_time' in submission['details']:
                start_time = parser.isoparse(submission['details']['survey_start_time'])  # New forms allow editing of time in case submitted after the fact
            else:
                start_time = parser.isoparse(submission['start_time'])  # Old forms

            # Confusingly, TurtleNestEncounter objects cover nest, track and nest & track encounters.
            encounter = TurtleNestEncounter(
                status='imported',
                source='odk',
                source_id=instance_id,
                where=parse_geopoint(submission['details']['observed_at']),
                when=start_time,
                observer=user,
                reporter=user,
                comments=f'{submission["details"]["comments"]} (Device ID {submission["device_id"]})',
                #nest_age=submission['details']['nest_age'],
                nest_type=submission['details']['nest_type'],
                species=submission['details']['species'],
            )

            encounter.encounter_type = encounter.get_encounter_type()

            if 'details' in submission:
                encounter.habitat = submission['details']['habitat']
                if submission['details']['disturbance_cause']:
                    encounter.disturbance = "yes"
                else:
                    encounter.disturbance = "no"

            # Try to determine the encounter site & area.
            encounter.area = encounter.guess_area
            encounter.site = encounter.guess_site

            encounter.save()
            LOGGER.info(f'Created TurtleNestEncounter: {encounter}')
            # TurtleTrackObservation object.
            if 'track_photos' in submission['details']:
                track_observation = submission['details']['track_photos']
                if track_observation['photo_track_1']:
                    filename = track_observation['photo_track_1']
                    LOGGER.info(f"Downloading {filename}")
                    attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                    photo = MediaAttachment(
                        encounter=encounter,
                        source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                        media_type='photograph',
                        title=f'Photo of track {filename}',
                        attachment=attachment,
                    )
                    photo.save()
                    LOGGER.info(f'Created MediaAttachment {photo}')
                if track_observation['photo_track_2']:
                    filename = track_observation['photo_track_2']
                    LOGGER.info(f"Downloading {filename}")
                    attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                    photo = MediaAttachment(
                        encounter=encounter,
                        source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                        media_type='photograph',
                        title=f'Photo of track {filename}',
                        attachment=attachment,
                    )
                    photo.save()
                    LOGGER.info(f'Created MediaAttachment {photo}')
                if any([
                    track_observation['max_track_width_front'],
                    track_observation['tail_pokes'],
                ]):
                    track_observation = TurtleTrackObservation(
                        encounter=encounter,
                        source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                        max_track_width_front=int(track_observation['max_track_width_front']) if track_observation['max_track_width_front'] else None,
                        tail_pokes=track_observation['tail_pokes'],
                    )
                    track_observation.save()
                    LOGGER.info(f'Created TurtleTrackObservation {track_observation}')

            # For this simple form we are just assuming tracks are a low disturbance event, with no other information collected
            # these are retrieved as a space delimited string "fox cat dog"
            if submission['details']['disturbance_cause']:
                disturbances = submission['details']['disturbance_cause'].split()
                for disturbance in disturbances:
                    disturbance = TurtleNestDisturbanceObservation(
                        encounter=encounter,
                        source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                        disturbance_cause=disturbance,
                    )
                    disturbance.save()
                    LOGGER.info(f'Created TurtleNestDisturbanceObservation: {disturbance}')
        except:
            LOGGER.exception(f"Exception during import of ODK {form_id} submission {instance_id}")


def import_site_visit_start(form_id="site_visit_start", initial_duration_hr=8, auth_headers=None):
    """Import submissions to the Site Visit Start ODK form.
    Each submission should create one Survey.
    """
    if not auth_headers:
        LOGGER.info("Downloading auth headers")
        auth_headers = get_auth_headers()
    project_id = settings.ODK_API_PROJECTID
    LOGGER.info(f"Downloading {form_id} submission data")
    submissions = get_form_submission_data(auth_headers, project_id, form_id)

    for submission in submissions:
        try:
            instance_id = submission['meta']['instanceID']
            if Survey.objects.filter(source='odk', source_id=instance_id):
                continue  # Skip records already imported.

            # Try to match the reporter to an existing User. If not, create a new one.
            reporter = submission['reporter']
            user = get_user(reporter)

            visit = submission['site_visit']
            # Check for new forms
            if 'survey_start_time' in visit:
                start_time = parser.isoparse(visit['survey_start_time'])  # New forms allow editing of time in case submitted after the fact
            else:
                start_time = parser.isoparse(submission['start_time'])  # Old forms

            survey = Survey(
                status='imported',
                source='odk',
                source_id=instance_id,
                device_id=submission['device_id'],
                reporter=user,
                start_location=parse_geopoint(visit['location']),
                start_location_accuracy_m=parse_geopoint_accuracy(visit['location']),
                start_time=start_time,
            )

            # Guess the area & site, and plug in an initial estimated end_time.
            # The correct end_time will (hopefully) be gathered from the Site Visit End form.
            survey.area = survey.guess_area
            survey.site = survey.guess_site
            survey.end_time = survey.start_time + timedelta(hours=initial_duration_hr)

            # Set training surveys to non production
            if survey.site is not None:
                if 'training' in survey.site.name.lower() or 'testing' in survey.site.name.lower():
                    survey.production = False
                    LOGGER.info(survey.site.name + " set as not production.")

            # We need to save before we can modify the M2M field or set the label.
            survey.save()
            survey.label = survey.make_label()
            if visit['team']:
                team = visit['team'].split(',')
                for name in team:
                    name = name.strip()
                    if User.objects.filter(is_active=True, name__icontains=name).exists():
                        user = User.objects.filter(is_active=True, name__icontains=name).first()
                    else:  # Create a new user.
                        user = create_new_user(name)
                        LOGGER.info(f"Created new user {user}")
                    survey.team.add(user)

            LOGGER.info(f'Created Survey {survey}')

            if visit['site_conditions']:
                filename = visit['site_conditions']
                LOGGER.info(f"Downloading {filename}")
                attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                photo = SurveyMediaAttachment(
                    source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                    survey=survey,
                    media_type='photograph',
                    title=f'Photo of site visit start {filename}',
                    attachment=attachment,
                )
                photo.save()
                LOGGER.info(f'Created SurveyMediaAttachment {photo}')
        except:
            LOGGER.exception(f"Exception during import of ODK {form_id} submission {instance_id}")


def import_site_visit_end(form_id="site_visit_end", duration_hr=8, auth_headers=None):
    """Import submissions to the Site Visit End ODK form.
    This differs from the functions above, in that it tries to match on an existing
    Survey object and update its details.
    """
    if not auth_headers:
        LOGGER.info("Downloading auth headers")
        auth_headers = get_auth_headers()
    project_id = settings.ODK_API_PROJECTID
    LOGGER.info(f"Downloading {form_id} submission data")
    submissions = get_form_submission_data(auth_headers, project_id, form_id)

    for submission in submissions:
        try:
            instance_id = submission["meta"]["instanceID"]
            if Survey.objects.filter(source="odk", end_source_id=instance_id):
                continue  # Skip records already imported.

            # Try to match a site by location (just use the first one returned by the database).
            visit = submission["site_visit"]
            location = parse_geopoint(visit["location"])
            site = Area.objects.filter(area_type=Area.AREATYPE_SITE, geom__covers=location).first()

            if not site:
                # Send a warning to the admins to investigate & address.
                log = (f"Site Visit End form: unable to match a site for survey end at {location.wkt}")
                LOGGER.warning(log)
                continue

            # Try to match one (only) existing Survey object.
            # Algorithm: filter Surveys in the same Site, having a start_time not before end_time by
            # greater than `duration_hr` hours.
            if "survey_start_time" in visit:
                end_time = parser.isoparse(visit["survey_end_time"])  # New forms allow editing of time in case submitted after the fact
            else:
                end_time = parser.isoparse(submission["end_time"])  # Old forms

            start_time_earliest = end_time - timedelta(hours=duration_hr)
            surveys = Survey.objects.filter(
                site=site, start_time__lt=end_time, start_time__gte=start_time_earliest,
            )
            if surveys.count() != 1:
                log = (f"Site Visit End form: unable to match a single Survey (matched {surveys.count()})")
                LOGGER.warning(log)
                continue
            else:
                survey = surveys.first()

            survey.end_source_id = instance_id
            survey.end_location = location
            survey.end_location_accuracy_m = parse_geopoint_accuracy(visit["location"])
            survey.end_time = end_time
            survey.end_comments = visit["comments"]
            survey.save()

            LOGGER.info(f"Updated Survey {survey}")

            if visit["site_conditions"]:
                filename = visit["site_conditions"]
                LOGGER.info(f"Downloading {filename}")
                attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                photo = SurveyMediaAttachment(
                    source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                    survey=survey,
                    media_type="photograph",
                    title=f"Photo of site visit end {filename}",
                    attachment=attachment,
                )
                photo.save()
                LOGGER.info(f"Created SurveyMediaAttachment {photo}")
        except:
            LOGGER.exception(f"Exception during import of ODK {form_id} submission {instance_id}")


def import_marine_wildlife_incident(form_id="marine_wildlife_incident", auth_headers=None):
    """Import submissions to the Marine Wildlife Incident ODK form.
        Each submission should create:
            1 AnimalEncounter
            0-1 TurtleMorphometricObservation
            0+ TurtleDamageObservation
            0+ TagObservation
    """
    if not auth_headers:
        LOGGER.info("Downloading auth headers")
        auth_headers = get_auth_headers()
    project_id = settings.ODK_API_PROJECTID
    LOGGER.info(f"Downloading {form_id} submission data")
    submissions = get_form_submission_data(auth_headers, project_id, form_id)

    for submission in submissions:
        try:
            instance_id = submission['meta']['instanceID']
            if AnimalEncounter.objects.filter(source='odk', source_id=instance_id):
                continue  # Skip records already imported.

            # Try to match the reporter to an existing User. If not, create a new one.
            reporter = submission['reporter']
            user = get_user(reporter)

            site_visit = submission['site_visit']
            if site_visit['habitat']:
                habitat = site_visit['habitat']
            else:
                habitat = NA_VALUE
            encounter = AnimalEncounter(
                status='imported',
                source='odk',
                source_id=instance_id,
                where=parse_geopoint(site_visit['observed_at']),
                when=parser.isoparse(site_visit['incident_time']),
                observer=user,
                reporter=user,
                comments='',
                habitat=habitat,
            )
            if site_visit['observed_at_manual']:
                encounter.where = parse_geopoint(site_visit['observed_at_manual'])
            if site_visit['location_comment']:
                encounter.comments += site_visit['location_comment'] + '\n'
            if submission['animal_fate']['animal_fate_comment']:
                encounter.comments += submission['animal_fate']['animal_fate_comment']

            details = submission['details']
            encounter.taxon = details['taxon']
            encounter.species = details['species']
            encounter.sex = details['sex']
            encounter.maturity = details['maturity']

            status = submission['status']
            encounter.health = status['health']
            encounter.activity = status['activity']
            encounter.behaviour = status['behaviour']

            death = submission['death'] if submission['death'] else 'Unknown health'
            encounter.cause_of_death = death['cause_of_death'] if death else 'Not applicable'
            encounter.cause_of_death_confidence = death['cause_of_death_confidence'] if death else 'Not applicable'

            checks = submission['checks']
            encounter.checked_for_injuries = checks['checked_for_injuries']
            encounter.scanned_for_pit_tags = checks['scanned_for_pit_tags']
            encounter.checked_for_flipper_tags = checks['checked_for_flipper_tags']

            encounter.save()
            LOGGER.info(f'Created AnimalEncounter: {encounter}')

            # All photo uploads.
            if submission['site_visit']['photo_habitat']:
                filename = submission['site_visit']['photo_habitat']
                LOGGER.info(f'Downloading {filename}')
                attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                photo = MediaAttachment(
                    encounter=encounter,
                    source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                    media_type='photograph',
                    title=f'Habitate photo {filename}',
                    attachment=attachment,
                )
                photo.save()
                LOGGER.info(f'Created MediaAttachment {photo}')

            if submission['photos_turtle']['photo_carapace_top']:
                filename = submission['photos_turtle']['photo_carapace_top']
                LOGGER.info(f'Downloading {filename}')
                attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                photo = MediaAttachment(
                    encounter=encounter,
                    source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                    media_type='photograph',
                    title=f'Carapace photo {filename}',
                    attachment=attachment,
                )
                photo.save()
                LOGGER.info(f'Created MediaAttachment {photo}')

            if submission['photos_turtle']['photo_head_top']:
                filename = submission['photos_turtle']['photo_head_top']
                LOGGER.info(f'Downloading {filename}')
                attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                photo = MediaAttachment(
                    encounter=encounter,
                    source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                    media_type='photograph',
                    title=f'Head top photo {filename}',
                    attachment=attachment,
                )
                photo.save()
                LOGGER.info(f'Created MediaAttachment {photo}')

            if submission['photos_turtle']['photo_head_side']:
                filename = submission['photos_turtle']['photo_head_side']
                LOGGER.info(f'Downloading {filename}')
                attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                photo = MediaAttachment(
                    encounter=encounter,
                    source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                    media_type='photograph',
                    title=f'Head side photo {filename}',
                    attachment=attachment,
                )
                photo.save()
                LOGGER.info(f'Created MediaAttachment {photo}')

            if submission['photos_turtle']['photo_head_front']:
                filename = submission['photos_turtle']['photo_head_front']
                LOGGER.info(f'Downloading {filename}')
                attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                photo = MediaAttachment(
                    encounter=encounter,
                    source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                    media_type='photograph',
                    title=f'Head front photo {filename}',
                    attachment=attachment,
                )
                photo.save()
                LOGGER.info(f'Created MediaAttachment {photo}')

            if submission['habitat_photos']['photo_habitat_1']:
                filename = submission['habitat_photos']['photo_habitat_1']
                LOGGER.info(f'Downloading {filename}')
                attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                photo = MediaAttachment(
                    encounter=encounter,
                    source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                    media_type='photograph',
                    title=f'Scene photo {filename}',
                    attachment=attachment,
                )
                photo.save()
                LOGGER.info(f'Created MediaAttachment {photo}')

            if submission['habitat_photos']['photo_habitat_2']:
                filename = submission['habitat_photos']['photo_habitat_2']
                LOGGER.info(f'Downloading {filename}')
                attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                photo = MediaAttachment(
                    encounter=encounter,
                    source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                    media_type='photograph',
                    title=f'Scene photo {filename}',
                    attachment=attachment,
                )
                photo.save()
                LOGGER.info(f'Created MediaAttachment {photo}')

            if submission['habitat_photos']['photo_habitat_3']:
                filename = submission['habitat_photos']['photo_habitat_3']
                LOGGER.info(f'Downloading {filename}')
                attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                photo = MediaAttachment(
                    encounter=encounter,
                    source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                    media_type='photograph',
                    title=f'Scene photo {filename}',
                    attachment=attachment,
                )
                photo.save()
                LOGGER.info(f'Created MediaAttachment {photo}')

            # TurtleDamageObservation
            if 'damage_observations' in submission:
                damage_observations = submission['damage_observations']['damage_observation']
                # Might be a list or a single object :|
                if not isinstance(damage_observations, list):
                    damage_observations = [damage_observations]

                for obs in damage_observations:
                    damage_observation = TurtleDamageObservation(
                        encounter=encounter,
                        source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                        body_part=obs['body_part'],
                        damage_type=obs['damage_type'],
                        damage_age=obs['damage_age'],
                        description=obs['description'],
                    )
                    damage_observation.save()
                    LOGGER.info(f'Created TurtleDamageObservation: {damage_observation}')

                    if obs['photo_damage']:
                        filename = obs['photo_damage']
                        LOGGER.info(f'Downloading {filename}')
                        attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                        photo = MediaAttachment(
                            encounter=encounter,
                            source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                            media_type='photograph',
                            title=f'Animal damage photo {filename}',
                            attachment=attachment,
                        )
                        photo.save()
                        LOGGER.info(f'Created MediaAttachment {photo}')

            # TagObservation
            if 'tag_observations' in submission:
                tag_observations = submission['tag_observations']['tag_observation']
                # Might be a list or a single object :|
                if not isinstance(tag_observations, list):
                    tag_observations = [tag_observations]

                for obs in tag_observations:
                    tag_observation = TagObservation(
                        encounter=encounter,
                        source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                        tag_type=obs['tag_type'],
                        tag_location=obs['tag_location'],
                        name=obs['tag_id'],
                        status=obs['tag_status'] if obs['tag_status'] else 'resighted',
                        recorder=user,
                        comments=obs['tag_comment'],
                    )
                    tag_observation.save()
                    LOGGER.info(f'Created TagObservation: {tag_observation}')

                    if obs['tag_photo']:
                        filename = obs['tag_photo']
                        LOGGER.info(f'Downloading {filename}')
                        attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                        photo = MediaAttachment(
                            encounter=encounter,
                            source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                            media_type='photograph',
                            title=f'Tag photo {filename}',
                            attachment=attachment,
                        )
                        photo.save()
                        LOGGER.info(f'Created MediaAttachment {photo}')

            # TurtleMorphometricObservation
            morph = submission['morphometrics']
            if any([
                morph['curved_carapace_length_mm'],
                morph['curved_carapace_width_mm'],
                morph['tail_length_carapace_mm'],
                morph['maximum_head_width_mm'],
            ]):
                morphometric_obs = TurtleMorphometricObservation(
                    encounter=encounter,
                    source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                    curved_carapace_length_mm=morph['curved_carapace_length_mm'],
                    curved_carapace_length_accuracy=morph['curved_carapace_length_accuracy'],
                    curved_carapace_width_mm=morph['curved_carapace_width_mm'],
                    curved_carapace_width_accuracy=morph['curved_carapace_width_accuracy'],
                    tail_length_carapace_mm=morph['tail_length_carapace_mm'],
                    tail_length_carapace_accuracy=morph['tail_length_carapace_accuracy'],
                    maximum_head_width_mm=morph['maximum_head_width_mm'],
                    maximum_head_width_accuracy=morph['maximum_head_width_accuracy'],
                )
                morphometric_obs.save()
                LOGGER.info(f'Created TurtleMorphometricObservation: {morphometric_obs}')
        except:
            LOGGER.exception(f"Exception during import of ODK {form_id} submission {instance_id}")


def import_turtle_sighting(form_id="turtle_sighting", auth_headers=None):
    """Import submissions to the Turtle Sighting ODK form.
    Each submission should create one AnimalEncounter.
    """
    if not auth_headers:
        LOGGER.info("Downloading auth headers")
        auth_headers = get_auth_headers()
    project_id = settings.ODK_API_PROJECTID
    LOGGER.info(f"Downloading {form_id} submission data")
    submissions = get_form_submission_data(auth_headers, project_id, form_id)

    for submission in submissions:
        try:
            instance_id = submission['meta']['instanceID']

            if AnimalEncounter.objects.filter(source='odk', source_id=instance_id):
                continue  # Skip records already imported.

            # Try to match the reporter to an existing User. If not, create a new one.
            reporter = submission['reporter']
            user = get_user(reporter)

            sighting = submission['encounter']
            encounter = AnimalEncounter(
                status='imported',
                source='odk',
                source_id=instance_id,
                where=parse_geopoint(sighting['observed_at']),
                when=parser.isoparse(submission['start_time']),
                observer=user,
                reporter=user,
                taxon='Cheloniidae',
                species=sighting['species'],
                maturity=sighting['maturity'],
                comments=sighting['comments'],
                encounter_type='other',
            )
            if sighting['interaction']:
                interaction_choices = dict(TURTLE_INTERACTION_CHOICES)
                encounter.behaviour = interaction_choices.get(sighting['interaction'], None)

            encounter.save()

            LOGGER.info(f"Created AnimalEncounter {encounter}")
        except:
            LOGGER.exception(f"Exception during import of ODK {form_id} submission {instance_id}")


def import_predator_or_disturbance(form_id="predator_or_disturbance", auth_headers=None):
    """Import submissions to the Predator or Disturbance ODK form.
    Each submission should create:
    1 Encounter (type: disturbance)
    1+ DisturbanceObservation (disturbance/predator observation)
    """
    if not auth_headers:
        LOGGER.info("Downloading auth headers")
        auth_headers = get_auth_headers()
    project_id = settings.ODK_API_PROJECTID
    LOGGER.info(f"Downloading {form_id} submission data")
    submissions = get_form_submission_data(auth_headers, project_id, form_id)

    for submission in submissions:
        try:
            instance_id = submission["meta"]["instanceID"]
            if Encounter.objects.filter(source="odk", source_id=instance_id):
                continue  # Skip records already imported.

            # Try to match the reporter to an existing user. If not, create a new one.
            reporter = submission["reporter"]
            user = get_user(reporter)
            start = parser.isoparse(submission["start_time"])
            disturbance = submission["disturbance"]

            encounter = Encounter(
                status="imported",
                source="odk",
                source_id=instance_id,
                where=parse_geopoint(disturbance["location"]),
                when=start,
                observer=user,
                reporter=user,
                encounter_type=Encounter.ENCOUNTER_DISTURBANCE,
            )
            # Try to determine the encounter site & area.
            encounter.area = encounter.guess_area
            encounter.site = encounter.guess_site
            encounter.save()
            LOGGER.info(f"Created Encounter: {encounter}")

            # MediaAttachment (photo).
            filename = disturbance["photo"]
            LOGGER.info(f"Downloading {filename}")
            attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
            photo = MediaAttachment(
                encounter=encounter,
                source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                media_type="photograph",
                title=f"Disturbance/predator photo {filename}",
                attachment=attachment,
            )
            photo.save()
            LOGGER.info(f"Created MediaAttachment {photo}")

            # DisturbanceObservation object.
            disturbance_observation = DisturbanceObservation(
                encounter=encounter,
                source=LegacySourceMixin.SOURCE_DIGITAL_CAPTURE_ODK,
                disturbance_cause=disturbance["cause"],
                disturbance_cause_confidence=disturbance["confidence"],
                comments=disturbance["comments"],
            )
            disturbance_observation.save()
            LOGGER.info(f"Created DisturbanceObservation {disturbance_observation}")
        except:
            LOGGER.exception(f"Exception during import of ODK {form_id} submission {instance_id}")
