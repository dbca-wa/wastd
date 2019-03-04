# -*- coding: utf-8 -*-
"""Occurrence views."""
from __future__ import unicode_literals

# from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView  # FormView,; DeleteView,
from occurrence.forms import (
    AreaEncounterForm,
    CommunityAreaEncounterForm,
    TaxonAreaEncounterForm,
    AssociatedSpeciesObservationForm,
    FireHistoryObservationForm
)
from occurrence.models import (
    AreaEncounter,
    TaxonAreaEncounter,
    CommunityAreaEncounter,
    ObservationGroup,
    AssociatedSpeciesObservation,
    FireHistoryObservation
)
from taxonomy.models import Community, Taxon
from shared.utils import Breadcrumb
from shared.views import (  # noqa
    SuccessUrlMixin,
    # ListViewBreadcrumbMixin,
    # DetailViewBreadcrumbMixin,
    UpdateViewBreadcrumbMixin,
    CreateViewBreadcrumbMixin
)
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


class AreaEncounterUpdateView(
        SuccessUrlMixin, UpdateViewBreadcrumbMixin, UpdateView):
    """Update view for AreaEncounter."""

    template_name = "occurrence/areaencounter_form.html"
    form_class = AreaEncounterForm

    def get_object(self, queryset=None):
        """Accommodate custom object pk from url conf."""
        return self.model.objects.get(pk=self.kwargs["occ_pk"])


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
        object = TaxonAreaEncounter.objects.get(pk=self.kwargs.get("pk"))
        return object

    def get_breadcrumbs(self, request, obj=None, add=False):
        """Create a list of breadcrumbs as named tuples of ('name', 'url')."""
        return (
            Breadcrumb(_('Home'), reverse('home')),
            Breadcrumb(self.subject._meta.verbose_name_plural, self.subject.list_url()),
            Breadcrumb(self.subject.__str__(), self.subject.get_absolute_url()),
            Breadcrumb(self.object.__str__(), self.object.get_absolute_url())
        )


class CommunityAreaEncounterDetailView(DetailView):
    """DetailView for CommunityAreaEncounter."""

    model = TaxonAreaEncounter
    context_object_name = "original"
    template_name = "occurrence/communityareaencounter_detail.html"

    def get_object(self):
        """Get Object by pk."""
        object = CommunityAreaEncounter.objects.get(pk=self.kwargs.get("pk"))
        return object

    def get_breadcrumbs(self, request, obj=None, add=False):
        """Create a list of breadcrumbs as named tuples of ('name', 'url')."""
        return (
            Breadcrumb(_('Home'), reverse('home')),
            Breadcrumb(self.subject._meta.verbose_name_plural, self.subject.list_url()),
            Breadcrumb(self.subject.__str__(), self.subject.get_absolute_url()),
            Breadcrumb(self.object.__str__(), self.object.get_absolute_url())
        )


# ---------------------------------------------------------------------------#
# ObservationGroup Views
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
        context["encounter"] = self.get_initial()["encounter"]
        return context

    def get_success_url(self):
        """Success: show AE detail view."""
        return self.object.encounter.get_absolute_url()


class ObservationGroupUpdateView(UpdateViewBreadcrumbMixin, UpdateView):
    """Update view for ObservationGroup."""

    template_name = "occurrence/obsgroup_form.html"
    model = ObservationGroup

    def get_object(self, queryset=None):
        """Accommodate custom object pk from url conf."""
        return self.model.objects.get(pk=self.kwargs["obs_pk"])

    def get_context_data(self, **kwargs):
        """Custom context."""
        context = super(ObservationGroupUpdateView, self
                        ).get_context_data(**kwargs)
        context["subject"] = self.model._meta.verbose_name
        context["encounter"] = self.get_object().encounter
        return context

    def get_success_url(self):
        """Success: show AE detail view."""
        return self.object.encounter.get_absolute_url()


# ---------------------------------------------------------------------------#
# ObservationGroup Instance Views
#
class AssociatedSpeciesObservationCreateView(ObservationGroupCreateView):
    """Create view for AssociatedSpeciesObservation."""

    model = AssociatedSpeciesObservation
    form_class = AssociatedSpeciesObservationForm


class AssociatedSpeciesObservationUpdateView(ObservationGroupUpdateView):
    """Update view for AssociatedSpeciesObservation."""

    model = AssociatedSpeciesObservation
    form_class = AssociatedSpeciesObservationForm


class FireHistoryObservationCreateView(ObservationGroupCreateView):
    """Create view for AssociatedSpeciesObservation."""

    model = FireHistoryObservation
    form_class = FireHistoryObservationForm


class FireHistoryObservationUpdateView(ObservationGroupUpdateView):
    """Update view for AssociatedSpeciesObservation."""

    model = FireHistoryObservation
    form_class = FireHistoryObservationForm
