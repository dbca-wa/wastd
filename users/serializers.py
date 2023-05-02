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
