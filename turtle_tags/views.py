from dateutil import tz
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import ListView, DetailView
import json
from wastd.utils import search_filter, Breadcrumb
from django.db import connection
from django.http import StreamingHttpResponse
import json
import datetime

from .models import (
    Turtle,
)


class TurtleList(LoginRequiredMixin, ListView):
    model = Turtle
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_count"] = self.get_queryset().count()
        context["page_title"] = f"{settings.SITE_CODE} | Tagged turtles"
        # Pass in any query string
        if "q" in self.request.GET:
            context["query_string"] = self.request.GET["q"]
        context["breadcrumbs"] = (
            Breadcrumb("Home", reverse("home")),
            Breadcrumb("Tagged turtles", None),
        )
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        # General-purpose search uses the `q` parameter.
        if "q" in self.request.GET and self.request.GET["q"]:
            from .admin import TurtleAdmin
            q = search_filter(TurtleAdmin.search_fields, self.request.GET["q"])
            qs = qs.filter(q).distinct()

        return qs.order_by("pk")


class TurtleDetail(LoginRequiredMixin, DetailView):
    model = Turtle

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context["page_title"] = f"{settings.SITE_CODE} | Tagged turtles | {obj.pk}"
        context["tags"] = obj.turtletag_set.all()
        encounters = obj.get_encounters()

        if encounters:
            context["encounters"] = encounters
            # Pass in a list of observation points as GeoJSON features.
            points = []
            for encounter in encounters:
                when = encounter.when.astimezone(tz.tzlocal()).strftime("%Y-%m-%d %H:%M %Z")
                who = encounter.observer.name
                points.append({
                    "type": "Feature",
                    "properties": {
                        "label": f"{when} by {who}",
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": encounter.where.coords,
                    }
                })
            if points:
                context["encounters_points"] = json.dumps(points)
            else:
                context["encounters_points"] = None
        else:
            context["encounters"] = None
            context["encounters_points"] = None

        return context


#get the tagged turtles
def taggedTurtles(request):
    query = '''
SELECT 
    t.id AS turtle_id,
    t.species,
    t.sex,
    t.name AS turtle_name,
    t.comments AS turtle_comments,
    tobs.tag_type,
    tobs.name AS tag_name,
    tobs.status AS tag_status,
    tobs.tag_location,
    tobs.comments AS tag_comments, 
    TO_CHAR(enc.when AT TIME ZONE \'Australia/Perth\', \'YYYY-MM-DD\') AS "encounter_date",
    TO_CHAR(enc."when" AT TIME ZONE \'Australia/Perth\', \'HH24:MI:SS\') AS "encounter_time",
    ST_Y(enc."where") as latitude,
    ST_X(enc."where") as longitude,
    enc.name AS encouter_name,
    enc.encounter_type,
    site."name" AS "site_name",
    area."name" AS "area_name"
FROM
    turtle_tags_turtle AS t
JOIN 
    turtle_tags_turtletag AS tt ON t.id = tt.turtle_id
JOIN 
    observations_tagobservation AS tobs ON tt.tag_type = tobs.tag_type AND tt.serial = tobs.name
LEFT JOIN 
    "observations_observation" obs ON (obs."id" = tobs."observation_ptr_id")
LEFT JOIN 
    "observations_encounter" enc ON (enc."id" = obs."encounter_id")
LEFT JOIN 
    "observations_survey" survey ON (enc."survey_id" = survey."id")
LEFT JOIN 
    "observations_area" site ON (enc."site_id" = site."id")
LEFT JOIN 
    "observations_area" area ON (enc."area_id" = area."id")
WHERE 
    (survey."production" = true OR survey."production" IS null) OR enc."survey_id" = null
ORDER BY 
    t.id;
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