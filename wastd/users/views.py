# -*- coding: utf-8 -*-
"""User views."""
from __future__ import absolute_import, unicode_literals

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from .models import User


class UserDetailView(LoginRequiredMixin, DetailView):
    """User detail view."""

    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = "username"
    slug_url_kwarg = "username"


class UserRedirectView(LoginRequiredMixin, RedirectView):
    """User redirect view."""

    permanent = False

    def get_redirect_url(self):
        """Get redirect url: user detail."""
        return reverse("users:detail",
                       kwargs={"username": self.request.user.username})


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """User update view."""

    fields = ["name", "nickname", "aliases", "role", "email", "phone"]

    # we already imported User in the view code above, remember?
    model = User

    # send the user back to their own page after a successful update
    def get_success_url(self):
        """Success url: uer detail."""
        return reverse("users:detail",
                       kwargs={"username": self.request.user.username})

    def get_object(self):
        """Only get the User record for the user making the request."""
        return User.objects.get(username=self.request.user.username)


class UserListView(LoginRequiredMixin, ListView):
    """User list view."""

    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = "username"
    slug_url_kwarg = "username"


def transfer_user(old, new):
    """Transfer all objects relating to a user to another user.

    Transfers all FK fields to User from old to new:

    * u.reporter.all()
    * u.observer.al()
    * u.morphometric_handler.all()
    * u.morphometric_recorder.all()
    * u.tag_handler.all()
    * u.tag_recorder.all()
    * u.revision_set.all()
    * u.statelog_set.all()
    * u.expedition_team.all()
    * u.surveyend_set.all()
    * u.survey_set.all()
    * u.survey_team.all()
    * u.fileattachment_set.all()
    * u.document_set.all()
    """
    raise NotImplementedError("transfer_user needs to be implemented")
