from datetime import datetime, timedelta
from dateutil import parser
from django.conf import settings
from wastd.odk import get_auth_headers, get_form_submission_data, parse_geopoint, parse_geopoint_accuracy, get_submission_attachment
from users.models import User
from .models import (
    TurtleNestEncounter,
    TurtleNestObservation,
    TurtleNestDisturbanceObservation,
    TurtleTrackObservation,
    NestTagObservation,
    LoggerObservation,
    HatchlingMorphometricObservation,
    TurtleHatchlingEmergenceObservation,
    TurtleHatchlingEmergenceOutlierObservation,
    LightSourceObservation,
    MediaAttachment,
    Survey,
    SurveyMediaAttachment,
    Area,
)
from .utils import guess_area, guess_site


def import_turtle_track_or_nest(form_id="turtle_track_or_nest"):
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
    print("Downloading auth headers")
    auth_headers = get_auth_headers()
    project_id = settings.ODK_API_PROJECTID
    print("Downloading submission data")
    submissions = get_form_submission_data(auth_headers, project_id, form_id)

    for submission in submissions:
        instance_id = submission['meta']['instanceID']
        if TurtleNestEncounter.objects.filter(source='odk', source_id=instance_id):
            print(f"Skipped {instance_id}")
            continue  # Skip records already imported.

        # Try to match the reporter to an existing User. If not, create a new one.
        reporter = submission['reporter'].strip()
        if User.objects.filter(name__icontains=reporter).exists() and User.objects.filter(name__icontains=reporter).count() == 1:
            user = User.objects.get(name__icontains=reporter)
        else:  # Create a new user.
            username = reporter.lower().replace(' ', '_')
            user = User.objects.create(name=reporter, username=username)
            user.set_unusable_password()
            print(f"Created new user {user}")

        # Confusingly, TurtleNestEncounter objects cover both nest, track and nest & nest encounters.
        encounter = TurtleNestEncounter(
            status='imported',
            source='odk',
            source_id=instance_id,
            where=parse_geopoint(submission['details']['observed_at']),
            when=parser.isoparse(submission['start_time']),
            observer=user,
            reporter=user,
            comments=f'Device ID {submission["device_id"]}',
            nest_age=submission['details']['nest_age'],
            nest_type=submission['details']['nest_type'],
            species=submission['details']['species'],
        )

        if submission['details']['nest_type'] in ['false-crawl', 'track-unsure', 'track-not-assessed']:
            encounter.encounter_type = 'tracks'
        else:
            encounter.encounter_type = 'nest'

        if 'nest' in submission:
            encounter.habitat = submission['nest']['habitat']
            encounter.disturbance = submission['nest']['disturbance']
            encounter.nest_tagged = submission['nest']['nest_tagged']
            encounter.logger_found = submission['nest']['logger_found']
            encounter.eggs_counted = submission['nest']['eggs_counted']
            encounter.hatchlings_measured = submission['nest']['hatchlings_measured']

        # Try to determine the encounter site & area.
        encounter.area = encounter.guess_area
        encounter.site = encounter.guess_site

        encounter.save()
        print(f'Created TurtleNestEncounter: {encounter}')

        # TurtleNestObservation object
        if 'egg_count' in submission:
            observation = submission['egg_count']
            nest_observation = TurtleNestObservation(
                encounter=encounter,
                no_egg_shells=int(observation['no_egg_shells']),
                no_live_hatchlings=int(observation['no_live_hatchlings']),
                no_dead_hatchlings=int(observation['no_dead_hatchlings']),
                no_undeveloped_eggs=int(observation['no_undeveloped_eggs']),
                no_unhatched_eggs=int(observation['no_unhatched_eggs']),
                no_unhatched_term=int(observation['no_unhatched_term']),
                no_depredated_eggs=int(observation['no_depredated_eggs']),
                nest_depth_top=int(observation['nest_depth_top']) if observation['nest_depth_top'] else None,
                nest_depth_bottom=int(observation['nest_depth_bottom']) if observation['nest_depth_bottom'] else None,
                comments=observation['nest_excavation_comments'],
            )
            nest_observation.egg_count = nest_observation.no_egg_shells + nest_observation.no_undeveloped_eggs + nest_observation.no_unhatched_eggs + nest_observation.no_unhatched_term
            nest_observation.eggs_laid = nest_observation.egg_count and nest_observation.egg_count > 0
            nest_observation.save()
            print(f'Created TurtleNestObservation {nest_observation}')

            # Photo of eggs.
            filename = observation['photo_eggs']
            print(f"Downloading {filename}")
            attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
            photo = MediaAttachment(
                encounter=encounter,
                media_type='photograph',
                title=f'Photo of nest eggs {filename}',
                attachment=attachment,
            )
            photo.save()
            print(f'Created MediaAttachment {photo}')

        # TurtleNestDisturbanceObservation objects
        if 'disturbance_observations' in submission:
            observations = submission['disturbance_observations']['disturbance_observation']
            for observation in observations:
                disturbance = TurtleNestDisturbanceObservation(
                    encounter=encounter,
                    disturbance_cause=observation['disturbance_cause'],
                    disturbance_cause_confidence=observation['disturbance_cause_confidence'],
                    disturbance_severity=observation['disturbance_severity'],
                    comments=observation['comments'],
                )
                disturbance.save()
                print(f'Created TurtleNestDisturbanceObservation: {disturbance}')

                # All photos are associated with the parent Encounter, as another Observation subclass.
                filename = observation['photo_disturbance']
                print(f"Downloading {filename}")
                attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                photo = MediaAttachment(
                    encounter=encounter,
                    media_type='photograph',
                    title=f'Photo of nest disturbance {filename}',
                    attachment=attachment,
                )
                photo.save()
                print(f'Created MediaAttachment {photo}')

        # TurtleTrackObservation object.
        if 'track_photos' in submission:
            track_observation = submission['track_photos']
            if track_observation['photo_track_1']:
                filename = track_observation['photo_track_1']
                print(f"Downloading {filename}")
                attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                photo = MediaAttachment(
                    encounter=encounter,
                    media_type='photograph',
                    title=f'Photo of track {filename}',
                    attachment=attachment,
                )
                photo.save()
                print(f'Created MediaAttachment {photo}')
            if track_observation['photo_track_2']:
                filename = track_observation['photo_track_2']
                print(f"Downloading {filename}")
                attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                photo = MediaAttachment(
                    encounter=encounter,
                    media_type='photograph',
                    title=f'Photo of track {filename}',
                    attachment=attachment,
                )
                photo.save()
                print(f'Created MediaAttachment {photo}')
            if any([
                track_observation['max_track_width_front'],
                track_observation['max_track_width_rear'],
                track_observation['carapace_drag_width'],
                track_observation['step_length'],
                track_observation['tail_pokes'],
            ]):
                track_observation = TurtleTrackObservation(
                    encounter=encounter,
                    max_track_width_front=int(track_observation['max_track_width_front']) if track_observation['max_track_width_front'] else None,
                    max_track_width_rear=int(track_observation['max_track_width_rear']) if track_observation['max_track_width_rear'] else None,
                    carapace_drag_width=int(track_observation['carapace_drag_width']) if track_observation['carapace_drag_width'] else None,
                    step_length=int(track_observation['step_length']) if track_observation['step_length'] else None,
                    tail_pokes=track_observation['tail_pokes'],
                )
                print(f'Created TurtleTrackObservation {track_observation}')

        # NestTagObservation object.
        if 'nest_tag' in submission:
            tag_observation = NestTagObservation(
                encounter=encounter,
                status=submission['nest_tag']['tag_status'],
                flipper_tag_id=submission['nest_tag']['flipper_tag_id'],
                date_nest_laid=datetime.strptime(submission['nest_tag']['date_nest_laid'], '%Y-%m-%d').date() if submission['nest_tag']['date_nest_laid'] else None,
                tag_label=submission['nest_tag']['tag_label'],
                comments=submission['nest_tag']['tag_comments'],
            )
            tag_observation.save()
            print(f'Created NestTagObservation {tag_observation}')
            # Tag photo
            if submission['nest_tag']['photo_tag']:
                filename = submission['nest_tag']['photo_tag']
                print(f"Downloading {filename}")
                attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                photo = MediaAttachment(
                    encounter=encounter,
                    media_type='photograph',
                    title=f'Photo of nest tag {filename}',
                    attachment=attachment,
                )
                photo.save()
                print(f'Created MediaAttachment {photo}')

        # LoggerObservation objects
        if 'loggers' in submission:
            loggers = submission['loggers']['logger_details']
            # Might be a list or a single object :|
            if isinstance(loggers, list):
                for logger in loggers:
                    logger_observation = LoggerObservation(
                        encounter=encounter,
                        logger_type=logger['logger_type'],
                        deployment_status=logger['logger_status'],
                        logger_id=logger['logger_id'],
                        comments=logger['logger_comments'],
                    )
                    logger_observation.save()
                    print(f'Created LoggerObservation: {logger_observation}')

                    if logger['photo_logger']:
                        filename = logger['photo_logger']
                        print(f'Downloading {filename}')
                        attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                        photo = MediaAttachment(
                            encounter=encounter,
                            media_type='photograph',
                            title=f'Photo of logger {filename}',
                            attachment=attachment,
                        )
                        photo.save()
                        print(f'Created MediaAttachment {photo}')
            else:
                # Address `loggers` as an object, instead of iterating on it.
                logger_observation = LoggerObservation(
                    encounter=encounter,
                    logger_type=loggers['logger_type'],
                    deployment_status=loggers['logger_status'],
                    logger_id=loggers['logger_id'],
                    comments=loggers['logger_comments'],
                )
                logger_observation.save()
                print(f'Created LoggerObservation: {logger_observation}')

                if loggers['photo_logger']:
                    filename = loggers['photo_logger']
                    print(f'Downloading {filename}')
                    attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                    photo = MediaAttachment(
                        encounter=encounter,
                        media_type='photograph',
                        title=f'Photo of logger {filename}',
                        attachment=attachment,
                    )
                    photo.save()
                    print(f'Created MediaAttachment {photo}')

        # HatchlingMorphometricObservation objects
        if 'hatchling_measurements' in submission:
            hatchlings = submission['hatchling_measurements']['hatchling_measurement']
            # Might be a list or a single object :|
            if isinstance(hatchlings, list):
                for hatchling in hatchlings:
                    hatchling_measurement = HatchlingMorphometricObservation(
                        encounter=encounter,
                        straight_carapace_length_mm=int(hatchling['straight_carapace_length_mm']) if hatchling['straight_carapace_length_mm'] else None,
                        straight_carapace_width_mm=int(hatchling['straight_carapace_width_mm']) if hatchling['straight_carapace_width_mm'] else None,
                        body_weight_g=int(hatchling['body_weight_g']) if hatchling['body_weight_g'] else None,
                    )
                    hatchling_measurement.save()
                    print(f'Created HatchlingMorphometricObservation: {hatchling_measurement}')
            else:
                # Address `hatchlings` as an object, instead of iterating on it.
                hatchling_measurement = HatchlingMorphometricObservation(
                    encounter=encounter,
                    straight_carapace_length_mm=int(hatchlings['straight_carapace_length_mm']) if hatchlings['straight_carapace_length_mm'] else None,
                    straight_carapace_width_mm=int(hatchlings['straight_carapace_width_mm']) if hatchlings['straight_carapace_width_mm'] else None,
                    body_weight_g=int(hatchlings['body_weight_g']) if hatchlings['body_weight_g'] else None,
                )
                hatchling_measurement.save()
                print(f'Created HatchlingMorphometricObservation: {hatchling_measurement}')

        # TurtleHatchlingEmergenceObservation objects
        if 'fan_angles' in submission:
            fan = submission['fan_angles']

            # Seawards photo
            filename = fan['photo_hatchling_tracks_seawards']
            print(f'Downloading {filename}')
            attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
            photo = MediaAttachment(
                encounter=encounter,
                media_type='photograph',
                title=f'Seawards photo of fan angles {filename}',
                attachment=attachment,
            )
            photo.save()
            print(f'Created MediaAttachment {photo}')

            # Relief photo
            filename = fan['photo_hatchling_tracks_relief']
            print(f'Downloading {filename}')
            attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
            photo = MediaAttachment(
                encounter=encounter,
                media_type='photograph',
                title=f'Relief photo of fan angles {filename}',
                attachment=attachment,
            )
            photo.save()
            print(f'Created MediaAttachment {photo}')

            emergence_obs = TurtleHatchlingEmergenceObservation(
                encounter=encounter,
                bearing_to_water_degrees=int(fan['bearing_to_water_manual']) if fan['bearing_to_water_manual'] else None,
                bearing_leftmost_track_degrees=int(fan['leftmost_track_manual']) if fan['leftmost_track_manual'] else None,
                bearing_rightmost_track_degrees=int(fan['rightmost_track_manual']) if fan['rightmost_track_manual'] else None,
                no_tracks_main_group=int(fan['no_tracks_main_group']) if fan['no_tracks_main_group'] else None,
                no_tracks_main_group_min=int(fan['no_tracks_main_group_min']) if fan['no_tracks_main_group_min'] else None,
                no_tracks_main_group_max=int(fan['no_tracks_main_group_max']) if fan['no_tracks_main_group_max'] else None,
                outlier_tracks_present=fan['outlier_tracks_present'],
                path_to_sea_comments=fan['path_to_sea_comments'],
                hatchling_emergence_time_known=fan['hatchling_emergence_time_known'],
                light_sources_present=fan['light_sources_present'],
                cloud_cover_at_emergence=int(fan['cloud_cover_at_emergence']) if fan['cloud_cover_at_emergence'] else None,
            )

            if 'hatchling_emergence_time_group' in submission:
                emergence = submission['hatchling_emergence_time_group']
                emergence_obs.hatchling_emergence_time = parser.isoparse(emergence['hatchling_emergence_time'])
                emergence_obs.hatchling_emergence_time_accuracy = emergence['hatchling_emergence_time_source']

            # TODO: path to sea record.
            emergence_obs.save()
            print(f'Created TurtleHatchlingEmergenceObservation {emergence_obs}')

            if 'outlier_tracks' in submission:
                # Might be a list or a single object :|
                outliers = submission['outlier_tracks']['outlier_track']
                if isinstance(outliers, list):
                    for outlier in outliers:
                        outlier_obs = TurtleHatchlingEmergenceOutlierObservation(
                            encounter=encounter,
                            bearing_outlier_track_degrees=int(outlier['outlier_track_bearing_manual']) if outlier['outlier_track_bearing_manual'] else None,
                            outlier_group_size=int(outlier['outlier_group_size']) if outlier['outlier_group_size'] else None,
                            outlier_track_comment=outlier['outlier_track_comment'],
                        )
                        outlier_obs.save()
                        print(f'Created TurtleHatchlingEmergenceOutlierObservation {outlier_obs}')
                        # Outlier photo
                        filename = outlier['outlier_track_photo']
                        print(f'Downloading {filename}')
                        attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                        photo = MediaAttachment(
                            encounter=encounter,
                            media_type='photograph',
                            title=f'Outlier track of fan angles {filename}',
                            attachment=attachment,
                        )
                        photo.save()
                        print(f'Created MediaAttachment {photo}')
                else:
                    outlier_obs = TurtleHatchlingEmergenceOutlierObservation(
                        encounter=encounter,
                        bearing_outlier_track_degrees=int(outliers['outlier_track_bearing_manual']) if outliers['outlier_track_bearing_manual'] else None,
                        outlier_group_size=int(outliers['outlier_group_size']) if outliers['outlier_group_size'] else None,
                        outlier_track_comment=outliers['outlier_track_comment'],
                    )
                    outlier_obs.save()
                    print(f'Created TurtleHatchlingEmergenceOutlierObservation {outlier_obs}')
                    # Outlier photo
                    filename = outliers['outlier_track_photo']
                    print(f'Downloading {filename}')
                    attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                    photo = MediaAttachment(
                        encounter=encounter,
                        media_type='photograph',
                        title=f'Outlier track of fan angles {filename}',
                        attachment=attachment,
                    )
                    photo.save()
                    print(f'Created MediaAttachment {photo}')

            if 'light_sources' in submission:
                # Might be a list or a single object :|
                light_sources = submission['light_sources']['light_source']
                if isinstance(light_sources, list):
                    for source in light_sources:
                        source_obs = LightSourceObservation(
                            encounter=encounter,
                            bearing_light_degrees=int(source['light_bearing_manual']) if source['light_bearing_manual'] else None,
                            light_source_type=source['light_source_type'],
                            light_source_description=source['light_source_description'],
                        )
                        source_obs.save()
                        print(f'Created LightSourceObservation {source_obs}')

                        # Light source photo
                        filename = source['light_source_photo']
                        print(f'Downloading {filename}')
                        attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                        photo = MediaAttachment(
                            encounter=encounter,
                            media_type='photograph',
                            title=f'Light source photo {filename}',
                            attachment=attachment,
                        )
                        photo.save()
                        print(f'Created MediaAttachment {photo}')
                else:
                    source_obs = LightSourceObservation(
                        encounter=encounter,
                        bearing_light_degrees=int(light_sources['light_bearing_manual']) if light_sources['light_bearing_manual'] else None,
                        light_source_type=light_sources['light_source_type'],
                        light_source_description=light_sources['light_source_description'],
                    )
                    source_obs.save()
                    print(f'Created LightSourceObservation {source_obs}')

                    # Light source photo
                    filename = light_sources['light_source_photo']
                    print(f'Downloading {filename}')
                    attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
                    photo = MediaAttachment(
                        encounter=encounter,
                        media_type='photograph',
                        title=f'Light source photo {filename}',
                        attachment=attachment,
                    )
                    photo.save()
                    print(f'Created MediaAttachment {photo}')


