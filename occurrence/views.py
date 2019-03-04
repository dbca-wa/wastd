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
    DetailViewBreadcrumbMixin,
    UpdateViewBreadcrumbMixin,
    CreateViewBreadcrumbMixin
)
# select2 forms
# from .admin import (AreaForm, TaxonAreaForm, CommunityAreaForm)


# ---------------------------------------------------------------------------#
# Create Views
#
class AreaEncounterCreateView(CreateViewBreadcrumbMixin, CreateView):
    """Create view for AreaEncounter."""

    model = AreaEncounter
    form_class = AreaEncounterForm
    template_name = "occurrence/areaencounter_form.html"

    def get_breadcrumbs(self, request, obj=None, add=False):
        """Create a list of breadcrumbs as named tuples of ('name', 'url')."""
        return (
            Breadcrumb(_('Home'), reverse('home')),
            # Breadcrumb(self.model.verbose_name_plural, self.model.list_url()),
            Breadcrumb("Report new {0}".format(self.model._meta.verbose_name), None)
        )


class AreaEncounterUpdateView(
        SuccessUrlMixin, UpdateViewBreadcrumbMixin, UpdateView):
    """Update view for AreaEncounter."""

    model = AreaEncounter
    form_class = AreaEncounterForm
    template_name = "occurrence/areaencounter_form.html"

    def get_object(self, queryset=None):
        """Accommodate custom object pk from url conf."""
        return self.model.objects.get(pk=self.kwargs["pk"])


class TaxonAreaEncounterCreateView(AreaEncounterCreateView):
    """Create view for TaxonAreaEncounter."""

    model = TaxonAreaEncounter
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

    model = TaxonAreaEncounter
    form_class = TaxonAreaEncounterForm
    template_name = "occurrence/taxonareaencounter_form.html"


class CommunityAreaEncounterCreateView(AreaEncounterCreateView):
    """Create view for CommunityAreaEncounter."""

    model = CommunityAreaEncounter
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

    model = CommunityAreaEncounter
    form_class = CommunityAreaEncounterForm
    template_name = "occurrence/communityareaencounter_form.html"


# ---------------------------------------------------------------------------#
# Detail Views
#
class TaxonAreaEncounterDetailView(DetailViewBreadcrumbMixin, DetailView):
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
            Breadcrumb(self.object.subject._meta.verbose_name_plural, self.object.subject.list_url()),
            Breadcrumb(self.object.subject.__str__(), self.object.subject.get_absolute_url()),
            Breadcrumb(self.object.__str__(), self.object.get_absolute_url())
        )


class CommunityAreaEncounterDetailView(DetailViewBreadcrumbMixin, DetailView):
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
            Breadcrumb(self.object.subject._meta.verbose_name_plural, self.object.subject.list_url()),
            Breadcrumb(self.object.subject.__str__(), self.object.subject.get_absolute_url()),
            Breadcrumb(self.object.__str__(), self.object.get_absolute_url())
        )


# ---------------------------------------------------------------------------#
# ObservationGroup Views
#
class ObservationGroupCreateView(CreateViewBreadcrumbMixin, CreateView):
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

    def get_breadcrumbs(self, request, obj=None, add=False):
        """Create a list of breadcrumbs as named tuples of ('name', 'url')."""
        if "occ_pk" in self.kwargs:
            enc = AreaEncounter.objects.get(pk=self.kwargs["occ_pk"])
            return (
                Breadcrumb(_('Home'), reverse('home')),
                Breadcrumb(enc._meta.verbose_name_plural, enc.list_url()),
                Breadcrumb(enc.__str__(), enc.get_absolute_url()),
                Breadcrumb("Report new {0}".format(self.model._meta.verbose_name), None)
            )

        else:
            return (
                Breadcrumb(_('Home'), reverse('home')),
                Breadcrumb("Report new {0}".format(self.model._meta.verbose_name), None)
            )


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
