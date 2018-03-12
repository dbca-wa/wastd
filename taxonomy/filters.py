"""Taxonomy filters."""
# from django.contrib.auth.models import User
import django_filters
from django_filters.filters import BooleanFilter
from django_filters.widgets import BooleanWidget

from .models import Taxon


class TaxonFilter(django_filters.FilterSet):
    """Filter for Taxon."""
    current = BooleanFilter(widget=BooleanWidget())

    class Meta:
        """Class opts."""

        model = Taxon
        fields = ['name', 'rank', 'current', 'publication_status']
