from dateutil import tz
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import ListView, DetailView
import json
from wastd.utils import search_filter, Breadcrumb

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
