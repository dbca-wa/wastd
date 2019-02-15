# -*- coding: utf-8 -*-
"""Conservation views."""
from __future__ import unicode_literals

# from django.shortcuts import render
# from django.views.generic.detail import DetailView
from django.utils import timezone
from django.views.generic.list import ListView

from conservation.filters import ConservationActionFilter
from conservation.models import ConservationAction

# ---------------------------------------------------------------------------#
# List Views
#


class ConservationActionListView(ListView):
    """A ListView for ConservationAction."""

    model = ConservationAction
    template_name = "conservation/conservationaction_list.html"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        """Add extra items to context."""
        context = super(ConservationActionListView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['list_filter'] = ConservationActionFilter(
            self.request.GET, queryset=self.get_queryset())
        return context

    def get_queryset(self):
        """Queryset: filter."""
        queryset = ConservationAction.objects.all()

        return ConservationActionFilter(self.request.GET, queryset=queryset).qs
