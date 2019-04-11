# -*- coding: utf-8 -*-
"""Conservation filters."""
from django.contrib.gis.db import models as geo_models
from django.contrib.gis.db.models import Extent, Union, Collect  # noqa
from django.db.models import Q

import django_filters

from conservation import models as cons_models
from conservation import widgets as cons_widgets
from occurrence import models as occ_models
from taxonomy import models as tax_models
from taxonomy import widgets as tax_widgets
from shared.filters import FILTER_OVERRIDES
from wastd.observations.models import Area


class ConservationThreatFilter(django_filters.FilterSet):
    """Filter for ConservationThreat."""

    target_area = geo_models.PolygonField()
    taxa = django_filters.ModelMultipleChoiceFilter(
        queryset=tax_models.Taxon.objects.all(),
        widget=tax_widgets.TaxonMultipleWidget()
    )
    communities = django_filters.ModelMultipleChoiceFilter(
        queryset=tax_models.Community.objects.all(),
        widget=tax_widgets.CommunityMultipleWidget()
    )
    document = django_filters.ModelMultipleChoiceFilter(
        queryset=cons_models.Document.objects.all(),
        widget=cons_widgets.DocumentMultipleWidget()
    )
    admin_areas = django_filters.ModelMultipleChoiceFilter(
        label="DBCA Regions and Districts",
        queryset=Area.objects.filter(
            area_type__in=[
                Area.AREATYPE_DBCA_REGION,
                Area.AREATYPE_DBCA_DISTRICT]),
        method='related_taxa_or_communities_in_area'
    )

    class Meta:
        """Class opts."""

        model = cons_models.ConservationThreat
        filter_overrides = FILTER_OVERRIDES
        fields = [
            "admin_areas",
            'category',
            'current_impact',
            'potential_onset',
            'potential_impact',
            "taxa",
            "taxa__paraphyletic_groups",
            "communities",
            "document",
            'target_area',
        ]

    def related_taxa_or_communities_in_area(self, queryset, name, value):
        """Return Threats with Taxa or Communities pertaining to the given Area.

        * The filter returns a list of Area objects as ``value``
        * We need to extract their PKs to create a queryset equivalent to
          the list of objects ``value``. Only querysets allow agggregation, not lists.
        * A search_area Multipolygon is collected from the geoms of Areas in ``value``


        * The Taxon PKs are calculated from occurrences (TaxonAreaEncounters)
          ``intersect``ing the search_area
        * The queryset is filtered by the list of Taxon PKs with occurrences
        """
        if value:
            search_area = Area.objects.filter(
                pk__in=[area.pk for area in value]
            ).aggregate(Collect('geom'))["geom__collect"]

            taxon_pks_in_area = set(
                [x["taxon__pk"]
                 for x in occ_models.TaxonAreaEncounter.objects.filter(
                    Q(point__intersects=search_area) |
                    Q(geom__intersects=search_area)
                ).values("taxon__pk")]
            )
            com_pks_in_area = set(
                [x["community__pk"]
                 for x in occ_models.CommunityAreaEncounter.objects.filter(
                    Q(point__intersects=search_area) |
                    Q(geom__intersects=search_area)
                ).values("community__pk")]
            )
            return queryset.filter(
                Q(taxa__pk__in=taxon_pks_in_area) |
                Q(communities__pk__in=com_pks_in_area)
            )
        else:
            return queryset


