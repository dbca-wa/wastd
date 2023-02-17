from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django_fsm_log.models import StateLog
from export_download.views import ResourceDownloadMixin
from django_tables2 import RequestConfig, SingleTableView, tables

from shared.views import ListViewBreadcrumbMixin, DetailViewBreadcrumbMixin
from observations import admin
from .filters import (
    SurveyFilter,
    EncounterFilter,
    AnimalEncounterFilter,
    TurtleNestEncounterFilter,
    LineTransectEncounterFilter,
)
from .forms import (
    EncounterListFormHelper,
    AnimalEncounterForm,
    FlipperTagObservationFormSet,
)
from .models import (
    Survey,
    Encounter,
    AnimalEncounter,
    TurtleNestEncounter,
    LineTransectEncounter,
    TagObservation,
)
from .resources import (
    SurveyResource,
    EncounterResource,
    AnimalEncounterResource,
    TurtleNestEncounterResource,
    LineTransectEncounterResource,
    # LoggerEncounterResource
)
from .tasks import import_odka, update_names, reconstruct_surveys, resave_surveys


@csrf_exempt
def import_odka_view(request):
    """Import all available ODK-Aggregate forms."""
    msg = import_odka.now()
    messages.success(request, msg)
    return HttpResponseRedirect("/")


@csrf_exempt
def update_names_view(request):
    """Reconstruct animal encounter case histories and sighting status."""
    msg = update_names.now()
    messages.success(request, msg)
    return HttpResponseRedirect("/")


@csrf_exempt
def resave_surveys_view(request):
    """Re-save all Surveys."""
    msg = resave_surveys.now()
    messages.success(request, msg)
    return HttpResponseRedirect("/")


@csrf_exempt
def reconstruct_surveys_view(request):
    """Import all available ODK-Aggregate forms."""
    msg = reconstruct_surveys.now()
    messages.success(request, msg)
    return HttpResponseRedirect("/")


class HomeView(ListView):
    """HomeView."""

    model = AnimalEncounter
    template_name = "pages/map.html"

    def get_context_data(self, **kwargs):
        """Context data."""
        context = super(HomeView, self).get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context

    def get_queryset(self, **kwargs):
        """Queryset."""
        return AnimalEncounter.objects.filter(encounter_type="stranding")


# -----------------------------------------------------------------------------#
# Survey
class SurveyList(ListViewBreadcrumbMixin, ResourceDownloadMixin, ListView):
    model = Survey
    template_name = "default_list.html"
    paginate_by = 20
    filter_class = SurveyFilter
    resource_class = SurveyResource

    def get_context_data(self, **kwargs):
        context = super(SurveyList, self).get_context_data(**kwargs)
        context["list_filter"] = SurveyFilter(
            self.request.GET, queryset=self.get_queryset()
        )
        return context

    def get_queryset(self):
        qs = (
            super(SurveyList, self)
            .get_queryset()
            .prefetch_related("reporter", "site", "encounter_set", "campaign")
            .order_by("-start_time")
        )
        return SurveyFilter(self.request.GET, queryset=qs).qs


class SurveyDetail(DetailViewBreadcrumbMixin, DetailView):
    model = Survey

    def get_context_data(self, **kwargs):
        data = super(SurveyDetail, self).get_context_data(**kwargs)
        return data


def close_survey_duplicates(request, pk):
    """Close duplicates for a given Survey PK with the request user as actor.


    All duplicate Surveys will be curated and marked as "not production".
    The given Survey will be curated and marked as "production",
    adopt all Encounters from all duplicate surveys, and adjust its duration.

    See Survey.close_duplicates() for implementation details.
    """
    s = Survey.objects.get(pk=pk)
    msg = s.close_duplicates(actor=request.user)
    messages.success(request, msg)
    return HttpResponseRedirect(s.get_absolute_url())


# Encounters -----------------------------------------------------------------#
# https://kuttler.eu/en/post/using-django-tables2-filters-crispy-forms-together/
# http://stackoverflow.com/questions/25256239/
class EncounterTable(tables.Table):
    """A data table for Encounters."""

    class Meta:
        """Model opts."""

        model = Encounter
        exclude = ["as_html", "as_latex", "polymorphic_ctype", "encounter_ptr"]
        attrs = {"class": "table table-hover table-inverse table-sm"}


