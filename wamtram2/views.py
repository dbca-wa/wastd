from django.conf import settings
from django.contrib import messages
from django.db import connections, DatabaseError
from django.db.models import Q, Exists, OuterRef
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic.edit import FormMixin
from django.views.generic import TemplateView, ListView, DetailView, FormView, DeleteView
from django.http import JsonResponse, QueryDict
from .models import TrtPlaces, TrtSpecies, TrtLocations
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
import os
import json
import re

from wastd.utils import Breadcrumb, PaginateMixin
from .models import (
    TrtTurtles,
    TrtTags,
    TrtPitTags,
    TrtEntryBatches,
    TrtDataEntry,
    TrtPersons,
    TrtObservations,
    Template
)
from .forms import TrtDataEntryForm, SearchForm, TrtEntryBatchesForm, TemplateForm


class HomePageView(LoginRequiredMixin, TemplateView):
    """
    A view for the home page.

    Attributes:
        template_name (str): The name of the template to be used for rendering the view.
    """

    template_name = "wamtram2/home.html"


class EntryBatchesListView(LoginRequiredMixin, ListView):
    """
    A view that displays a list of entry batches.

    Attributes:
        model (Model): The model class to use for the list view.
        template_name (str): The name of the template to use for rendering the list view.
        context_object_name (str): The name of the variable to use in the template for the list of objects.
        paginate_by (int): The number of objects to display per page.

    Methods:
        get_queryset(): Returns the queryset of objects for the list view.
        get_context_data(**kwargs): Returns the context data for rendering the list view.
    """

    model = TrtEntryBatches
    template_name = "trtentrybatches_list.html"
    context_object_name = "batches"
    paginate_by = 50

    def dispatch(self, request, *args, **kwargs):
        # FIXME: Permission check
        if not (
            request.user.groups.filter(name="Tagging Data Entry").exists()
            or request.user.groups.filter(name="Tagging Data Curation").exists()
            or request.user.is_superuser
        ):
            return HttpResponseForbidden(
                "You do not have permission to view this record"
            )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Returns the queryset of objects for the list view.

        Returns:
            QuerySet: The queryset of objects.
        """
        queryset = super().get_queryset()

        # Check if the user has requested to filter by TrtEntryBatches that have TrtDataEntrys with no observation_id
        if (
            "filter" in self.request.GET
            and self.request.GET["filter"] == "no_observation_id"
        ):
            # Subquery that checks if a TrtDataEntry with no observation_id exists for a TrtEntryBatch
            has_dataentry_no_observation_id = Exists(
                TrtDataEntry.objects.filter(
                    entry_batch_id=OuterRef("pk"), observation_id__isnull=True
                )
            )

            # Filter the queryset
            queryset = queryset.filter(has_dataentry_no_observation_id)

        return queryset.order_by("-entry_batch_id")

    def get_context_data(self, **kwargs):
        """
        Returns the context data for rendering the list view.

        Returns:
            dict: The context data.
        """
        context = super().get_context_data(**kwargs)
        context["persons"] = {
            person.person_id: person for person in TrtPersons.objects.all()
        }
        return context


class EntryBatchDetailView(LoginRequiredMixin, FormMixin, ListView):
    """
    A view for displaying list of a batch of TrtDataEntry objects.

    Attributes:
        model (Model): The model class for the TrtDataEntry objects.
        template_name (str): The name of the template to be used for rendering the view.
        context_object_name (str): The name of the variable to be used in the template for the queryset.
        paginate_by (int): The number of objects to display per page.

    Methods:
        get_queryset(): Returns the queryset of TrtDataEntry objects filtered by entry_batch_id.
        get_context_data(**kwargs): Returns the context data for rendering the template, including the persons dictionary.
        load_templates(): Loads the templates from the templates.json file.

    """

    model = TrtDataEntry
    template_name = "wamtram2/trtentrybatch_detail.html"
    context_object_name = "batch"
    paginate_by = 50
    form_class = TrtEntryBatchesForm
    
    def get_initial(self):
        initial = super().get_initial()
        batch_id = self.kwargs.get("batch_id")
        cookies_key_prefix = batch_id
        default_enterer = self.request.COOKIES.get(f'{cookies_key_prefix}_default_enterer')
        use_default_enterer = self.request.COOKIES.get(f'{cookies_key_prefix}_use_default_enterer', False)
        
        if default_enterer == "None" or not default_enterer or default_enterer == "":
            default_enterer = None

        if use_default_enterer and default_enterer:
            initial['entered_person_id'] = default_enterer
        
        return initial
        
    def load_templates(self):
        """
        Loads the templates from the templates.json file.
        """
        json_file_path = os.path.join(settings.BASE_DIR, 'wamtram2', 'templates.json')
        with open(json_file_path, 'r') as file:
            return json.load(file)

    def dispatch(self, request, *args, **kwargs):
        # FIXME: Permission check
        if not (
            request.user.groups.filter(name="Tagging Data Entry").exists()
            or request.user.groups.filter(name="Tagging Data Curation").exists()
            or request.user.is_superuser
        ):
            return HttpResponseForbidden(
                "You do not have permission to view this record"
            )
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests.

        This method checks if a 'batch_id' is in 'kwargs'. If not, it creates a new TrtEntryBatches object
        and sets the 'batch_id' key in 'kwargs' to the newly created batch's entry_batch_id.
        Then, it calls the 'get' method of the parent class using 'super()' and returns the result.

        Args:
            request: The HTTP request object.
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.

        Returns:
            The response returned by the 'get' method of the parent class.
        """
        if "batch_id" not in kwargs:
            new_batch = TrtEntryBatches.objects.create(
                pr_date_convention=False
            )  # All dates should be entered as calander dates
            self.kwargs["batch_id"] = new_batch.entry_batch_id
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """
        Returns the queryset of TrtDataEntry objects filtered by entry_batch_id.

        Returns:
            queryset (QuerySet): The filtered queryset of TrtDataEntry objects.
        """
        queryset = super().get_queryset()
        batch_id = self.kwargs.get("batch_id")

        filter_value = self.request.GET.get("filter")
        if filter_value == "processed":
            queryset = queryset.filter(entry_batch_id=batch_id, do_not_process=False)
        elif filter_value == "not_processed":
            queryset = queryset.filter(entry_batch_id=batch_id, do_not_process=True)
        else:
            queryset = queryset.filter(entry_batch_id=batch_id)

        return queryset.order_by("-data_entry_id")

    def get_context_data(self, **kwargs):
            """
            Returns the context data for rendering the template, including the persons dictionary.

            Args:
                **kwargs: Additional keyword arguments.

            Returns:
                context (dict): The context data for rendering the template.

            """
            context = super().get_context_data(**kwargs)
            context["persons"] = {
                person.person_id: person for person in TrtPersons.objects.all()
            }

            batch = TrtEntryBatches.objects.get(entry_batch_id=self.kwargs.get("batch_id"))
            context["batch"] = batch  # add the batch to the context
            initial = self.get_initial()
            context["form"] = TrtEntryBatchesForm(
                instance=batch,
                initial=initial
            )  # Add the form to the context data
            
            # Add the templates to the context data
            cookies_key_prefix = self.kwargs.get("batch_id")
            context['selected_template'] = self.request.COOKIES.get(f'{cookies_key_prefix}_selected_template', '')
            context['use_default_enterer'] = self.request.COOKIES.get(f'{cookies_key_prefix}_use_default_enterer', False)
            context['default_enterer'] = self.request.COOKIES.get(f'{cookies_key_prefix}_default_enterer', None)

            context['cookies_key_prefix'] = cookies_key_prefix
            context['default_enterer_value'] = context['default_enterer']
            context['templates'] = self.load_templates()
            
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
            return self.form_invalid(form)

    def form_valid(self, form):
        batch = form.save(commit=False)

        batch_id = batch.entry_batch_id

        # Get the existing instance from the database
        existing_batch = TrtEntryBatches.objects.get(entry_batch_id=batch_id)

        # Update the PR_DATE_CONVENTION field with the existing value
        batch.pr_date_convention = existing_batch.pr_date_convention
        batch.entry_date = existing_batch.entry_date
        batch.filename = existing_batch.filename

        # Save the batch instance
        batch.save()

        # Redirect to the success URL
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
            request.user.groups.filter(name="Tagging Data Entry").exists()
            or request.user.groups.filter(name="Tagging Data Curation").exists()
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
        json_file_path = os.path.join(settings.BASE_DIR, 'wamtram2', 'templates.json')
        with open(json_file_path, 'r') as file:
            templates = json.load(file)
        return templates.get(template_key)

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
        use_default_enterer = self.request.COOKIES.get(f'{cookies_key_prefix}_use_default_enterer', False)
        default_enterer = self.request.COOKIES.get(f'{cookies_key_prefix}_default_enterer', None)
        
        if default_enterer == "None" or not default_enterer or default_enterer == "":
            default_enterer = None
        
        # If a tag is selected, populate the form with the tag data
        if tag_id and tag_type:
            if tag_type == 'recapture_tag':
                if tag_side == 'L':
                    initial['recapture_left_tag_id'] = tag_id
                elif tag_side == 'R':
                    initial['recapture_right_tag_id'] = tag_id
            elif tag_type == 'recapture_pit_tag':
                initial['recapture_pittag_id'] = tag_id

        # If a template is selected, populate the form with the template data
        if selected_template:
            template_data = self.get_template_data(selected_template)
            if template_data:
                initial['place_code'] = template_data.get('place_code')
                # Only set species_code and sex from template if turtle_id is not present
                if not turtle_id:
                    initial['species_code'] = template_data.get('species_code')
                    initial['sex'] = template_data.get('sex')
                    
        if batch_id:
            initial["entry_batch"] = get_object_or_404(TrtEntryBatches, entry_batch_id=batch_id)
            if use_default_enterer and default_enterer:
                initial['entered_by_id'] = default_enterer

        if turtle_id:
            turtle = get_object_or_404(TrtTurtles.objects.prefetch_related('trttags_set', 'trtpittags_set'), pk=turtle_id)
            initial["turtle_id"] = turtle_id
            initial["species_code"] = turtle.species_code
            initial["sex"] = turtle.sex
        
        # editing an existing observation we need to populate the person id fields from the strings stored
        # using the old MS Access system
        
        if entry_id:
            trtdataentry = get_object_or_404(TrtDataEntry, data_entry_id=entry_id)
            measured_by = trtdataentry.measured_by
            recorded_by = trtdataentry.recorded_by
            tagged_by = trtdataentry.tagged_by
            entered_by = trtdataentry.entered_by
            measured_recorded_by = trtdataentry.measured_recorded_by

            if measured_by:
                first_name, last_name = measured_by.split(" ")
                person = TrtPersons.objects.filter(
                    first_name=first_name, surname=last_name
                ).first()
                if person:
                    initial["measured_by_id"] = person.person_id
            if recorded_by:
                first_name, last_name = recorded_by.split(" ")
                person = TrtPersons.objects.filter(
                    first_name=first_name, surname=last_name
                ).first()
                if person:
                    initial["recorded_by_id"] = person.person_id
            if tagged_by:
                first_name, last_name = tagged_by.split(" ")
                person = TrtPersons.objects.filter(
                    first_name=first_name, surname=last_name
                ).first()
                if person:
                    initial["tagged_by_id"] = person.person_id
            if entered_by:
                first_name, last_name = entered_by.split(" ")
                person = TrtPersons.objects.filter(
                    first_name=first_name, surname=last_name
                ).first()
                if person:
                    initial["entered_by_id"] = person.person_id
            if measured_recorded_by:
                first_name, last_name = measured_recorded_by.split(" ")
                person = TrtPersons.objects.filter(
                    first_name=first_name, surname=last_name
                ).first()
                if person:
                    initial["measured_recorded_by_id"] = person.person_id

        return initial

    def form_valid(self, form):
        batch_id = form.cleaned_data["entry_batch"].entry_batch_id
        do_not_process_cookie_name = f"{batch_id}_do_not_process"
        do_not_process_cookie_value = self.request.COOKIES.get(do_not_process_cookie_name)
        if do_not_process_cookie_value == 'true':
            form.instance.do_not_process = True
        form.save()
        success_url = reverse("wamtram2:entry_batch_detail", args=[batch_id])
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'redirect_url': success_url})
        else:
            return redirect(success_url)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors})
        else:
            return super().form_invalid(form)
        
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
        if entry_id:
            context["entry_id"] = entry_id  # Editing existing entry
            context["entry"] = get_object_or_404(TrtDataEntry.objects.select_related('turtle_id'), data_entry_id=entry_id)
        if batch_id:
            context["batch_id"] = batch_id  # Creating new entry in batch
            context["selected_template"] = self.request.COOKIES.get(f'{cookies_key_prefix}_selected_template')
            context["use_default_enterer"] = self.request.COOKIES.get(f'{cookies_key_prefix}_use_default_enterer', False)
            context["default_enterer"] = self.request.COOKIES.get(f'{cookies_key_prefix}_default_enterer', None)
            # Add the tag id and tag type to the context data
            context["cookie_tag_id"] = self.request.COOKIES.get(f'{cookies_key_prefix}_tag_id')
            context["cookie_tag_type"] = self.request.COOKIES.get(f'{cookies_key_prefix}_tag_type')
            context["cookie_tag_side"] = self.request.COOKIES.get(f'{cookies_key_prefix}_tag_side')

        return context


