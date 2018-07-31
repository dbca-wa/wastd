# -*- coding: utf-8 -*-
"""Occurrence models.

These models support opportunistic encounters with threatened and priority
Fauna, Flora and Comunities (defined in taxonomy).

Observer name / address / phone / email is captured through the observer being
a system user.
"""
from __future__ import unicode_literals, absolute_import

# import itertools
import logging
# import os
# import urllib
# import slugify
# from datetime import timedelta
# from dateutil import tz

# from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_delete, pre_save, post_save  # noqa
from django.dispatch import receiver
from django.contrib.gis.db import models as geo_models
# from django.contrib.gis.db.models.query import GeoQuerySet
from django.urls import reverse
# from rest_framework.reverse import reverse as rest_reverse
from django.template import loader
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

# from durationfield.db.models.fields.duration import DurationField
# from django.db.models.fields import DurationField
# from django_fsm import FSMField, transition
# from django_fsm_log.decorators import fsm_log_by
# from django_fsm_log.models import StateLog
from polymorphic.models import PolymorphicModel

# from wastd.users.models import User
from shared.models import (LegacySourceMixin,
                           ObservationAuditMixin,
                           QualityControlMixin)
from taxonomy.models import Taxon, Community

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class Area(PolymorphicModel, LegacySourceMixin, ObservationAuditMixin, QualityControlMixin, geo_models.Model):
    """An Area with a polygonal extent and an additional point representation.

    This model accommodates anything with a spatial extent, providing:

    * Area type (to classify different kinds of areas)
    * Area code to identify multiple measurements of the same Area
    * Polygonal or Point representation of the area
    * Mixins: data QA levels, legacy source tracking

    Some additional fields are populated behind the scenes at each save and
    serve to cache low churn, high use content:

    * label: the cached __str__ representation
    * point: set from geom centroid id empty
    * northern extent: useful to sort Areas by latitude
    * as html: a pre-compiled HTML map popup
    """

    AREA_TYPE_EPHEMERAL_SITE = 0
    AREA_TYPE_PERMANENT_SITE = 1
    AREA_TYPE_CRITICAL_HABITAT = 2
    AREA_TYPE_TEC_BOUNDARY = 10
    AREA_TYPE_TEC_BUFFER = 11
    AREA_TYPE_TEC_SITE = 12
    AREA_TYPE_FLORA_POPULATION = 20
    AREA_TYPE_FLORA_SUBPOPULATION = 21
    AREA_TYPE_FAUNA_SITE = 30
    AREA_TYPE_MPA = 40
    AREA_TYPE_LOCALITY = 41

    AREA_TYPES = (
        (AREA_TYPE_EPHEMERAL_SITE, "Ephemeral Site"),
        (AREA_TYPE_PERMANENT_SITE, "Permanent Site"),
        (AREA_TYPE_CRITICAL_HABITAT, "Critical Habitat"),
        (AREA_TYPE_TEC_BOUNDARY, "TEC Boundary"),
        (AREA_TYPE_TEC_BUFFER, "TEC Buffer"),
        (AREA_TYPE_TEC_SITE, "TEC Site"),
        (AREA_TYPE_FLORA_POPULATION, "Flora Population"),
        (AREA_TYPE_FLORA_SUBPOPULATION, "Flora Subpopulation"),
        (AREA_TYPE_FAUNA_SITE, "Fauna Site"),
        (AREA_TYPE_MPA, "Marine Protected Area"),
        (AREA_TYPE_LOCALITY, "Locality"),
    )

    area_type = models.PositiveIntegerField(
        verbose_name=_("Area type"),
        default=AREA_TYPE_EPHEMERAL_SITE,
        choices=AREA_TYPES,
        help_text=_("The area type."), )

    accuracy = models.FloatField(
        blank=True, null=True,
        verbose_name=_("Accuracy [m]"),
        help_text=_("The measured or estimated accuracy of the location in meters."),
    )

    code = models.CharField(
        max_length=1000,
        verbose_name=_("Code"),
        help_text=_("A URL-safe, short code. Multiple records of the same Area "
                    "will be recognised by the same area type and code."),
    )

    label = models.CharField(
        blank=True, null=True,
        max_length=1000,
        editable=False,
        verbose_name=_("Label"),
        help_text=_("A short but comprehensive label, populated from the model's "
                    "string representation."),
    )

    name = models.CharField(
        blank=True, null=True,
        max_length=1000,
        verbose_name=_("Name"),
        help_text=_("A human-readable name."),
    )

    description = models.TextField(
        blank=True, null=True,
        verbose_name=_("Description"),
        help_text=_("A comprehensive description."),
    )

    point = geo_models.PointField(
        srid=4326,
        blank=True, null=True,
        verbose_name=_("Representative Point"),
        help_text=_("A Point representing the Area."
                    " If empty, the centroid will be calculated from the Area's polygon extent."))

    northern_extent = models.FloatField(
        verbose_name=_("Northernmost latitude"),
        editable=False,
        blank=True, null=True,
        help_text=_("The northernmost latitude serves to sort areas."),)

    as_html = models.TextField(
        verbose_name=_("HTML representation"),
        blank=True, null=True, editable=False,
        help_text=_("The cached HTML representation for display purposes."),)

    geom = geo_models.PolygonField(
        srid=4326,
        blank=True, null=True,
        verbose_name=_("Location"),
        help_text=_("The exact extent of the area as polygon in WGS84, if available."))

    class Meta:
        """Class options."""

        ordering = ["-northern_extent", "name"]
        verbose_name = "Area"
        verbose_name_plural = "Areas"

    def __str__(self):
        """The unicode representation."""
        return "[{0}] ({1}) {2}".format(
            self.get_area_type_display(),
            self.code,
            self.name)

    @property
    def derived_point(self):
        """The point, derived from the polygon."""
        if self.geom:
            return self.geom.centroid
        else:
            return None

    @property
    def derived_northern_extent(self):
        """The northern extent, derived from the polygon."""
        if self.geom:
            return self.geom.extent[3]
        elif self.point:
            return self.point.y
        else:
            return None

    @property
    def absolute_admin_url(self):
        """Return the absolute admin change URL."""
        return reverse('admin:{0}_{1}_change'.format(
            self._meta.app_label, self._meta.model_name), args=[self.pk])

    @property
    def derived_html(self):
        """Generate HTML popup content."""
        template = "occurrence/popup/{0}.html".format(self._meta.model_name)
        try:
            t = loader.get_template(template)
            return mark_safe(t.render({"original": self}))
        except:
            logger.info("[occurrence.models.area] Template missing: {0}".format(template))
            return self.__str__()


@python_2_unicode_compatible
class TaxonArea(Area):
    """An Area related to a Taxon."""

    taxon = models.ForeignKey(Taxon, on_delete=models.CASCADE, related_name="taxon_related_areas")

    def __str__(self):
        """The unicode representation."""
        return "[{0}] ({1}) {2}".format(
            self.get_area_type_display(),
            self.code,
            self.name)


@python_2_unicode_compatible
class CommunityArea(Area):
    """An Area related to a Taxon."""

    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="community_related_areas")

    def __str__(self):
        """The unicode representation."""
        return "[{0}] ({1}) {2}".format(
            self.get_area_type_display(),
            self.code,
            self.name)


@receiver(pre_save, sender=TaxonArea)
@receiver(pre_save, sender=CommunityArea)
def area_caches(sender, instance, *args, **kwargs):
    """Area: Cache expensive lookups."""
    if instance.pk:
        logger.info("[area_caches] Updating cache fields.")
        instance.label = instance.__str__()
        if not instance.point:
            instance.point = instance.derived_point
        instance.northern_extent = instance.derived_northern_extent
        instance.as_html = instance.derived_html
    else:
        logger.info("[area_caches] New Area, re-save to populate caches.")
