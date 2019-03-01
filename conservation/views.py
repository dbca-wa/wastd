# -*- coding: utf-8 -*-
"""Conservation views."""
from __future__ import unicode_literals

from collections import namedtuple

# from django.shortcuts import render
from django.http import Http404
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView  # FormView,; DeleteView,  # noqa
from django.views.generic.list import ListView


from conservation.filters import ConservationActionFilter
from conservation.models import ConservationAction
from conservation.forms import ConservationActionForm

Breadcrumb = namedtuple('Breadcrumb', ['name', 'url'])


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
        context['breadcrumbs'] = self.get_breadcrumbs(self.request)
        return context

    def get_queryset(self):
        """Queryset: filter."""
        queryset = ConservationAction.objects.all().prefetch_related(
            "taxa", "communities", "document", "conservationactivity_set", "category")

        return ConservationActionFilter(self.request.GET, queryset=queryset).qs

    def get_breadcrumbs(self, request, obj=None, add=False):
        """Create a list of breadcrumbs as named tuples of ('name', 'url')."""
        return (Breadcrumb(_('Home'), reverse('home')),
                Breadcrumb(self.model._meta.verbose_name_plural,
                           reverse('conservationaction-list')))


class ConservationActionDetailView(DetailView):
    """Conservation Action DetailView."""

    model = ConservationAction
    template_name = "conservation/conservationaction_detail.html"

    def get_object(self):
        """Get Object by pk."""
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

    def get_context_data(self, **kwargs):
        """Custom context."""
        context = super(ConservationActionDetailView, self).get_context_data(**kwargs)
        return context


class ConservationActionUpdateView(UpdateView):
    """Update view for ConservationAction."""

    template_name = "conservation/conservationaction_form.html"
    form_class = ConservationActionForm
    model = ConservationAction

    def get_object(self, queryset=None):
        """Accommodate custom object pk from url conf.

        TODO prefetch taxa, communities, document.
        """
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

    def get_success_url(self):
        """Success: TODO show ConservationAction detail view."""
        return reverse('conservationaction-list')


class ConservationActionCreateView(CreateView):
    """Create view for ConservationAction."""

    template_name = "conservation/conservationaction_form.html"
    form_class = ConservationActionForm
    model = ConservationAction

    def get_success_url(self):
        """Success: TODO show ConservationAction detail view."""
        return reverse('conservationaction-list')

    def get_initial(self):
        """Initial form values.

        TODO create different urls.
        """
        initial = dict()
        # if "name_id" in self.kwargs:
        #     initial["taxa"] = Taxon.objects.get(name_id=self.kwargs["name_id"])
        # if "area_code" in self.kwargs:
        #     initial["area_code"] = self.kwargs["area_code"]
        return initial
