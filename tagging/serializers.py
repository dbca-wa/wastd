from typing import Dict, Any


def turtle_tag_serializer(obj) -> Dict[str, Any]:

    return {
        'type': 'Feature',
        'geometry': None,
        'properties': {
            'id': obj.pk,
            'serial': obj.serial,
            'turtle_id': obj.turtle.pk if obj.turtle else None,
            'status': obj.get_status_display(),
            'side': obj.get_side_display(),
            'return_date': obj.return_date.isoformat() if obj.return_date else None,
        },
    }


class TurtleTagSerializer(object):
    def serialize(obj):
        return turtle_tag_serializer(obj)


def turtle_pit_tag_serializer(obj) -> Dict[str, Any]:

    return {
        'type': 'Feature',
        'geometry': None,
        'properties': {
            'id': obj.pk,
            'serial': obj.serial,
            'turtle_id': obj.turtle.pk if obj.turtle else None,
            'status': obj.get_status_display(),
            'return_date': obj.return_date.isoformat() if obj.return_date else None,
        },
    }


class TurtlePitTagSerializer(object):
    def serialize(obj):
        return turtle_pit_tag_serializer(obj)
