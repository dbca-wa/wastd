from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from wastd.utils import search_filter

from .models import TrtTurtles


class TurtleList(LoginRequiredMixin, ListView):
    model = TrtTurtles
    paginate_by = 50
    template_name = "wamtram/turtle_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_count"] = self.get_queryset().count()
        context["page_title"] = f"{settings.SITE_CODE} | Tagged turtles"
        # Pass in any query string
        if 'q' in self.request.GET:
            context['query_string'] = self.request.GET['q']
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        if 'q' in self.request.GET and self.request.GET['q']:
            from .admin import TrtTurtlesAdmin
            q = search_filter(TrtTurtlesAdmin.search_fields, self.request.GET['q'])
            qs = qs.filter(q).distinct()
        return qs


class TurtleDetail(LoginRequiredMixin, DetailView):
    model = TrtTurtles
    template_name = "wamtram/turtle_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context["page_title"] = f"{settings.SITE_CODE} | Tagged turtles | {obj.pk}"
        points = []
        for obs in obj.observations.all():
            if obs.get_point():
                points.append(obs.get_point().geojson)
        if points:
            context["observation_points"] = points
        else:
            context["observation_points"] = None
        return context
