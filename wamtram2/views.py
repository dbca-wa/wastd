from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from django.db import connections, DatabaseError
from django.db.models import Q, Exists, OuterRef
from django.http import HttpResponseForbidden, HttpResponseRedirect, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic.edit import FormMixin
from django.views.generic import TemplateView, ListView, DetailView, FormView, DeleteView
from django.http import JsonResponse
from .models import TrtPlaces, TrtSpecies, TrtLocations
from django.db.models import Count, Exists, OuterRef, Subquery
from django.core.paginator import Paginator
from openpyxl import Workbook
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.template.loader import render_to_string
from django.core.serializers.json import DjangoJSONEncoder
import json
import csv
from django.core.exceptions import ValidationError


from wastd.utils import Breadcrumb, PaginateMixin
from .models import (
    TrtTurtles,
    TrtTags,
    TrtPitTags,
    TrtEntryBatches,
    TrtDataEntry,
    TrtPersons,
    TrtObservations,
    Template,
    TrtTagStates,
    TrtTurtleStatus
)
from .forms import TrtDataEntryForm, SearchForm, TrtEntryBatchesForm, TemplateForm, BatchesCodeForm, BatchesSearchForm


class HomePageView(LoginRequiredMixin, TemplateView):
    """
    A view for the home page.

    Attributes:
        template_name (str): The name of the template to be used for rendering the view.
    """

    template_name = "wamtram2/home.html"


