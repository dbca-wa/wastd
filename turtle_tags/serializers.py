from typing import Dict, Any


def turtle_serializer(obj) -> Dict[str, Any]:

    return {
        'type': 'Feature',
        'geometry': None,
        'properties': {
            'id': obj.pk,
            'species': obj.get_species_display(),
            'sex': obj.get_sex_display(),
            'name': obj.name,
            'comments': obj.comments,
        },
    }


class TurtleSerializer(object):
    def serialize(obj):
        return turtle_serializer(obj)


def turtle_tag_serializer(obj) -> Dict[str, Any]:

    return {
        'type': 'Feature',
        'geometry': None,
        'properties': {
            'id': obj.pk,
            'serial': obj.serial,
            'tag_type': obj.get_tag_type_display(),
            'turtle_id': obj.turtle.pk if obj.turtle else None,
            'side': obj.get_side_display(),
            'return_date': obj.return_date.isoformat() if obj.return_date else None,
            'return_condition': obj.return_condition,
            'comments': obj.comments,
            'batch_number': obj.batch_number,
            'box_number': obj.box_number,
        },
    }


class TurtleTagSerializer(object):
    def serialize(obj):
        return turtle_tag_serializer(obj)
