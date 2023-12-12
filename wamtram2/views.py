from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views import generic
from django.conf import settings
from wastd.utils import search_filter, Breadcrumb

from .models import TrtTurtles,TrtTags,TrtPitTags, TrtEntryBatches,TrtDataEntry,TrtPersons
from .forms import TrtDataEntryForm, SearchForm
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from django.views import View
from django.shortcuts import redirect
from django.db import connections
from django.views.generic import ListView
from django.contrib import messages
from django.db import DatabaseError


class EntryBatchesListView(ListView):
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
    template_name = 'trtentrybatches_list.html'  
    context_object_name = 'batches'
    paginate_by = 50

    def get_queryset(self):
        """
        Returns the queryset of objects for the list view.

        Returns:
            QuerySet: The queryset of objects.
        """
        queryset = super().get_queryset()
        return queryset.order_by('-entry_batch_id')
    
    def get_context_data(self, **kwargs):
        """
        Returns the context data for rendering the list view.

        Returns:
            dict: The context data.
        """
        context = super().get_context_data(**kwargs)
        context['persons'] = {person.person_id: person for person in TrtPersons.objects.all()}
        return context

class EntryBatchDetailView(generic.ListView):
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

    """

    model = TrtDataEntry
    template_name = 'wamtram2/trtentrybatch_detail.html'  
    context_object_name = 'batch'
    paginate_by = 50
    from django.utils import timezone


    def get(self, request, *args, **kwargs):
        """
        Handle GET requests.

        This method checks if a 'batch_id' is in 'kwargs'. If not, it creates a new TrtEntryBatches object and sets the 'batch_id' key in 'kwargs' to the newly created batch's entry_batch_id.
        Then, it calls the 'get' method of the parent class using 'super()' and returns the result.

        Args:
            request: The HTTP request object.
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.

        Returns:
            The response returned by the 'get' method of the parent class.
        """
        if 'batch_id' not in kwargs:
            new_batch = TrtEntryBatches.objects.create(pr_date_convention=False) #all dates should be entered as calander dates
            self.kwargs['batch_id'] = new_batch.entry_batch_id
        return super().get(request, *args, **kwargs)
        
    def get_queryset(self):
        """
        Returns the queryset of TrtDataEntry objects filtered by entry_batch_id.

        Returns:
            queryset (QuerySet): The filtered queryset of TrtDataEntry objects.

        """
        queryset = super().get_queryset()
        batch_id = self.kwargs.get('batch_id')
        return queryset.filter(entry_batch_id=batch_id).order_by('-entry_batch_id')

    def get_context_data(self, **kwargs):
        """
        Returns the context data for rendering the template, including the persons dictionary.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            context (dict): The context data for rendering the template.

        """
        context = super().get_context_data(**kwargs)
        context['persons'] = {person.person_id: person for person in TrtPersons.objects.all()}
        context['batch'] = TrtEntryBatches.objects.get(entry_batch_id=self.kwargs.get('batch_id'))  # add the batch to the context
        return context

class TrtDataEntryForm(LoginRequiredMixin, generic.FormView):
    """
    A form view for entering TRT data.

    Inherits from LoginRequiredMixin and generic.FormView.
    """

    template_name = 'wamtram2/trtdataentry_form.html'
    form_class = TrtDataEntryForm

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
        entry_id = self.kwargs.get('entry_id')
        if entry_id:
            entry = get_object_or_404(TrtDataEntry, data_entry_id=entry_id)
            kwargs['instance'] = entry
        
        return kwargs

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.

        Returns:
            dict: The initial data for the form.
        """
        initial = super().get_initial()
        batch_id = self.kwargs.get('batch_id')
        turtle_id = self.kwargs.get('turtle_id')
        if batch_id:
            initial['entry_batch'] = get_object_or_404(TrtEntryBatches, entry_batch_id=batch_id)
        if turtle_id:
            turtle = get_object_or_404(TrtTurtles, turtle_id=turtle_id)
            initial['turtle_id'] = turtle_id 
            initial['recapture_left_tag_id'] = turtle.trttags_set.filter(side='L').all().order_by('tag_order_id')[0] if turtle.trttags_set.filter(side='L').count() > 0 else None
            initial['recapture_left_tag_id_2'] = turtle.trttags_set.filter(side='L').all().order_by('tag_order_id')[1] if turtle.trttags_set.filter(side='L').count() > 1 else None
            initial['recapture_right_tag_id_2'] = turtle.trttags_set.filter(side='L').all().order_by('tag_order_id')[2] if turtle.trttags_set.filter(side='L').count() > 2 else None
            initial['recapture_right_tag_id'] = turtle.trttags_set.filter(side='R').all().order_by('tag_order_id')[0] if turtle.trttags_set.filter(side='R').count() > 0 else None
            initial['recapture_right_tag_id_2'] = turtle.trttags_set.filter(side='R').all().order_by('tag_order_id')[1] if turtle.trttags_set.filter(side='R').count() > 1 else None
            initial['recapture_right_tag_id_3'] = turtle.trttags_set.filter(side='R').all().order_by('tag_order_id')[2] if turtle.trttags_set.filter(side='R').count() > 2 else None
        
            initial['recapture_pit_tag_id'] = turtle.trtpittags_set.all().order_by('tag_order_id')[0] if turtle.trtpittags_set.count() > 0 else None
            initial['recapture_pit_tag_id_2'] = turtle.trtpittags_set.all().order_by('tag_order_id')[1] if turtle.trtpittags_set.count() > 1 else None
        return initial
        
    def form_valid(self, form):
        """
        Saves the form and returns the success URL.

        Args:
            form (Form): The form instance.

        Returns:
            str: The success URL.
        """
        form.save()

        # Get the batch_id 
        batch_id = form.cleaned_data['entry_batch'].entry_batch_id

        # Set the success URL
        self.success_url = reverse('wamtram2:entry_batch_detail', args=[batch_id])
        
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """
        Returns the context data for rendering the template.

        Adds the entry_id and entry objects to the context.

        Returns:
            dict: The context data.
        """
        context = super().get_context_data(**kwargs)
        entry_id = self.kwargs.get('entry_id')
        batch_id = self.kwargs.get('batch_id')
        if entry_id:
            context['entry_id'] = entry_id #editing existing entry
            context['entry'] = get_object_or_404(TrtDataEntry, data_entry_id=entry_id)
        if batch_id:
            context['batch_id'] = batch_id #creating new entry in batch
          
        return context
    
    # def get_success_url(self):
    #     """
    #     Returns the success URL for redirecting after form submission.

    #     Returns:
    #         str: The success URL.
    #     """
    #     batch_id = self.kwargs.get('batch_id')
    #     return reverse('wamtram2:entry_batch_detail', args=[batch_id])
    