class EntryBatchesListView(LoginRequiredMixin, ListView):
    model = TrtEntryBatches
    template_name = "wamtram2/trtentrybatches_list.html"
    context_object_name = "batches"
    paginate_by = 30

    def dispatch(self, request, *args, **kwargs):
        if not (
            request.user.groups.filter(name="WAMTRAM2_VOLUNTEER").exists()
            or request.user.groups.filter(name="WAMTRAM2_TEAM_LEADER").exists()
            or request.user.groups.filter(name="WAMTRAM2_STAFF").exists()
            or request.user.is_superuser
        ):
            return HttpResponseForbidden(
                "You do not have permission to view this record"
            )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().order_by("-entry_batch_id")

        if (
            "filter" in self.request.GET
            and self.request.GET["filter"] == "no_observation_id"
        ):
            has_dataentry_no_observation_id = Exists(
                TrtDataEntry.objects.filter(
                    entry_batch_id=OuterRef("pk"), observation_id__isnull=True
                )
            )
            queryset = queryset.filter(has_dataentry_no_observation_id)

        # Use Subquery to fetch the last place_code for each batch
        last_place_code_subquery = Subquery(
            TrtDataEntry.objects.filter(entry_batch_id=OuterRef("pk"))
            .order_by("-data_entry_id")
            .values("place_code")[:1]
        )
        
        # Annotate the queryset with entry_count, last_place_code, and do_not_process_count
        queryset = queryset.annotate(
            entry_count=Count('trtdataentry'),
            last_place_code=last_place_code_subquery,
            do_not_process_count=Count(
                'trtdataentry',
                filter=Q(trtdataentry__do_not_process=True)
            )
        )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Paginate the queryset
        queryset = self.get_queryset()
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Retrieve place_code from paginated object list and fetch corresponding TrtPlaces objects
        place_codes = [batch.last_place_code for batch in page_obj.object_list if batch.last_place_code]
        places = TrtPlaces.objects.filter(place_code__in=place_codes)
        places_dict = {place.place_code: place for place in places}

        # Attach TrtPlaces objects to each batch in the paginated list
        for batch in page_obj.object_list:
            batch.last_place_code_obj = places_dict.get(batch.last_place_code)
            
            batch.highlight_row = int(batch.do_not_process_count) > 0

        context['page_obj'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()
        context['object_list'] = page_obj.object_list
        context["persons"] = {
            person.person_id: person for person in TrtPersons.objects.all()
        }

        return context


class EntryBatchDetailView(LoginRequiredMixin, FormMixin, ListView):
    """
    A view for displaying list of a batch of TrtDataEntry objects.
    """

    model = TrtDataEntry
    template_name = "wamtram2/trtentrybatch_detail.html"
    context_object_name = "object_list"
    paginate_by = 30
    form_class = TrtEntryBatchesForm
    
    def get_initial(self):
        initial = super().get_initial()
        # batch_id = self.kwargs.get("batch_id")
        # cookies_key_prefix = batch_id
        # default_enterer = self.request.COOKIES.get(f'{cookies_key_prefix}_default_enterer')
        # use_default_enterer = self.request.COOKIES.get(f'{cookies_key_prefix}_use_default_enterer', False)
        
        # if default_enterer == "None" or not default_enterer or default_enterer == "":
        #     default_enterer = None

        # if use_default_enterer and default_enterer:
        #     initial['entered_person_id'] = default_enterer
        
        return initial

    def dispatch(self, request, *args, **kwargs):
        if not (
            request.user.groups.filter(name="WAMTRAM2_VOLUNTEER").exists()
            or request.user.groups.filter(name="WAMTRAM2_TEAM_LEADER").exists()
            or request.user.groups.filter(name="WAMTRAM2_STAFF").exists()
            or request.user.is_superuser
        ):
            return HttpResponseForbidden(
                "You do not have permission to view this record"
            )
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if "batch_id" not in kwargs:
            new_batch = TrtEntryBatches.objects.create(
                pr_date_convention=False,
                entry_date=timezone.now().date()
            )
            self.kwargs["batch_id"] = new_batch.entry_batch_id
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        batch_id = self.kwargs.get("batch_id")
    
        filter_value = self.request.GET.get("filter")
        if filter_value == "needs_review":
            queryset = queryset.filter(entry_batch_id=batch_id, do_not_process=True)
        elif filter_value == "not_saved":
            queryset = queryset.filter(entry_batch_id=batch_id, observation_id__isnull=True)
        else:
            queryset = queryset.filter(entry_batch_id=batch_id)
            
        return queryset.select_related('observation_id').order_by("-data_entry_id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["persons"] = {
            person.person_id: person for person in TrtPersons.objects.all()
        }

        batch = TrtEntryBatches.objects.get(entry_batch_id=self.kwargs.get("batch_id"))
        context["batch"] = batch
        initial = self.get_initial()
        context["form"] = TrtEntryBatchesForm(
            instance=batch,
            initial=initial
        )
        
        # Add a `highlight_row` attribute to each entry if it meets the conditions
        for entry in context['object_list']:
            entry.highlight_row = entry.do_not_process and entry.error_message not in ['None', 'Observation added to database']
        
        context['templates'] = Template.objects.all()

        cookies_key_prefix = self.kwargs.get("batch_id")
        context['selected_template'] = self.request.COOKIES.get(f'{cookies_key_prefix}_selected_template', '')
        # context['use_default_enterer'] = self.request.COOKIES.get(f'{cookies_key_prefix}_use_default_enterer', False)
        # context['default_enterer'] = self.request.COOKIES.get(f'{cookies_key_prefix}_default_enterer', None)

        context['cookies_key_prefix'] = cookies_key_prefix
        # context['default_enterer_value'] = context['default_enterer']
        
        # Add entries with do_not_process = True to the context
        context["do_not_process_entries"] = TrtDataEntry.objects.filter(
            entry_batch_id=batch.entry_batch_id,
            do_not_process=True
        ).order_by("-data_entry_id")
        
        # Add entries with do_not_process = False to the context
        context["process_entries"] = TrtDataEntry.objects.filter(
            entry_batch_id=batch.entry_batch_id,
            do_not_process=False
        ).order_by("-data_entry_id")
        
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        form.instance.entry_batch_id = self.kwargs.get("batch_id")
        
        if form.is_valid():
            return self.form_valid(form)
        else:
            context = self.get_context_data(form=form, object_list=self.get_queryset())
            return self.render_to_response(context)

    def form_valid(self, form):
        batch = form.save(commit=False)
        entered_person_id = form.cleaned_data.get('entered_person_id')
        comments = form.cleaned_data.get('comments')
        if entered_person_id or comments:
            if not batch.entry_date:
                batch.entry_date = timezone.now()

            batch_id = batch.entry_batch_id

            existing_batch = TrtEntryBatches.objects.get(entry_batch_id=batch_id)
            batch.pr_date_convention = existing_batch.pr_date_convention
            batch.entry_date = existing_batch.entry_date
            batch.filename = existing_batch.filename
            messages.success(self.request, 'Batch detail saved')
            batch.save()
        else:
            context = self.get_context_data(form=form, object_list=self.get_queryset())
            return self.render_to_response(context)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        batch_id = self.kwargs.get("batch_id")
        return reverse("wamtram2:entry_batch_detail", args=[batch_id])


class TrtDataEntryFormView(LoginRequiredMixin, FormView):
    """
    A form view for entering TRT data.
    """

    template_name = "wamtram2/trtdataentry_form.html"
    form_class = TrtDataEntryForm

    def dispatch(self, request, *args, **kwargs):
        # FIXME: Permission check
        if not (
            request.user.groups.filter(name="WAMTRAM2_VOLUNTEER").exists()
            or request.user.groups.filter(name="WAMTRAM2_TEAM_LEADER").exists()
            or request.user.groups.filter(name="WAMTRAM2_STAFF").exists()
            or request.user.is_superuser
        ):
            return HttpResponseForbidden(
                "You do not have permission to view this record"
            )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.

        If an entry_id is provided in the URL, retrieves the corresponding TrtDataEntry instance
        and adds it as the 'instance' argument in the form kwargs. If no entry_id is provided,
        a new, blank form is instantiated.

        Returns:
            dict: The keyword arguments for instantiating the form.
        """
        kwargs = super().get_form_kwargs()
        entry_id = self.kwargs.get("entry_id")
        if entry_id:
            entry = get_object_or_404(TrtDataEntry.objects.select_related('turtle_id'), data_entry_id=entry_id)
            kwargs["instance"] = entry

        return kwargs

    def get_template_data(self, template_key):
        try:
            template = Template.objects.get(pk=template_key)
            return {
                'place_code': template.place_code,
                'species_code': template.species_code,
                'sex': template.sex,
                'location_code': template.location_code
            }
        except Template.DoesNotExist:
            return None

    def get_initial(self):
        initial = super().get_initial()
        batch_id = self.kwargs.get("batch_id")
        turtle_id = self.kwargs.get("turtle_id")
        entry_id = self.kwargs.get("entry_id")
        
        cookies_key_prefix = batch_id
        
        tag_id = self.request.COOKIES.get(f'{cookies_key_prefix}_tag_id')
        tag_type = self.request.COOKIES.get(f'{cookies_key_prefix}_tag_type')
        tag_side = self.request.COOKIES.get(f'{cookies_key_prefix}_tag_side')

        selected_template = self.request.COOKIES.get(f'{cookies_key_prefix}_selected_template')
        
        # If a tag is selected, populate the form with the tag data
        if tag_id and tag_type:
            if tag_type == 'recapture_tag':
                if tag_side == 'L':
                    initial['recapture_left_tag_id'] = tag_id
                elif tag_side == 'R':
                    initial['recapture_right_tag_id'] = tag_id
            elif tag_type == 'recapture_pit_tag':
                initial['recapture_pittag_id'] = tag_id
                
        if batch_id:
            try:
                batch = TrtEntryBatches.objects.get(entry_batch_id=batch_id)
                if batch.template:
                    selected_template = str(batch.template.template_id)
            except TrtEntryBatches.DoesNotExist:
                pass

        if selected_template:
            template_data = self.get_template_data(selected_template)
            if template_data:
                place_code = template_data.get('place_code') or ""
                initial['default_place_code'] = place_code or ""
                self.default_place_code = place_code
                default_place_obj = TrtPlaces.objects.filter(place_code=self.default_place_code).first()
                if default_place_obj:
                    self.default_place_full_name = default_place_obj.get_full_name()
                    initial['default_place_full_name'] = self.default_place_full_name or ""
                if not turtle_id:
                    initial['species_code'] = template_data.get('species_code') or ""
                    initial['sex'] = template_data.get('sex') or ""
                

        if batch_id:
            initial["entry_batch"] = get_object_or_404(TrtEntryBatches, entry_batch_id=batch_id)

        if turtle_id:
            turtle = get_object_or_404(TrtTurtles.objects.prefetch_related('trttags_set', 'trtpittags_set'), pk=turtle_id)
            initial["turtle_id"] = turtle_id
            initial["species_code"] = turtle.species_code
            initial["sex"] = turtle.sex

        if entry_id:
            trtdataentry = get_object_or_404(TrtDataEntry, data_entry_id=entry_id)
            
            measured_by = trtdataentry.measured_by
            recorded_by = trtdataentry.recorded_by
            tagged_by = trtdataentry.tagged_by
            entered_by = trtdataentry.entered_by
            place_code = trtdataentry.place_code
            
            if place_code:
                place = TrtPlaces.objects.filter(place_code=place_code).first()
                if place:
                    initial["place_code"] = place_code
                    self.place_full_name = place.get_full_name()
                else:
                    self.place_full_name = ""
            
            if measured_by:
                first_name, last_name = measured_by.split(" ")
                person = TrtPersons.objects.filter(first_name=first_name, surname=last_name).first()
                if person:
                    initial["measured_by_id"] = person.person_id
                    self.measured_by_full_name = measured_by
                else:
                    self.measured_by_full_name = ""

            if recorded_by:
                first_name, last_name = recorded_by.split(" ")
                person = TrtPersons.objects.filter(first_name=first_name, surname=last_name).first()
                if person:
                    initial["recorded_by_id"] = person.person_id
                    self.recorded_by_full_name = recorded_by
                else:
                    self.recorded_by_full_name = ""

            if tagged_by:
                first_name, last_name = tagged_by.split(" ")
                person = TrtPersons.objects.filter(first_name=first_name, surname=last_name).first()
                if person:
                    initial["tagged_by_id"] = person.person_id
                    self.tagged_by_full_name = tagged_by
                else:
                    self.tagged_by_full_name = ""

            if entered_by:
                first_name, last_name = entered_by.split(" ")
                person = TrtPersons.objects.filter(first_name=first_name, surname=last_name).first()
                if person:
                    initial["entered_by_id"] = person.person_id
                    self.entered_by_full_name = entered_by
                else:
                    self.entered_by_full_name = ""


        return initial

    def form_valid(self, form):
        batch_id = form.cleaned_data["entry_batch"].entry_batch_id
        do_not_process_cookie_name = f"{batch_id}_do_not_process"
        do_not_process_cookie_value = self.request.COOKIES.get(do_not_process_cookie_name)
        if do_not_process_cookie_value == 'true':
            form.instance.do_not_process = True
        entry = form.save()
        success_url = reverse("wamtram2:find_turtle", args=[batch_id])
        
        if form.instance.do_not_process:
            message = f"Entry created successfully and will be reviewed later. Please write the Entry ID: {entry.data_entry_id} on the data sheet"
            message_tag = 'warning'
        else:
            message = f"Entry created successfully. Entry ID: {entry.data_entry_id}"
            message_tag = 'success'
        
        messages.add_message(self.request, getattr(messages, message_tag.upper()), message)
        
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'redirect_url': success_url,
                'message': message,
                'message_tag': message_tag
            })
        else:
            return redirect(success_url)

    def form_invalid(self, form):
        error_message = "Error saving the entry. If you cannot resolve the issue, please set aside this data sheet for admin review and continue with the next data sheet."
        
        messages.error(self.request, error_message)
        
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'errors': form.errors,
                'message': error_message
            })
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        """
        Returns the context data for rendering the template.

        Adds the entry_id and entry objects to the context.

        Returns:
            dict: The context data.
        """
        context = super().get_context_data(**kwargs)
        entry_id = self.kwargs.get("entry_id")
        batch_id = self.kwargs.get("batch_id")
        cookies_key_prefix = batch_id
        form = context.get('form')
        
        if form.is_bound:
            context.update({
                'entered_by_id': form.data.get('entered_by_id'),
                'recorded_by_id': form.data.get('recorded_by_id'),
                'measured_by_id': form.data.get('measured_by_id'),
                'tagged_by_id': form.data.get('tagged_by_id'),
                'place_code': form.data.get('place_code'),
                'entered_by_name': self.get_person_name(form.data.get('entered_by_id')),
                'recorded_by_name': self.get_person_name(form.data.get('recorded_by_id')),
                'measured_by_name': self.get_person_name(form.data.get('measured_by_id')),
                'tagged_by_name': self.get_person_name(form.data.get('tagged_by_id')),
                'place_name': self.get_place_name(form.data.get('place_code')),
            })

        if entry_id:
            entry = get_object_or_404(TrtDataEntry.objects.select_related('turtle_id'), data_entry_id=entry_id)
            context["entry_id"] = entry_id  # Editing existing entry
            context["entry"] = entry
            
            if entry.observation_id:
                context["observation"] = entry.observation_id
            else:
                context["observation"] = None
        
        if batch_id:
            context["batch_id"] = batch_id  # Creating new entry in batch
            batch = TrtEntryBatches.objects.get(entry_batch_id=batch_id)
            if batch.template:
                context["selected_template"] = str(batch.template.template_id)
            else:
                context["selected_template"] = self.request.COOKIES.get(f'{cookies_key_prefix}_selected_template') or None
            # context["use_default_enterer"] = self.request.COOKIES.get(f'{cookies_key_prefix}_use_default_enterer', False)
            # context["default_enterer"] = self.request.COOKIES.get(f'{cookies_key_prefix}_default_enterer', '')
            # Add the tag id and tag type to the context data
            context["cookie_tag_id"] = self.request.COOKIES.get(f'{cookies_key_prefix}_tag_id')
            context["cookie_tag_type"] = self.request.COOKIES.get(f'{cookies_key_prefix}_tag_type')
            context["cookie_tag_side"] = self.request.COOKIES.get(f'{cookies_key_prefix}_tag_side')

            context["default_enterer_full_name"] = getattr(self, 'default_enterer_full_name', '')
            context["default_place_full_name"] = getattr(self, 'default_place_full_name', '')
            context["default_place_code"] = getattr(self, 'default_place_code', '')
        
            context['measured_by_full_name'] = getattr(self, 'measured_by_full_name', '')
            context['recorded_by_full_name'] = getattr(self, 'recorded_by_full_name', '')
            context['tagged_by_full_name'] = getattr(self, 'tagged_by_full_name', '')
            context['entered_by_full_name'] = getattr(self, 'entered_by_full_name', '')
            context['place_name'] = getattr(self, 'place_full_name', '')

        return context

    def get_person_name(self, person_id):
        if person_id:
            try:
                person = TrtPersons.objects.get(person_id=person_id)
                return f"{person.first_name} {person.surname}"
            except TrtPersons.DoesNotExist:
                return ""
        return ""
        
    def get_place_name(self, place_code):
        if place_code:
            try:
                place = TrtPlaces.objects.get(place_code=place_code)
                return place.get_full_name()
            except TrtPlaces.DoesNotExist:
                return ""
        return ""


class DeleteBatchView(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):
        # FIXME: Permission check
        if not (
            request.user.groups.filter(name="WAMTRAM2_TEAM_LEADER").exists()
            or request.user.groups.filter(name="WAMTRAM2_STAFF").exists()
            or request.user.is_superuser
        ):
            return HttpResponseForbidden(
                "You do not have permission to view this record"
            )
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, batch_id):
        batch = get_object_or_404(TrtEntryBatches, entry_batch_id=batch_id)
        batch.delete()
        return redirect("wamtram2:batches_curation")


class ValidateDataEntryBatchView(LoginRequiredMixin, View):
    """
    View class for validating a data entry batch.

    This view executes a stored procedure to validate the data in a batch
    identified by the 'batch_id' parameter. If the validation is successful,
    a success message is added to the request's messages framework. If there
    is a database error, an error message is added instead.

    After the validation, the view redirects to the 'entry_batch_detail' view
    with the 'batch_id' parameter.

    Attributes:
        - request: The HTTP request object.
        - args: Additional positional arguments passed to the view.
        - kwargs: Additional keyword arguments passed to the view.
    """

    def dispatch(self, request, *args, **kwargs):
        # FIXME: Permission check
        if not (
            request.user.groups.filter(name="WAMTRAM2_STAFF").exists()
            or request.user.is_superuser
        ):
            return HttpResponseForbidden(
                "You do not have permission to view this record"
            )
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            with connections["wamtram2"].cursor() as cursor:
                cursor.execute(
                    "EXEC dbo.ValidateDataEntryBatchWEB @ENTRY_BATCH_ID = %s",
                    [self.kwargs["batch_id"]],
                )
                messages.add_message(request, messages.INFO, "Validation finished.")
        except DatabaseError as e:
            messages.add_message(
                request, messages.ERROR, "Database error: {}".format(e)
            )
        return redirect("wamtram2:entry_batch_detail", batch_id=self.kwargs["batch_id"])


class DeleteEntryView(LoginRequiredMixin,DeleteView):
    model = TrtDataEntry
    success_url = reverse_lazy('wamtram2:batches_curation')
    
    def dispatch(self, request, *args, **kwargs):
        # FIXME: Permission check
        if not (
            request.user.groups.filter(name="WAMTRAM2_STAFF").exists()
            or request.user.is_superuser
        ):
            return HttpResponseForbidden(
                "You do not have permission to view this record"
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        batch_id = self.kwargs['batch_id']
        return reverse_lazy('wamtram2:entry_batch_detail', kwargs={'batch_id': batch_id})

class ProcessDataEntryBatchView(LoginRequiredMixin, View):
    """
    View class for processing a data entry batch.

    This view executes a stored procedure to process a data entry batch
    identified by the batch ID provided in the URL parameters. It uses the
    'wamtram2' database connection and redirects the user to the detail page
    of the processed batch.

    Attributes:
        None

    Methods:
        get: Handles the GET request and executes the stored procedure.

    Raises:
        DatabaseError: If there is an error executing the stored procedure.

    Returns:
        HttpResponseRedirect: Redirects the user to the detail page of the
        processed batch.
    """

    def dispatch(self, request, *args, **kwargs):
        # FIXME: Permission check
        if not (
            request.user.groups.filter(name="WAMTRAM2_STAFF").exists()
            or request.user.is_superuser
        ):
            return HttpResponseForbidden(
                "You do not have permission to view this record"
            )
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            with connections["wamtram2"].cursor() as cursor:
                cursor.execute(
                    "EXEC dbo.EntryBatchProcessWEB @ENTRY_BATCH_ID = %s;",
                    [self.kwargs["batch_id"]],
                )
                messages.add_message(request, messages.INFO, "Processing finished.")
        except DatabaseError as e:
            messages.add_message(
                request, messages.ERROR, "Database error: {}".format(e)
            )
        return redirect("wamtram2:entry_batch_detail", batch_id=self.kwargs["batch_id"])

class FindTurtleView(LoginRequiredMixin, View):
    """
    View class for finding a turtle based on tag and pit tag ID.
    """

    def dispatch(self, request, *args, **kwargs):
        if not (
            request.user.groups.filter(name="WAMTRAM2_VOLUNTEER").exists()
            or request.user.groups.filter(name="WAMTRAM2_TEAM_LEADER").exists()
            or request.user.groups.filter(name="WAMTRAM2_STAFF").exists()
            or request.user.is_superuser
        ):
            return HttpResponseForbidden("You do not have permission to view this record")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        batch_id = kwargs.get("batch_id")
        form = SearchForm(initial={"batch_id": batch_id})
        no_turtle_found = request.COOKIES.get(f'{batch_id}_no_turtle_found') == "true"
        tag_id = request.COOKIES.get(f'{batch_id}_tag_id')
        tag_type = request.COOKIES.get(f'{batch_id}_tag_type')
        tag_side = request.COOKIES.get(f'{batch_id}_tag_side')
        turtle = None
        first_observation_date = None
        latest_site = None
        batch = None
        template_name = "No template associated"
        new_tag_entry = None
        if tag_id and tag_type and not turtle:
            new_tag_entry = TrtDataEntry.objects.filter(
                Q(new_left_tag_id__tag_id=tag_id) |
                Q(new_left_tag_id_2__tag_id=tag_id) |
                Q(new_right_tag_id__tag_id=tag_id) |
                Q(new_right_tag_id_2__tag_id=tag_id) |
                Q(new_pittag_id__pittag_id=tag_id) |
                Q(new_pittag_id_2__pittag_id=tag_id) |
                Q(new_pittag_id_3__pittag_id=tag_id) |
                Q(new_pittag_id_4__pittag_id=tag_id)
            ).select_related('entry_batch', 'place_code', 'species_code').order_by('-entry_batch__entry_date').first()

        if batch_id:
            batch = TrtEntryBatches.objects.filter(entry_batch_id=batch_id).first()
            if batch and batch.template:
                template_name = batch.template.name

        if tag_id and tag_type and not no_turtle_found:
            tag = TrtTags.objects.select_related('turtle').filter(tag_id=tag_id).first()
            if tag:
                turtle = tag.turtle
            else:
                pit_tag = TrtPitTags.objects.select_related('turtle').filter(pittag_id=tag_id).first()
                if pit_tag:
                    turtle = pit_tag.turtle

            if turtle:
                first_observation = turtle.trtobservations_set.order_by('observation_date').first()
                if first_observation:
                    first_observation_date = first_observation.observation_date

                latest_observation = turtle.trtobservations_set.order_by('-observation_date').first()
                if latest_observation and latest_observation.place_code:
                    latest_site = latest_observation.place_code.place_name

        return render(request, "wamtram2/find_turtle.html", {
            "form": form,
            "turtle": turtle,
            "no_turtle_found": no_turtle_found,
            "tag_id": tag_id,
            "tag_type": tag_type,
            "tag_side": tag_side,
            "first_observation_date": first_observation_date,
            "latest_site": latest_site,
            "batch_id": batch_id,
            "batch": batch,
            "template_name": template_name,
            "new_tag_entry": new_tag_entry,
        })


    def set_cookie(self, response, batch_id, tag_id=None, tag_type=None, tag_side=None, no_turtle_found=False, do_not_process=False):
        if tag_id:
            response.set_cookie(f'{batch_id}_tag_id', tag_id, max_age=63072000)
        if tag_type:
            response.set_cookie(f'{batch_id}_tag_type', tag_type, max_age=63072000)
        if tag_side:
            response.set_cookie(f'{batch_id}_tag_side', tag_side, max_age=63072000)
        response.set_cookie(f'{batch_id}_no_turtle_found', 'true' if no_turtle_found else 'false', max_age=63072000)
        response.set_cookie(f'{batch_id}_do_not_process', 'true' if do_not_process else 'false', max_age=63072000)
        return response

    def post(self, request, *args, **kwargs):
        batch_id = kwargs.get("batch_id")
        form = SearchForm(request.POST, initial={"batch_id": batch_id})
        no_turtle_found = False
        tag_type = None
        tag_id = None
        tag_side = None
        turtle = None
        create_and_review = request.POST.get('create_and_review') == 'true'
        new_tag_entry = None

        if form.is_valid():
            tag_id = form.cleaned_data["tag_id"]

            if not create_and_review:
                tag = TrtTags.objects.select_related('turtle').filter(tag_id=tag_id).first()
                if tag:
                    turtle = tag.turtle
                    tag_type = "recapture_tag"
                    tag_side = tag.side
                else:
                    pit_tag = TrtPitTags.objects.select_related('turtle').filter(pittag_id=tag_id).first()
                    if pit_tag:
                        turtle = pit_tag.turtle
                        tag_type = "recapture_pit_tag"
                    else:
                        tag_type = "unknown_tag"
                        
                if not turtle:
                    new_tag_entry = TrtDataEntry.objects.filter(
                        Q(new_left_tag_id__tag_id=tag_id) |
                        Q(new_left_tag_id_2__tag_id=tag_id) |
                        Q(new_right_tag_id__tag_id=tag_id) |
                        Q(new_right_tag_id_2__tag_id=tag_id) |
                        Q(new_pittag_id__pittag_id=tag_id) |
                        Q(new_pittag_id_2__pittag_id=tag_id) |
                        Q(new_pittag_id_3__pittag_id=tag_id) |
                        Q(new_pittag_id_4__pittag_id=tag_id)
                    ).order_by('-entry_batch__entry_date').first()

                    if new_tag_entry:
                        if any([str(new_tag_entry.new_left_tag_id) == str(tag_id), 
                                str(new_tag_entry.new_left_tag_id_2) == str(tag_id)]):
                            tag_type = "recapture_tag"
                            tag_side = "L"
                        elif any([str(new_tag_entry.new_right_tag_id) == str(tag_id), 
                                    str(new_tag_entry.new_right_tag_id_2) == str(tag_id)]):
                            tag_type = "recapture_tag"
                            tag_side = "R"
                        else:
                            tag_type = "recapture_pit_tag"
                            tag_side = None
                    else:
                        no_turtle_found = True

                if turtle:
                    response = redirect(reverse('wamtram2:find_turtle', kwargs={'batch_id': batch_id}))
                    return self.set_cookie(response, batch_id, tag_id, tag_type, tag_side)
                elif new_tag_entry:
                    response = render(request, "wamtram2/find_turtle.html", {
                        "form": form,
                        "turtle": turtle,
                        "new_tag_entry": new_tag_entry,
                        "no_turtle_found": no_turtle_found,
                        "tag_id": tag_id,
                        "tag_type": tag_type,
                        "tag_side": tag_side,
                        "batch_id": batch_id,
                    })
                    return self.set_cookie(response, batch_id, tag_id, tag_type, tag_side, no_turtle_found)
                else:
                    response = redirect(reverse('wamtram2:find_turtle', kwargs={'batch_id': batch_id}))
                    return self.set_cookie(response, batch_id, tag_id, tag_type, tag_side, no_turtle_found=True)
            else:
                tag_type = request.POST.get('tag_type', 'unknown_tag')
                tag_side = request.POST.get('tag_side', None)
                response = redirect(reverse('wamtram2:newtrtdataentry', kwargs={'batch_id': batch_id}))
                return self.set_cookie(response, batch_id, tag_id, tag_type, tag_side, do_not_process=True)
        else:
            response = render(request, "wamtram2/find_turtle.html", {
                "form": form,
                "no_turtle_found": no_turtle_found,
                "tag_id": tag_id,
                "tag_type": tag_type,
                "tag_side": tag_side,
                "batch_id": batch_id,
            })

        return self.set_cookie(response, batch_id, tag_id, tag_type, tag_side)
    
class ObservationDetailView(LoginRequiredMixin, DetailView):
    model = TrtObservations
    template_name = "wamtram2/observation_detail.html"
    
    def dispatch(self, request, *args, **kwargs):
        if not (
            request.user.groups.filter(name="WAMTRAM2_VOLUNTEER").exists()
            or request.user.groups.filter(name="WAMTRAM2_TEAM_LEADER").exists()
            or request.user.groups.filter(name="WAMTRAM2_STAFF").exists()
            or request.user.is_superuser
        ):
            return HttpResponseForbidden("You do not have permission to view this record")
        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = get_object_or_404(TrtObservations, observation_id=self.kwargs.get("pk"))
        context["observation"] = obj
        context["tags"] = obj.trtrecordedtags_set.all()
        context["pittags"] = obj.trtrecordedpittags_set.all()
        context["measurements"] = obj.trtmeasurements_set.all()
        
        if obj.place_code:
            context["place_full_name"] = obj.place_code.get_full_name()
        else:
            context["place_full_name"] = ""
        return context


class TurtleListView(LoginRequiredMixin, PaginateMixin, ListView):
    """
    View class for displaying a list of turtles.

    Attributes:
        model (Model): The model class representing the turtles.
        paginate_by (int): The number of turtles to display per page.
    """

    model = TrtTurtles
    paginate_by = 50

    def get_context_data(self, **kwargs):
        """
        Retrieves the context data for rendering the template.

        Returns:
            dict: The context data.
        """
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"{settings.SITE_CODE} | WAMTRAM2"
        # Pass in any query string
        if "q" in self.request.GET:
            context["query_string"] = self.request.GET["q"]
        context["breadcrumbs"] = (
            Breadcrumb("Home", reverse("home")),
            Breadcrumb("Tagged turtles", None),
        )
        return context

    def get_queryset(self):
        """
        Retrieves the queryset of turtles to be displayed.

        Returns:
            QuerySet: The queryset of turtles.
        """
        qs = super().get_queryset()
        # General-purpose search uses the `q` parameter.
        if "q" in self.request.GET and self.request.GET["q"]:
            q = self.request.GET["q"]
            qs = qs.filter(
                Q(pk__icontains=q)
                | Q(trttags__tag_id__icontains=q)
                | Q(trtpittags__pittag_id__icontains=q)
            ).distinct()

        return qs.order_by("pk")


class TurtleDetailView(LoginRequiredMixin, DetailView):
    """
    View class for displaying the details of a turtle.

    Attributes:
        model (Model): The model class representing the turtle.
    """

    model = TrtTurtles
    
    def dispatch(self, request, *args, **kwargs):
        if not (
            request.user.groups.filter(name="WAMTRAM2_VOLUNTEER").exists()
            or request.user.groups.filter(name="WAMTRAM2_TEAM_LEADER").exists()
            or request.user.groups.filter(name="WAMTRAM2_STAFF").exists()
            or request.user.is_superuser
        ):
            return HttpResponseForbidden("You do not have permission to view this record")
        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        """
        Retrieves the context data for rendering the template.

        Returns:
            dict: The context data.
        """
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        
        pittags = obj.recorded_pittags.all().order_by('pittag_id', '-observation_id')
        seen = set()
        unique_pittags = []
        for tag in pittags:
            if tag.pittag_id_id not in seen:
                unique_pittags.append(tag)
                seen.add(tag.pittag_id_id)
        
        context["page_title"] = f"{settings.SITE_CODE} | WAMTRAM2 | {obj.pk}"
        context["tags"] = obj.trttags_set.all()
        context["pittags"] = unique_pittags
        context["observations"] = obj.trtobservations_set.all()
        return context

SEX_CHOICES = [
    ("M", "Male"),
    ("F", "Female"),
    ("I", "Indeterminate"),
]

class TemplateManageView(LoginRequiredMixin, FormView):
    template_name = 'wamtram2/template_manage.html'
    form_class = TemplateForm
    def dispatch(self, request, *args, **kwargs):
        if not (
            request.user.groups.filter(name="WAMTRAM2_TEAM_LEADER").exists()
            or request.user.groups.filter(name="WAMTRAM2_STAFF").exists()
            or request.user.is_superuser
        ):
            return HttpResponseForbidden("You do not have permission to access this page.")
        
        elif request.method == 'DELETE':
            return self.delete(request, *args, **kwargs)
        elif request.method == 'GET' and 'location_code' in request.GET:
            return self.get_places(request)
        
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Template created successfully')
        return redirect('wamtram2:template_manage')

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['templates'] = Template.objects.all().order_by('-template_id')
        context['locations'] = list(TrtLocations.get_ordered_locations())
        context['places'] = list(TrtPlaces.objects.all())
        context['species'] = list(TrtSpecies.objects.all())
        context['sex_choices'] = SEX_CHOICES
        return context

    def delete(self, request, template_key):
        template = get_object_or_404(Template, pk=template_key)
        template.delete()
        return JsonResponse({'message': 'Template deleted'})
    
    def get_places(self, request):
        """
        Retrieves places based on the provided location code.

        Args:
            request (HttpRequest): The HTTP request.

        Returns:
            JsonResponse: The JSON response with places data.
        """
        location_code = request.GET.get('location_code')
        places = TrtPlaces.objects.filter(location_code=location_code)
        places_list = list(places.values('place_code', 'place_name'))
        return JsonResponse(places_list, safe=False)


def get_place_full_name(request):
    place_code = request.GET.get('place_code')
    try:
        place = TrtPlaces.objects.get(place_code=place_code)
        full_name = place.get_full_name()
        return JsonResponse({'full_name': full_name})
    except TrtPlaces.DoesNotExist:
        return JsonResponse({'error': 'Place not found'}, status=404)
    
    
def check_template_name(request):
    name = request.GET.get('name')
    is_available = not Template.objects.filter(name=name).exists()
    return JsonResponse({'is_available': is_available})
    
    
class ValidateTagView(View):
    """
    View for validating tags.
    Provides functionality to validate different types of tags.

    Methods:
        validate_recaptured_tag(request): Validates a recaptured tag.
        validate_new_tag(request): Validates a new tag.
        validate_new_pit_tag(request): Validates a new PIT tag.
        validate_recaptured_pit_tag(request): Validates a recaptured PIT tag.
        get(request, *args, **kwargs): Handles GET requests.
    """

    def validate_recaptured_tag(self, request):
        """
        Validates a recaptured tag.

        Args:
            request (HttpRequest): The HTTP request.

        Returns:
            JsonResponse: The JSON response.
        """
        turtle_id = request.GET.get('turtle_id')
        tag = request.GET.get('tag')
        side = request.GET.get('side')

        print(turtle_id, tag, side)

        if not tag or not side:
            return JsonResponse({'valid': False, 'wrong_side': False, 'message': 'Missing parameters'})
        if turtle_id:
            try:
                turtle_id = int(turtle_id)
                tag_obj = TrtTags.objects.filter(tag_id=tag).first()

                if tag_obj:
                    if tag_obj.turtle_id != turtle_id:
                        return JsonResponse({
                            'valid': False, 
                            'wrong_side': False, 
                            'message': 'Tag belongs to another turtle', 
                            'other_turtle_id': tag_obj.turtle_id,
                            'status': tag_obj.tag_status.description
                        })
                    else:
                        if tag_obj.tag_status.tag_status != 'ATT':
                            return JsonResponse({
                                'valid': False,
                                'wrong_side': False,
                                'message': f'Tag status: {tag_obj.tag_status.description}',
                                'status': tag_obj.tag_status.description
                            })
                        is_valid = True
                        wrong_side = (tag_obj.side.lower() != side.lower())
                        return JsonResponse({
                            'valid': is_valid, 
                            'wrong_side': wrong_side, 
                            'other_turtle_id': None,
                            'status': tag_obj.tag_status.description
                        })
            except TrtTurtles.DoesNotExist:
                    return JsonResponse({'valid': False, 'wrong_side': False, 'message': 'Turtle not found'})

        new_tag_entry = TrtDataEntry.objects.filter(
            Q(new_left_tag_id__tag_id=tag) |
            Q(new_left_tag_id_2__tag_id=tag) |
            Q(new_right_tag_id__tag_id=tag) |
            Q(new_right_tag_id_2__tag_id=tag)
        ).order_by('-entry_batch__entry_date').first()
                
        if new_tag_entry:
            if new_tag_entry.new_left_tag_id.tag_id == tag or new_tag_entry.new_left_tag_id_2.tag_id == tag:
                actual_side = 'L'
            else:
                actual_side = 'R'
            
            wrong_side = (actual_side.lower() != side.lower())
            
            return JsonResponse({
                'valid': True, 
                'wrong_side': wrong_side,
                'message': 'Tag found in previous unprocessed entry',
                'entry_date': new_tag_entry.entry_batch.entry_date.strftime('%Y-%m-%d')
            })
        else:
            return JsonResponse({'valid': False, 'wrong_side': False, 'message': 'Tag not found', 'tag_not_found': True})



    def validate_new_tag(self, request):
        """
        Validates a new tag.

        Args:
            request (HttpRequest): The HTTP request.

        Returns:
            JsonResponse: The JSON response.
        """
        tag = request.GET.get('tag')
        if not tag:
            return JsonResponse({'valid': False, 'message': 'Missing tag parameter'})

        try:
            tag_obj = TrtTags.objects.filter(tag_id=tag).select_related('tag_status').first()
            if tag_obj:
                if tag_obj.turtle_id:
                    return JsonResponse({
                        'valid': False, 
                        'message': 'Tag belongs to another turtle', 
                        'other_turtle_id': tag_obj.turtle_id,
                        'status': tag_obj.tag_status.description
                    })
                if tag_obj.tag_status.tag_status == 'U':
                    return JsonResponse({'valid': True, 'other_turtle_id': None, 'status': tag_obj.tag_status.description})
                else:
                    return JsonResponse({'valid': False, 'status': tag_obj.tag_status.description})
            else:
                return JsonResponse({'valid': False, 'message': 'Flipper tag not found', 'tag_not_found': True})
        except Exception as e:
            return JsonResponse({'valid': False, 'message': str(e)})

    def validate_new_pit_tag(self, request):
        """
        Validates a new PIT tag.

        Args:
            request (HttpRequest): The HTTP request.

        Returns:
            JsonResponse: The JSON response.
        """
        tag = request.GET.get('tag')
        if not tag:
            return JsonResponse({'valid': False, 'message': 'Missing tag parameter'})

        try:
            pit_tag = TrtPitTags.objects.filter(pittag_id=tag).select_related('turtle', 'pit_tag_status').first()
            if pit_tag:
                if pit_tag.turtle:
                    return JsonResponse({
                        'valid': False, 
                        'message': 'PIT tag belongs to another turtle', 
                        'other_turtle_id': pit_tag.turtle.turtle_id,
                        'status': pit_tag.pit_tag_status.description
                    })
                if pit_tag.pit_tag_status.pit_tag_status == 'U':
                    return JsonResponse({'valid': True, 'other_turtle_id': None, 'status': pit_tag.pit_tag_status.description})
                else:
                    return JsonResponse({'valid': False, 'status': pit_tag.pit_tag_status.description})
            else:
                return JsonResponse({'valid': False, 'message': 'PIT tag not found', 'tag_not_found': True})
        except Exception as e:
            return JsonResponse({'valid': False, 'message': str(e)})

    def validate_recaptured_pit_tag(self, request):
        """
        Validates a recaptured PIT tag.

        Args:
            request (HttpRequest): The HTTP request.

        Returns:
            JsonResponse: The JSON response.
        """
        turtle_id = request.GET.get('turtle_id')
        tag = request.GET.get('tag')

        if not tag:
            return JsonResponse({'valid': False, 'message': 'Missing parameters'})

        try:
            if turtle_id:
                turtle_id = int(turtle_id)
                pit_tag = TrtPitTags.objects.filter(pittag_id=tag).select_related('turtle').first()

                if pit_tag:
                    if pit_tag.turtle and pit_tag.turtle.turtle_id != int(turtle_id):
                        return JsonResponse({
                            'valid': False,
                            'message': 'PIT tag belongs to another turtle',
                            'other_turtle_id': pit_tag.turtle.turtle_id,
                            'status': pit_tag.pit_tag_status.description
                        })
                    elif pit_tag.pit_tag_status.pit_tag_status != 'ATT':
                        return JsonResponse({
                            'valid': False,
                            'message': f'PIT tag status: {pit_tag.pit_tag_status.description}',
                            'status': pit_tag.pit_tag_status.description
                        })
                    else:
                        return JsonResponse({'valid': True})
                else:
                    return JsonResponse({'valid': False, 'message': 'PIT tag not found'})
            else:
                new_pit_tag_entry = TrtDataEntry.objects.filter(
                Q(new_pittag_id__pittag_id=tag) |
                Q(new_pittag_id_2__pittag_id=tag) |
                Q(new_pittag_id_3__pittag_id=tag) |
                Q(new_pittag_id_4__pittag_id=tag),
                ).order_by('-entry_batch__entry_date').first()
                
                if new_pit_tag_entry:
                    return JsonResponse({
                        'valid': True, 
                        'message': 'Tag found in previous unprocessed entry',
                        'entry_date': new_pit_tag_entry.entry_batch.entry_date.strftime('%Y-%m-%d')
                    })
                else:
                    return JsonResponse({'valid': False, 'message': 'PIT tag not found', 'tag_not_found': True})
        except Exception as e:
            return JsonResponse({'valid': False, 'message': str(e)})




    def get(self, request, *args, **kwargs):
        """
        Handles GET requests for tag validation.

        Args:
            request (HttpRequest): The HTTP request.

        Returns:
            JsonResponse: The JSON response.
        """
        validation_type = request.GET.get('type')
        if validation_type == 'recaptured_tag':
            return self.validate_recaptured_tag(request)
        elif validation_type == 'new_tag':
            return self.validate_new_tag(request)
        elif validation_type == 'new_pit_tag':
            return self.validate_new_pit_tag(request)
        elif validation_type == 'recaptured_pit_tag':
            return self.validate_recaptured_pit_tag(request)
        else:
            return JsonResponse({'valid': False, 'message': 'Invalid validation type'})


def search_persons(request):
    query = request.GET.get('q', '')
    query_parts = query.split()

    # Build the query
    if len(query_parts) == 1:
        persons = TrtPersons.objects.filter(
            Q(first_name__icontains=query_parts[0]) | Q(surname__icontains=query_parts[0])
        ).values('person_id', 'first_name', 'surname')
    elif len(query_parts) >= 2:
        persons = TrtPersons.objects.filter(
            Q(first_name__icontains=query_parts[0]) & Q(surname__icontains=query_parts[1])
        ).values('person_id', 'first_name', 'surname')

    return JsonResponse(list(persons), safe=False)


def search_places(request):
    query = request.GET.get('q', '')
    
    if '(' in query and ')' in query:
        place_name, location_code = query.split('(', 1)
        location_code = location_code.rstrip(')')
        places = TrtPlaces.objects.filter(
            place_name__icontains=place_name.strip(),
            location_code__location_name__icontains=location_code.strip()
        ).values('place_code', 'place_name', 'location_code__location_name')[:10]
    else:
        places = TrtPlaces.objects.filter(
            Q(place_name__icontains=query) | Q(location_code__location_name__icontains=query)
        ).values('place_code', 'place_name', 'location_code__location_name')[:10]
        
    for place in places:
        place['full_name'] = f"{place['place_name']} ({place['location_code__location_name']})"
    
    return JsonResponse(list(places), safe=False)


class ExportDataView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        # Permission check: only allow users in the specific groups or superusers
        if not (
            request.user.groups.filter(name="WAMTRAM2_STAFF").exists()
            or request.user.is_superuser
        ):
            return HttpResponseForbidden(
                "You do not have permission to view this record"
            )
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        # Handle different actions based on the 'action' parameter
        action = request.GET.get('action')
        if action == 'get_places':
            return self.get_places(request)
        elif action == 'get_species':
            return self.get_species(request)
        elif action == 'get_sexes':
            return self.get_sexes(request)
        return self.export_data(request)

    def export_data(self, request):
        # Retrieve filter parameters from the request
        observation_date_from = request.GET.get("observation_date_from")
        observation_date_to = request.GET.get("observation_date_to")
        place_code = request.GET.get("place_code")
        species = request.GET.get("species")
        sex = request.GET.get("sex")
        file_format = request.GET.get("format", "csv")

        queryset = TrtDataEntry.objects.filter(observation_id__isnull=False)
        
        # Filter by date range
        if observation_date_from and observation_date_to:
            queryset = queryset.filter(observation_date__range=[observation_date_from, observation_date_to])
        elif observation_date_from:
            queryset = queryset.filter(observation_date__gte=observation_date_from)
        elif observation_date_to:
            queryset = queryset.filter(observation_date__lte=observation_date_to)
        
        # Filter by place
        if place_code:
            queryset = queryset.filter(place_code=place_code)

        # Filter by species
        if species:
            queryset = queryset.filter(species_code=species)

        # Filter by sex
        if sex:
            queryset = queryset.filter(sex=sex)

        # File generation logic
        if file_format == "csv":
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="data_export.csv"'
            writer = csv.writer(response)
            writer.writerow([field.name for field in TrtDataEntry._meta.fields])  # Write header
            for entry in queryset:
                writer.writerow([getattr(entry, field.name) for field in TrtDataEntry._meta.fields])
        elif file_format == "xlsx":
            response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response["Content-Disposition"] = 'attachment; filename="data_export.xlsx"'
            wb = Workbook()
            ws = wb.active
            ws.append([field.name for field in TrtDataEntry._meta.fields])  # Write header
            for entry in queryset:
                ws.append([getattr(entry, field.name) for field in TrtDataEntry._meta.fields])
            wb.save(response)

        return response

    def get_places(self, request):
        """Retrieve places based on the specified date range."""
        observation_date_from = request.GET.get("observation_date_from")
        observation_date_to = request.GET.get("observation_date_to")

        places = TrtPlaces.objects.filter(
            trtdataentry__observation_date__range=[observation_date_from, observation_date_to]
        ).select_related('location_code').distinct()

        place_list = [
            {
                "value": place.place_code,
                "label": place.get_full_name(),
                "location_name": place.location_code.location_name,
            }
            for place in places
        ]
        
        return JsonResponse({"places": place_list})

    def get_species(self, request):
        """Retrieve species based on the specified date range."""
        observation_date_from = request.GET.get("observation_date_from")
        observation_date_to = request.GET.get("observation_date_to")

        species = TrtSpecies.objects.filter(
            trtdataentry__observation_date__range=[observation_date_from, observation_date_to]
        ).distinct()

        species_list = [
            {"value": specie.species_code, "label": specie.common_name}
            for specie in species
        ]

        return JsonResponse({"species": species_list})

    def get_sexes(self, request):
        """Retrieve available sex choices based on the defined SEX_CHOICES."""
        # Directly use the SEX_CHOICES to return the options for the frontend
        sex_list = [
            {"value": choice[0], "label": choice[1]}
            for choice in SEX_CHOICES
        ]

        return JsonResponse({"sexes": sex_list})


class FilterFormView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        # Permission check: only allow users in the specific groups or superusers
        if not (
            request.user.groups.filter(name="WAMTRAM2_VOLUNTEER").exists()
            or request.user.groups.filter(name="WAMTRAM2_TEAM_LEADER").exists()
            or request.user.groups.filter(name="WAMTRAM2_STAFF").exists()
            or request.user.is_superuser
        ):
            return HttpResponseForbidden(
                "You do not have permission to view this record"
            )
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        action = request.GET.get('action')
        if action == 'get_filter_options':
            return self.get_filter_options(request)
        return render(request, 'wamtram2/export_form.html')

    def get_filter_options(self, request):
        from_date = request.GET.get('observation_date_from')
        to_date = request.GET.get('observation_date_to')

        observations = TrtObservations.objects.filter(
            observation_date__range=[from_date, to_date]
        )
        
        places = observations.values('place__place_code', 'place__location_name', 'place__place_name').distinct()
        species = TrtSpecies.objects.filter(observations__in=observations).distinct()
        sexes = observations.values_list('sex', flat=True).distinct()
        turtle_statuses = TrtTurtleStatus.objects.filter(observations__in=observations).distinct()

        return JsonResponse({
            'places': [{'value': p.place_code, 'label': f"{p.location_code.location_name} - {p.place_name}"} for p in places],
            'species': [{'value': s.species_code, 'label': s.common_name} for s in species],
            'sexes': [{'value': s, 'label': self.get_sex_label(s)} for s in sexes],
            'turtle_statuses': [{'value': ts.turtle_status, 'label': ts.description} for ts in turtle_statuses],
        })
        
    def get_sex_label(self, sex_code):
        sex_choices = {
            'M': 'Male',
            'F': 'Female',
            'I': 'Indeterminate',
        }
        return sex_choices.get(sex_code, 'Unknown')


class DudTagManageView(LoginRequiredMixin, View):
    template_name = 'wamtram2/dud_tag_manage.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden("You do not have permission to view this record")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        entries = TrtDataEntry.objects.filter(
            dud_filpper_tag__isnull=False
        ).select_related('observation_id', 'turtle_id')
        tag_states = TrtTagStates.objects.all()
        return render(request, self.template_name, {'entries': entries, 'tag_states': tag_states})

    def post(self, request):
        entry_id = request.POST.get('entry_id')
        tag_type = request.POST.get('tag_type')
        tag_id = request.POST.get('tag_id')
        entry = get_object_or_404(TrtDataEntry, pk=entry_id)

        if entry.observation_id:
            observation = entry.observation_id
            
            if tag_type == 'flipper':
                observation.dud_filpper_tag = tag_id
            elif tag_type == 'flipper_2':
                observation.dud_filpper_tag_2 = tag_id
            elif tag_type == 'pit':
                observation.dud_pit_tag = tag_id
            elif tag_type == 'pit_2':
                observation.dud_pit_tag_2 = tag_id

            observation.save()

        return redirect('wamtram2:dud_tag_manage')

class BatchesCurationView(LoginRequiredMixin,ListView):
    model = TrtEntryBatches
    template_name = 'wamtram2/batches_curation.html'
    context_object_name = 'batches'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        if not (
            request.user.groups.filter(name="WAMTRAM2_TEAM_LEADER").exists()
            or request.user.groups.filter(name="WAMTRAM2_STAFF").exists()
            or request.user.is_superuser
        ):
            return HttpResponseForbidden("You do not have permission to view this record")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().annotate(
            entry_count=Count('trtdataentry'),
            flagged_entry_count=Count('trtdataentry', filter=Q(trtdataentry__do_not_process=True))
        )
        
        location = self.request.GET.get('location')
        place = self.request.GET.get('place')
        year = self.request.GET.get('year')
        show_all = self.request.GET.get('show_all')
        
        if not self.request.GET:
            return queryset.order_by('-entry_batch_id')[:20]
        
        if self.request.GET.get('show_all'):
            return queryset.order_by('-entry_batch_id')
        
        if not (location or year):
            return TrtEntryBatches.objects.none()

        query = Q()

        if location and place and year:
            year_code = str(year)[-2:]
            query = Q(batches_code__contains=place) & Q(batches_code__endswith=year_code)
        elif location and year:
            year_code = str(year)[-2:]
            query = Q(batches_code__contains=location) & Q(batches_code__endswith=year_code)
        elif location:
            query = Q(batches_code__contains=location)
        elif year:
            year_code = str(year)[-2:]
            query = Q(batches_code__endswith=year_code)
            
        if query:
            result = queryset.filter(query).order_by('-entry_batch_id')
            return result
        else:
            result = queryset.order_by('-entry_batch_id')
            return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['locations'] = list(TrtLocations.get_ordered_locations())
        context['places'] = TrtPlaces.objects.all().order_by('place_name')
        current_year = timezone.now().year
        context['years'] = range(2022, current_year + 1)
        context['selected_location'] = self.request.GET.get('location', '')
        context['selected_place'] = self.request.GET.get('place', '')
        context['selected_year'] = self.request.GET.get('year', '')
        context['templates'] = Template.objects.all()
        context['batches'] = self.get_queryset()
        context['is_initial_load'] = not bool(self.request.GET)
        places = TrtPlaces.objects.select_related('location_code').all()
        places_data = [
            {
                'place_code': place.place_code,
                'place_name': place.place_name,
                'full_name': place.get_full_name()
            }
            for place in places
        ]
        context['places_json'] = json.dumps(places_data, cls=DjangoJSONEncoder)
        context['show_all'] = self.request.GET.get('show_all', False)

        return context
    def get(self, request, *args, **kwargs):
        if 'action' in request.GET:
            action = request.GET.get('action')
            if action == 'check_batch_code':
                return self.check_batch_code(request)
            
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_to_string('wamtram2/batches_curation.html', context, request=request)
            return JsonResponse({
                'html': html,
                'count': context['paginator'].count if 'paginator' in context else 0,
                'num_pages': context['paginator'].num_pages if 'paginator' in context else 1,
                'current_page': context['page_obj'].number if 'page_obj' in context else 1,
                'show_all': context.get('show_all', False),
            })
        return super().get(request, *args, **kwargs)
    
    def check_batch_code(self, request):
        code = request.GET.get('code')
        batch_id = request.GET.get('batch_id')
        if batch_id:
            is_unique = not TrtEntryBatches.objects.filter(batches_code=code).exclude(pk=batch_id).exists()
        else:
            is_unique = not TrtEntryBatches.objects.filter(batches_code=code).exists()
        return JsonResponse({'is_unique': is_unique})
    
    def get_places(self, request):
        location_code = request.GET.get('location_code')
        places = TrtPlaces.objects.filter(location_code=location_code).values('place_code', 'place_name')
        return JsonResponse(list(places), safe=False)
    
    
class CreateNewEntryView(LoginRequiredMixin, ListView):
    model = TrtEntryBatches
    template_name = 'wamtram2/create_new_entry.html'
    context_object_name = 'batches'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        # Permission check: only allow users in the specific groups or superusers
        if not (
            request.user.groups.filter(name="WAMTRAM2_VOLUNTEER").exists()
            or request.user.groups.filter(name="WAMTRAM2_TEAM_LEADER").exists()
            or request.user.groups.filter(name="WAMTRAM2_STAFF").exists()
            or request.user.is_superuser
        ):
            return HttpResponseForbidden(
                "You do not have permission to view this record"
            )
        return super().dispatch(request, *args, **kwargs)
    

    def get_queryset(self):
        """
        Filter the batches data based on query parameters
        """
        queryset = super().get_queryset()
        
        if self.request.GET.get('show_all'):
            return queryset.order_by('-entry_batch_id')

        location = self.request.GET.get('location')
        place = self.request.GET.get('place')
        year = self.request.GET.get('year')

        query = Q()
        current_year = timezone.now().year
        years = {str(year): str(year)[-2:] for year in range(2022, current_year + 1)}

        # Generate queries based on different filter parameters
        if location and place and year:
            year_code = years.get(year)
            if year_code:
                query = Q(batches_code__contains=place) & Q(batches_code__endswith=year_code)
        elif location and year:
            year_code = years.get(year)
            if year_code:
                query = Q(batches_code__contains=location) & Q(batches_code__endswith=year_code)
        elif location:
            query = Q(batches_code__contains=location)
        elif year:
            year_code = years.get(year)
            if year_code:
                query = Q(batches_code__endswith=year_code)

        if query:
            return queryset.filter(query).order_by('-entry_batch_id')
        else:
            return TrtEntryBatches.objects.none()

    def get_context_data(self, **kwargs):
        """
        Provide context data to the template, including locations, places, and years
        """
        context = super().get_context_data(**kwargs)
        locations = TrtLocations.get_ordered_locations()
        places = TrtPlaces.objects.none()

        if 'location' in self.request.GET and self.request.GET['location']:
            places = TrtPlaces.objects.filter(location_code=self.request.GET['location'])

        current_year = timezone.now().year
        years = {str(year): str(year)[-2:] for year in range(2022, current_year + 1)}

        context.update({
            'locations': locations,
            'places': places,
            'years': years,
            'selected_location': self.request.GET.get('location', ''),
            'selected_place': self.request.GET.get('place', ''),
            'selected_year': self.request.GET.get('year', ''),
            'templates': Template.objects.all(),
        })

        return context

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_to_string('wamtram2/create_new_entry.html', context, request=request)
            return JsonResponse({
                'html': html,
                'count': context['paginator'].count if 'paginator' in context else 0,
                'num_pages': context['paginator'].num_pages if 'paginator' in context else 1,
                'current_page': context['page_obj'].number if 'page_obj' in context else 1,
            })
        return super().get(request, *args, **kwargs)
    
    
@login_required
@require_POST
def quick_add_batch(request):
    if request.method == 'POST':
        batches_code = request.POST.get('batches_code')
        comments = request.POST.get('comments', '')
        template_id = request.POST.get('template')
        entered_person_id = request.POST.get('entered_person_id')
        
        entered_person = get_object_or_404(TrtPersons, pk=entered_person_id)
        
        template = None
        if template_id:
            template = get_object_or_404(Template, pk=template_id)

        batch = TrtEntryBatches.objects.create(
            batches_code=batches_code,
            comments=comments,
            entry_date=timezone.now(),
            pr_date_convention=False,
            entered_person_id=entered_person,
            template=template
        )
        try:
            batch.save()
            return JsonResponse({'success': True})
        except ValidationError as e:
                return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})

    
class BatchCodeManageView(View):
    template_name = 'wamtram2/add_batches_code.html'

    def dispatch(self, request, *args, **kwargs):
        
        if not (
            request.user.groups.filter(name="WAMTRAM2_TEAM_LEADER").exists()
            or request.user.groups.filter(name="WAMTRAM2_STAFF").exists()
            or request.user.is_superuser
        ):
            return HttpResponseForbidden(
                "You do not have permission to view this record"
            )
            
        if request.method == 'GET' and 'action' in request.GET:
            action = request.GET.get('action')
            if action == 'get_places':
                return self.get_places(request)
            elif action == 'check_batch_code':
                return self.check_batch_code(request)
        return super().dispatch(request, *args, **kwargs)
    
    def get_places(self, request):
        location_code = request.GET.get('location_code')
        places = TrtPlaces.objects.filter(location_code=location_code).values('place_code', 'place_name')
        return JsonResponse(list(places), safe=False)

    def get(self, request, batch_id=None):
        if batch_id:
            batch = get_object_or_404(TrtEntryBatches, pk=batch_id)
            form = BatchesCodeForm(instance=batch)
            entered_person = batch.entered_person_id
            entered_person_full_name = str(entered_person) if entered_person else ''
            entered_person_id = entered_person.person_id if entered_person else ''
        else:
            form = BatchesCodeForm()
            entered_person_full_name = ''
            entered_person_id = ''

        locations = TrtLocations.get_ordered_locations()
        current_year = timezone.now().year
        years = {str(year): str(year)[-2:] for year in range(2022, current_year + 1)}
        templates = Template.objects.all()

        entered_person_full_name = str(form.instance.entered_person_id) if form.instance.entered_person_id else ''
        template_selected = form.instance.template.template_id if form.instance.template else None
        context = {
            'form': form,
            'locations': locations,
            'years': years,
            'current_year': current_year,
            'templates': templates,
            'batch_id': batch_id,
            'entered_person_full_name': entered_person_full_name,
            'entered_person_id': entered_person_id,
            'template_selected': template_selected,
        }
        return render(request, self.template_name, context)

    def post(self, request, batch_id=None):
        if batch_id:
            batch = get_object_or_404(TrtEntryBatches, pk=batch_id)
            form = BatchesCodeForm(request.POST, instance=batch)
        else:
            form = BatchesCodeForm(request.POST)

        if form.is_valid():
            new_batch = form.save(commit=False)
            if not TrtEntryBatches.objects.filter(batches_code=new_batch.batches_code).exclude(pk=batch_id).exists():
                new_batch.entered_person_id = form.cleaned_data['entered_person_id']
                new_batch.template = form.cleaned_data['template']
                new_batch.save()
                return redirect(reverse('wamtram2:batches_curation'))
            else:
                form.add_error('batches_code', 'This batch code already exists.')

        locations = TrtLocations.get_ordered_locations()
        current_year = timezone.now().year
        years = {str(year): str(year)[-2:] for year in range(2022, current_year + 1)}
        templates = Template.objects.all()

        context = {
            'form': form,
            'locations': locations,
            'years': years,
            'current_year': current_year,
            'templates': templates,
            'batch_id': batch_id,
        }
        return render(request, self.template_name, context)

    @method_decorator(require_http_methods(["GET"]))
    def check_batch_code(self, request):
        code = request.GET.get('code')
        batch_id = request.GET.get('batch_id')
        if batch_id:
            is_unique = not TrtEntryBatches.objects.filter(batches_code=code).exclude(pk=batch_id).exists()
        else:
            is_unique = not TrtEntryBatches.objects.filter(batches_code=code).exists()
        return JsonResponse({'is_unique': is_unique})

    
@require_GET
def get_places(request):
    location_code = request.GET.get('location_code')
    places = TrtPlaces.objects.filter(location_code=location_code).values('place_code', 'place_name')
    return JsonResponse(list(places), safe=False)
