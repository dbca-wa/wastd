# -*- coding: utf-8 -*-
"""Occurrence views."""
from __future__ import unicode_literals

# from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from export_download.views import ResourceDownloadMixin

from occurrence import forms as occ_forms
from occurrence import models as occ_models
from occurrence import resources as occ_resources
from occurrence import filters as occ_filters
from taxonomy.models import Community, Taxon
from shared.utils import Breadcrumb
from shared.views import (  # noqa
    SuccessUrlMixin,
    ListViewBreadcrumbMixin,
    DetailViewBreadcrumbMixin,
    UpdateViewBreadcrumbMixin,
    CreateViewBreadcrumbMixin
)
# select2 forms
# from .admin import (AreaForm, TaxonAreaForm, CommunityAreaForm)


# ---------------------------------------------------------------------------#
# List Views
#
class TaxonAreaEncounterListView(
        ListViewBreadcrumbMixin,
        ResourceDownloadMixin,
        ListView):
    """A ListView for TaxonAreaEncounter."""

    model = occ_models.TaxonAreaEncounter
    template_name = "occurrence/areaencounter_list.html"
    resource_class = occ_resources.TaxonAreaEncounterResource
    resource_formats = ['csv', 'tsv', 'xls', 'json']
    filter_class = occ_filters.TaxonAreaEncounterFilter
    paginate_by = 12

    def get_context_data(self, **kwargs):
        """Context with list filter and current time."""
        context = super(TaxonAreaEncounterListView, self).get_context_data(**kwargs)
        context['show_subject'] = True
        context['list_filter'] = occ_filters.TaxonAreaEncounterFilter(
            self.request.GET,
            queryset=self.get_queryset()
        )
        return context

    def get_queryset(self):
        """Queryset with custom filter."""
        queryset = occ_models.TaxonAreaEncounter.objects.all().prefetch_related(
            "taxon",
            # "conservationactivity_set",
        )
        return occ_filters.TaxonAreaEncounterFilter(
            self.request.GET,
            queryset=queryset
        ).qs


class CommunityAreaEncounterListView(
        ListViewBreadcrumbMixin,
        ResourceDownloadMixin,
        ListView):
    """A ListView for CommunityAreaEncounter."""

    model = occ_models.CommunityAreaEncounter
    template_name = "occurrence/areaencounter_list.html"
    resource_class = occ_resources.CommunityAreaEncounterResource
    resource_formats = ['csv', 'tsv', 'xls', 'json']
    filter_class = occ_filters.CommunityAreaEncounterFilter
    paginate_by = 12

    def get_context_data(self, **kwargs):
        """Context with list filter and current time."""
        context = super(CommunityAreaEncounterListView, self).get_context_data(**kwargs)
        context['show_subject'] = True
        context['list_filter'] = occ_filters.CommunityAreaEncounterFilter(
            self.request.GET,
            queryset=self.get_queryset()
        )
        return context

    def get_queryset(self):
        """Queryset with custom filter."""
        queryset = occ_models.CommunityAreaEncounter.objects.all().prefetch_related(
            "community",
            # "conservationactivity_set",
        )
        return occ_filters.CommunityAreaEncounterFilter(
            self.request.GET,
            queryset=queryset
        ).qs


# ---------------------------------------------------------------------------#
# Create Views
#
class AreaEncounterCreateView(CreateViewBreadcrumbMixin, CreateView):
    """Create view for AreaEncounter."""

    model = occ_models.AreaEncounter
    form_class = occ_forms.AreaEncounterForm
    template_name = "occurrence/areaencounter_form.html"

    def get_breadcrumbs(self, request, obj=None, add=False):
        """Create a list of breadcrumbs as named tuples of ('name', 'url')."""
        return (
            Breadcrumb(_('Home'), reverse('home')),
            Breadcrumb(self.model._meta.verbose_name_plural, self.model.list_url()),
            Breadcrumb("Report new {0}".format(self.model._meta.verbose_name), None)
        )


class AreaEncounterUpdateView(
        SuccessUrlMixin, UpdateViewBreadcrumbMixin, UpdateView):
    """Update view for AreaEncounter."""

    model = occ_models.AreaEncounter
    form_class = occ_forms.AreaEncounterForm
    template_name = "occurrence/areaencounter_form.html"

    # def get_object(self, queryset=None):
    #     """Accommodate custom object pk from url conf."""
    #     return self.model.objects.get(pk=self.kwargs["pk"])


class TaxonAreaEncounterCreateView(AreaEncounterCreateView):
    """Create view for TaxonAreaEncounter."""

    model = occ_models.TaxonAreaEncounter
    form_class = occ_forms.TaxonAreaEncounterForm

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

    model = occ_models.TaxonAreaEncounter
    form_class = occ_forms.TaxonAreaEncounterForm
    template_name = "occurrence/taxonareaencounter_form.html"


class CommunityAreaEncounterCreateView(AreaEncounterCreateView):
    """Create view for CommunityAreaEncounter."""

    model = occ_models.CommunityAreaEncounter
    form_class = occ_forms.CommunityAreaEncounterForm

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

    model = occ_models.CommunityAreaEncounter
    form_class = occ_forms.CommunityAreaEncounterForm
    template_name = "occurrence/communityareaencounter_form.html"


