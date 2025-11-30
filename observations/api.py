import datetime
from django.db import connection
from django.http import HttpResponseBadRequest, StreamingHttpResponse, JsonResponse
from django.urls import reverse
from django.views.generic.base import View
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.gis.geos import Point
import json
from wastd.utils import ListResourceView, DetailResourceView

from .models import (
    Area,
    Survey,
    SurveyMediaAttachment,
    Encounter,
    AnimalEncounter,
    TurtleNestEncounter,
    MediaAttachment,
    TurtleNestObservation,
    TurtleHatchlingEmergenceObservation,
    NestTagObservation,
    TurtleNestDisturbanceObservation,
    LoggerObservation,
    HatchlingMorphometricObservation,
    TurtleHatchlingEmergenceOutlierObservation,
    LightSourceObservation,
    DisturbanceObservation,
)
from .serializers import (
    AreaSerializer,
    SurveySerializer,
    SurveyMediaAttachmentSerializer,
    EncounterSerializer,
    AnimalEncounterSerializer,
    TurtleNestEncounterSerializer,
    MediaAttachmentSerializer,
    TurtleNestObservationSerializer,
    TurtleHatchlingEmergenceObservationSerializer,
    NestTagObservationSerializer,
    TurtleNestDisturbanceObservationSerializer,
    LoggerObservationSerializer,
    HatchlingMorphometricObservationSerializer,
    TurtleHatchlingEmergenceOutlierObservationSerializer,
    LightSourceObservationSerializer,
    DisturbanceObservationSerializer,
)


class ObservationsResourceSummary(View):
    """A custom view to return a list of resource API endpoints.
    """
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        # Generate a list of resources and endpoints.
        resources = [
            ("area", "area_list_resource"),
            ("survey", "survey_list_resource"),
            ("survey-media-attachment", "survey_media_attachment_list_resource"),
            ("encounter", "encounter_list_resource"),
            ("animal-encounter", "animal_encounter_list_resource"),
            ("turtle-nest-encounter", "turtle_nest_encounter_list_resource"),
            ("media-attachment", "media_attachment_list_resource"),
            ("turtle-nest-observation", "turtle_nest_observation_list_resource"),
            ("turtle-hatchling-emergence-observation", "turtle_hatchling_emergence_observation_list_resource"),
            ("nest-tag-observation", "nest_tag_observation_list_resource"),
            ("turtle-nest-disturbance-observation", "turtle_nest_disturbance_observation_list_resource"),
            ("logger-observation", "logger_observation_list_resource"),
            ("hatchling-morphometric-observation", "hatchling_morphometric_observation_list_resource"),
            ("turtle-hatchling-emergence-outlier-observation", "turtle_hatchling_emergence_outlier_observation_list_resource"),
            ("light-source-observation", "light_source_observation_list_resource"),
            ("disturbance-observation", "disturbance_observation_list_resource"),
        ]
        endpoints = []

        for resource in resources:
            endpoints.append(
                {"resource": resource[0], "endpoint_url": request.build_absolute_uri(reverse(f"api:{resource[1]}"))}
            )
        return JsonResponse(endpoints, safe=False)


class AreaDiagnostics(View):
    """Return geometry diagnostics for an Area, for troubleshooting ODK mismatches.

    Query params:
      - id: Area PK (optional)
      - name: Area name (optional; used if id missing)
      - lon, lat: optional coordinate in EPSG:4326 to test ST_Covers
    """
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        area_obj = None
        area_id = request.GET.get("id")
        area_name = request.GET.get("name")
        try:
            if area_id:
                area_obj = Area.objects.get(pk=int(area_id))
            elif area_name:
                area_obj = Area.objects.get(name=area_name)
            else:
                return JsonResponse({"error": "Provide id or name"}, status=400)
        except (ObjectDoesNotExist, ValueError):
            return JsonResponse({"error": "Area not found"}, status=404)

        # Optional covers test
        covers = None
        lon = request.GET.get("lon")
        lat = request.GET.get("lat")
        if lon is not None and lat is not None:
            try:
                pt = Point(float(lon), float(lat), srid=4326)
                covers = area_obj.geom.covers(pt)
            except Exception as e:
                covers = f"error: {e}"

        try:
            xmin, ymin, xmax, ymax = area_obj.geom.extent
        except Exception:
            xmin = ymin = xmax = ymax = None

        data = {
            "id": area_obj.pk,
            "name": area_obj.name,
            "area_type": area_obj.area_type,
            "srid": area_obj.geom.srid,
            "geom_type": area_obj.geom.geom_type,
            "valid": area_obj.geom.valid,
            "centroid": area_obj.geom.centroid.wkt if area_obj.geom else None,
            "extent": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax},
            "covers_test": covers,
        }
        return JsonResponse(data, safe=False)


class AreaListResource(ListResourceView):
    model = Area
    serializer = AreaSerializer


class AreaDetailResource(DetailResourceView):
    model = Area
    serializer = AreaSerializer


class SurveyListResource(ListResourceView):
    model = Survey
    serializer = SurveySerializer


class SurveyDetailResource(DetailResourceView):
    model = Survey
    serializer = SurveySerializer


class SurveyMediaAttachmentListResource(ListResourceView):
    model = SurveyMediaAttachment
    serializer = SurveyMediaAttachmentSerializer


