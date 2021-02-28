# -*- coding: utf-8 -*-
"""User models."""
from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone  # noqa
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework.authtoken.models import Token

import logging

# from shared.models import (
#     # CodeLabelDescriptionMixin,
#     RenderMixin,
#     # LegacySourceMixin,
#     # ObservationAuditMixin,
#     # QualityControlMixin,
#     UrlsMixin
# )

logger = logging.getLogger(__name__)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Create API auth token."""
    if created:
        Token.objects.create(user=instance)
        # try:
            # Token.objects.create(user=instance)
        # except:
            # logger.warning("Failed to create Token for User {0}".format(instance))


class User(AbstractUser):
    """WAStD User.

    Mixins are not imported from shared.models to avoid circular import.
    """

    # First Name and Last Name do not cover name patterns around the globe.
    name = models.CharField(
        _("Name of User"),
        blank=True,
        max_length=255
    )

    nickname = models.CharField(
        _("Preferred name"),
        blank=True,
        max_length=255
    )

    aliases = models.TextField(
        _("Aliases of User"),
        blank=True,
        help_text=_("Any names this user is known as in other "
                    "databases and data collection forms. "
                    "Separate names by comma.")
    )

    role = models.TextField(
        _("Role of User"),
        blank=True, null=True,
        help_text=_("The role of the user.")
    )

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
                    "Spaces are accepted but will be removed on saving."),
    )

    class Meta:
        """Class opts."""

        ordering = ["name", "username"]
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    # -------------------------------------------------------------------------
    # Representation
    def __str__(self):
        """The unicode representation."""
        return "{0} [{1} {2}]".format(self.name, self.pk, self.username)

    def save(self, *args, **kwargs):
        """Guess site."""
        if not self.password:
            self.set_unusable_password()
        if not self.date_joined:
            self.date_joined = timezone.now()
        super(User, self).save(*args, **kwargs)

    # -------------------------------------------------------------------------
    # Templates
    def card_template(self):
        return 'users/cards/user.html'

    # -------------------------------------------------------------------------
    # Properties
    def fullname(self):
        """The full name plus email."""
        return "{0} ({1})".format(self.name or self.username, self.role)

    @property
    def apitoken(self):
        """The API token."""
        return Token.objects.get_or_create(user=self)[0].key

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

    # -------------------------------------------------------------------------
    # URLs
    # Override create and update until we have front end forms
    @classmethod
    def create_url(cls):
        """Create url. Default: app:model-create."""
        return reverse('admin:{0}_{1}_add'.format(
            cls._meta.app_label, cls._meta.model_name))

    @property
    def update_url(self):
        """Update url. Redirects to admin update URL, as we don't have a front end form yet."""
        return self.absolute_admin_url

    @property
    def absolute_admin_url(self):
        """Return the absolute admin change URL.

        Default: admin:app_model_change(**pk)
        """
        return reverse('admin:{0}_{1}_change'.format(
            self._meta.app_label, self._meta.model_name), args=[self.pk])

    def get_absolute_url(self):
        """Detail url, used by Django to link admin to site.

        Default: app:model-detail(**pk).
        """
        return reverse('{0}:{1}-detail'.format(
            self._meta.app_label, self._meta.model_name),
            kwargs={'pk': self.pk})

    @classmethod
    def list_url(cls):
        """List url property. Default: app:model-list."""
        return reverse('{0}:{1}-list'.format(
            cls._meta.app_label, cls._meta.model_name))