class AnimalEncounterTable(tables.Table):
    """A data table for AnimalEncounters."""

    class Meta:
        """Model opts."""

        model = AnimalEncounter
        exclude = ["as_html", "as_latex", "polymorphic_ctype", "encounter_ptr"]
        attrs = {"class": "table table-hover table-inverse table-sm"}


class PagedFilteredTableView(SingleTableView):
    """Generic class for paged, filtered SingleTableView.

    Inherit from this class and set the class level attributes (``model`` etc.).

    Source:
    http://kuttler.eu/post/using-django-tables2-filters-crispy-forms-together/
    """

    # Set these in instantiated classes:
    model = None
    table_class = None
    paginate_by = 10
    filter_class = None
    formhelper_class = None
    context_filter_name = "filter"

    def get_queryset(self, **kwargs):
        """Run the queryset through the specified filter class."""
        qs = super(PagedFilteredTableView, self).get_queryset()
        self.filter = self.filter_class(self.request.GET, queryset=qs)
        self.filter.form.helper = self.formhelper_class()
        return self.filter.qs

    def get_table(self, **kwargs):
        """Paginate the table as per paginate_by and request parameters."""
        table = super(PagedFilteredTableView, self).get_table()
        RequestConfig(
            self.request,
            paginate={
                "page": self.kwargs["page"] if "page" in self.kwargs else 1,
                "per_page": self.paginate_by,
            },
        ).configure(table)
        return table

    def get_context_data(self, **kwargs):
        """Add the specified filter class to context."""
        context = super(PagedFilteredTableView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        return context


class EncounterTableView(PagedFilteredTableView):
    """Filtered paginated TableView for Encounter."""

    model = Encounter
    table_class = EncounterTable
    paginate_by = 5
    filter_class = EncounterFilter
    formhelper_class = EncounterListFormHelper


# -----------------------------------------------------------------------------#
# Encounter
class EncounterList(ListViewBreadcrumbMixin, ResourceDownloadMixin, ListView):
    model = Encounter
    template_name = "default_list.html"
    paginate_by = 20
    filter_class = EncounterFilter
    resource_class = EncounterResource

    def get_context_data(self, **kwargs):
        context = super(EncounterList, self).get_context_data(**kwargs)
        context["list_filter"] = EncounterFilter(
            self.request.GET, queryset=self.get_queryset()
        )
        context["model_admin"] = admin.EncounterAdmin
        return context

    def get_queryset(self):
        qs = (
            super(EncounterList, self)
            .get_queryset()
            .prefetch_related("observer", "reporter", "area", "site")
            .order_by("-when")
        )
        return EncounterFilter(self.request.GET, queryset=qs).qs


class EncounterDetail(DetailViewBreadcrumbMixin, DetailView):
    model = Encounter

    def get_context_data(self, **kwargs):
        data = super(EncounterDetail, self).get_context_data(**kwargs)
        # data['tags'] = TagObservation.objects.filter(encounter__in=[self.get_object()])
        return data


class AnimalEncounterList(ListViewBreadcrumbMixin, ResourceDownloadMixin, ListView):
    model = AnimalEncounter
    template_name = "default_list.html"
    paginate_by = 20
    filter_class = AnimalEncounterFilter
    resource_class = AnimalEncounterResource

    def get_context_data(self, **kwargs):
        context = super(AnimalEncounterList, self).get_context_data(**kwargs)
        context["list_filter"] = AnimalEncounterFilter(
            self.request.GET, queryset=self.get_queryset()
        )
        context["model_admin"] = admin.AnimalEncounterAdmin
        return context

    def get_queryset(self):
        qs = (
            super(AnimalEncounterList, self)
            .get_queryset()
            .prefetch_related(
                "observer",
                "reporter",
                "area",
                "site",
                "site_of_first_sighting",
                "site_of_last_sighting",
            )
            .order_by("-when")
        )
        return AnimalEncounterFilter(self.request.GET, queryset=qs).qs


class AnimalEncounterCreate(CreateView):
    model = AnimalEncounter
    form_class = AnimalEncounterForm

    def get_context_data(self, **kwargs):
        data = super(AnimalEncounterCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data["flipper_tags"] = FlipperTagObservationFormSet(self.request.POST)
        else:
            data["flipper_tags"] = FlipperTagObservationFormSet()
        data["formset_prefix"] = "encounter"  # We set this in order to give the JavaScript something to match.
        return data

    def post(self, request, *args, **kwargs):
        # If the user clicked Cancel, redirect back to the list view.
        if request.POST.get("cancel"):
            return redirect("observations:animalencounter-list")
        return super(AnimalEncounterCreate, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        context = self.get_context_data()
        flipper_tags = context["flipper_tags"]
        with transaction.atomic():
            # Set observer and reporter to the request user.
            form.instance.observer = self.request.user
            form.instance.reporter = self.request.user
            self.object = form.save()
            if flipper_tags.is_valid():
                flipper_tags.instance = self.object
                flipper_tags.tag_type = "flipper-tag"
                flipper_tags.save()
        return super(AnimalEncounterCreate, self).form_valid(form)


class AnimalEncounterDetail(DetailViewBreadcrumbMixin, DetailView):
    model = AnimalEncounter

    def get_context_data(self, **kwargs):
        data = super(AnimalEncounterDetail, self).get_context_data(**kwargs)
        obj = self.get_object()
        data["tags"] = TagObservation.objects.filter(encounter__in=[obj])
        data["state_logs"] = StateLog.objects.for_(obj)
        return data


class AnimalEncounterUpdate(UpdateView):
    model = AnimalEncounter
    form_class = AnimalEncounterForm

    def get_context_data(self, **kwargs):
        data = super(AnimalEncounterUpdate, self).get_context_data(**kwargs)
        if self.request.POST:
            data["flipper_tags"] = FlipperTagObservationFormSet(
                self.request.POST, instance=self.object
            )
        else:
            data["flipper_tags"] = FlipperTagObservationFormSet(instance=self.object)
        data["formset_prefix"] = "encounter"  # We set this in order to give the JavaScript something to match.
        return data

    def post(self, request, *args, **kwargs):
        # If the user clicked Cancel, redirect back to the detail view.
        if request.POST.get("cancel"):
            return redirect(self.get_object().get_absolute_url())
        return super(AnimalEncounterUpdate, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        context = self.get_context_data()
        flipper_tags = context["flipper_tags"]
        with transaction.atomic():
            self.object = form.save()
            if flipper_tags.is_valid():
                flipper_tags.instance = self.object
                flipper_tags.save()
        return super(AnimalEncounterUpdate, self).form_valid(form)


class TurtleNestEncounterList(ListViewBreadcrumbMixin, ResourceDownloadMixin, ListView):
    model = TurtleNestEncounter
    template_name = "default_list.html"
    paginate_by = 20
    filter_class = TurtleNestEncounterFilter
    resource_class = TurtleNestEncounterResource

    def get_context_data(self, **kwargs):
        context = super(TurtleNestEncounterList, self).get_context_data(**kwargs)
        context["list_filter"] = TurtleNestEncounterFilter(
            self.request.GET, queryset=self.get_queryset()
        )
        context["model_admin"] = admin.TurtleNestEncounterAdmin
        return context

    def get_queryset(self):
        qs = (
            super(TurtleNestEncounterList, self)
            .get_queryset()
            .prefetch_related("observer", "reporter", "area", "site")
            .order_by("-when")
        )
        return TurtleNestEncounterFilter(self.request.GET, queryset=qs).qs


class TurtleNestEncounterDetail(DetailViewBreadcrumbMixin, DetailView):
    model = TurtleNestEncounter


class LineTransectEncounterList(
    ListViewBreadcrumbMixin, ResourceDownloadMixin, ListView
):
    model = LineTransectEncounter
    template_name = "default_list.html"
    paginate_by = 20
    filter_class = LineTransectEncounterFilter
    resource_class = LineTransectEncounterResource

    def get_context_data(self, **kwargs):
        context = super(LineTransectEncounterList, self).get_context_data(**kwargs)
        context["list_filter"] = LineTransectEncounterFilter(
            self.request.GET, queryset=self.get_queryset()
        )
        context["model_admin"] = admin.LineTransectEncounterAdmin
        return context

    def get_queryset(self):
        qs = (
            super(LineTransectEncounterList, self)
            .get_queryset()
            .prefetch_related("observer", "reporter", "area", "site")
            .order_by("-when")
        )
        return LineTransectEncounterFilter(self.request.GET, queryset=qs).qs


class LineTransectEncounterDetail(DetailViewBreadcrumbMixin, DetailView):
    model = LineTransectEncounter

    def get_context_data(self, **kwargs):
        data = super(LineTransectEncounterDetail, self).get_context_data(**kwargs)
        # data['tags'] = TagObservation.objects.filter(encounter__in=[self.get_object()])
        return data
