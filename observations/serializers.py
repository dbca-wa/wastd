from django.conf import settings
from typing import Dict, Any


def area_serializer(obj) -> Dict[str, Any]:
    return {
        'type': 'Feature',
        'geometry': {
            'type': 'Polygon',
            'coordinates': obj.geom.coords,
        },
        'properties': {
            'id': obj.pk,
            'area_type': obj.get_area_type_display(),
            'name': obj.name,
            'w2_location_code': obj.w2_location_code,
            'w2_place_code': obj.w2_place_code,
            'length_surveyed_m': obj.length_surveyed_m,
            'length_survey_roundtrip_m': obj.length_survey_roundtrip_m,
        },
    }


class AreaSerializer(object):
    def serialize(obj):
        return area_serializer(obj)


def survey_serializer(obj) -> Dict[str, Any]:
    if obj.start_location:
        geometry = {
            'type': 'Point',
            'coordinates': [obj.start_location.x, obj.start_location.y],
        }
    else:
        geometry = None
    return {
        'type': 'Feature',
        'geometry': geometry,
        'properties': {
            'id': obj.pk,
            'status': obj.get_status_display(),
            'source': obj.get_source_display(),
            'source_id': obj.source_id,
            'device_id': obj.device_id,
            'area_id': obj.area.pk if obj.area else None,
            'site_id': obj.site.pk if obj.site else None,
            'reporter_id': obj.reporter.pk if obj.reporter else None,
            'start_location_accuracy_m': obj.start_location_accuracy_m,
            'start_time': obj.start_time.astimezone(settings.TZ).isoformat(),
            'start_photo': settings.MEDIA_URL + obj.start_photo.name if obj.start_photo else None,  # FIXME: absolute URL
            'start_comments': obj.start_comments,
            'end_source_id': obj.end_source_id,
            'end_device_id': obj.end_device_id,
            'end_location': obj.end_location.wkt if obj.end_location else None,
            'end_location_accuracy_m': obj.end_location_accuracy_m,
            'end_time': obj.end_time.astimezone(settings.TZ).isoformat(),
            'end_photo': settings.MEDIA_URL + obj.end_photo.name if obj.end_photo else None,  # FIXME: absolute URL
            'end_comments': obj.end_comments,
            'production': obj.production,
            'team': [user.pk for user in obj.team.all()],
            'label': obj.label,
        },
    }


class SurveySerializer(object):
    def serialize(obj):
        return survey_serializer(obj)


def survey_media_attachment_serializer(obj) -> Dict[str, Any]:
    return {
        'type': 'Feature',
        'properties': {
            'id': obj.pk,
            'source': obj.survey.get_source_display(),
            'source_id': obj.survey.source_id,
            'survey_id': obj.survey.pk,
            'media_type': obj.get_media_type_display(),
            'title': obj.title,
            'attachment': settings.MEDIA_URL + obj.attachment.name,  # FIXME: absolute URL
        },
    }


class SurveyMediaAttachmentSerializer(object):
    def serialize(obj):
        return survey_media_attachment_serializer(obj)


def encounter_serializer(obj) -> Dict[str, Any]:
    """This serializer is the equivalent of /encounters-fast and /encounters-src output in the v1 API.
    """
    if obj.where:
        geometry = {
            'type': 'Point',
            'coordinates': [obj.where.x, obj.where.y],
        }
    else:
        geometry = None
    return {
        'type': 'Feature',
        'geometry': geometry,
        'properties': {
            'id': obj.pk,
            'survey_id': obj.survey.pk if obj.survey else None,
            'area_id': obj.area.pk if obj.area else None,
            'site_id': obj.site.pk if obj.site else None,
            'source': obj.get_source_display(),
            'source_id': obj.source_id,
            'when': obj.when.astimezone(settings.TZ).isoformat(),
            'location_accuracy': obj.location_accuracy,
            'location_accuracy_m': obj.location_accuracy_m,
            'name': obj.name,
            'observer_id': obj.observer.pk if obj.observer else None,
            'reporter_id': obj.reporter.pk if obj.reporter else None,
            'encounter_type': obj.get_encounter_type_display() if obj.encounter_type else None,
            'comments': obj.comments,
            'status': obj.get_status_display(),
        },
    }


class EncounterSerializer(object):
    def serialize(encounter):
        return encounter_serializer(encounter)


