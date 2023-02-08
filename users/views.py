"""User views."""
import logging
from export_download.views import ResourceDownloadMixin

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import (
    DetailView,
    ListView,
    RedirectView,
    UpdateView,
    FormView,
)
from django.http import HttpResponseRedirect, Http404
from .models import User
from .forms import MergeForm, TransferForm
from .filters import UserFilter
from .utils import transfer_user, change_user_for_area
from observations.models import Area

from shared.views import ListViewBreadcrumbMixin, DetailViewBreadcrumbMixin

logger = logging.getLogger(__name__)


class UserListView(ListViewBreadcrumbMixin, ResourceDownloadMixin, LoginRequiredMixin, ListView):
    model = User
    paginate_by = 20
    template_name = "default_list.html"
    filter_class = UserFilter

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        context["collapse_details"] = True
        context["list_filter"] = UserFilter(
            self.request.GET, queryset=self.get_queryset()
        )
        return context

    def get_queryset(self):
        qs = super(UserListView, self).get_queryset().order_by("username")
        return UserFilter(self.request.GET, queryset=qs).qs


class UserDetailView(DetailViewBreadcrumbMixin, LoginRequiredMixin, DetailView):
    """User detail view."""

    model = User
    # These next two lines tell the view to index lookups by username
    # slug_field = "username"
    # slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        from observations.models import Survey, Encounter

        context = super(UserDetailView, self).get_context_data(**kwargs)
        context["collapse_details"] = False
        context["surveys"] = Survey.objects.filter(
            reporter_id=self.kwargs["pk"]
        ).prefetch_related(
            "encounter_set", "reporter", "area", "site", "encounter_set__observations"
        )[
            0:100
        ]
        context["encounters"] = Encounter.objects.filter(
            reporter_id=self.kwargs["pk"]
        ).prefetch_related("observer", "reporter", "area", "site", "observations")[
            0:100
        ]
        return context

    def get_object(self):
        """Get Object by pk."""
        obj = (
            User.objects.filter(pk=self.kwargs.get("pk"))
            .prefetch_related(
                # "reported_surveys",
                # "encounters_observed",
                # "encounters_observed__reporter",
                # "encounters_observed__observer",
                # "encounters_reported",
                # "encounters_reported__reporter",
                # "encounters_reported__observer",
                # "encounters_reported__area",
                # "encounters_reported__site",
            )
            .first()
        )
        if not obj:
            raise Http404  # pragma: no cover
        return obj


class UserRedirectView(LoginRequiredMixin, RedirectView):
    """User redirect view."""

    permanent = False

    def get_redirect_url(self):
        """Get redirect url: user detail."""
        return reverse("users:user-detail", kwargs={"pk": self.request.user.pk})


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """User update view."""

    fields = ["name", "nickname", "aliases", "role", "email", "phone"]

    # we already imported User in the view code above, remember?
    model = User

    # send the user back to their own page after a successful update
    def get_success_url(self):
        """Success url: user detail."""
        return reverse("users:user-detail", kwargs={"pk": self.request.user.pk})

    def get_object(self):
        """Only get the User record for the user making the request."""
        return User.objects.get(pk=self.request.user.pk)


class MergeView(FormView):
    """Merge any two User profiles."""

    template_name = "pages/default_form.html"
    form_class = MergeForm

    def get_initial(self):
        """
        Set initial user choices to old or new user if provided.

        This View can be used and populated from three URLs,
        providing no User PK, only the old, or both User PKs.
        """
        initial = super().get_initial()
        if "old_pk" in self.kwargs:
            initial["old"] = User.objects.get(pk=self.kwargs["old_pk"])
        if "new_pk" in self.kwargs:
            initial["new"] = User.objects.get(pk=self.kwargs["new_pk"])
        return initial

    def form_valid(self, form):
        """Transfer user, show result as success message, return to new user's detail."""
        old = form.cleaned_data["old"]
        new = form.cleaned_data["new"]
        msg = transfer_user(old, new)
        messages.success(self.request, msg)
        self.success_url = reverse("users:user-detail", kwargs={"pk": new.pk})
        return super().form_valid(form)


def merge_users(request, old_pk, new_pk):
    """Merge two users."""
    try:
        old = User.objects.get(pk=old_pk)
    except:
        messages.error(request, "User with PK {0} not found.".format(old_pk))
        return HttpResponseRedirect("/")
    try:
        new = User.objects.get(pk=new_pk)
    except:
        messages.error(request, "User with PK {0} not found.".format(new_pk))
        return HttpResponseRedirect("/")

    msg = transfer_user(old, new)
    messages.success(request, msg)

    return HttpResponseRedirect(reverse("users:user-detail", kwargs={"pk": new.pk}))


class TransferView(FormView):
    """Transfer data between two User profiles for a given Area."""

    template_name = "pages/default_form.html"
    form_class = TransferForm

    def get_initial(self):
        """
        Set initial user choices to old or new user if provided.

        This View can be used and populated from three URLs,
        providing no User PK, only the old, or both User PKs.
        """
        initial = super().get_initial()
        if "old_pk" in self.kwargs:
            initial["old"] = User.objects.get(pk=self.kwargs["old_pk"])
        if "new_pk" in self.kwargs:
            initial["new"] = User.objects.get(pk=self.kwargs["new_pk"])
        if "area_pk" in self.kwargs:
            initial["area"] = Area.objects.get(pk=self.kwargs["area_pk"])
        return initial

    def form_valid(self, form):
        """Transfer user, show result as success message, return to new user's detail."""
        old = form.cleaned_data["old"]
        new = form.cleaned_data["new"]
        area = form.cleaned_data["area"]
        msg = change_user_for_area(old, new, area)
        messages.success(self.request, msg)
        self.success_url = reverse("users:user-detail", kwargs={"pk": new.pk})
        return super().form_valid(form)


def transfer_user_view(request, old_pk, new_pk, area_pk):
    """Transfer data between two User profiles for a given Area."""
    try:
        old = User.objects.get(pk=old_pk)
    except:
        messages.error(request, "User with PK {0} not found.".format(old_pk))
        return HttpResponseRedirect("/")
    try:
        new = User.objects.get(pk=new_pk)
    except:
        messages.error(request, "User with PK {0} not found.".format(new_pk))
        return HttpResponseRedirect("/")
    try:
        area = Area.objects.get(pk=area_pk)
    except:
        messages.error(request, "Area with PK {0} not found.".format(area_pk))
        return HttpResponseRedirect("/")

    msg = change_user_for_area(old, new, area)
    messages.success(request, msg)

    return HttpResponseRedirect(reverse("users:user-detail", kwargs={"pk": new.pk}))
