from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, TemplateView, ListView, DetailView, FormView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from django_fsm_log.models import StateLog

from wastd.utils import (
    ListViewBreadcrumbMixin,
    BreadcrumbContextMixin,
    DetailViewBreadcrumbMixin,
    ResourceDownloadMixin,
    PaginateMixin,
    Breadcrumb,
)
from .admin import (
    EncounterAdmin,
    AnimalEncounterAdmin,
    TurtleNestEncounterAdmin,
    LineTransectEncounterAdmin,
    TurtleNestDisturbanceObservationAdmin,
    DisturbanceObservationAdmin,
    TrackTallyObservationAdmin,
)
from .filters import (
    SurveyFilter,
    EncounterFilter,
    AnimalEncounterFilter,
    TurtleNestEncounterFilter,
    LineTransectEncounterFilter,
    TurtleNestDisturbanceObservationFilter,
    DisturbanceObservationFilter,
    TrackTallyObservationFilter,
)
from .forms import (
    SurveyMergeForm,
    SurveyCloseDuplicatesForm,
    SurveyMakeProductionForm,
    EncounterUpdateSurveyForm,
)
from .models import (
    Survey,
    SurveyMediaAttachment,
    Encounter,
    AnimalEncounter,
    TurtleNestEncounter,
    LineTransectEncounter,
    Area,
    TagObservation,
    TurtleNestDisturbanceObservation,
    DisturbanceObservation,
    TrackTallyObservation,
)
from .resources import (
    SurveyResource,
    EncounterResource,
    AnimalEncounterResource,
    TurtleNestEncounterResource,
    LineTransectEncounterResource,
    TurtleNestDisturbanceObservationResource,
    DisturbanceObservationResource,
    TrackTallyObservationResource,
)


class MapView(TemplateView):
    template_name = "observations/map.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"{settings.SITE_CODE} | Map"
        return context


class AreaSatelliteView(DetailView):
    model = Area
    template_name = "observations/area_satellite.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        area = self.get_object()
        # Provide geometry and bounds for the template map
        context["area_name"] = area.__str__()
        try:
            context["geom_geojson"] = area.geom.geojson
        except Exception:
            context["geom_geojson"] = None
        try:
            xmin, ymin, xmax, ymax = area.geom.extent
            context["bounds"] = {
                "south": ymin,
                "west": xmin,
                "north": ymax,
                "east": xmax,
            }
        except Exception:
            context["bounds"] = None
        return context