def import_site_visit_start(form_id="site_visit_start"):
    """Import submissions to the Site Visit Start ODK form.
    Each submission should create one Survey.
    """
    print("Downloading auth headers")
    auth_headers = get_auth_headers()
    project_id = settings.ODK_API_PROJECTID
    print("Downloading submission data")
    submissions = get_form_submission_data(auth_headers, project_id, form_id)

    for submission in submissions:
        instance_id = submission['meta']['instanceID']
        if Survey.objects.filter(source='odk', source_id=instance_id):
            print(f"Skipped {instance_id}")
            continue  # Skip records already imported.

        # Try to match the reporter to an existing User. If not, create a new one.
        reporter = submission['reporter'].strip()
        if User.objects.filter(name__icontains=reporter).exists() and User.objects.filter(name__icontains=reporter).count() == 1:
            user = User.objects.get(name__icontains=reporter)
        else:  # Create a new user.
            username = reporter.lower().replace(' ', '_')
            user = User.objects.create(name=reporter, username=username)
            user.set_unusable_password()
            print(f"Created new user {user}")

        visit = submission['site_visit']
        survey = Survey(
            status='imported',
            source='odk',
            source_id=instance_id,
            device_id=submission['device_id'],
            reporter=user,
            start_location=parse_geopoint(visit['location']),
            start_location_accuracy_m=parse_geopoint_accuracy(visit['location']),
            start_time=parser.isoparse(submission['start_time']),
            start_comments=visit['comments'],
        )
        survey.area = guess_area(survey)
        survey.site = guess_site(survey)

        # We need to save before we can modify the M2M field or set the label.
        survey.save()
        survey.label = survey.make_label
        if visit['team']:
            team = visit['team'].split(',')
            for name in team:
                name = name.strip()
                if User.objects.filter(name__icontains=name).exists() and User.objects.filter(name__icontains=name).count() == 1:
                    user = User.objects.get(name__icontains=name)
                else:  # Create a new user.
                    username = name.lower().replace(' ', '_')
                    user = User.objects.create(name=name, username=username)
                    user.set_unusable_password()
                    print(f"Created new user {user}")
                survey.team.add(user)

        print(f'Created Survey {survey}')

        if visit['site_conditions']:
            filename = visit['site_conditions']
            print(f"Downloading {filename}")
            attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
            photo = SurveyMediaAttachment(
                survey=survey,
                media_type='photograph',
                title=f'Photo of site visit start {filename}',
                attachment=attachment,
            )
            photo.save()
            print(f'Created SurveyMediaAttachment {photo}')


