# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from phonenumber_field.modelfields import PhoneNumberField


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@python_2_unicode_compatible
class User(AbstractUser):

    # First Name and Last Name do not cover name patterns around the globe.
    name = models.CharField(_('Name of User'), blank=True, max_length=255)
    role = models.CharField(_('Role of User'),
                            blank=True, null=True,
                            max_length=1000,
                            help_text=_('The role of the user.'))
    phone = PhoneNumberField(
        verbose_name=_('Phone Number'),
        blank=True, null=True,
        help_text=_('The primary contact number including national prefix, '
                    'e.g. +61 4 12 345 678. '
                    'Spaces are accepted but will be removed on saving.'), )

    def __str__(self):
        """The unicode representation."""
        return self.name or self.username

    def fullname(self):
        """The full name plus email."""
        return "{0} ({1})".format(self.name or self.username, self.role)

    def get_absolute_url(self):
        """The absolute URL."""
        return reverse('users:detail', kwargs={'username': self.username})

    @staticmethod
    def autocomplete_search_fields():
        """Search fields for Grappelli admin skin."""
        return ("id__iexact", "name__icontains", "role__icontains")

    @property
    def apitoken(self):
        """The API token."""
        return Token.objects.get_or_create(user=self)[0].key
