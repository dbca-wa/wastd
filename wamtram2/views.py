from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

# Create your views here.
from .models import TrtTurtles, TrtObservations, TrtDataEntry,TrtTags
from .forms import TrtDataEntryForm
from django_select2.views import AutoResponseView

# class MyAutocompleteView(AutoResponseView):
#      def get_queryset(self):
#          return TrtTags.objects.filter(tag_id__icontains=self.term)
    # def get(self, request, *args, **kwargs):
    #    self.widget = self.get_widget_or_404()
    #    self.term = kwargs.get("term", request.GET.get("term", ""))
    #    self.object_list = self.get_queryset()

    #    context = self.get_context_data()

    #    response_obj = {
    #      "results": [
    #         {"text": self.widget.label_from_instance(obj), "id": obj.tag_id}
    #         for obj in context["object_list"]
    #     ],
    #     "more": context["page_obj"].has_next(),
    #    }
    #    response = JsonResponse(response_obj)
    #    return response


def TrtDataEntryView(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = TrtDataEntryForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect("/thanks/")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = TrtDataEntryForm()

    return render(request, "wamtram2/name.html", {"form": form})

# class TrtDataEntryView(generic.CreateView):
#     model = TrtDataEntry
#     form_class = TrtDataEntryForm
#     success_url = "/"


class TurtleListView(LoginRequiredMixin, generic.ListView):
    model = TrtTurtles
    paginate_by = 50

class TurtleDetailView(generic.DetailView):
    model = TrtTurtles