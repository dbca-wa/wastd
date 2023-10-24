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
from django.db import connection
from django.http import StreamingHttpResponse
import json
import datetime



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
    resource_formats = ["csv", "xlsx"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_filter"] = SurveyFilter(self.request.GET, queryset=self.get_queryset())
        context["object_count"] = self.get_queryset().count()
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


#This just dumps the database as json for use by external tools such as PowerBI or Shiny
def nestAndTracks(request):
    query = '''
SELECT 
    e."id" as encounter_id,
    e."status",
    org."label" AS "data_owner",
    TO_CHAR(e."when" AT TIME ZONE \'Australia/Perth\', \'YYYY-MM-DD\') AS "date",
    TO_CHAR(e."when" AT TIME ZONE \'Australia/Perth\', \'HH24:MI:SS\') AS "time",
    CASE 
        WHEN EXTRACT(HOUR FROM e."when" AT TIME ZONE \'Australia/Perth\') < 12 THEN
            TO_CHAR(e."when" AT TIME ZONE \'Australia/Perth\' - INTERVAL \'1 day\', \'YYYY-MM-DD\')
        ELSE
            TO_CHAR(e."when" AT TIME ZONE \'Australia/Perth\', \'YYYY-MM-DD\')
    END AS "turtle_date",
    site."name" AS "site_name",
    ST_Y(e."where") as latitude,
    ST_X(e."where") as longitude,
    area."name" AS "area_name",
    e."name" AS encounter_name,
    obs."name" AS "observer",
    rep."name" AS "reporter",
    e."encounter_type",
    e."comments",
    t."nest_age",
    t."nest_type",
    t."species",
    t."habitat",
    t."disturbance",
    t."nest_tagged",
    t."logger_found",
    t."eggs_counted",
    t."hatchlings_measured",
    t."fan_angles_measured",
    n."eggs_laid",
    n."egg_count",
    n."no_egg_shells",
    n."no_live_hatchlings_neck_of_nest",
    n."no_live_hatchlings",
    n."no_dead_hatchlings",
    n."no_undeveloped_eggs",
    n."no_unhatched_eggs",
    n."no_unhatched_term",
    n."no_depredated_eggs",
    n."nest_depth_top",
    n."nest_depth_bottom",
    n."sand_temp",
    n."air_temp",
    n."water_temp",
    n."egg_temp",
    n."comments" AS "turtle_observation_comments",
    tag."comments" AS "tag_observation_comments",
    hatch."bearing_to_water_degrees",
    hatch."bearing_leftmost_track_degrees",
    hatch."bearing_rightmost_track_degrees",
    hatch."no_tracks_main_group_max",
    hatch."outlier_tracks_present",
    hatch."path_to_sea_comments",
    hatch."hatchling_emergence_time_known",
    hatch."hatchling_emergence_time",
    hatch."hatchling_emergence_time_accuracy",
    hatch."cloud_cover_at_emergence_known",
    hatch."cloud_cover_at_emergence",
    tag."status" AS "nest_tag_status",
    tag."flipper_tag_id",
    TO_CHAR(tag."date_nest_laid" AT TIME ZONE \'Australia/Perth\', \'YYYY-MM-DD\') AS "date_nest_laid",
    tag."tag_label"
FROM 
    "observations_turtlenestencounter" t
INNER JOIN 
    "observations_encounter" e ON (t."encounter_ptr_id" = e."id")
LEFT JOIN 
    "observations_area" area ON (e."area_id" = area."id")
LEFT JOIN 
    "observations_area" site ON (e."site_id" = site."id")
LEFT JOIN 
    "observations_survey" survey ON (e."survey_id" = survey."id")
LEFT JOIN 
    "users_user" obs ON (e."observer_id" = obs."id")
LEFT JOIN 
    "users_user" rep ON (e."reporter_id" = rep."id")
LEFT JOIN 
    "observations_observation" o ON (e."id" = o."encounter_id" AND o."polymorphic_ctype_id" IN (26))
LEFT JOIN 
    "observations_turtlenestobservation" n ON (o."id" = n."observation_ptr_id")
LEFT JOIN 
    "observations_observation" obs_tag ON (e."id" = obs_tag."encounter_id" AND obs_tag."polymorphic_ctype_id" IN (38))
LEFT JOIN 
    "observations_nesttagobservation" tag ON (obs_tag."id" = tag."observation_ptr_id")
LEFT JOIN 
    "observations_observation" obs_hatch ON (e."id" = obs_hatch."encounter_id" AND obs_hatch."polymorphic_ctype_id" IN (279))
LEFT JOIN 
    "observations_turtlehatchlingemergenceobservation" hatch ON (obs_hatch."id" = hatch."observation_ptr_id")
LEFT JOIN 
  "observations_campaign" c ON (e."campaign_id" = c."id")
LEFT JOIN 
  "users_organisation" org ON (c."owner_id" = org."id")
WHERE 
    survey."production" = true
ORDER BY 
    e."when" DESC
    '''
 
    response = StreamingHttpResponse(stream_data(query), content_type="application/json")
    return response

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)

def stream_data(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        
        # Get column names from cursor.description
        columns = [col[0] for col in cursor.description]
        
        yield '['  # Start of JSON array
        first_row = True
        row = cursor.fetchone()
        while row:
            if not first_row:
                yield ','
            else:
                first_row = False
            
            # Convert row data to dictionary with column names as keys
            row_dict = dict(zip(columns, row))
            
            # Convert the dictionary to JSON and yield
            yield json.dumps(row_dict, cls=DateTimeEncoder)
            
            row = cursor.fetchone()
        yield ']'  # End of JSON array