class DeleteBatchView(View):
    def get(self, request, batch_id):
        batch = get_object_or_404(TrtEntryBatches, entry_batch_id=batch_id)
        batch.delete()
        return redirect('wamtram2:entry_batches')

class ValidateDataEntryBatchView(View):
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

    def get(self, request, *args, **kwargs):
        try:
            with connections['wamtram2'].cursor() as cursor:
                cursor.execute("EXEC dbo.ValidateDataEntryBatch @ENTRY_BATCH_ID = %s", [self.kwargs['batch_id']])
                messages.add_message(request, messages.INFO, "Validation finished.")
        except DatabaseError as e:
            messages.add_message(request, messages.ERROR, 'Database error: {}'.format(e))
        return redirect('wamtram2:entry_batch_detail', batch_id=self.kwargs['batch_id'])


class ProcessDataEntryBatchView(View):
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
    def get(self, request, *args, **kwargs):
        try:
            with connections['wamtram2'].cursor() as cursor:
                cursor.execute("EXEC dbo.EntryBatchProcess @ENTRY_BATCH_ID = %s;", [self.kwargs['batch_id']])
                messages.add_message(request, messages.INFO, "Processing finished.")
        except DatabaseError as e:
            messages.add_message(request, messages.ERROR, 'Database error: {}'.format(e))
        return redirect('wamtram2:entry_batch_detail', batch_id=self.kwargs['batch_id'])

class FindTurtleView(LoginRequiredMixin,View):
    """
    View class for finding a turtle based on tag and pit tag ID.
    """

    def get(self, request, *args, **kwargs):
        batch_id = kwargs.get('batch_id')
        form = SearchForm(initial={'batch_id': batch_id})
        return render(request, 'wamtram2/find_turtle.html', {'form': form})

    def post(self, request, *args, **kwargs):
        batch_id = kwargs.get('batch_id')
        form = SearchForm(request.POST,initial={'batch_id': batch_id})
        if form.is_valid():
            tag_id = form.cleaned_data['tag_id']
            try:
                tag = TrtTags.objects.filter(tag_id=tag_id).first()
                pit_tag = TrtPitTags.objects.filter(pit_tag_id=tag_id).first()
                if tag:
                    turtle = tag.turtle
                elif pit_tag:
                    turtle = pit_tag.turtle
                else:
                    raise TrtTags.DoesNotExist

                if turtle:
                    tags = TrtTags.objects.filter(turtle=turtle)
                    pittags = TrtPitTags.objects.filter(turtle=turtle)
                    # Pass the turtle variable to the template
                    return render(request, 'wamtram2/find_turtle.html', {'form': form, 'turtle': turtle, 'tags': tags, 'pittags': pittags})
                else:
                    raise TrtTags.DoesNotExist

               
            except TrtTags.DoesNotExist:
                form.add_error(None, 'No Turtle found with the given tag id.')

        return render(request, 'wamtram2/find_turtle.html', {'form': form})







class TurtleListView(LoginRequiredMixin, generic.ListView):
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
        context["object_count"] = self.get_queryset().count()
        context["page_title"] = f"{settings.SITE_CODE} | WAMTRAM2"
        # Pass in any query string
        if "q" in self.request.GET:
            context["query_string"] = self.request.GET["q"]
        context["breadcrumbs"] = (
            Breadcrumb("Home", reverse("home")),
            Breadcrumb("WAMTRAM2", None),
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
            from .admin import TurtleAdmin
            q = search_filter(TurtleAdmin.search_fields, self.request.GET["q"])
            qs = qs.filter(q).distinct()

        return qs.order_by("pk")


class TurtleDetailView(LoginRequiredMixin,generic.DetailView):
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
        return context