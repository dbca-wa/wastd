from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.geos import Point
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, FormView
import json
from shared.utils import Breadcrumb
from users.models import User
from wastd.utils import search_filter

from .models import (
    Turtle,
    TurtleObservation,
    TurtleTag,
    TurtlePitTag,
    TurtleTagObservation,
    TurtlePitTagObservation,
    MeasurementType,
    TurtleMeasurement,
    TurtleDamage,
    TurtleSample,
)
from .forms import TurtleTagObservationAddForm


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
        # Pass in a list of observation points as GeoJSON features.
        points = []
        for obs in obj.turtleobservation_set.filter(point__isnull=False):
            points.append({
                "type": "Feature",
                "properties": {
                    "label": f"{obs.get_observed_awst().strftime('%c')} {obs.get_status_display()}".strip(),
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": obs.point.coords,
                }
            })
        if points:
            context["observation_points"] = json.dumps(points)
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


class TurtleObservationAdd(LoginRequiredMixin, FormView):
    form_class = TurtleTagObservationAddForm
    template_name = 'tagging/turtleobservation_add.html'

    def dispatch(self, request, *args, **kwargs):
        # FIXME: Proper permissions check.
        if not request.user.is_staff:
            return HttpResponseForbidden("Insufficient permission")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"{settings.SITE_CODE} | Turtle observations | Add"
        if "turtle_id" in self.request.GET and self.request.GET["turtle_id"]:
            context["turtle"] = Turtle.objects.get(pk=self.request.GET["turtle_id"])
        else:
            context["turtle"] = None
        context["breadcrumbs"] = (
            Breadcrumb("Home", reverse("home")),
            Breadcrumb("Turtle observations", reverse("tagging:turtleobservation_list")),
            Breadcrumb("Add", None),
        )
        return context

    def get_initial(self):
        """If the Turtle PK is passed in, set initial data in the form.
        """
        initial = super().get_initial()

        if "turtle_id" in self.request.GET and self.request.GET["turtle_id"]:
            turtle = Turtle.objects.get(pk=self.request.GET["turtle_id"])
            initial['species'] = turtle.species
            initial['sex'] = turtle.sex
            initial['existing_turtle_id'] = turtle.pk

            tags = TurtleTag.objects.filter(turtle=turtle)
            for tag in tags:
                # Attached tags, left side
                if tag.is_attached() and tag.side == 'L':
                    initial['old_flipper_tags'] = 'y'
                    # If we've set the first form tag, set the second instead.
                    if 'tag_l1' in initial:
                        initial['tag_l2'] = tag.serial
                        initial['tag_l2_new'] = 'n'
                    else:
                        initial['tag_l1'] = tag.serial
                        initial['tag_l1_new'] = 'n'
                if tag.is_attached() and tag.side == 'R':
                    initial['old_flipper_tags'] = 'y'
                    # If we've set the first form tag, set the second instead.
                    if 'tag_r1' in initial:
                        initial['tag_r2'] = tag.serial
                        initial['tag_r2_new'] = 'n'
                    else:
                        initial['tag_r1'] = tag.serial
                        initial['tag_r1_new'] = 'n'

            # Note that the pit tags data model doesn't currently save "left" or "right",
            # so we just push them into the form in random order.
            pit_tags = TurtlePitTag.objects.filter(turtle=turtle)
            for tag in pit_tags:
                initial['pit_tag_present'] = 'y'
                if tag.is_functional():
                    # If we've set the first form tag, set the second instead.
                    if 'pit_tag_l' in initial:
                        initial['pit_tag_r'] = tag.serial
                        initial['pit_tag_r_new'] = 'n'
                    else:
                        initial['pit_tag_l'] = tag.serial
                        initial['pit_tag_l_new'] = 'n'

        return initial

    def get_form_kwargs(self):
        """Pass optional turtle_id kwarg into the form.
        """
        kwargs = super().get_form_kwargs()
        if "turtle_id" in self.request.GET and self.request.GET["turtle_id"]:
            kwargs["turtle_id"] = Turtle.objects.get(pk=self.request.GET["turtle_id"])
        return kwargs

    def post(self, request, *args, **kwargs):
        # If the user clicked Cancel, redirect back to the turtle observations list view.
        if request.POST.get("cancel"):
            return redirect("tagging:turtleobservation_list")
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        print(form.data)
        return super().form_invalid(form)

    def form_valid(self, form):
        print(form.cleaned_data)
        data = form.cleaned_data

        if data['existing_turtle_id']:  # Existing turtle
            turtle = Turtle.objects.get(pk=data['existing_turtle_id'])
        else:  # New turtle
            turtle = Turtle.objects.create(
                entered_by=self.request.user,
                species=data['species'],
                sex=data['sex'],
                location=data['place'].location,
            )

        # TurtleObservation
        observation = TurtleObservation(
            turtle=turtle,
            entered_by=User.objects.get(pk=data['recorded_by']),
            observed=data['observed'],
            place=data['place'],
            comments=data['comments'],
        )
        if data['longitude'] and data['latitude']:
            observation.point = Point(x=float(data['longitude']), y=float(data['latitude']), srid=4326)

        # TODO: other field values.
        observation.save()

        # TurtleTag / TurtleTagObservation
        if data['tagged_by']:
            tagged_by = User.objects.get(pk=data['tagged_by'])
        else:
            tagged_by = None

        # Each turtle tag in the form might be new or an existing one.
        # Assume that validation has all happened prior
        # Create each new one, then create a TurtleTagObservation for each one.
        # Each tag might be new or an existing one.

        # L1 tag
        if data['tag_l1'] and data['tag_l1_new'] == 'y':  # New tag.
            tag = TurtleTag.objects.create(
                serial=data['tag_l1'],
                turtle=turtle,
                field_person=tagged_by,
                side='L',
            )
            tag_created = True
        elif data['tag_l1'] and data['tag_l1_new'] == 'n':  # Existing tag.
            tag = TurtleTag.objects.get(turtle=turtle, serial=data['tag_l1'])
            tag_created = False
        TurtleTagObservation.objects.create(
            tag=tag,
            observation=observation,
            status='P_OK' if tag_created else 'A1',
            position=1,
            barnacles=data['tag_l1_barnacles'] == 'y',
        )

        # TODO: L2, R1, R2 tags

        # Left pit tag
        if data['pit_tag_l'] and data['pit_tag_l_new'] == 'y':  # New tag.
            pit_tag = TurtlePitTag.objects.create(
                serial=data['pit_tag_l1'],
                turtle=turtle,
                field_person=tagged_by,
                side='L',
            )
            pit_tag_created = True
        elif data['pit_tag_l'] and data['pit_tag_l_new'] == 'n':  # Existing tag.
            pit_tag = TurtlePitTag.objects.get(turtle=turtle, serial=data['pit_tag_l'])
            pit_tag_created = False
        TurtlePitTagObservation.objects.create(
            tag=pit_tag,
            observation=observation,
            status='A1' if pit_tag_created else 'P',
            position='LF',  # FIXME: check this assumption.
        )

        # TODO: right pit tag

        # TurtleMeasurement
        ccl = MeasurementType.objects.get(short_desc='CCL')
        ccw = MeasurementType.objects.get(short_desc='CCW')
        weight = MeasurementType.objects.get(short_desc='WEIGHT K')

        if data['ccl_max']:
            TurtleMeasurement.objects.create(observation=observation, measurement_type=ccl, value=float(data['ccl_max']))
        elif data['ccl_min']:
            TurtleMeasurement.objects.create(observation=observation, measurement_type=ccl, value=float(data['ccl_min']))

        if data['cc_width']:
            TurtleMeasurement.objects.create(observation=observation, measurement_type=ccw, value=float(data['cc_width']))

        if data['weight']:
            TurtleMeasurement.objects.create(observation=observation, measurement_type=weight, value=float(data['weight']))

        # TurtleDamage
        if data['damage_1_part'] and data['damage_1_type']:
            TurtleDamage.objects.create(observation=observation, body_part=data['damage_1_part'], damage=data['damage_1_type'])
        if data['damage_2_part'] and data['damage_2_type']:
            TurtleDamage.objects.create(observation=observation, body_part=data['damage_2_part'], damage=data['damage_2_type'])

        # TODO: damage 3, 4, 5

        # TurtleSample
        if data['sample_1_type'] and data['sample_1_label']:
            TurtleSample.objects.create(observation=observation, tissue_type=data['sample_1_type'], label=data['sample_1_label'])
        if data['sample_2_type'] and data['sample_2_label']:
            TurtleSample.objects.create(observation=observation, tissue_type=data['sample_2_type'], label=data['sample_2_label'])

        messages.success(self.request, "Turtle observation {} has been created.".format(observation))
        return HttpResponseRedirect(observation.get_absolute_url())
