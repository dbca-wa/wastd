# -*- coding: utf-8 -*-
"""Conservation views."""
from __future__ import unicode_literals

# from django.shortcuts import render
from django.http import Http404
from django.utils import timezone
# from django.utils.translation import ugettext_lazy as _
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView


from conservation.filters import ConservationActionFilter
from conservation.models import ConservationAction
from conservation.forms import ConservationActionForm

from shared.views import (
    SuccessUrlMixin,
    ListViewBreadcrumbMixin,
    DetailViewBreadcrumbMixin,
    UpdateViewBreadcrumbMixin,
    CreateViewBreadcrumbMixin
)


# ---------------------------------------------------------------------------#
# List Views
#
class ConservationActionListView(ListViewBreadcrumbMixin, ListView):
    """A ListView for ConservationAction."""

    model = ConservationAction
    template_name = "conservation/conservationaction_list.html"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        """Context with list filter and current time."""
        context = super(ConservationActionListView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['list_filter'] = ConservationActionFilter(
            self.request.GET, queryset=self.get_queryset())
        return context

    def get_queryset(self):
        """Queryset with custom filter."""
        queryset = ConservationAction.objects.all().prefetch_related(
            "taxa", "communities", "document", "conservationactivity_set", "category")
        return ConservationActionFilter(self.request.GET, queryset=queryset).qs


# ---------------------------------------------------------------------------#
# Detail Views
#
class ConservationActionDetailView(DetailViewBreadcrumbMixin, DetailView):
    """Conservation Action DetailView."""

    model = ConservationAction
    template_name = "conservation/conservationaction_detail.html"

    def get_object(self):
        """Get object, handle 404, refetch for performance."""
        obj = self.model.objects.filter(
            pk=self.kwargs.get("pk")
        ).prefetch_related(
            "communities",
            "taxa",
            "document"
        ).first()
        if not obj:
            raise Http404
        return obj


# ---------------------------------------------------------------------------#
# Update Views
#
class ConservationActionUpdateView(
        SuccessUrlMixin, UpdateViewBreadcrumbMixin, UpdateView):
    """Update view for ConservationAction."""

    template_name = "conservation/conservationaction_form.html"
    form_class = ConservationActionForm
    model = ConservationAction

    def get_object(self, queryset=None):
        """Get object, handle 404, refetch for performance."""
        obj = self.model.objects.filter(
            pk=self.kwargs.get("pk")
        ).prefetch_related(
            "communities",
            "taxa",
            "document"
        ).first()
        if not obj:
            raise Http404
        return obj


# ---------------------------------------------------------------------------#
# Create Views
#
class ConservationActionCreateView(
        CreateViewBreadcrumbMixin, SuccessUrlMixin, CreateView):
    """Create view for ConservationAction."""

    template_name = "conservation/conservationaction_form.html"
    form_class = ConservationActionForm
    model = ConservationAction

    # def get_initial(self):
    #     """Initial form values.

    #     TODO create different urls.
    #     """
    #     initial = dict()
    #     # if "name_id" in self.kwargs:
    #     #     initial["taxa"] = Taxon.objects.get(name_id=self.kwargs["name_id"])
    #     # if "area_code" in self.kwargs:
    #     #     initial["area_code"] = self.kwargs["area_code"]
    #     return initial