def animalencounter_serializer(obj) -> Dict[str, Any]:
    d = {
        'taxon': obj.get_taxon_display(),
        'species': obj.get_species_display(),
        'sex': obj.get_sex_display(),
        'maturity': obj.get_maturity_display(),
        'health': obj.get_health_display(),
        'activity': obj.get_activity_display(),
        'behaviour': obj.behaviour,
        'habitat': obj.get_habitat_display(),
        #'sighting_status': obj.get_sighting_status_display(),
        #'sighting_status_reason': obj.sighting_status_reason,
        #'identifiers': obj.identifiers,
        #'datetime_of_last_sighting': obj.datetime_of_last_sighting.astimezone(settings.TZ).isoformat() if obj.datetime_of_last_sighting else None,
        #'site_of_last_sighting_id': obj.site_of_last_sighting.pk if obj.site_of_last_sighting else None,
        #'site_of_first_sighting_id': obj.site_of_first_sighting.pk if obj.site_of_first_sighting else None,
        'nesting_event': obj.get_nesting_event_display(),
        'nesting_disturbed': obj.get_nesting_disturbed_display(),
        'laparoscopy': obj.laparoscopy,
        'checked_for_injuries': obj.get_checked_for_injuries_display(),
        'scanned_for_pit_tags': obj.get_scanned_for_pit_tags_display(),
        'checked_for_flipper_tags': obj.get_checked_for_flipper_tags_display(),
        'cause_of_death': obj.get_cause_of_death_display(),
        'cause_of_death_confidence': obj.get_cause_of_death_confidence_display(),
    }
    obj = encounter_serializer(obj)
    # Extend the serialised object.
    obj['properties'].update(d)

    return obj


class AnimalEncounterSerializer(object):
    def serialize(encounter):
        return animalencounter_serializer(encounter)


def turtlenestencounter_serializer(obj) -> Dict[str, Any]:
    d = {
        'nest_age': obj.get_nest_age_display(),
        'nest_type': obj.get_nest_type_display(),
        'species': obj.get_species_display(),
        'habitat': obj.get_habitat_display(),
        'disturbance': obj.get_disturbance_display(),
        'nest_tagged': obj.get_nest_tagged_display(),
        'logger_found': obj.get_logger_found_display(),
        'eggs_counted': obj.get_eggs_counted_display(),
        'hatchlings_measured': obj.get_hatchlings_measured_display(),
        'fan_angles_measured': obj.get_fan_angles_measured_display(),
    }
    obj = encounter_serializer(obj)
    # Extend the serialised object.
    obj['properties'].update(d)

    return obj


class TurtleNestEncounterSerializer(object):
    def serialize(encounter):
        return turtlenestencounter_serializer(encounter)


def observation_serializer(obj) -> Dict[str, Any]:
    return {
        'type': 'Feature',
        'properties': {
            'id': obj.pk,
            'encounter_id': obj.encounter.pk,
            'source': obj.get_source_display(),
            'source_id': obj.source_id,
        },
    }


def media_attachment_serializer(obj) -> Dict[str, Any]:
    d = {
        'media_type': obj.get_media_type_display(),
        'title': obj.title,
        'attachment': settings.MEDIA_URL + obj.attachment.name,
    }
    obj = observation_serializer(obj)
    # Extend the serialised object.
    obj['properties'].update(d)

    return obj


class MediaAttachmentSerializer(object):
    def serialize(obj):
        return media_attachment_serializer(obj)


def turtle_nest_observation_serializer(obj) -> Dict[str, Any]:
    d = {
        'eggs_laid': obj.eggs_laid,
        'egg_count': obj.egg_count,
        'no_egg_shells': obj.no_egg_shells,
        'no_live_hatchlings_neck_of_nest': obj.no_live_hatchlings_neck_of_nest,
        'no_live_hatchlings': obj.no_live_hatchlings,
        'no_dead_hatchlings': obj.no_dead_hatchlings,
        'no_undeveloped_eggs': obj.no_undeveloped_eggs,
        'no_unhatched_eggs': obj.no_unhatched_eggs,
        'no_unhatched_term': obj.no_unhatched_term,
        'no_depredated_eggs': obj.no_depredated_eggs,
        'nest_depth_top': obj.nest_depth_top,
        'nest_depth_bottom': obj.nest_depth_bottom,
        'sand_temp': obj.sand_temp,
        'air_temp': obj.air_temp,
        'water_temp': obj.water_temp,
        'egg_temp': obj.egg_temp,
        'comments': obj.comments,
    }
    obj = observation_serializer(obj)
    # Extend the serialised object.
    obj['properties'].update(d)

    return obj


class TurtleNestObservationSerializer(object):
    def serialize(obj):
        return turtle_nest_observation_serializer(obj)


