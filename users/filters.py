"""Filters for WAStD Users."""
from django_filters import FilterSet
from django_filters.filters import (  # noqa
    BooleanFilter,
    CharFilter,
    RangeFilter,
    ChoiceFilter,
    MultipleChoiceFilter,
    ModelChoiceFilter,
    ModelMultipleChoiceFilter,
)
from shared.filters import FILTER_OVERRIDES
from users.models import User


class UserFilter(FilterSet):
    """User Filter.

    https://django-filter.readthedocs.io/en/latest/usage.html
    """

    class Meta:
        """Options for UserFilter."""

        model = User
        filter_overrides = FILTER_OVERRIDES
        fields = [
            "username",
            "name",
            "nickname",
            "aliases",
            "role",
            "email",
            "phone",
            "affiliation",
            # 'organisations',
            "is_staff",
            "is_active",
            "date_joined",
            "last_login",
            "is_superuser",
            "alive",
        ]
