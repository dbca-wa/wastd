from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from shared.utils import Breadcrumb
from wastd.utils import search_filter

from .models import Turtle, TurtleObservation
from .forms import (
    #TurtleSearchForm,
    TurtleCreateForm,
    TurtleObservationCreateForm,
    TurtleTagUpdateForm,
    TurtleTagFormSet,
    PitTagFormSet,
    TurtleTagFormSetHelper,
)


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
        #context["search_form"] = TurtleSearchForm()
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


class TurtleCreate(LoginRequiredMixin, CreateView):
    model = Turtle
    form_class = TurtleCreateForm

    def dispatch(self, request, *args, **kwargs):
        # FIXME: permissions checking
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"{settings.SITE_CODE} | Create new turtle"
        context["title"] = "Create new turtle"
        context["breadcrumbs"] = (
            Breadcrumb("Home", reverse("home")),
            Breadcrumb("Tagged Turtles", reverse("tagging:turtle_list")),
            Breadcrumb("Create new turtle", None),
        )
        return context

    def get_success_url(self):
        # Turtle detail view.
        return self.object.get_absolute_url()

    def post(self, request, *args, **kwargs):
        # If the user clicked Cancel, redirect back to the turtle list view.
        if request.POST.get("cancel"):
            return redirect("tagging:turtle_list")
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        # Saves the form instance, sets the current object for the view,
        # and redirects to get_success_url().
        self.object = form.save(commit=False)
        self.object.entered_by_person = self.request.user
        self.object.save()
        messages.success(self.request, "{} has been created.".format(self.object))
        return HttpResponseRedirect(self.get_success_url())


class TurtleTagsUpdate(LoginRequiredMixin, UpdateView):
    model = Turtle
    template_name = "tagging/turtle_tags_form.html"
    # We don't really use the form class, but we need to define it for the view class.
    form_class = TurtleTagUpdateForm

    def dispatch(self, request, *args, **kwargs):
        # FIXME: permissions checking
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"{settings.SITE_CODE} | Tagged turtles | {self.object.pk} | Update tags"
        context["title"] = f"Turtle {self.object.pk} - Update tags"
        context["tag_type"] = "Pit tags"
        if self.request.POST:
            context["tag_formset"] = TurtleTagFormSet(self.request.POST, instance=self.object, prefix="tag")
        else:
            context["tag_formset"] = TurtleTagFormSet(instance=self.object, prefix="tag")
        context["tag_formset"].helper = TurtleTagFormSetHelper()
        context["breadcrumbs"] = (
            Breadcrumb("Home", reverse("home")),
            Breadcrumb("Tagged Turtles", reverse("tagging:turtle_list")),
            Breadcrumb(self.object.pk, self.object.get_absolute_url()),
            Breadcrumb("Update tags", None),
        )
        return context

    def post(self, request, *args, **kwargs):
        # If the user clicked Cancel, redirect back to the turtle detail page.
        if request.POST.get("cancel"):
            return redirect(self.get_object().get_absolute_url())
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        tag_formset = TurtleTagFormSet(self.request.POST, instance=self.object, prefix="tag")
        if tag_formset.is_valid():
            tag_formset.save()
            messages.success(self.request, f"Turtle {self.object} tags have been updated.")
        else:
            return self.render_to_response(self.get_context_data(form=form))
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return self.object.get_absolute_url()


class TurtlePitTagsUpdate(TurtleTagsUpdate):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"{settings.SITE_CODE} | Tagged turtles | {self.object.pk} | Update pit tags"
        context["title"] = f"Turtle {self.object.pk} - Update pit tags"
        context["tag_type"] = "Pit tags"
        if self.request.POST:
            context["tag_formset"] = PitTagFormSet(self.request.POST, instance=self.object, prefix="pit_tag")
        else:
            context["tag_formset"] = PitTagFormSet(instance=self.object, prefix="pit_tag")
        context["tag_formset"].helper = TurtleTagFormSetHelper()
        context["breadcrumbs"] = (
            Breadcrumb("Home", reverse("home")),
            Breadcrumb("Tagged Turtles", reverse("tagging:turtle_list")),
            Breadcrumb(self.object.pk, self.object.get_absolute_url()),
            Breadcrumb("Update pit tags", None),
        )
        return context

    def form_valid(self, form):
        tag_formset = PitTagFormSet(self.request.POST, instance=self.object, prefix="pit_tag")
        if tag_formset.is_valid():
            tag_formset.save()
            messages.success(self.request, f"Turtle {self.object} pit tags have been updated.")
        else:
            return self.render_to_response(self.get_context_data(form=form))
        return HttpResponseRedirect(self.get_success_url())


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


class TurtleObservationCreate(LoginRequiredMixin, CreateView):
    model = TurtleObservation
    form_class = TurtleObservationCreateForm
    template_name = "tagging/turtle_observation_create.html"

    def get_turtle(self):
        return get_object_or_404(Turtle, pk=self.kwargs["pk"])

    def dispatch(self, request, *args, **kwargs):
        # FIXME: permissions checking
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        # If the user clicked Cancel, redirect back to the turtle detail page.
        if request.POST.get("cancel"):
            return redirect(self.get_turtle().get_absolute_url())
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.turtle = self.get_turtle()
        return

    def get_success_url(self):
        pass