class SurveyMediaAttachmentDetailResource(DetailResourceView):
    model = SurveyMediaAttachment
    serializer = SurveyMediaAttachmentSerializer


class EncounterListResource(ListResourceView):
    model = Encounter
    serializer = EncounterSerializer

    def get_queryset(self):
        # FIXME: permissions checking per object.
        return self.model.objects.all(
        ).prefetch_related(
            'observer',
            'reporter',
            'area',
            'site',
            'survey',
        )


class EncounterDetailResource(DetailResourceView):
    model = Encounter
    serializer = EncounterSerializer


class AnimalEncounterListResource(EncounterListResource):
    model = AnimalEncounter
    serializer = AnimalEncounterSerializer


class AnimalEncounterDetailResource(EncounterDetailResource):
    model = AnimalEncounter
    serializer = AnimalEncounterSerializer


class TurtleNestEncounterListResource(EncounterListResource):
    model = TurtleNestEncounter
    serializer = TurtleNestEncounterSerializer

    def get_queryset(self):
        # Filtering options.
        queryset = super().get_queryset()
        if 'nest_type' in self.request.GET and self.request.GET['nest_type']:
            queryset = queryset.filter(nest_type=self.request.GET['nest_type'])
        if 'species' in self.request.GET and self.request.GET['species']:
            queryset = queryset.filter(nest_type=self.request.GET['species'])

        return queryset


class TurtleNestEncounterDetailResource(EncounterDetailResource):
    model = TurtleNestEncounter
    serializer = TurtleNestEncounterSerializer


class ObservationListResource(ListResourceView):

    def dispatch(self, request, *args, **kwargs):
        if 'encounter_id' in request.GET and request.GET['encounter_id']:
            try:
                int(request.GET['encounter_id'])
            except:
                return HttpResponseBadRequest()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()

        if 'encounter_id' in self.request.GET and self.request.GET['encounter_id']:
            queryset = queryset.filter(encounter__pk=int(self.request.GET['encounter_id']))

        return queryset


class MediaAttachmentListResource(ObservationListResource):
    model = MediaAttachment
    serializer = MediaAttachmentSerializer


class MediaAttachmentDetailResource(DetailResourceView):
    model = MediaAttachment
    serializer = MediaAttachmentSerializer


class TurtleNestObservationListResource(ObservationListResource):
    model = TurtleNestObservation
    serializer = TurtleNestObservationSerializer


class TurtleNestObservationDetailResource(DetailResourceView):
    model = TurtleNestObservation
    serializer = TurtleNestObservationSerializer


class TurtleHatchlingEmergenceObservationListResource(ObservationListResource):
    model = TurtleHatchlingEmergenceObservation
    serializer = TurtleHatchlingEmergenceObservationSerializer


class TurtleHatchlingEmergenceObservationDetailResource(DetailResourceView):
    model = TurtleHatchlingEmergenceObservation
    serializer = TurtleHatchlingEmergenceObservationSerializer


class NestTagObservationListResource(ObservationListResource):
    model = NestTagObservation
    serializer = NestTagObservationSerializer


class NestTagObservationDetailResource(DetailResourceView):
    model = NestTagObservation
    serializer = NestTagObservationSerializer


class TurtleNestDisturbanceObservationListResource(ObservationListResource):
    model = TurtleNestDisturbanceObservation
    serializer = TurtleNestDisturbanceObservationSerializer


class TurtleNestDisturbanceObservationDetailResource(DetailResourceView):
    model = TurtleNestDisturbanceObservation
    serializer = TurtleNestDisturbanceObservationSerializer


class LoggerObservationListResource(ObservationListResource):
    model = LoggerObservation
    serializer = LoggerObservationSerializer


class LoggerObservationDetailResource(DetailResourceView):
    model = LoggerObservation
    serializer = LoggerObservationSerializer


class HatchlingMorphometricObservationListResource(ObservationListResource):
    model = HatchlingMorphometricObservation
    serializer = HatchlingMorphometricObservationSerializer


class HatchlingMorphometricObservationDetailResource(DetailResourceView):
    model = HatchlingMorphometricObservation
    serializer = HatchlingMorphometricObservationSerializer


class TurtleHatchlingEmergenceOutlierObservationListResource(ObservationListResource):
    model = TurtleHatchlingEmergenceOutlierObservation
    serializer = TurtleHatchlingEmergenceOutlierObservationSerializer


class TurtleHatchlingEmergenceOutlierObservationDetailResource(DetailResourceView):
    model = TurtleHatchlingEmergenceOutlierObservation
    serializer = TurtleHatchlingEmergenceOutlierObservationSerializer


class LightSourceObservationListResource(ObservationListResource):
    model = LightSourceObservation
    serializer = LightSourceObservationSerializer


class LightSourceObservationDetailResource(DetailResourceView):
    model = LightSourceObservation
    serializer = LightSourceObservationSerializer


class DisturbanceObservationListResource(ObservationListResource):
    model = DisturbanceObservation
    serializer = DisturbanceObservationSerializer


class DisturbanceObservationDetailResource(DetailResourceView):
    model = DisturbanceObservation
    serializer = DisturbanceObservationSerializer


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


def nests_tracks_streaming_json(request):
    """This view streams the database query as JSON for use by external tools such as PowerBI.
    """
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
ORDER BY
    e."when" DESC
    '''

    response = StreamingHttpResponse(stream_data(query), content_type="application/json")
    return response
