# -*- coding: utf-8 -*-
"""Occurrence views."""
from __future__ import unicode_literals

# from django.shortcuts import render
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView  # FormView,; DeleteView,
from occurrence.forms import (
    AreaEncounterForm, CommunityAreaEncounterForm, TaxonAreaEncounterForm,
    AssociatedSpeciesObservationForm)
from occurrence.models import (
    AreaEncounter, TaxonAreaEncounter, CommunityAreaEncounter,
    ObservationGroup, AssociatedSpeciesObservation)
from taxonomy.models import Community, Taxon

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


class AreaEncounterUpdateView(UpdateView):
    """Update view for AreaEncounter."""

    template_name = "occurrence/areaencounter_form.html"
    form_class = AreaEncounterForm
    success_url = "/"  # default: form model's get_absolute_url()

    def get_object(self, queryset=None):
        """Accommodate custom object pk from url conf."""
        return self.model.objects.get(pk=self.kwargs["occ_pk"])

    def get_success_url(self):
        """Success: show AE detail view."""
        return self.model.detail_url


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


class TaxonAreaEncounterUpdateView(AreaEncounterUpdateView):
    """UpdateView for TaxonAreaEncounter."""

    template_name = "occurrence/taxonareaencounter_form.html"
    form_class = TaxonAreaEncounterForm
    model = TaxonAreaEncounter

    def get_success_url(self):
        """Success: show TAE detail view."""
        obj = self.get_object()
        return reverse('taxon-occurrence-detail',
                       kwargs={'name_id': obj.taxon.name_id, 'occ_pk': obj.pk})


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


class CommunityAreaEncounterUpdateView(AreaEncounterUpdateView):
    """UpdateView for CommunityAreaEncounter."""

    template_name = "occurrence/communityareaencounter_form.html"
    form_class = CommunityAreaEncounterForm
    model = CommunityAreaEncounter

    def get_success_url(self):
        """Success: show CAE detail view."""
        obj = self.get_object()
        return reverse('community-occurrence-detail',
                       kwargs={'pk': obj.community.pk, 'occ_pk': obj.pk})


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


# ---------------------------------------------------------------------------#
# AssociatedSpeciesObservation Views
#

class ObservationGroupCreateView(CreateView):
    """Base CreateView for ObservationGroup."""

    template_name = "occurrence/obsgroup_form.html"
    model = ObservationGroup

    def get_initial(self):
        """Initial form values."""
        initial = dict()
        if "occ_pk" in self.kwargs:
            initial["encounter"] = AreaEncounter.objects.get(pk=self.kwargs["occ_pk"])
        return initial

    def get_context_data(self, **kwargs):
        """Custom context."""
        context = super(ObservationGroupCreateView, self
                        ).get_context_data(**kwargs)
        context["subject"] = self.model._meta.verbose_name
        return context

    def get_success_url(self):
        """Success: show AE detail view."""
        return self.object.encounter.get_absolute_url()


class ObservationGroupUpdateView(UpdateView):
    """Update view for ObservationGroup."""

    template_name = "occurrence/obsgroup_form.html"
    model = ObservationGroup

    def get_object(self, queryset=None):
        """Accommodate custom object pk from url conf."""
        return self.model.objects.get(pk=self.kwargs["obs_pk"])

    def get_success_url(self):
        """Success: show AE detail view."""
        return self.object.encounter.get_absolute_url()


class AssociatedSpeciesObservationCreateView(ObservationGroupCreateView):
    """Create view for AssociatedSpeciesObservation."""

    model = AssociatedSpeciesObservation
    form_class = AssociatedSpeciesObservationForm


class AssociatedSpeciesObservationUpdateView(ObservationGroupUpdateView):
    """Update view for AssociatedSpeciesObservation."""

    model = AssociatedSpeciesObservation
    form_class = AssociatedSpeciesObservationForm
