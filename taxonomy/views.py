# -*- coding: utf-8 -*-
"""Taxonomy views."""
from __future__ import unicode_literals
from itertools import chain

from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.views.generic.list import ListView

from taxonomy.utils import update_taxon as update_taxon_util
from taxonomy.models import Taxon
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
        """Queryset: filter by name_id if in pars."""
        queryset = Taxon.objects.all()
        if self.request.GET.get('name_id'):
            t = queryset.filter(name_id=self.request.GET.get('name_id'))
            queryset = list(chain(t.first().get_ancestors(), t, t.first().get_children()))
        return queryset
