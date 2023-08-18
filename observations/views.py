from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, TemplateView, ListView, DetailView
from django.views.generic.detail import SingleObjectMixin
from django_fsm_log.models import StateLog
from wastd.utils import ListViewBreadcrumbMixin, DetailViewBreadcrumbMixin, ResourceDownloadMixin

from .admin import (
    EncounterAdmin,
    AnimalEncounterAdmin,
    TurtleNestEncounterAdmin,
    LineTransectEncounterAdmin,
)
from .filters import (
    SurveyFilter,
    EncounterFilter,
    AnimalEncounterFilter,
    TurtleNestEncounterFilter,
    LineTransectEncounterFilter,
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
)


class MapView(TemplateView):
    template_name = "observations/map.html"


class SurveyList(ListViewBreadcrumbMixin, ResourceDownloadMixin, ListView):
    model = Survey
    template_name = "default_list.html"
    paginate_by = 20
    filter_class = SurveyFilter
    resource_class = SurveyResource
    resource_formats = ['csv', 'xlsx']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_filter"] = SurveyFilter(self.request.GET, queryset=self.get_queryset())
        context["object_count"] = self.get_queryset().count()
        context["page_title"] = f"{settings.SITE_CODE} | Surveys"
        return context

    def get_queryset(self):
        qs = super().get_queryset().prefetch_related("reporter", "site", "encounter_set", "campaign").order_by("-start_time")
        return SurveyFilter(self.request.GET, queryset=qs).qs


class SurveyDetail(DetailViewBreadcrumbMixin, DetailView):
    model = Survey

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context["page_title"] = f"{settings.SITE_CODE} | Survey {obj.pk}"
        return context


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


class EncounterList(ListViewBreadcrumbMixin, ResourceDownloadMixin, ListView):
    model = Encounter
    template_name = "default_list.html"
    paginate_by = 20
    filter_class = EncounterFilter
    resource_class = EncounterResource
    resource_formats = ['csv', 'xlsx']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_filter"] = EncounterFilter(
            self.request.GET, queryset=self.get_queryset()
        )
        context["model_admin"] = EncounterAdmin
        context["page_title"] = f"{settings.SITE_CODE} | Encounters"
        return context

    def get_queryset(self):
        qs = super().get_queryset().prefetch_related("observer", "reporter", "area", "site").order_by("-when")
        return EncounterFilter(self.request.GET, queryset=qs).qs


class EncounterDetail(DetailViewBreadcrumbMixin, DetailView):
    model = Encounter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context["page_title"] = f"{settings.SITE_CODE} | Encounter {obj.pk}"
        # data['tags'] = TagObservation.objects.filter(encounter__in=[self.get_object()])
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


class AnimalEncounterList(ListViewBreadcrumbMixin, ResourceDownloadMixin, ListView):
    model = AnimalEncounter
    template_name = "default_list.html"
    paginate_by = 20
    filter_class = AnimalEncounterFilter
    resource_class = AnimalEncounterResource
    resource_formats = ["csv", "xlsx"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        context["list_filter"] = AnimalEncounterFilter(self.request.GET, queryset=qs)
        context["model_admin"] = AnimalEncounterAdmin
        context["object_count"] = qs.count()
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


class TurtleNestEncounterList(ListViewBreadcrumbMixin, ResourceDownloadMixin, ListView):
    model = TurtleNestEncounter
    template_name = "default_list.html"
    paginate_by = 20
    filter_class = TurtleNestEncounterFilter
    resource_class = [
        TurtleNestEncounterResource,
    ]
    resource_formats = ['csv', 'xlsx']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        context["list_filter"] = TurtleNestEncounterFilter(self.request.GET, queryset=qs)
        context["model_admin"] = TurtleNestEncounterAdmin
        context["object_count"] = qs.count()
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


class LineTransectEncounterList(ListViewBreadcrumbMixin, ResourceDownloadMixin, ListView):
    model = LineTransectEncounter
    template_name = "default_list.html"
    paginate_by = 20
    filter_class = LineTransectEncounterFilter
    resource_class = LineTransectEncounterResource
    resource_formats = ['csv', 'xlsx']

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