class ConservationActionFilter(django_filters.FilterSet):
    """Filter for ConservationAction."""

    target_area = geo_models.PolygonField()
    taxa = django_filters.ModelMultipleChoiceFilter(
        queryset=tax_models.Taxon.objects.all(),
        widget=tax_widgets.TaxonMultipleWidget()
    )
    communities = django_filters.ModelMultipleChoiceFilter(
        queryset=tax_models.Community.objects.all(),
        widget=tax_widgets.CommunityMultipleWidget()
    )
    document = django_filters.ModelMultipleChoiceFilter(
        queryset=cons_models.Document.objects.all(),
        widget=cons_widgets.DocumentMultipleWidget()
    )
    admin_areas = django_filters.ModelMultipleChoiceFilter(
        label="DBCA Regions and Districts",
        queryset=Area.objects.filter(
            area_type__in=[
                Area.AREATYPE_DBCA_REGION,
                Area.AREATYPE_DBCA_DISTRICT]),
        method='related_taxa_or_communities_in_area'
    )

    class Meta:
        """Class opts."""

        model = cons_models.ConservationAction
        filter_overrides = FILTER_OVERRIDES
        fields = [
            "admin_areas",
            'category',
            'status',
            "taxa",
            "taxa__paraphyletic_groups",
            "communities",
            "document",
            'target_area',
        ]

    def related_taxa_or_communities_in_area(self, queryset, name, value):
        """Return Actions with Taxa or Communities pertaining to the given Area.

        * The filter returns a list of Area objects as ``value``
        * We need to extract their PKs to create a queryset equivalent to
          the list of objects ``value``. Only querysets allow agggregation, not lists.
        * A search_area Multipolygon is collected from the geoms of Areas in ``value``


        * The Taxon PKs are calculated from occurrences (TaxonAreaEncounters)
          ``intersect``ing the search_area
        * The queryset is filtered by the list of Taxon PKs with occurrences
        """
        if value:
            search_area = Area.objects.filter(
                pk__in=[area.pk for area in value]
            ).aggregate(Collect('geom'))["geom__collect"]

            taxon_pks_in_area = set(
                [x["taxon__pk"]
                 for x in occ_models.TaxonAreaEncounter.objects.filter(
                    Q(point__intersects=search_area) |
                    Q(geom__intersects=search_area)
                ).values("taxon__pk")]
            )
            com_pks_in_area = set(
                [x["community__pk"]
                 for x in occ_models.CommunityAreaEncounter.objects.filter(
                    Q(point__intersects=search_area) |
                    Q(geom__intersects=search_area)
                ).values("community__pk")]
            )
            return queryset.filter(
                Q(taxa__pk__in=taxon_pks_in_area) |
                Q(communities__pk__in=com_pks_in_area)
            )
        else:
            return queryset


class DocumentFilter(django_filters.FilterSet):
    """Filter for Document."""

    taxa = django_filters.ModelMultipleChoiceFilter(
        queryset=tax_models.Taxon.objects.all(),
        widget=tax_widgets.TaxonMultipleWidget()
    )
    communities = django_filters.ModelMultipleChoiceFilter(
        queryset=tax_models.Community.objects.all(),
        widget=tax_widgets.CommunityMultipleWidget()
    )
    admin_areas = django_filters.ModelMultipleChoiceFilter(
        label="DBCA Regions and Districts",
        queryset=Area.objects.filter(
            area_type__in=[
                Area.AREATYPE_DBCA_REGION,
                Area.AREATYPE_DBCA_DISTRICT]),
        method='related_taxa_or_communities_in_area'
    )

    class Meta:
        """Class opts."""

        model = cons_models.Document
        filter_overrides = FILTER_OVERRIDES
        fields = [
            "admin_areas",
            "document_type",
            "status",
            "effective_from",
            "effective_to",
            "effective_from_commonwealth",
            "effective_to_commonwealth",
            "last_reviewed_on",
            "review_due",
            "taxa__paraphyletic_groups",
            "taxa",
            "communities",
        ]

    def related_taxa_or_communities_in_area(self, queryset, name, value):
        """Return Documents with Taxa or Communities pertaining to the given Area.

        * The filter returns a list of Area objects as ``value``
        * We need to extract their PKs to create a queryset equivalent to
          the list of objects ``value``. Only querysets allow agggregation, not lists.
        * A search_area Multipolygon is collected from the geoms of Areas in ``value``


        * The Taxon PKs are calculated from occurrences (TaxonAreaEncounters)
          ``intersect``ing the search_area
        * The queryset is filtered by the list of Taxon PKs with occurrences
        """
        if value:
            search_area = Area.objects.filter(
                pk__in=[area.pk for area in value]
            ).aggregate(Collect('geom'))["geom__collect"]

            taxon_pks_in_area = set(
                [x["taxon__pk"]
                 for x in occ_models.TaxonAreaEncounter.objects.filter(
                    Q(point__intersects=search_area) |
                    Q(geom__intersects=search_area)
                ).values("taxon__pk")]
            )
            com_pks_in_area = set(
                [x["community__pk"]
                 for x in occ_models.CommunityAreaEncounter.objects.filter(
                    Q(point__intersects=search_area) |
                    Q(geom__intersects=search_area)
                ).values("community__pk")]
            )
            return queryset.filter(
                Q(taxa__pk__in=taxon_pks_in_area) |
                Q(communities__pk__in=com_pks_in_area)
            )
        else:
            return queryset
