from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from wastd.utils import search_filter

from .models import Turtle
from .forms import TurtleSearchForm


class TurtleList(LoginRequiredMixin, ListView):
    model = Turtle
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_count"] = self.get_queryset().count()
        context["page_title"] = f"{settings.SITE_CODE} | Tagged turtles"
        # Pass in any query string
        #if 'q' in self.request.GET:
        #    context['query_string'] = self.request.GET['q']
        context["search_form"] = TurtleSearchForm()
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        # NOTE: General-purpose search is too slow to use.
        #if 'q' in self.request.GET and self.request.GET['q']:
        #    from .admin import TrtTurtlesAdmin
        #    q = search_filter(TrtTurtlesAdmin.search_fields, self.request.GET['q'])
        #    qs = qs.filter(q).distinct()
        if 'turtle_id' in self.request.GET and self.request.GET['turtle_id']:
            return qs.filter(pk=self.request.GET['turtle_id'])
        if 'tag_id' in self.request.GET and self.request.GET['tag_id']:
            return qs.filter(tags__pk=self.request.GET['tag_id'])
        if 'pit_tag_id' in self.request.GET and self.request.GET['pit_tag_id']:
            return qs.filter(pit_tags__pk=self.request.GET['pit_tag_id'])
        return qs


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
