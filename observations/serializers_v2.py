from django.conf import settings
from django.utils import timezone
from typing import Dict, Any
from users.serializers import user_serializer_basic


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
        'start_time': obj.start_time.astimezone(timezone.get_current_timezone()).isoformat(),
        'end_time': obj.end_time.astimezone(timezone.get_current_timezone()).isoformat(),
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
            'start_time': obj.start_time.astimezone(timezone.get_current_timezone()).isoformat(),
            'start_comments': obj.start_comments,
            'end_source_id': obj.end_source_id,
            'end_device_id': obj.end_device_id,
            'end_location': None,  # TODO
            'end_location_accuracy_m': obj.end_location_accuracy_m,
            'end_time': obj.end_time.astimezone(timezone.get_current_timezone()).isoformat(),
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
            'when': obj.when.astimezone(timezone.get_current_timezone()).isoformat(),
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


def media_attachment_serializer(obj) -> Dict[str, Any]:
    return {
        'type': 'Feature',
        'properties': {
            'id': obj.pk,
            'source': obj.encounter.source,
            'source_id': obj.encounter.source_id,
            'encounter': encounter_serializer(obj.encounter),
            'media_type': obj.get_media_type_display(),
            'title': obj.title,
            'attachment': settings.MEDIA_URL + obj.attachment.name,  # FIXME: absolute URL
        },
    }


class MediaAttachmentSerializer(object):
    def serialize(obj):
        return media_attachment_serializer(obj)
