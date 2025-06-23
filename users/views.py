from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.db.models import ForeignObject
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import (DetailView, FormView, ListView, RedirectView,
                                  UpdateView)

from observations.models import Area
from wastd.utils import (Breadcrumb, BreadcrumbContextMixin,
                         DetailViewBreadcrumbMixin, ListViewBreadcrumbMixin,
                         ResourceDownloadMixin)

from .filters import UserFilter
from .forms import TransferForm, UserMergeForm
from .models import User
from .utils import change_user_for_area, transfer_user


class UserListView(ListViewBreadcrumbMixin, ResourceDownloadMixin, LoginRequiredMixin, ListView):
    model = User
    paginate_by = 20
    template_name = "default_list.html"
    filter_class = UserFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["collapse_details"] = True
        qs = self.get_queryset()
        context["list_filter"] = UserFilter(self.request.GET, queryset=qs)
        context["object_count"] = qs.count()
        context["page_title"] = f"{settings.SITE_CODE} | Users"
        return context

    def get_queryset(self):
        qs = super().get_queryset().order_by("username")
        return UserFilter(self.request.GET, queryset=qs).qs


class UserDetailView(DetailViewBreadcrumbMixin, LoginRequiredMixin, DetailView):
    """User detail view."""

    model = User

    def get_object(self, queryset=None):
        """Only get the User record for the user making the request."""
        if "pk" not in self.kwargs:
            return self.request.user

        return super().get_object(queryset)

    def get_context_data(self, **kwargs):
        from observations.models import Encounter, Survey

        context = super().get_context_data(**kwargs)
        context["collapse_details"] = False
        context["page_title"] = f"{settings.SITE_CODE} | User profile"
        if "pk" not in self.kwargs:
            context["surveys"] = Survey.objects.filter(
                reporter=self.request.user
            ).prefetch_related("encounter_set", "reporter", "area", "site", "encounter_set__observations")[0:100]
            context["encounters"] = Encounter.objects.filter(
                reporter=self.request.user
            ).prefetch_related("observer", "reporter", "area", "site", "observations")[0:100]
        else:
            context["surveys"] = Survey.objects.filter(
                reporter_id=self.kwargs["pk"]
            ).prefetch_related("encounter_set", "reporter", "area", "site", "encounter_set__observations")[0:100]
            context["encounters"] = Encounter.objects.filter(
                reporter_id=self.kwargs["pk"]
            ).prefetch_related("observer", "reporter", "area", "site", "observations")[0:100]

        return context


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


class UserMergeView(BreadcrumbContextMixin, FormView):
    """Merge any two User profiles.
    """
    template_name = "users/user_form.html"
    form_class = UserMergeForm

    def get_initial(self):
        """Set initial user choices to old or new user if provided.

        This View can be used and populated from three URLs,
        providing no User PK, only the old, or both User PKs.
        """
        initial = super().get_initial()
        if "old_pk" in self.kwargs:
            initial["user_old"] = User.objects.get(pk=self.kwargs["old_pk"])
        if "new_pk" in self.kwargs:
            initial["user_new"] = User.objects.get(pk=self.kwargs["new_pk"])
        return initial

    def get_breadcrumbs(self, request, obj=None, add=False):
        """Create a list of breadcrumbs as named tuples of ('name', 'url')."""
        return (
            Breadcrumb("Home", reverse("home")),
            Breadcrumb("Users", reverse("users:user-list") + "?is_active=true"),
            Breadcrumb("Merge user profiles", None),
        )

    def form_valid(self, form):
        """Transfer user, show result as success message, return to new user's detail.
        """
        old = form.cleaned_data["user_old"]
        new = form.cleaned_data["user_new"]
        msg = transfer_user(old, new)
        messages.success(self.request, msg)
        self.success_url = reverse("users:user-detail", kwargs={"pk": new.pk})
        return super().form_valid(form)


class TransferView(BreadcrumbContextMixin, FormView):
    """Transfer data between two User profiles for a given Area.
    """
    template_name = "users/user_form.html"
    form_class = TransferForm

    def get_initial(self):
        """
        Set initial user choices to old or new user if provided.

        This View can be used and populated from three URLs,
        providing no User PK, only the old, or both User PKs.
        """
        initial = super().get_initial()
        if "old_pk" in self.kwargs:
            initial["user_old"] = User.objects.get(pk=self.kwargs["old_pk"])
        if "new_pk" in self.kwargs:
            initial["user_new"] = User.objects.get(pk=self.kwargs["new_pk"])
        if "area_pk" in self.kwargs:
            initial["area"] = Area.objects.get(pk=self.kwargs["area_pk"])
        return initial

    def get_breadcrumbs(self, request, obj=None, add=False):
        """Create a list of breadcrumbs as named tuples of ('name', 'url')."""
        return (
            Breadcrumb("Home", reverse("home")),
            Breadcrumb("Users", reverse("users:user-list") + "?is_active=true"),
            Breadcrumb("Transfer data", None),
        )

    def form_valid(self, form):
        """Transfer user, show result as success message, return to new user's detail."""
        old = form.cleaned_data["user_old"]
        new = form.cleaned_data["user_new"]
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