class DeleteBatchView(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):
        # FIXME: Permission check
        if not (
            request.user.groups.filter(name="Tagging Data Entry").exists()
            or request.user.groups.filter(name="Tagging Data Curation").exists()
            or request.user.is_superuser
        ):
            return HttpResponseForbidden(
                "You do not have permission to view this record"
            )
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, batch_id):
        batch = get_object_or_404(TrtEntryBatches, entry_batch_id=batch_id)
        batch.delete()
        return redirect("wamtram2:entry_batches")


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
            request.user.groups.filter(name="Tagging Data Entry").exists()
            or request.user.groups.filter(name="Tagging Data Curation").exists()
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
                    "EXEC dbo.ValidateDataEntryBatch @ENTRY_BATCH_ID = %s",
                    [self.kwargs["batch_id"]],
                )
                messages.add_message(request, messages.INFO, "Validation finished.")
        except DatabaseError as e:
            messages.add_message(
                request, messages.ERROR, "Database error: {}".format(e)
            )
        return redirect("wamtram2:entry_batch_detail", batch_id=self.kwargs["batch_id"])


class DeleteEntryView(DeleteView):
    model = TrtDataEntry
    success_url = reverse_lazy('wamtram2:entry_batches')

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
            request.user.groups.filter(name="Tagging Data Entry").exists()
            or request.user.groups.filter(name="Tagging Data Curation").exists()
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
                    "EXEC dbo.EntryBatchProcess @ENTRY_BATCH_ID = %s;",
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

    # FIXME: Permission check
    def dispatch(self, request, *args, **kwargs):
        if not (
            request.user.groups.filter(name="Tagging Data Entry").exists()
            or request.user.groups.filter(name="Tagging Data Curation").exists()
            or request.user.is_superuser
        ):
            return HttpResponseForbidden(
                "You do not have permission to view this record"
            )
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
            batch_id = kwargs.get("batch_id")
            form = SearchForm(initial={"batch_id": batch_id})
            no_turtle_found = request.COOKIES.get(f'{batch_id}_no_turtle_found') == "true"
            tag_id = request.COOKIES.get(f'{batch_id}_tag_id')
            tag_type = request.COOKIES.get(f'{batch_id}_tag_type')
            tag_side = request.COOKIES.get(f'{batch_id}_tag_side')
            turtle = None

            if tag_id and tag_type and not no_turtle_found:
                tag = TrtTags.objects.select_related('turtle').filter(tag_id=tag_id).first()
                if tag:
                    turtle = tag.turtle
                else:
                    pit_tag = TrtPitTags.objects.select_related('turtle').filter(pittag_id=tag_id).first()
                    if pit_tag:
                        turtle = pit_tag.turtle

            return render(request, "wamtram2/find_turtle.html", {
                "form": form,
                "turtle": turtle,
                "no_turtle_found": no_turtle_found,
                "tag_id": tag_id,
                "tag_type": tag_type,
                "tag_side": tag_side
            })

    def set_cookie(self, response, batch_id, tag_id=None, tag_type=None, tag_side=None, no_turtle_found=False, do_not_process=False):
        if tag_id:
            response.set_cookie(f'{batch_id}_tag_id', tag_id, max_age=3600)
        if tag_type:
            response.set_cookie(f'{batch_id}_tag_type', tag_type, max_age=3600)
        if tag_side:
            response.set_cookie(f'{batch_id}_tag_side', tag_side, max_age=3600)
        response.set_cookie(f'{batch_id}_no_turtle_found', 'true' if no_turtle_found else 'false', max_age=3600)
        response.set_cookie(f'{batch_id}_do_not_process', 'true' if do_not_process else 'false', max_age=3600)
        return response

    def post(self, request, *args, **kwargs):
        batch_id = kwargs.get("batch_id")
        form = SearchForm(request.POST, initial={"batch_id": batch_id})
        no_turtle_found = False
        tag_type = None
        tag_id = None
        tag_side = None
        create_and_review = request.POST.get('create_and_review') == 'true'

        if form.is_valid():
            tag_id = form.cleaned_data["tag_id"]
            turtle = None

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

                if turtle:
                    turtle = TrtTurtles.objects.prefetch_related('trttags_set', 'trtpittags_set').get(pk=turtle.pk)
                    response = redirect(reverse('wamtram2:find_turtle', kwargs={'batch_id': batch_id}))
                    return self.set_cookie(response, batch_id, tag_id, tag_type, tag_side)
                else:
                    no_turtle_found = True
                    response = redirect(reverse('wamtram2:find_turtle', kwargs={'batch_id': batch_id}))
                    return self.set_cookie(response, batch_id, tag_id, tag_type, tag_side, no_turtle_found)
            else:
                tag_type = request.POST.get('tag_type', 'unknown_tag')
                tag_side = request.POST.get('tag_side', None)
                response = redirect(reverse('wamtram2:newtrtdataentry', kwargs={'batch_id': batch_id}))
                return self.set_cookie(response, batch_id, tag_id, tag_type, tag_side, do_not_process=True)
        else:
            response = render(request, "wamtram2/find_turtle.html", {"form": form})

        return self.set_cookie(response, batch_id, tag_id, tag_type, tag_side)


