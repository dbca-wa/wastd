from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import ListView, DetailView
from shared.utils import Breadcrumb
from wastd.utils import search_filter

from .models import Turtle, TurtleObservation


class TurtleList(LoginRequiredMixin, ListView):
    model = Turtle
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_count"] = self.get_queryset().count()
        context["page_title"] = f"{settings.SITE_CODE} | Tagged turtles"
        # Pass in any query string
        if 'q' in self.request.GET:
            context['query_string'] = self.request.GET['q']
        context["breadcrumbs"] = (
            Breadcrumb("Home", reverse("home")),
            Breadcrumb("Tagged turtles", None),
        )
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        # General-purpose search uses the `q` parameter.
        if 'q' in self.request.GET and self.request.GET['q']:
            from .admin import TurtleAdmin
            q = search_filter(TurtleAdmin.search_fields, self.request.GET['q'])
            return qs.filter(q).distinct().order_by('pk')
        if 'turtle_id' in self.request.GET and self.request.GET['turtle_id']:
            return qs.filter(pk=self.request.GET['turtle_id']).order_by('pk')
        if 'tag_id' in self.request.GET and self.request.GET['tag_id']:
            return qs.filter(tags__serial__icontains=self.request.GET['tag_id']).order_by('pk')
        if 'pit_tag_id' in self.request.GET and self.request.GET['pit_tag_id']:
            return qs.filter(pit_tags__serial__icontains=self.request.GET['pit_tag_id']).order_by('pk')
        return qs.order_by('pk')


class TurtleDetail(LoginRequiredMixin, DetailView):
    model = Turtle

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context["page_title"] = f"{settings.SITE_CODE} | Tagged turtles | {obj.pk}"
        points = []
        for obs in obj.turtleobservation_set.all():
            if obs.point:
                points.append(obs.point.geojson)
        if points:
            context["observation_points"] = points
        else:
            context["observation_points"] = None
        return context


class TurtleObservationList(LoginRequiredMixin, ListView):
    model = TurtleObservation
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_count"] = self.get_queryset().count()
        context["page_title"] = f"{settings.SITE_CODE} | Turtle observations"
        # Pass in any query string
        if 'q' in self.request.GET:
            context['query_string'] = self.request.GET['q']
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        # General-purpose search uses the `q` parameter.
        if 'q' in self.request.GET and self.request.GET['q']:
            from .admin import TurtleObservationAdmin
            q = search_filter(TurtleObservationAdmin.search_fields, self.request.GET['q'])
            return qs.filter(q).distinct().order_by('pk')
        return qs.order_by('pk')


class TurtleObservationDetail(LoginRequiredMixin, DetailView):
    model = TurtleObservation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context["page_title"] = f"{settings.SITE_CODE} | Turtle observations | {obj.pk}"
        points = []
        if obj.point:
            points.append(obj.point.geojson)
        if points:
            context["observation_points"] = points
        else:
            context["observation_points"] = None
        return context