# ---------------------------------------------------------------------------#
# Detail Views
#
class TaxonAreaEncounterDetailView(DetailViewBreadcrumbMixin, DetailView):
    """DetailView for TaxonAreaEncounter."""

    model = occ_models.TaxonAreaEncounter
    context_object_name = "original"
    template_name = "occurrence/taxonareaencounter_detail.html"

    def get_breadcrumbs(self, request, obj=None, add=False):
        """Create a list of breadcrumbs as named tuples of ('name', 'url')."""
        return (
            Breadcrumb(_('Home'), reverse('home')),
            Breadcrumb(self.object.subject._meta.verbose_name_plural, self.object.subject.list_url()),
            Breadcrumb(self.model._meta.verbose_name_plural, self.model.list_url()),
            Breadcrumb(self.object.subject.__str__(), self.object.subject.get_absolute_url()),
            Breadcrumb(self.object.__str__(), self.object.get_absolute_url())
        )


class CommunityAreaEncounterDetailView(DetailViewBreadcrumbMixin, DetailView):
    """DetailView for CommunityAreaEncounter."""

    model = occ_models.CommunityAreaEncounter
    context_object_name = "original"
    template_name = "occurrence/communityareaencounter_detail.html"

    def get_breadcrumbs(self, request, obj=None, add=False):
        """Create a list of breadcrumbs as named tuples of ('name', 'url')."""
        return (
            Breadcrumb(_('Home'), reverse('home')),
            Breadcrumb(self.object.subject._meta.verbose_name_plural, self.object.subject.list_url()),
            Breadcrumb(self.model._meta.verbose_name_plural, self.model.list_url()),
            Breadcrumb(self.object.subject.__str__(), self.object.subject.get_absolute_url()),
            Breadcrumb(self.object.__str__(), self.object.get_absolute_url())
        )


# ---------------------------------------------------------------------------#
# ObservationGroup Views
#
class ObservationGroupCreateView(CreateViewBreadcrumbMixin, CreateView):
    """Base CreateView for ObservationGroup."""

    template_name = "occurrence/obsgroup_form.html"
    model = occ_models.ObservationGroup

    def get_initial(self):
        """Initial form values."""
        initial = dict()
        if "occ_pk" in self.kwargs:
            initial["encounter"] = occ_models.AreaEncounter.objects.get(pk=self.kwargs["occ_pk"])
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
            enc = occ_models.AreaEncounter.objects.get(pk=self.kwargs["occ_pk"])
            return (
                Breadcrumb(_('Home'), reverse('home')),
                Breadcrumb(enc._meta.verbose_name_plural, enc.list_url()),
                Breadcrumb(enc.__str__(), enc.get_absolute_url()),
                Breadcrumb(_("Report new {0}").format(self.model._meta.verbose_name), None)
            )

        else:
            return (
                Breadcrumb(_('Home'), reverse('home')),
                Breadcrumb(_("Report new {0}").format(self.model._meta.verbose_name), None)
            )


class ObservationGroupUpdateView(UpdateViewBreadcrumbMixin, UpdateView):
    """Update view for ObservationGroup."""

    template_name = "occurrence/obsgroup_form.html"
    model = occ_models.ObservationGroup

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

    model = occ_models.AssociatedSpeciesObservation
    form_class = occ_forms.AssociatedSpeciesObservationForm


class AssociatedSpeciesObservationUpdateView(ObservationGroupUpdateView):
    """Update view for AssociatedSpeciesObservation."""

    model = occ_models.AssociatedSpeciesObservation
    form_class = occ_forms.AssociatedSpeciesObservationForm


class FireHistoryObservationCreateView(ObservationGroupCreateView):
    """Create view for FireHistoryObservation."""

    model = occ_models.FireHistoryObservation
    form_class = occ_forms.FireHistoryObservationForm


class FireHistoryObservationUpdateView(ObservationGroupUpdateView):
    """Update view for FireHistoryObservation."""

    model = occ_models.FireHistoryObservation
    form_class = occ_forms.FireHistoryObservationForm


class FileAttachmentObservationCreateView(ObservationGroupCreateView):
    """Create view for FileAttachmentObservation."""

    model = occ_models.FileAttachmentObservation
    form_class = occ_forms.FileAttachmentObservationForm

    def get_initial(self):
        """Initial form values."""
        initial = super(FileAttachmentObservationCreateView, self).get_initial()
        initial["author"] = initial["encounter"].encountered_by
        return initial


class FileAttachmentObservationUpdateView(ObservationGroupUpdateView):
    """Update view for FileAttachmentObservation."""

    model = occ_models.FileAttachmentObservation
    form_class = occ_forms.FileAttachmentObservationForm


class AreaAssessmentObservationCreateView(ObservationGroupCreateView):
    """Create view for AreaAssessmentObservation."""

    model = occ_models.AreaAssessmentObservation
    form_class = occ_forms.AreaAssessmentObservationForm


class AreaAssessmentObservationUpdateView(ObservationGroupUpdateView):
    """Update view for AreaAssessmentObservation."""

    model = occ_models.AreaAssessmentObservation
    form_class = occ_forms.AreaAssessmentObservationForm
