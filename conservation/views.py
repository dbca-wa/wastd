# -*- coding: utf-8 -*-
"""Conservation views."""
from __future__ import unicode_literals

from django.http import Http404
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from export_download.views import ResourceDownloadMixin

from conservation import filters as cons_filters
from conservation import models as cons_models
from conservation import forms as cons_forms
from conservation import resources as cons_resources
from shared.utils import Breadcrumb
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
class ConservationActionListView(
        ListViewBreadcrumbMixin,
        ResourceDownloadMixin,
        ListView):
    """A ListView for ConservationAction."""

    model = cons_models.ConservationAction
    template_name = "conservation/conservationaction_list.html"
    resource_class = cons_resources.ConservationActionResource
    resource_formats = ['csv', 'tsv', 'xls', 'json']
    filter_class = cons_filters.ConservationActionFilter
    paginate_by = 20

    def get_context_data(self, **kwargs):
        """Context with list filter and current time."""
        context = super(ConservationActionListView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['list_filter'] = cons_filters.ConservationActionFilter(
            self.request.GET,
            queryset=self.get_queryset()
        )
        return context

    def get_queryset(self):
        """Queryset with custom filter."""
        queryset = cons_models.ConservationAction.objects.all().prefetch_related(
            "taxa",
            "communities",
            "document",
            "conservationactivity_set",
            "category"
        )
        return cons_filters.ConservationActionFilter(
            self.request.GET,
            queryset=queryset
        ).qs


# ---------------------------------------------------------------------------#
# Detail Views
#
class ConservationActionDetailView(DetailViewBreadcrumbMixin, DetailView):
    """Conservation Action DetailView."""

    model = cons_models.ConservationAction
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

    template_name = "shared/default_form.html"
    form_class = cons_forms.ConservationActionForm
    model = cons_models.ConservationAction

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


class ConservationActivityUpdateView(
        SuccessUrlMixin, UpdateViewBreadcrumbMixin, UpdateView):
    """Update view for ConservationActivity."""

    template_name = "shared/default_form.html"
    form_class = cons_forms.ConservationActivityForm
    model = cons_models.ConservationActivity

    def get_object(self, queryset=None):
        """Get object, handle 404, refetch for performance."""
        obj = self.model.objects.filter(
            pk=self.kwargs.get("pk")
        ).prefetch_related(
            "conservation_action"
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

    template_name = "shared/default_form.html"
    form_class = cons_forms.ConservationActionForm
    model = cons_models.ConservationAction

    def get_initial(self):
        """Initial form values.

        TODO create different urls.
        """
        initial = super(ConservationActionCreateView, self).get_initial()
        if "taxa" in self.request.GET:
            initial["taxa"] = self.request.GET["taxa"]
        if "communities" in self.request.GET:
            initial["communities"] = self.request.GET["communities"]
        if "document" in self.request.GET:
            initial["document_id"] = self.request.GET["document_id"]
        if "occurrence_area_code" in self.request.GET:
            initial["occurrence_area_code"] = self.request.GET["occurrence_area_code"]
        return initial


class ConservationActivityCreateView(
        CreateViewBreadcrumbMixin, SuccessUrlMixin, CreateView):
    """Create view for ConservationActivity."""

    template_name = "shared/default_form.html"
    form_class = cons_forms.ConservationActivityForm
    model = cons_models.ConservationActivity

    def get_initial(self):
        """Initial form values."""
        initial = super(ConservationActivityCreateView, self).get_initial()
        if "pk" in self.kwargs:
            initial["conservation_action"] = cons_models.ConservationAction.objects.get(pk=self.kwargs["pk"])
        return initial

    def get_breadcrumbs(self, request, obj=None, add=False):
        """Create a list of breadcrumbs as named tuples of ('name', 'url')."""
        ca = self.get_initial()["conservation_action"]
        return (
            Breadcrumb(_('Home'), reverse('home')),
            Breadcrumb(ca, ca.get_absolute_url()),
            Breadcrumb("Create a new {0}".format(self.model._meta.verbose_name), None)
        )
