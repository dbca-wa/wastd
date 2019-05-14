# -*- coding: utf-8 -*-
"""User models."""
from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Create API auth token."""
    if created:
        Token.objects.create(user=instance)


@python_2_unicode_compatible
class User(AbstractUser):
    """WAStD User."""

    # First Name and Last Name do not cover name patterns around the globe.
    name = models.CharField(_("Name of User"), blank=True, max_length=255)

    nickname = models.CharField(_("Preferred name"), blank=True, max_length=255)

    aliases = models.TextField(
        _("Aliases of User"),
        blank=True,
        help_text=_("Any names this user is known as in other "
                    "databases and data collection forms. "
                    "Separate names by comma.")
    )

    role = models.CharField(_("Role of User"),
                            blank=True, null=True,
                            max_length=1000,
                            help_text=_("The role of the user."))
    affiliation = models.TextField(
        _("Affiliation"),
        blank=True,
        help_text=_("The organisational affiliation of the user.")
    )
    phone = PhoneNumberField(
        verbose_name=_("Phone Number"),
        blank=True, null=True,
        help_text=_("The primary contact number including national prefix, "
                    "e.g. +61 412 345 678. "
                    "Spaces are accepted but will be removed on saving."), )

    class Meta:
        """Class opts."""

        ordering = ["name", "username"]

    def __str__(self):
        """The unicode representation."""
        return self.name or self.username

    def fullname(self):
        """The full name plus email."""
        return "{0} ({1})".format(self.name or self.username, self.role)

    def get_absolute_url(self):
        """The absolute URL."""
        return reverse("users:detail", kwargs={"username": self.username})

    @staticmethod
    def autocomplete_search_fields():
        """Search fields for Grappelli admin skin."""
        return (
            "id__iexact",
            "name__icontains",
            "role__icontains",
            "aliases__icontains",
            "affiliation__icontains"
        )

    @property
    def apitoken(self):
        """The API token."""
        return Token.objects.get_or_create(user=self)[0].key
