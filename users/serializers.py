from typing import Dict, Any
from .models import User


def user_serializer_basic(user: User) -> Dict[str, Any]:
    """Function to return minimal attributes of a passed-in User as a simple dict.
    """
    return {
        'id': user.pk,
        'username': user.username,
        'name': user.name,
    }


def user_serializer(user: User) -> Dict[str, Any]:
    """Function to return attributes of a passed-in User as a simple dict.
    """
    return {
        'type': 'Feature',
        'properties': {
            'id': user.pk,
            'username': user.username,
            'name': user.name,
            'nickname': user.nickname,
            'aliases': user.aliases,
            'role': user.role,
            'affiliation': user.affiliation,
            'email': user.email,
            'phone': user.phone.__str__() if user.phone else '',
            'is_active': user.is_active,
            'alive': user.alive,
        },
    }


class UserSerializer(object):
    def serialize(obj):
        return user_serializer(obj)
