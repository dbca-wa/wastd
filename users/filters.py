from django_filters import FilterSet
from users.models import User


class UserFilter(FilterSet):

    class Meta:
        model = User
        fields = {
            "name": ["icontains"],
            "email": ["icontains"],
            "phone": ["contains"],
            "is_active": ["exact"],
        }
