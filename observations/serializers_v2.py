from django.conf import settings
from django.utils import timezone
from typing import Dict, Any
from users.serializers import user_serializer_basic


TZ = timezone.get_current_timezone()


def area_serializer_basic(obj) -> Dict[str, Any]:
    return {
        'id': obj.pk,
        'area_type': obj.area_type,
        'name': obj.name,
    }


def area_serializer(obj) -> Dict[str, Any]:
    if obj.centroid:
        centroid = {
            'type': 'Point',
            'coordinates': [obj.centroid.x, obj.centroid.y],
        }
    else:
        centroid = None
    return {
        'type': 'Feature',
        'geometry': {
            'type': 'Polygon',
            'coordinates': obj.geom.coords,
        },
        'properties': {
            'id': obj.pk,
            'area_type': obj.area_type,
            'name': obj.name,
            'w2_location_code': obj.w2_location_code,
            'w2_place_code': obj.w2_place_code,
            'northern_extent': obj.northern_extent,
            'centroid': centroid,
            'length_surveyed_m': obj.length_surveyed_m,
            'length_survey_roundtrip_m': obj.length_survey_roundtrip_m,
        },
    }


class AreaSerializer(object):
    def serialize(obj):
        return area_serializer(obj)


def survey_serializer_basic(obj) -> Dict[str, Any]:
    return {
        'id': obj.pk,
        'area': area_serializer_basic(obj.area) if obj.area else None,
        'site': area_serializer_basic(obj.site) if obj.site else None,
        'start_time': obj.start_time.astimezone(TZ).isoformat(),
        'end_time': obj.end_time.astimezone(TZ).isoformat(),
        'start_comments': obj.start_comments,
        'end_comments': obj.end_comments,
        'reporter': user_serializer_basic(obj.reporter) if obj.reporter else None,
        'absolute_admin_url': obj.absolute_admin_url,
        'production': obj.production,
    }


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
            'campaign': None,  # TODO
            'reporter': user_serializer_basic(obj.reporter) if obj.reporter else None,
            'area': area_serializer_basic(obj.area) if obj.area else None,
            'site': area_serializer_basic(obj.site) if obj.site else None,
            'status': obj.status,
            'absolute_admin_url': obj.absolute_admin_url,
            'start_photo': settings.MEDIA_URL + obj.start_photo.name if obj.start_photo else None,  # FIXME: absolute URL
            'end_photo': settings.MEDIA_URL + obj.end_photo.name if obj.end_photo else None,  # FIXME: absolute URL
            'source': obj.source,
            'source_id': obj.source_id,
            'device_id': obj.device_id,
            'start_location_accuracy_m': obj.start_location_accuracy_m,
            'start_time': obj.start_time.astimezone(TZ).isoformat(),
            'start_comments': obj.start_comments,
            'end_source_id': obj.end_source_id,
            'end_device_id': obj.end_device_id,
            'end_location': None,  # TODO
            'end_location_accuracy_m': obj.end_location_accuracy_m,
            'end_time': obj.end_time.astimezone(TZ).isoformat(),
            'end_comments': obj.end_comments,
            'production': obj.production,
            'label': obj.label,
            'team': [user_serializer_basic(user) for user in obj.team.all()],
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
            'source': obj.survey.source,
            'source_id': obj.survey.source_id,
            'survey': survey_serializer_basic(obj.survey),
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
            'source': obj.source,
            'source_id': obj.source_id,
            'encounter_type': obj.encounter_type,
            'status': obj.status,
            'when': obj.when.astimezone(TZ).isoformat(),
            'latitude': obj.where.y if obj.where else None,
            'longitude': obj.where.x if obj.where else None,
            'crs': obj.where.srid if obj.where else None,
            'location_accuracy': obj.location_accuracy,
            'location_accuracy_m': obj.location_accuracy_m,
            'name': obj.name,
            'leaflet_title': obj.leaflet_title,
            'observer': user_serializer_basic(obj.observer) if obj.observer else None,
            'reporter': user_serializer_basic(obj.reporter) if obj.reporter else None,
            'comments': obj.comments,
            'area': area_serializer_basic(obj.area) if obj.area else None,
            'site': area_serializer_basic(obj.site) if obj.site else None,
            'survey': survey_serializer_basic(obj.survey) if obj.survey else None,
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
        'sighting_status': obj.get_sighting_status_display(),
        'sighting_status_reason': obj.sighting_status_reason,
        'identifiers': obj.identifiers,
        'datetime_of_last_sighting': obj.datetime_of_last_sighting.astimezone(TZ).isoformat() if obj.datetime_of_last_sighting else None,
        'site_of_last_sighting': area_serializer_basic(obj.site_of_last_sighting) if obj.site_of_last_sighting else None,
        'site_of_first_sighting': area_serializer_basic(obj.site_of_first_sighting) if obj.site_of_first_sighting else None,
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
            'source': obj.source,
            'source_id': obj.source_id,
            'encounter_id': obj.encounter.pk,
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
