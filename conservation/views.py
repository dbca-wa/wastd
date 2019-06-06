# -*- coding: utf-8 -*-
"""Conservation views."""
from __future__ import unicode_literals
from dateutil.relativedelta import relativedelta

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
class ConservationThreatListView(
        ListViewBreadcrumbMixin,
        ResourceDownloadMixin,
        ListView):
    """A ListView for ConservationAction."""

    model = cons_models.ConservationThreat
    template_name = "pages/default_list.html"
    resource_class = cons_resources.ConservationThreatResource
    resource_formats = ['csv', 'tsv', 'xls', 'json']
    filter_class = cons_filters.ConservationThreatFilter
    paginate_by = 12

    def get_context_data(self, **kwargs):
        """Context with list filter and current time."""
        context = super(ConservationThreatListView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['list_filter'] = cons_filters.ConservationThreatFilter(
            self.request.GET,
            queryset=self.get_queryset()
        )
        return context

    def get_queryset(self):
        """Queryset with custom filter."""
        queryset = cons_models.ConservationThreat.objects.all().prefetch_related(
            "taxa",
            "communities",
            "document",
            "category"
        )
        return cons_filters.ConservationThreatFilter(
            self.request.GET,
            queryset=queryset
        ).qs


class ConservationActionListView(
        ListViewBreadcrumbMixin,
        ResourceDownloadMixin,
        ListView):
    """A ListView for ConservationAction."""

    model = cons_models.ConservationAction
    template_name = "pages/default_list.html"
    resource_class = cons_resources.ConservationActionResource
    resource_formats = ['csv', 'tsv', 'xls', 'json']
    filter_class = cons_filters.ConservationActionFilter
    paginate_by = 12

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


class DocumentListView(
        ListViewBreadcrumbMixin,
        ResourceDownloadMixin,
        ListView):
    """A ListView for Documents."""

    model = cons_models.Document
    template_name = "pages/default_list.html"
    resource_class = cons_resources.DocumentResource
    resource_formats = ['csv', 'tsv', 'xls', 'json']
    filter_class = cons_filters.DocumentFilter
    paginate_by = 12

    def get_context_data(self, **kwargs):
        """Context with list filter and current time."""
        context = super(DocumentListView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['list_filter'] = cons_filters.DocumentFilter(
            self.request.GET,
            queryset=self.get_queryset()
        )
        return context

    def get_queryset(self):
        """Queryset with custom filter."""
        queryset = cons_models.Document.objects.all().prefetch_related(
            "taxa",
            "communities",
            "conservationaction_set",
            "conservationthreat_set",
        )
        return cons_filters.DocumentFilter(
            self.request.GET,
            queryset=queryset
        ).qs


# ---------------------------------------------------------------------------#
# Detail Views
#
class ConservationThreatDetailView(DetailViewBreadcrumbMixin, DetailView):
    """ConservationThreat DetailView."""

    model = cons_models.ConservationThreat
    template_name = "pages/default_detail.html"

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


class ConservationActionDetailView(DetailViewBreadcrumbMixin, DetailView):
    """Conservation Action DetailView."""

    model = cons_models.ConservationAction
    template_name = "pages/default_detail.html"

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


class DocumentDetailView(DetailViewBreadcrumbMixin, DetailView):
    """Document DetailView."""

    model = cons_models.Document
    template_name = "pages/default_detail.html"

    def get_object(self):
        """Get object, handle 404, refetch for performance."""
        obj = self.model.objects.filter(
            pk=self.kwargs.get("pk")
        ).prefetch_related(
            "communities",
            "taxa",

        ).first()
        if not obj:
            raise Http404
        return obj


# ---------------------------------------------------------------------------#
# Update Views
#
class ConservationThreatUpdateView(
        SuccessUrlMixin, UpdateViewBreadcrumbMixin, UpdateView):
    """Update view for ConservationThreat."""

    template_name = "pages/default_form.html"
    form_class = cons_forms.ConservationThreatForm
    model = cons_models.ConservationThreat

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

    def get_context_data(self, **kwargs):
        """Context with inline formsets."""
        data = super(ConservationThreatUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['formset'] = cons_forms.FileAttachmentFormSet(self.request.POST, instance=self.object)
        else:
            data['formset'] = cons_forms.FileAttachmentFormSet(instance=self.object)
        data["formset_helper"] = cons_forms.FileAttachmentFormSetHelper()
        return data


class ConservationActionUpdateView(
        SuccessUrlMixin, UpdateViewBreadcrumbMixin, UpdateView):
    """Update view for ConservationAction."""

    template_name = "pages/default_form.html"
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

    def get_context_data(self, **kwargs):
        """Context with inline formsets."""
        data = super(ConservationActionUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['formset'] = cons_forms.FileAttachmentFormSet(self.request.POST, instance=self.object)
        else:
            data['formset'] = cons_forms.FileAttachmentFormSet(instance=self.object)
        data["formset_helper"] = cons_forms.FileAttachmentFormSetHelper()
        return data


class ConservationActivityUpdateView(
        SuccessUrlMixin, UpdateViewBreadcrumbMixin, UpdateView):
    """Update view for ConservationActivity."""

    template_name = "pages/default_form.html"
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

    def get_context_data(self, **kwargs):
        """Context with inline formsets."""
        data = super(ConservationActivityUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['formset'] = cons_forms.FileAttachmentFormSet(self.request.POST, instance=self.object)
        else:
            data['formset'] = cons_forms.FileAttachmentFormSet(instance=self.object)
        data["formset_helper"] = cons_forms.FileAttachmentFormSetHelper()
        return data


class DocumentUpdateView(
        SuccessUrlMixin, UpdateViewBreadcrumbMixin, UpdateView):
    """Update view for Document."""

    template_name = "pages/default_form.html"
    form_class = cons_forms.DocumentForm
    model = cons_models.Document

    def get_object(self, queryset=None):
        """Get object, handle 404, refetch for performance."""
        obj = self.model.objects.filter(
            pk=self.kwargs.get("pk")
        ).prefetch_related(
            "taxa", "communities",
        ).first()
        if not obj:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        """Context with inline formsets."""
        data = super(DocumentUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['formset'] = cons_forms.FileAttachmentFormSet(self.request.POST, instance=self.object)
        else:
            data['formset'] = cons_forms.FileAttachmentFormSet(instance=self.object)
        data["formset_helper"] = cons_forms.FileAttachmentFormSetHelper()
        return data


# ---------------------------------------------------------------------------#
# Create Views
#
class ConservationThreatCreateView(
        SuccessUrlMixin, CreateViewBreadcrumbMixin, CreateView):
    """Create view for ConservationThreat."""

    template_name = "pages/default_form.html"
    form_class = cons_forms.ConservationThreatForm
    model = cons_models.ConservationThreat

    def get_initial(self):
        """Initial form values."""
        initial = super(ConservationThreatCreateView, self).get_initial()
        initial["encountered_on"] = timezone.now()
        if self.request.user:
            initial["encountered_by"] = self.request.user
        if "taxa" in self.request.GET:
            initial["taxa"] = self.request.GET["taxa"]
        if "communities" in self.request.GET:
            initial["communities"] = self.request.GET["communities"]
        if "document" in self.request.GET:
            initial["document_id"] = self.request.GET["document_id"]
        if "occurrence_area_code" in self.request.GET:
            initial["occurrence_area_code"] = self.request.GET["occurrence_area_code"]
        if "encountered_on" in self.request.GET:
            initial["encountered_on"] = self.request.GET["encountered_on"]
        if "encountered_by" in self.request.GET:
            initial["encountered_by"] = self.request.GET["encountered_by"]
        return initial


class ConservationActionCreateView(
        SuccessUrlMixin, CreateViewBreadcrumbMixin, CreateView):
    """Create view for ConservationAction."""

    template_name = "pages/default_form.html"
    form_class = cons_forms.ConservationActionForm
    model = cons_models.ConservationAction

    def get_initial(self):
        """Initial form values.

        TODO create different urls.
        """
        initial = super(ConservationActionCreateView, self).get_initial()
        initial["encountered_on"] = timezone.now()  # TODO format correctly https://github.com/dbca-wa/wastd/issues/184
        if self.request.user:
            initial["encountered_by"] = self.request.user
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
        SuccessUrlMixin, CreateViewBreadcrumbMixin, CreateView):
    """Create view for ConservationActivity."""

    template_name = "pages/default_form.html"
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

    def get_context_data(self, **kwargs):
        """Context with inline formsets."""
        data = super(ConservationActivityCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['formset'] = cons_forms.FileAttachmentFormSet(self.request.POST)
        else:
            data['formset'] = cons_forms.FileAttachmentFormSet()
        data["formset_helper"] = cons_forms.FileAttachmentFormSetHelper()
        return data


class TaxonConservationListingCreateView(
        SuccessUrlMixin, CreateViewBreadcrumbMixin, CreateView):
    """Create view for Taxon Conservation Listing."""

    template_name = "pages/default_form.html"
    form_class = cons_forms.TaxonConservationListingForm
    model = cons_models.TaxonConservationListing

    def get_initial(self):
        """Initial form values."""
        initial = super(TaxonConservationListingCreateView, self).get_initial()
        if "taxon" in self.request.GET:
            initial["taxon"] = self.request.GET["taxon"]
        initial["proposed_on"] = timezone.now()
        initial["review_due"] = timezone.now() + relativedelta(years=+5)
        return initial

    def get_context_data(self, **kwargs):
        """Context with inline formsets."""
        data = super(TaxonConservationListingCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['formset'] = cons_forms.FileAttachmentFormSet(self.request.POST)
        else:
            data['formset'] = cons_forms.FileAttachmentFormSet()
        data["formset_helper"] = cons_forms.FileAttachmentFormSetHelper()
        return data

    def get_breadcrumbs(self, request, obj=None, add=False):
        """Create a list of breadcrumbs as named tuples of ('name', 'url')."""
        return (
            Breadcrumb(_('Home'), reverse('home')),
            Breadcrumb(_("Nominate any current, terminal taxonomic name for conservation listing in Western Australia"),
                       reverse("conservation:taxonconservationlisting-create"))
        )


class CommunityConservationListingCreateView(
        SuccessUrlMixin, CreateViewBreadcrumbMixin, CreateView):
    """Create view for Community Conservation Listing."""

    template_name = "pages/default_form.html"
    form_class = cons_forms.CommunityConservationListingForm
    model = cons_models.CommunityConservationListing

    def get_initial(self):
        """Initial form values."""
        initial = super(CommunityConservationListingCreateView, self).get_initial()
        if "community" in self.request.GET:
            initial["community"] = self.request.GET["community"]
        initial["proposed_on"] = timezone.now()
        initial["review_due"] = timezone.now() + relativedelta(years=+5)
        return initial

    def get_context_data(self, **kwargs):
        """Context with inline formsets."""
        data = super(CommunityConservationListingCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['formset'] = cons_forms.FileAttachmentFormSet(self.request.POST)
        else:
            data['formset'] = cons_forms.FileAttachmentFormSet()
        data["formset_helper"] = cons_forms.FileAttachmentFormSetHelper()
        return data

    def get_breadcrumbs(self, request, obj=None, add=False):
        """Create a list of breadcrumbs as named tuples of ('name', 'url')."""
        return (
            Breadcrumb(_('Home'), reverse('home')),
            Breadcrumb(_("Nominate any ecological community for conservation listing in Western Australia"),
                       reverse("conservation:communityconservationlisting-create"))
        )


class DocumentCreateView(
        SuccessUrlMixin, CreateViewBreadcrumbMixin, CreateView):
    """Create view for Document."""

    template_name = "pages/default_form.html"
    form_class = cons_forms.DocumentForm
    model = cons_models.Document

    def get_initial(self):
        """Initial form values."""
        initial = super(DocumentCreateView, self).get_initial()
        # if "pk" in self.kwargs:
        #     initial["conservation_action"] = cons_models.ConservationAction.objects.get(pk=self.kwargs["pk"])
        return initial

    def get_context_data(self, **kwargs):
        """Context with inline formsets."""
        data = super(DocumentCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['formset'] = cons_forms.FileAttachmentFormSet(self.request.POST)
        else:
            data['formset'] = cons_forms.FileAttachmentFormSet()
        data["formset_helper"] = cons_forms.FileAttachmentFormSetHelper()
        return data