def turtle_hatchling_emergence_observation_serializer(obj) -> Dict[str, Any]:
    d = {
        'bearing_to_water_degrees': obj.bearing_to_water_degrees,
        'bearing_leftmost_track_degrees': obj.bearing_leftmost_track_degrees,
        'bearing_rightmost_track_degrees': obj.bearing_rightmost_track_degrees,
        'no_tracks_main_group': obj.no_tracks_main_group,
        'no_tracks_main_group_min': obj.no_tracks_main_group_min,
        'no_tracks_main_group_max': obj.no_tracks_main_group_max,
        'outlier_tracks_present': obj.get_outlier_tracks_present_display(),
        'path_to_sea_comments': obj.path_to_sea_comments,
        'hatchling_emergence_time_known': obj.get_hatchling_emergence_time_known_display(),
        'cloud_cover_at_emergence_known': obj.get_cloud_cover_at_emergence_known_display(),
        'light_sources_present': obj.get_light_sources_present_display(),
        'hatchling_emergence_time': obj.hatchling_emergence_time.astimezone(settings.TZ).isoformat() if obj.hatchling_emergence_time else None,
        'hatchling_emergence_time_accuracy': obj.hatchling_emergence_time_accuracy,
        'cloud_cover_at_emergence': obj.cloud_cover_at_emergence,
    }
    obj = observation_serializer(obj)
    # Extend the serialised object.
    obj['properties'].update(d)

    return obj


class TurtleHatchlingEmergenceObservationSerializer(object):
    def serialize(obj):
        return turtle_hatchling_emergence_observation_serializer(obj)


def nest_tag_observation_serializer(obj) -> Dict[str, Any]:
    d = {
        'status': obj.get_status_display(),
        'flipper_tag_id': obj.flipper_tag_id,
        'date_nest_laid': obj.date_nest_laid.isoformat() if obj.date_nest_laid else None,
        'tag_label': obj.tag_label,
        'comments': obj.comments,
    }
    obj = observation_serializer(obj)
    # Extend the serialised object.
    obj['properties'].update(d)

    return obj


class NestTagObservationSerializer(object):
    def serialize(obj):
        return nest_tag_observation_serializer(obj)


def turtle_nest_disturbance_observation_serializer(obj) -> Dict[str, Any]:
    d = {
        'disturbance_cause': obj.get_disturbance_cause_display(),
        'disturbance_cause_confidence': obj.get_disturbance_cause_confidence_display(),
        'disturbance_severity': obj.get_disturbance_severity_display(),
        'comments': obj.comments,
    }
    obj = observation_serializer(obj)
    # Extend the serialised object.
    obj['properties'].update(d)

    return obj


class TurtleNestDisturbanceObservationSerializer(object):
    def serialize(obj):
        return turtle_nest_disturbance_observation_serializer(obj)


def logger_observation_serializer(obj) -> Dict[str, Any]:
    d = {
        'logger_type': obj.get_logger_type_display(),
        'deployment_status': obj.get_deployment_status_display(),
        'logger_id': obj.logger_id,
        'comments': obj.comments,
    }
    obj = observation_serializer(obj)
    # Extend the serialised object.
    obj['properties'].update(d)

    return obj


class LoggerObservationSerializer(object):
    def serialize(obj):
        return logger_observation_serializer(obj)


def hatchling_morphometric_observation_serializer(obj) -> Dict[str, Any]:
    d = {
        'straight_carapace_length_mm': obj.straight_carapace_length_mm,
        'straight_carapace_width_mm': obj.straight_carapace_width_mm,
        'body_weight_g': obj.body_weight_g,
    }
    obj = observation_serializer(obj)
    # Extend the serialised object.
    obj['properties'].update(d)

    return obj


class HatchlingMorphometricObservationSerializer(object):
    def serialize(obj):
        return hatchling_morphometric_observation_serializer(obj)


def turtle_hatchling_emergence_outlier_observation_serializer(obj) -> Dict[str, Any]:
    d = {
        'bearing_outlier_track_degrees': obj.bearing_outlier_track_degrees,
        'outlier_group_size': obj.outlier_group_size,
        'outlier_track_comment': obj.outlier_track_comment,
    }
    obj = observation_serializer(obj)
    # Extend the serialised object.
    obj['properties'].update(d)

    return obj


class TurtleHatchlingEmergenceOutlierObservationSerializer(object):
    def serialize(obj):
        return turtle_hatchling_emergence_outlier_observation_serializer(obj)


def light_source_observation_serializer(obj) -> Dict[str, Any]:
    d = {
        'bearing_light_degrees': obj.bearing_light_degrees,
        'light_source_type': obj.get_light_source_type_display(),
        'light_source_description': obj.light_source_description,
    }
    obj = observation_serializer(obj)
    # Extend the serialised object.
    obj['properties'].update(d)

    return obj


class LightSourceObservationSerializer(object):
    def serialize(obj):
        return light_source_observation_serializer(obj)
