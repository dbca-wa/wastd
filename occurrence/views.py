# -*- coding: utf-8 -*-
"""Occurrence views."""
from __future__ import unicode_literals

# from django.shortcuts import render
from django.views.generic.edit import (
    # FormView,
    CreateView
    # DeleteView,
    # UpdateView
)
from django.views.generic.detail import DetailView

from taxonomy.models import (Taxon, Community)
from occurrence.models import (TaxonAreaEncounter, CommunityAreaEncounter)
from occurrence.forms import (
    AreaEncounterForm,
    TaxonAreaEncounterForm,
    CommunityAreaEncounterForm)

# select2 forms
# from .admin import (AreaForm, TaxonAreaForm, CommunityAreaForm)


# ---------------------------------------------------------------------------#
# Create Views
#
class AreaEncounterCreateView(CreateView):
    """Create view for AreaEncounter."""

    template_name = "occurrence/areaencounter_form.html"
    form_class = AreaEncounterForm
    success_url = "/"  # default: form model's get_absolute_url()


class TaxonAreaEncounterCreateView(AreaEncounterCreateView):
    """Create view for TaxonAreaEncounter."""

    template_name = "occurrence/taxonareaencounter_form.html"
    form_class = TaxonAreaEncounterForm

    def get_initial(self):
        """Initial form values."""
        initial = dict()
        if "name_id" in self.kwargs:
            initial["taxon"] = Taxon.objects.get(name_id=self.kwargs["name_id"])
        if "area_code" in self.kwargs:
            initial["code"] = self.kwargs["area_code"]
        return initial


class CommunityAreaEncounterCreateView(AreaEncounterCreateView):
    """Create view for CommunityAreaEncounter."""

    template_name = "occurrence/communityareaencounter_form.html"
    form_class = CommunityAreaEncounterForm

    def get_initial(self):
        """Initial form values."""
        initial = dict()
        if "pk" in self.kwargs:
            initial["community"] = Community.objects.get(pk=self.kwargs["pk"])
        if "area_code" in self.kwargs:
            initial["code"] = self.kwargs["area_code"]
        return initial


# ---------------------------------------------------------------------------#
# Detail Views
#
class TaxonAreaEncounterDetailView(DetailView):
    """DetailView for TaxonAreaEncounter."""

    model = TaxonAreaEncounter
    context_object_name = "original"
    template_name = "occurrence/taxonareaencounter_detail.html"

    def get_object(self):
        """Get Object by name_id."""
        object = TaxonAreaEncounter.objects.get(pk=self.kwargs.get("occ_pk"))
        return object

    def get_context_data(self, **kwargs):
        """Custom context."""
        context = super(TaxonAreaEncounterDetailView, self).get_context_data(**kwargs)
        # obj = self.get_object()
        #
        return context


class CommunityAreaEncounterDetailView(DetailView):
    """DetailView for CommunityAreaEncounter."""

    model = TaxonAreaEncounter
    context_object_name = "original"
    template_name = "occurrence/communityareaencounter_detail.html"

    def get_object(self):
        """Get Object by name_id."""
        object = CommunityAreaEncounter.objects.get(pk=self.kwargs.get("occ_pk"))
        return object

    def get_context_data(self, **kwargs):
        """Custom context."""
        context = super(CommunityAreaEncounterDetailView, self).get_context_data(**kwargs)
        # obj = self.get_object()
        #
        return context