class SurveyList(ListViewBreadcrumbMixin, ResourceDownloadMixin, PaginateMixin, ListView):
    model = Survey
    template_name = "default_list.html"
    paginate_by = 20
    filter_class = SurveyFilter
    resource_class = SurveyResource
    resource_formats = ["csv", "xlsx"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_filter"] = SurveyFilter(self.request.GET, queryset=self.get_queryset())
        context["page_title"] = f"{settings.SITE_CODE} | Surveys"
        return context

    def get_queryset(self):
        qs = super().get_queryset().prefetch_related("reporter", "site", "encounter_set").order_by("-start_time")
        return SurveyFilter(self.request.GET, queryset=qs).qs


class SurveyDetail(DetailViewBreadcrumbMixin, DetailView):
    model = Survey

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context["page_title"] = f"{settings.SITE_CODE} | Survey {obj.pk}"
        return context


class SurveyMerge(BreadcrumbContextMixin, FormView):
    """Merge a survey into another.
    """
    template_name = "observations/survey_form.html"
    form_class = SurveyMergeForm

    def get_object(self):
        return Survey.objects.get(pk=self.kwargs["pk"])

    def get_breadcrumbs(self, request, obj=None, add=False):
        return (
            Breadcrumb("Home", reverse("home")),
            Breadcrumb("Surveys", reverse("observations:survey-list")),
            Breadcrumb(self.get_object().pk, self.get_object().get_absolute_url()),
            Breadcrumb("Merge duplicates", None),
        )

    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def post(self, request, *args, **kwargs):
        # If the user clicked Cancel, redirect back to the survey detail.
        if request.POST.get("cancel"):
            return redirect(self.get_success_url())
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        """Update encounters for the merged survey, display success message, return to survey detail.
        """
        survey = self.get_object()
        survey_to_merge = form.cleaned_data["survey_duplicates"]

        # Merge any Encounters on the old survey.
        encounters = Encounter.objects.filter(survey=survey_to_merge)
        for encounter in encounters:
            encounter.survey = survey
            encounter.save()

        # Merge any media attachments on the old survey.
        attachments = SurveyMediaAttachment.objects.filter(survey=survey_to_merge)
        for media in attachments:
            media.survey = survey
            media.save()

        # Update the merged survey to be non-production.
        survey_to_merge.production = False
        survey_to_merge.save()

        messages.success(self.request, f"Merged encounters and attachments for survey {survey_to_merge.pk} to survey {survey.pk}")
        return super().form_valid(form)


class SurveyCloseDuplicates(BreadcrumbContextMixin, UpdateView):
    model = Survey
    template_name = "observations/survey_form.html"
    form_class = SurveyCloseDuplicatesForm

    def get_breadcrumbs(self, request, obj=None, add=False):
        return (
            Breadcrumb("Home", reverse("home")),
            Breadcrumb("Surveys", reverse("observations:survey-list")),
            Breadcrumb(self.get_object().pk, self.get_object().get_absolute_url()),
            Breadcrumb("Close duplicates", None),
        )

    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def post(self, request, *args, **kwargs):
        # If the user clicked Cancel, redirect back to the survey detail.
        if request.POST.get("cancel"):
            return redirect(self.get_success_url())
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        """Close duplicates for a given Survey PK with the request user as actor.

        All duplicate Surveys will be curated and marked as "not production".
        The given Survey will be curated and marked as "production",
        adopt all Encounters from all duplicate surveys, and adjust its duration.

        See Survey.close_duplicates() for implementation details.
        """
        survey = self.get_object()
        msg = survey.close_duplicates(actor=self.request.user)
        messages.success(self.request, msg)
        return HttpResponseRedirect(self.get_success_url())


class SurveyMakeProduction(SurveyCloseDuplicates):
    form_class = SurveyMakeProductionForm

    def form_valid(self, form):
        survey = self.get_object()
        msg = survey.make_production()
        messages.success(self.request, msg)
        return HttpResponseRedirect(self.get_success_url())


class EncounterUpdateSurvey(BreadcrumbContextMixin, UpdateView):
    model = Encounter
    template_name = "observations/encounter_form.html"
    form_class = EncounterUpdateSurveyForm

    def get_breadcrumbs(self, request, obj=None, add=False):
        return (
            Breadcrumb("Home", reverse("home")),
            Breadcrumb("Encounters", reverse("observations:encounter-list")),
            Breadcrumb(self.get_object().pk, self.get_object().get_absolute_url()),
            Breadcrumb("Update survey", None),
        )

    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def post(self, request, *args, **kwargs):
        # If the user clicked Cancel, redirect back to the object detail view.
        if request.POST.get("cancel"):
            return redirect(self.get_success_url())
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        encounter = self.get_object()
        # Note that we don't have form.cleaned_data, because we bypass validation in this form.
        if "survey" in form.data and form.data["survey"]:
            encounter.survey = Survey.objects.get(pk=form.data["survey"])
            encounter.save()
        return HttpResponseRedirect(self.get_success_url())


class EncounterList(ListViewBreadcrumbMixin, ResourceDownloadMixin, PaginateMixin, ListView):
    model = Encounter
    template_name = "default_list.html"
    paginate_by = 20
    filter_class = EncounterFilter
    resource_class = EncounterResource
    resource_formats = ["csv", "xlsx"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_filter"] = EncounterFilter(
            self.request.GET, queryset=self.get_queryset()
        )
        context["model_admin"] = EncounterAdmin
        context["page_title"] = f"{settings.SITE_CODE} | Encounters"
        return context

    def get_queryset(self):
        qs = super().get_queryset().prefetch_related("observer", "area", "site").order_by("-when")
        return EncounterFilter(self.request.GET, queryset=qs).qs


class EncounterDetail(DetailViewBreadcrumbMixin, DetailView):
    model = Encounter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context["page_title"] = f"{settings.SITE_CODE} | Encounter {obj.pk}"
        return context


class EncounterCurate(LoginRequiredMixin, SingleObjectMixin, View):
    """Minimal view to handle HTTP request to mark a record as curated.
    """
    model = Encounter

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        # FIXME: Permission check
        if not request.user.is_staff:
            return HttpResponseForbidden("You do not have permission to curate this record")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.curate(by=request.user, description="Curated record as trustworthy")
        obj.save()
        messages.success(request, f"Curated {obj} as trustworthy")
        return HttpResponseRedirect(obj.get_absolute_url())


class EncounterFlag(LoginRequiredMixin, SingleObjectMixin, View):
    """Minimal view to handle HTTP request to mark a record as flagged.
    """

    def dispatch(self, request, *args, **kwargs):
        # FIXME: Permission check
        if not request.user.is_staff:
            return HttpResponseForbidden("You do not have permission to flag this record")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.flag(by=request.user, description="Flagged record as untrustworthy")
        obj.save()
        messages.warning(request, f"Flagged {obj} as untrustworthy")
        return HttpResponseRedirect(obj.get_absolute_url())


class EncounterReject(LoginRequiredMixin, SingleObjectMixin, View):
    """Minimal view to handle HTTP request to mark a record as rejected.
    """

    def dispatch(self, request, *args, **kwargs):
        # FIXME: Permission check
        if not request.user.is_staff:
            return HttpResponseForbidden("You do not have permission to reject this record")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.reject(by=request.user, description="Rejected record as untrustworthy")
        obj.save()
        messages.error(request, f"Rejected {obj} as untrustworthy")
        return HttpResponseRedirect(obj.get_absolute_url())


class AnimalEncounterList(ListViewBreadcrumbMixin, ResourceDownloadMixin, PaginateMixin, ListView):
    model = AnimalEncounter
    template_name = "default_list.html"
    paginate_by = 20
    filter_class = AnimalEncounterFilter
    resource_class = AnimalEncounterResource
    resource_formats = ["csv", "xlsx"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_filter"] = AnimalEncounterFilter(self.request.GET, queryset=self.get_queryset())
        context["model_admin"] = AnimalEncounterAdmin
        context["page_title"] = f"{settings.SITE_CODE} | Animal encounters"
        return context

    def get_queryset(self):
        qs = super().get_queryset().prefetch_related("observer", "reporter", "area", "site").order_by("-when")
        return AnimalEncounterFilter(self.request.GET, queryset=qs).qs


class AnimalEncounterDetail(DetailViewBreadcrumbMixin, DetailView):
    model = AnimalEncounter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context["tag_observations"] = TagObservation.objects.filter(encounter__in=[obj])
        context["state_logs"] = StateLog.objects.for_(obj)
        context["page_title"] = f"{settings.SITE_CODE} | Animal encounter {obj.pk}"
        return context


class AnimalEncounterCurate(EncounterCurate):
    model = AnimalEncounter


class AnimalEncounterFlag(EncounterFlag):
    model = AnimalEncounter


class AnimalEncounterReject(EncounterReject):
    model = AnimalEncounter


class TurtleNestEncounterList(ListViewBreadcrumbMixin, ResourceDownloadMixin, PaginateMixin, ListView):
    model = TurtleNestEncounter
    template_name = "default_list.html"
    paginate_by = 20
    filter_class = TurtleNestEncounterFilter
    resource_class = TurtleNestEncounterResource
    resource_formats = ["csv", "xlsx"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_filter"] = TurtleNestEncounterFilter(self.request.GET, queryset=self.get_queryset())
        context["model_admin"] = TurtleNestEncounterAdmin
        context["page_title"] = f"{settings.SITE_CODE} | Turtle nest encounters"
        return context

    def get_queryset(self):
        # FIXME: filtering via permissions model.
        qs = super().get_queryset()
        return TurtleNestEncounterFilter(self.request.GET, queryset=qs).qs


class TurtleNestEncounterDetail(DetailViewBreadcrumbMixin, DetailView):
    # FIXME: filtering via permissions model.
    model = TurtleNestEncounter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context["state_logs"] = StateLog.objects.for_(obj)
        context["page_title"] = f"{settings.SITE_CODE} | Turtle nest encounter {obj.pk}"
        return context


class TurtleNestEncounterCurate(EncounterCurate):
    model = TurtleNestEncounter


class TurtleNestEncounterFlag(EncounterFlag):
    model = TurtleNestEncounter


class TurtleNestEncounterReject(EncounterReject):
    model = TurtleNestEncounter


class TurtleNestDisturbanceObservationList(ListViewBreadcrumbMixin, ResourceDownloadMixin, PaginateMixin, ListView):
    model = TurtleNestDisturbanceObservation
    template_name = "default_list.html"
    paginate_by = 20
    filter_class = TurtleNestDisturbanceObservationFilter
    resource_class = TurtleNestDisturbanceObservationResource
    resource_formats = ["csv", "xlsx"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_filter"] = TurtleNestDisturbanceObservationFilter(self.request.GET, queryset=self.get_queryset())
        context["model_admin"] = TurtleNestDisturbanceObservationAdmin
        context["page_title"] = f"{settings.SITE_CODE} | Turtle nest disturbance observations"
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        return TurtleNestDisturbanceObservationFilter(self.request.GET, queryset=qs).qs


class DisturbanceObservationList(ListViewBreadcrumbMixin, ResourceDownloadMixin, PaginateMixin, ListView):
    model = DisturbanceObservation
    template_name = "default_list.html"
    paginate_by = 20
    filter_class = DisturbanceObservationFilter
    resource_class = DisturbanceObservationResource
    resource_formats = ["csv", "xlsx"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_filter"] = DisturbanceObservationFilter(self.request.GET, queryset=self.get_queryset())
        context["model_admin"] = DisturbanceObservationAdmin
        context["page_title"] = f"{settings.SITE_CODE} | Predators / disturbance observations"
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        return DisturbanceObservationFilter(self.request.GET, queryset=qs).qs


class LineTransectEncounterList(ListViewBreadcrumbMixin, ResourceDownloadMixin, PaginateMixin, ListView):
    model = LineTransectEncounter
    template_name = "default_list.html"
    paginate_by = 20
    filter_class = LineTransectEncounterFilter
    resource_class = LineTransectEncounterResource
    resource_formats = ["csv", "xlsx"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_filter"] = LineTransectEncounterFilter(self.request.GET, queryset=self.get_queryset())
        context["model_admin"] = LineTransectEncounterAdmin
        return context

    def get_queryset(self):
        qs = super().get_queryset().prefetch_related("observer", "reporter", "area", "site").order_by("-when")
        return LineTransectEncounterFilter(self.request.GET, queryset=qs).qs


class LineTransectEncounterDetail(DetailViewBreadcrumbMixin, DetailView):
    model = LineTransectEncounter


class TrackTallyObservationList(ListViewBreadcrumbMixin, ResourceDownloadMixin, PaginateMixin, ListView):
    model = TrackTallyObservation
    template_name = "default_list.html"
    paginate_by = 20
    filter_class = TrackTallyObservationFilter
    resource_class = TrackTallyObservationResource
    resource_formats = ["csv", "xlsx"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_filter"] = TrackTallyObservationFilter(self.request.GET, queryset=self.get_queryset())
        context["model_admin"] = TrackTallyObservationAdmin
        context["page_title"] = f"{settings.SITE_CODE} | Turtle track tally observations"
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        return TrackTallyObservationFilter(self.request.GET, queryset=qs).qs
