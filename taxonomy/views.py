# -*- coding: utf-8 -*-
"""Taxonomy views."""
from __future__ import absolute_import, unicode_literals

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, Http404
# from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from export_download.views import ResourceDownloadMixin

from taxonomy.filters import CommunityFilter, TaxonFilter
from taxonomy.models import Community, Taxon
from taxonomy.tables import CommunityAreaEncounterTable, TaxonAreaEncounterTable
from taxonomy.utils import update_taxon as update_taxon_util
from taxonomy import resources as tax_resources
from shared.utils import Breadcrumb
from shared.views import (
    # SuccessUrlMixin,
    ListViewBreadcrumbMixin,
    DetailViewBreadcrumbMixin,
    # UpdateViewBreadcrumbMixin,
    # CreateViewBreadcrumbMixin
)


@csrf_exempt
def update_taxon(request):
    """Update Taxon."""
    msg = update_taxon_util()
    messages.success(request, msg)
    return HttpResponseRedirect("/")


# ---------------------------------------------------------------------------#
# List Views
#
class TaxonListView(ListViewBreadcrumbMixin, ResourceDownloadMixin, ListView):
    """A ListView for Taxon."""

    model = Taxon
    template_name = "pages/default_list.html"
    resource_class = tax_resources.TaxonResource
    resource_formats = ['csv', 'tsv', 'xls', 'json']
    paginate_by = 12

    def get_context_data(self, **kwargs):
        """Add extra items to context."""
        context = super(TaxonListView, self).get_context_data(**kwargs)
        context["now"] = timezone.now()
        context["list_filter"] = TaxonFilter(self.request.GET, queryset=self.get_queryset())
        return context

    def get_queryset(self):
        """Queryset: filter by name_id if in pars.

        There are two mutually exclusive ways of filtering data:

        * Taxon card > explore: GET name_id = show this taxon, its parents
          and all children. Do not process the other filter fields.
        * Search filter: name (icontains), rank, is current, publication status.

        DO NOT use taxon_filter.qs in template:
        https://github.com/django-mptt/django-mptt/issues/632
        """
        queryset = Taxon.objects.order_by(
            "-rank",
        ).prefetch_related(
            "paraphyletic_groups",
            "taxon_gazettal",
            "conservationthreat_set",
            "conservationaction_set",
            "document_set",
        )

        # name_id is mutually exclusive to other parameters
        if self.request.GET.get("name_id"):
            # t = queryset.filter(name_id=self.request.GET.get("name_id"))
            # return list(chain(t.first().get_ancestors(), t, t.first().get_children()))
            try:
                return queryset.filter(
                    name_id=self.request.GET.get("name_id")
                ).get().get_family()
            except ObjectDoesNotExist:
                messages.warning(self.request, "This Name ID does not exist.")
                return queryset

        return TaxonFilter(self.request.GET, queryset=queryset).qs


class CommunityListView(ListViewBreadcrumbMixin, ResourceDownloadMixin, ListView):
    """A ListView for Community."""

    model = Community
    template_name = "pages/default_list.html"
    resource_class = tax_resources.CommunityResource
    resource_formats = ['csv', 'tsv', 'xls', 'json']
    paginate_by = 12

    def get_context_data(self, **kwargs):
        """Add extra items to context."""
        context = super(CommunityListView, self).get_context_data(**kwargs)
        context["now"] = timezone.now()
        context["list_filter"] = CommunityFilter(
            self.request.GET,
            queryset=self.get_queryset()
        )
        return context

    def get_queryset(self):
        """Queryset."""
        queryset = Community.objects.all().prefetch_related(
            "community_gazettal",
            "conservationthreat_set",
            "conservationaction_set",
            "document_set"
        )
        return CommunityFilter(self.request.GET, queryset=queryset).qs


# ---------------------------------------------------------------------------#
# Detail Views
#
class TaxonDetailView(DetailViewBreadcrumbMixin, DetailView):
    """DetailView for Taxon."""

    model = Taxon
    context_object_name = "original"

    def get_object(self):
        """Get Object by name_id."""
        t = Taxon.objects.filter(
            name_id=self.kwargs.get("name_id")
        ).prefetch_related(
            "taxon_occurrences",
            "conservationaction_set",
        ).first()
        if not t:
            raise Http404
        return t

    def get_context_data(self, **kwargs):
        """Custom context."""
        context = super(TaxonDetailView, self).get_context_data(**kwargs)
        obj = self.object
        occ = obj.taxon_occurrences.prefetch_related("encountered_by")
        mt = obj.conservationthreat_set.all()
        ma = obj.conservationaction_set.all()
        max_cards = 100
        context["occurrence_table"] = TaxonAreaEncounterTable(occ.all()[:max_cards])
        context["occurrences"] = occ.all()
        context["max_cards"] = max_cards
        # if occ:
        context["occurrence_total"] = occ.count() if occ else 0
        # else:
        # context["occurrence_total"] = 0
        context["conservationthreats_general"] = mt.filter(document=None, occurrence_area_code=None)
        context["conservationthreats_area"] = mt.exclude(occurrence_area_code=None)
        context["conservationactions_general"] = ma.filter(document=None, occurrence_area_code=None)
        context["conservationactions_area"] = ma.exclude(occurrence_area_code=None)
        return context

    def get_breadcrumbs(self, request, obj=None, add=False):
        """Create a list of breadcrumbs as named tuples of ('name', 'url')."""
        return (
            Breadcrumb(_('Home'), reverse('home')),
            Breadcrumb(self.model._meta.verbose_name_plural, self.model.list_url()),
            Breadcrumb(
                "Phylogeny of {0}".format(self.object.canonical_name),
                '{0}?name_id={1}'.format(reverse('taxonomy:taxon-list'), self.object.name_id)
            ),
            Breadcrumb(self.object.__str__(), self.object.get_absolute_url())
        )


class CommunityDetailView(DetailViewBreadcrumbMixin, DetailView):
    """DetailView for Community."""

    model = Community
    context_object_name = "original"

    def get_object(self):
        """Get Object by pk."""
        com = Community.objects.filter(
            pk=self.kwargs.get("pk")
        ).prefetch_related(
            "community_occurrences",
            "conservationaction_set"
        ).first()
        if not com:
            raise Http404  # pragma: no cover
        return com

    def get_context_data(self, **kwargs):
        """Custom context."""
        context = super(CommunityDetailView, self).get_context_data(**kwargs)
        obj = self.get_object()
        occ = obj.community_occurrences
        mt = obj.conservationthreat_set.all()
        ma = obj.conservationaction_set.all()
        max_cards = 100
        context["max_cards"] = max_cards
        # if occ:
        context["occurrence_total"] = occ.count() if occ else 0
        # else:
        # context["occurrence_total"] = 0
        context["occurrence_table"] = CommunityAreaEncounterTable(occ.all()[:max_cards])
        context["occurrences"] = occ.all()
        context["conservationthreats_general"] = mt.filter(document=None, occurrence_area_code=None)
        context["conservationthreats_area"] = mt.exclude(occurrence_area_code=None)
        context["conservationactions_general"] = ma.filter(document=None, occurrence_area_code=None)
        context["conservationactions_area"] = ma.exclude(occurrence_area_code=None)
        return context
