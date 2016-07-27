# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.gis.db import models as geo_models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from wastd.users.models import User


@python_2_unicode_compatible
class Observation(geo_models.Model):
    """The base Observation class."""

    when = models.DateTimeField(
        verbose_name=_("Observed on"),
        blank=True, null=True,
        help_text=_("The observation datetime"))
    where = geo_models.PointField(
        srid=4326,
        verbose_name=_("Observed at"),
        blank=True, null=True,
        help_text=_("The observation location as point in WGS84"))
    who = models.ForeignKey(
        User,
        verbose_name=_("Observed by"),
        blank=True, null=True,
        help_text=_("The observer as system user"))

    def __str__(self):
        return "Obs {0} on {1} by {2}".format(self.pk, self.when, self.who)