class ObservationDetailView(LoginRequiredMixin, DetailView):
    model = TrtObservations
    template_name = "wamtram2/observation_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = get_object_or_404(TrtObservations, observation_id=self.kwargs.get("pk"))
        context["observation"] = obj
        context["tags"] = obj.trtrecordedtags_set.all()
        context["pittags"] = obj.trtrecordedpittags_set.all()
        context["measurements"] = obj.trtmeasurements_set.all()
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

    def get_context_data(self, **kwargs):
        """
        Retrieves the context data for rendering the template.

        Returns:
            dict: The context data.
        """
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context["page_title"] = f"{settings.SITE_CODE} | WAMTRAM2 | {obj.pk}"
        context["tags"] = obj.trttags_set.all()
        context["pittags"] = obj.trtpittags_set.all()
        context["observations"] = obj.trtobservations_set.all()
        return context


SEX_CHOICES = [
    ("M", "Male"),
    ("F", "Female"),
    ("I", "Indeterminate"),
]
class TemplateManageView(LoginRequiredMixin, FormView):
    """
    View for managing templates.
    Provides functionality to create, update, and delete templates.

    Attributes:
        template_name (str): The name of the template used to render the view.
        form_class (Form): The form class used to create or update templates.
    """
    template_name = 'wamtram2/template_manage.html'
    form_class = TemplateForm

    def get_json_path(self):
        """
        Returns the path to the JSON file storing the templates.

        Returns:
            str: The file path.
        """
        return os.path.join(settings.BASE_DIR, 'wamtram2', 'templates.json')

    def load_templates_from_json(self):
        """
        Loads templates from the JSON file.

        Returns:
            dict: The templates data.
        """
        try:
            with open(self.get_json_path(), 'r') as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return {}

    def save_templates_to_json(self, templates):
        """
        Saves the templates data to the JSON file.

        Args:
            templates (dict): The templates data to save.
        """
        try:
            with open(self.get_json_path(), 'w') as file:
                json.dump(templates, file, indent=4)
        except IOError as e:
            print(f"Error writing to JSON file: {e}")
            raise

    def get_next_template_key(self, templates):
        """
        Generates the next key for a new template.

        Args:
            templates (dict): The current templates data.

        Returns:
            str: The new template key.
        """
        max_key = 0
        template_key_pattern = re.compile(r'^template(\d+)$')
        for key in templates.keys():
            match = template_key_pattern.match(key)
            if match:
                max_key = max(max_key, int(match.group(1)))
        return f"template{max_key + 1}"

    def form_valid(self, form):
        """
        Handles the form submission for creating or updating a template.

        Args:
            form (Form): The submitted form.

        Returns:
            HttpResponse: The HTTP response.
        """
        new_template = form.save(commit=False)
        templates = self.load_templates_from_json()
        new_template_data = {
            'name': new_template.name,
            'location_code': self.request.POST.get('location_code'),
            'place_code': self.request.POST.get('place_code'),
            'species_code': self.request.POST.get('species_code'),
            'sex': self.request.POST.get('sex')
        }

        template_key = self.get_next_template_key(templates)
        templates[template_key] = new_template_data
        try:
            self.save_templates_to_json(templates)
            return redirect('wamtram2:template_manage')
        except Exception as e:
            return render(self.request, 'wamtram2/template_manage.html', {
                'form': form,
                'templates': templates,
                'locations': list(TrtLocations.objects.all()),
                'places': list(TrtPlaces.objects.all()), 
                'species': list(TrtSpecies.objects.all()),
                'sex_choices': SEX_CHOICES,
                'error_message': f"Error saving template: {e}"
            })

    def get_context_data(self, **kwargs):
        """
        Retrieves the context data for rendering the template.

        Returns:
            dict: The context data.
        """
        context = super().get_context_data(**kwargs)
        context['templates'] = self.load_templates_from_json()
        context['locations'] = list(TrtLocations.objects.all())
        context['places'] = list(TrtPlaces.objects.all())
        context['species'] = list(TrtSpecies.objects.all())
        context['sex_choices'] = SEX_CHOICES
        return context

    def delete(self, request, template_key):
        """
        Deletes a template based on the provided key.

        Args:
            request (HttpRequest): The HTTP request.
            template_key (str): The key of the template to delete.

        Returns:
            JsonResponse: The JSON response.
        """
        templates = self.load_templates_from_json()
        if template_key in templates:
            del templates[template_key]
            try:
                self.save_templates_to_json(templates)
                return JsonResponse({'message': 'Template deleted'})
            except Exception as e:
                return JsonResponse({'error': f"Error deleting template: {e}"}, status=500)
        return JsonResponse({'error': 'Template not found'}, status=404)

    def dispatch(self, request, *args, **kwargs):
        """
        Handles different HTTP methods for the view.

        Args:
            request (HttpRequest): The HTTP request.

        Returns:
            HttpResponse: The HTTP response.
        """
        if not request.user.is_superuser:
            return HttpResponseForbidden("You do not have permission to access this page.")
        
        if request.method == 'PUT':
            return self.put(request, *args, **kwargs)
        elif request.method == 'DELETE':
            return self.delete(request, *args, **kwargs)
        elif request.method == 'GET' and 'location_code' in request.GET:
            return self.get_places(request)
        return super().dispatch(request, *args, **kwargs)
    
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
    
    def put(self, request, template_key):
        """
        Updates a template based on the provided key.

        Args:
            request (HttpRequest): The HTTP request.
            template_key (str): The key of the template to update.

        Returns:
            JsonResponse: The JSON response.
        """
        templates = self.load_templates_from_json()
        template_data = templates.get(template_key)
        if not template_data:
            return JsonResponse({'error': 'Template not found'}, status=404)
        
        put_data = QueryDict(request.body)
    
        # Debugging output
        print(put_data)
        
        template_instance = Template(
            name=template_data['name'],
            location_code=template_data['location_code'],
            place_code=template_data['place_code'],
            species_code=template_data['species_code'],
            sex=template_data['sex']
        )
        
        form = TemplateForm(put_data, instance=template_instance)
        if form.is_valid():
            updated_template = form.save(commit=False)
            updated_template_data = {
                'name': updated_template.name,
                'location_code': put_data.get('location_code'),
                'place_code': put_data.get('place_code'),
                'species_code': put_data.get('species_code'),
                'sex': put_data.get('sex')
            }
            templates[template_key] = updated_template_data
            try:
                self.save_templates_to_json(templates)
                return JsonResponse(updated_template_data)
            except Exception as e:
                return JsonResponse({'error': f"Error saving template: {e}"}, status=500)
        return JsonResponse({'errors': form.errors}, status=400)

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

        if not turtle_id or not tag or not side:
            return JsonResponse({'valid': False, 'wrong_side': False, 'message': 'Missing parameters'})

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
            else:
                return JsonResponse({'valid': False, 'wrong_side': False, 'message': 'Tag not found', 'tag_not_found': True})
        except TrtTurtles.DoesNotExist:
            return JsonResponse({'valid': False, 'wrong_side': False, 'message': 'Turtle not found'})

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

        if not turtle_id or not tag:
            return JsonResponse({'valid': False, 'message': 'Missing parameters'})

        try:
            pit_tag = TrtPitTags.objects.filter(pittag_id=tag).select_related('turtle').first()
            if pit_tag:
                if pit_tag.turtle and pit_tag.turtle.turtle_id != int(turtle_id):
                    return JsonResponse({
                        'valid': False,
                        'message': 'PIT tag belongs to another turtle',
                        'other_turtle_id': pit_tag.turtle.turtle_id,
                        'status': pit_tag.pit_tag_status.description
                    })
                else:
                    if pit_tag.pit_tag_status.pit_tag_status != 'ATT':
                        return JsonResponse({
                            'valid': False,
                            'message': f'PIT tag status: {pit_tag.pit_tag_status.description}',
                            'status': pit_tag.pit_tag_status.description
                        })
                    return JsonResponse({'valid': True})
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
    query = request.GET.get('q')
    persons = TrtPersons.objects.filter(
        first_name__icontains=query
    ).values('person_id', 'first_name', 'surname')[:10]
    return JsonResponse(list(persons), safe=False)
