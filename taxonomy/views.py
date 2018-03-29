# -*- coding: utf-8 -*-
"""Taxonomy views."""
from __future__ import unicode_literals, absolute_import
from itertools import chain

from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.views.generic.list import ListView

from taxonomy.utils import update_taxon as update_taxon_util
from taxonomy.models import Taxon, Community
from taxonomy.filters import TaxonFilter


# Utilities ------------------------------------------------------------------#


@csrf_exempt
def update_taxon(request):
    """Update Taxon."""
    msg = update_taxon_util()
    messages.success(request, msg)
    return HttpResponseRedirect("/")


class TaxonListView(ListView):
    """A ListView for Taxon.

    TODO http://inmagik.github.io/django-search-views
    """

    model = Taxon
    template_name = "pages/dashboard.html"
    paginate_by = 12

    def get_context_data(self, **kwargs):
        """Add extra items to context."""
        context = super(TaxonListView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['taxon_filter'] = TaxonFilter(self.request.GET, queryset=self.get_queryset())
        return context

    def get_queryset(self):
        """Queryset: filter by name_id if in pars.

        There are two mutually exclusive ways of filtering data:

        * Taxon card > explore: GET name_id = show this taxon, its parents
          and one generation of children. Do not process the other filter fields.
        * Search filter: name (icontains), rank, is current, publication status.

        DO NOT use taxon_filter.qs in template: https://github.com/django-mptt/django-mptt/issues/632
        """
        queryset = Taxon.objects.all()

        # name_id is mutually exclusive to other parameters
        if self.request.GET.get('name_id'):
            t = queryset.filter(name_id=self.request.GET.get('name_id'))
            return list(chain(t.first().get_ancestors(), t, t.first().get_children()))

        return TaxonFilter(self.request.GET, queryset=queryset).qs


class CommunityListView(ListView):
    """A ListView for Community."""

    model = Community
    template_name = "pages/community_list.html"
    paginate_by = 12