def import_site_visit_end(form_id="site_visit_end", duration_hr=8):
    """Import submissions to the Site Visit End ODK form.
    This differs from the functions above, in that it tries to match on an existing
    Survey object and update its details.
    """
    print("Downloading auth headers")
    auth_headers = get_auth_headers()
    project_id = settings.ODK_API_PROJECTID
    print("Downloading submission data")
    submissions = get_form_submission_data(auth_headers, project_id, form_id)

    for submission in submissions:
        instance_id = submission['meta']['instanceID']
        if Survey.objects.filter(source='odk', end_source_id=instance_id):
            print(f"Skipped {instance_id}")
            continue  # Skip records already imported.

        # Try to match the reporter to an existing User. If no match, skip record.
        reporter = submission['reporter'].strip()
        if User.objects.filter(name__icontains=reporter).exists() and User.objects.filter(name__icontains=reporter).count() == 1:
            user = User.objects.get(name__icontains=reporter)
        else:
            continue

        visit = submission['site_visit']
        location = parse_geopoint(visit['location'])
        end_time = parser.isoparse(submission['end_time'])
        start_time_earliest = end_time - timedelta(hours=duration_hr)
        site = Area.objects.filter(area_type=Area.AREATYPE_SITE, geom__covers=location).first()
        if not site:
            #print("Unable to match a suitable site")
            continue

        # Try to match one (only) existing Survey object.
        # Algorithm: filter Surveys in the same Site, having the same reporter, having
        # start_time before end_time by no greater than 8 hours.
        surveys = Survey.objects.filter(
            reporter=user, site=site, start_time__lt=end_time, start_time__gte=start_time_earliest,
        )
        if surveys.count() != 1:
            print(f"Unable to match a Survey (matched {surveys.count()})")
            continue
        else:
            survey = surveys.first()

        survey.end_source_id = instance_id
        survey.end_location = location
        survey.end_location_accuracy_m = parse_geopoint_accuracy(visit['location'])
        survey.end_time = end_time
        survey.end_comments = visit['comments']
        survey.save()

        print(f'Updated Survey {survey}')

        if visit['site_conditions']:
            filename = visit['site_conditions']
            print(f"Downloading {filename}")
            attachment = get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename)
            photo = SurveyMediaAttachment(
                survey=survey,
                media_type='photograph',
                title=f'Photo of site visit end {filename}',
                attachment=attachment,
            )
            photo.save()
            print(f'Created SurveyMediaAttachment {photo}')
