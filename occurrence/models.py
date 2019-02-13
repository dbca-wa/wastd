# -*- coding: utf-8 -*-
"""Occurrence models.

These models support opportunistic encounters with threatened and priority
Fauna, Flora and Comunities (defined in taxonomy).

Observer name / address / phone / email is captured through the observer being
a system user.
"""
from __future__ import absolute_import, unicode_literals

# import itertools
import logging

from django.contrib.gis.db import models as geo_models
# from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save, pre_delete, pre_save  # noqa
from django.dispatch import receiver
# from rest_framework.reverse import reverse as rest_reverse
from django.template import loader
# from django.contrib.gis.db.models.query import GeoQuerySet
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
# from durationfield.db.models.fields.duration import DurationField
# from django.db.models.fields import DurationField
# from django_fsm import FSMField, transition
# from django_fsm_log.decorators import fsm_log_by
# from django_fsm_log.models import StateLog
from polymorphic.models import PolymorphicModel
# from wastd.users.models import User
from shared.models import LegacySourceMixin, ObservationAuditMixin, QualityControlMixin
from taxonomy.models import Community, Taxon

# import os
# import urllib
# import slugify
# from datetime import timedelta
# from dateutil import tz


logger = logging.getLogger(__name__)


class AreaEncounter(PolymorphicModel,
                    LegacySourceMixin,
                    ObservationAuditMixin,
                    QualityControlMixin,
                    geo_models.Model):
    """An Encounter with an Area.

    The Area is represented spatially throuh a polygonal extent
    and an additional point.

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
    AREA_TYPE_PARTIAL_SURVEY = 3
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
        (AREA_TYPE_PARTIAL_SURVEY, "Partial survey"),
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

    COMMUNITY_AREA_TYPES = (
        (AREA_TYPE_PARTIAL_SURVEY, "Partial survey"),
        (AREA_TYPE_TEC_BOUNDARY, "TEC Boundary"),
        (AREA_TYPE_TEC_BUFFER, "TEC Buffer"),
        (AREA_TYPE_TEC_SITE, "TEC Site"),
    )

    TAXON_AREA_TYPES = (
        (AREA_TYPE_EPHEMERAL_SITE, "Ephemeral Site"),
        (AREA_TYPE_PERMANENT_SITE, "Permanent Site"),
        (AREA_TYPE_PARTIAL_SURVEY, "Partial survey"),
        (AREA_TYPE_FLORA_POPULATION, "Flora Population"),
        (AREA_TYPE_FLORA_SUBPOPULATION, "Flora Subpopulation"),
    )

    # Naming -----------------------------------------------------------------#
    code = models.SlugField(
        max_length=1000,
        blank=True, null=True,
        verbose_name=_("Area code"),
        help_text=_("A URL-safe, short code for the area. "
                    "Multiple records of the same Area "
                    "will be recognised by the same area type and code."),
    )

    label = models.CharField(
        blank=True, null=True,
        max_length=1000,
        editable=False,
        verbose_name=_("Label"),
        help_text=_("A short but comprehensive label for the encounter, "
                    "populated from the model's string representation."),
    )

    name = models.CharField(
        blank=True, null=True,
        max_length=1000,
        verbose_name=_("Area name"),
        help_text=_("A human-readable name for the observed area."),
    )

    description = models.TextField(
        blank=True, null=True,
        verbose_name=_("Description"),
        help_text=_("A comprehensive description."),
    )

    # Time: ObservationAuditMixin provides date and observer -----------------#
    #
    # Geolocation ------------------------------------------------------------#
    area_type = models.PositiveIntegerField(
        verbose_name=_("Area type"),
        default=AREA_TYPE_EPHEMERAL_SITE,
        choices=AREA_TYPES,
        help_text=_(
            "What type describes the area occupied by the encounter "
            "most accurately? The area can be an opportunistic, once-off chance "
            "encounter (point), a fixed survey site (polygon), a partial or a "
            "complete survey of an area occupied by the encountered subject (polygon)."),
    )

    accuracy = models.FloatField(
        blank=True, null=True,
        verbose_name=_("Accuracy [m]"),
        help_text=_("The measured or estimated accuracy of the location in meters."),
    )

    point = geo_models.PointField(
        srid=4326,
        blank=True, null=True,
        verbose_name=_("Representative Point"),
        help_text=_(
            "A point representing the area occupied by the encountered subject."
            " If empty, the point will be calculated as the centroid of the polygon extent."))

    northern_extent = models.FloatField(
        verbose_name=_("Northernmost latitude"),
        editable=False,
        blank=True, null=True,
        help_text=_("The northernmost latitude is derived from location "
                    "polygon or point and serves to sort areas."),)

    geom = geo_models.PolygonField(
        srid=4326,
        blank=True, null=True,
        verbose_name=_("Location"),
        help_text=_("The exact extent of the area occupied by the encountered "
                    "subject as polygon in WGS84, if available."))

    # Cached fields ----------------------------------------------------------#
    as_html = models.TextField(
        verbose_name=_("HTML representation"),
        blank=True, null=True, editable=False,
        help_text=_("The cached HTML representation for display purposes."),)

    class Meta:
        """Class options."""

        ordering = ["-northern_extent", "name"]
        verbose_name = "Area Encounter"
        verbose_name_plural = "Area Encounters"

    def __str__(self):
        """The unicode representation."""
        return "Encounter at [{0}] ({1}) {2} on {3} by {4}".format(
            self.get_area_type_display(),
            self.code,
            self.name,
            self.encountered_on,
            self.encountered_by)

    # -------------------------------------------------------------------------
    # URLs
    def get_absolute_url(self):
        """Detail url."""
        return "/"

    @property
    def detail_url(self):
        """Hook for detail url."""
        return self.get_absolute_url()

    @property
    def update_url(self):
        """Hook for update url."""
        return "/"

    @property
    def absolute_admin_url(self):
        """Return the absolute admin change URL."""
        return reverse('admin:{0}_{1}_change'.format(
            self._meta.app_label, self._meta.model_name), args=[self.pk])

    # -------------------------------------------------------------------------
    # Derived properties
    @property
    def derived_point(self):
        """The point, derived from the polygon."""
        if self.geom:
            return self.geom.centroid
        else:
            return None

    @property
    def derived_northern_extent(self):
        """The northernmost extent of the polygon, or the latitude of the point."""
        if self.geom:
            return self.geom.extent[3]
        elif self.point:
            return self.point.y
        else:
            return None

    @property
    def derived_html(self):
        """Generate HTML popup content."""
        template = "occurrence/popup/{0}.html".format(self._meta.model_name)
        try:
            t = loader.get_template(template)
            return mark_safe(t.render({"original": self}))
        except:
            logger.info(
                "[occurrence.models.{0}] Template missing: {1}".format(
                    self._meta.model_name, template))
            return self.__str__()

    # -------------------------------------------------------------------------
    # Functions
    def get_nearby_encounters(self, dist_dd=0.005):
        """Get encounters within dist_dd (default 0.005 degrees, ca 500m).

        Arguments:

        dist_dd <float> The search radius in decimal degrees. Default: 0.005 (ca 500 m).

        Returns:
        A queryset of nearby AreaEncounters.
        """
        return AreaEncounter.objects.filter(point__distance_lte=(self.point, dist_dd))


@python_2_unicode_compatible
class TaxonAreaEncounter(AreaEncounter):
    """An Encounter in time and space with a Taxon."""

    taxon = models.ForeignKey(Taxon, on_delete=models.CASCADE, related_name="taxon_occurrences")

    class Meta:
        """Class options."""

        verbose_name = "Taxon Encounter"
        verbose_name_plural = "Taxon Encounters"

    def __str__(self):
        """The unicode representation."""
        return "Encounter of {5} at [{0}] ({1}) {2} on {3} by {4}".format(
            self.get_area_type_display(),
            self.code,
            self.name,
            self.encountered_on,
            self.encountered_by,
            self.taxon)

    # -------------------------------------------------------------------------
    # URLs
    def get_absolute_url(self):
        """Detail url."""
        return reverse(
            'taxon-occurrence-detail',
            kwargs={'name_id': self.taxon.name_id, 'occ_pk': self.pk})

    @property
    def detail_url(self):
        """Hook for detail url."""
        return self.get_absolute_url()

    @property
    def update_url(self):
        """Hook for update url."""
        return reverse(
            'taxon-occurrence-update',
            kwargs={'name_id': self.taxon.name_id, 'occ_pk': self.pk})

    # -------------------------------------------------------------------------
    # Derived properties

    # -------------------------------------------------------------------------
    # Functions
    def nearby_same(self, dist_dd=0.005):
        """Return encounters with same taxon within search radius (dist_dd).

        Arguments:

        dist_dd <float> The search radius in decimal degrees. Default: 0.005 (ca 500 m).

        Returns:
        A queryset of nearby TaxonAreaEncounters.
        """
        return TaxonAreaEncounter.objects.filter(
            taxon=self.taxon,
            point__distance_lte=(self.point, dist_dd)
        )


@python_2_unicode_compatible
class CommunityAreaEncounter(AreaEncounter):
    """An Encounter in time and space with a community."""

    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="community_occurrences")

    class Meta:
        """Class options."""

        verbose_name = "Community Encounter"
        verbose_name_plural = "Community Encounters"

    def __str__(self):
        """The unicode representation."""
        return "Encounter of {5} at [{0}] ({1}) {2} on {3} by {4}".format(
            self.get_area_type_display(),
            self.code,
            self.name,
            self.encountered_on,
            self.encountered_by,
            self.community)

    # -------------------------------------------------------------------------
    # URLs
    def get_absolute_url(self):
        """Detail url."""
        return reverse(
            'community-occurrence-detail',
            kwargs={'pk': self.community.pk, 'occ_pk': self.pk})

    @property
    def detail_url(self):
        """Hook for detail url."""
        return self.get_absolute_url()

    @property
    def update_url(self):
        """Hook for update url."""
        return reverse('community-occurrence-update',
                       kwargs={'pk': self.community.pk, 'occ_pk': self.pk})

    # -------------------------------------------------------------------------
    # Derived properties

    # -------------------------------------------------------------------------
    # Functions
    def nearby_same(self, dist_dd=0.005):
        """Return encounters with same community within search radius (dist_dd).

        Arguments:

        dist_dd <float> The search radius in decimal degrees. Default: 0.005 (ca 500 m).

        Returns:
        A queryset of nearby CommunityAreaEncounters.
        """
        return CommunityAreaEncounter.objects.filter(
            community=self.community,
            point__distance_lte=(self.point, dist_dd)
        )


@receiver(pre_save, sender=TaxonAreaEncounter)
@receiver(pre_save, sender=CommunityAreaEncounter)
def area_caches(sender, instance, *args, **kwargs):
    """AreaEncounter: Cache expensive lookups."""
    if instance.pk:
        logger.info("[area_caches] Updating cache fields.")
        instance.label = instance.__str__()
        if not instance.point:
            instance.point = instance.derived_point
        instance.northern_extent = instance.derived_northern_extent
        instance.as_html = instance.derived_html
    else:
        logger.info("[area_caches] New Area, re-save to populate caches.")
    if instance.code:
        instance.code = slugify(instance.code)


# Observation models ---------------------------------------------------------#
@python_2_unicode_compatible
class ObservationGroup(QualityControlMixin, PolymorphicModel, models.Model):
    """The Observation base class for area encounter observations.

    Everything happens somewhere, at a time, to someone, and someone records it.
    Therefore, an ObservationGroup must happen during an Encounter.

    The ObservationGroup shares with Encounter:

    * location,
    * datetime,
    * reporter,
    * subject (species or community).

    The ObservationGroup has its own:

    * QA trust levels.

    Having separate QA trust levels allows to synthesize the "best available information"
    about a Species / Community occurrence, hand-selected by custodians from different
    TAE/CAE.
    """

    encounter = models.ForeignKey(
        AreaEncounter,
        on_delete=models.CASCADE,
        verbose_name=_("Area Encounter"),
        related_name="observations",
        help_text=("The Area Encounter during which the observation group was observed."),)

    class Meta:
        """Class options."""

        verbose_name = "Observation Group"

    def __str__(self):
        """The unicode representation."""
        return u"Obs {0} for {1}".format(self.pk, self.encounter.__str__())

    # -------------------------------------------------------------------------
    # URLs
    def get_absolute_url(self):
        """Detail url."""
        return self.encounter.get_absolute_url()

    @property
    def detail_url(self):
        """Hook for detail url."""
        return self.get_absolute_url()

    @property
    def update_url(self):
        """Hook for update url."""
        return "/"

    @property
    def absolute_admin_url(self):
        """Return the absolute admin change URL."""
        return reverse(
            'admin:{0}_{1}_change'.format(
                self._meta.app_label, self._meta.model_name), args=[self.pk])

    # -------------------------------------------------------------------------
    # Derived properties
    # Location and date
    @property
    def point(self):
        """Return the encounter point location."""
        return self.encounter.point

    @property
    def latitude(self):
        """The encounter's latitude."""
        return self.encounter.point.y or ''

    @property
    def longitude(self):
        """The encounter's longitude."""
        return self.encounter.point.x or ''

    def datetime(self):
        """The encounter's timestamp."""
        return self.encounter.observed_on or ''

    # Display and cached properties
    @property
    def observation_name(self):
        """The concrete model name.

        This method will inherit down the polymorphic chain, and always return
        the actual child model's name.

        `observation_name` can be included as field e.g. in API serializers,
        so e.g. a writeable serializer would know which child model to `create`
        or `update`.
        """
        return self.polymorphic_ctype.model

    @property
    def model_name_verbose(self):
        """Return the model's verbose name."""
        return self._meta.verbose_name

    @property
    def as_html(self):
        """Return as rendered HTML popup."""
        t = loader.get_template("occurrence/popup/{0}.html".format(self.observation_name))
        # c = Context({"original": self})
        return mark_safe(t.render({"original": self}))

    @property
    def as_card(self):
        """Return as rendered HTML card."""
        t = loader.get_template("occurrence/cards/{0}.html".format(self.observation_name))
        return mark_safe(t.render({"original": self}))

    @property
    def as_latex(self):
        """Return as raw Latex fragment."""
        t = loader.get_template("occurrence/latex/{0}.tex".format(self.observation_name))
        # c = Context({"original": self})
        return mark_safe(t.render({"original": self}))

    # -------------------------------------------------------------------------
    # Functions

    # FAUNA ENC
    # Survey
    # Threats
    # Habitat and habitat conditions
    # Fire history
    # Vegetation class
    # Associated species
    # mgmt actions required
    # comments
    # DRF permit no
    # TaxonSpecimenEncounter
    # TaxonSampleEncounter

    # FLORA ENC
    # Location Description
    # Survey: often no survey as most fauna enc are opportunistic
    # Plant count
    # Threats
    # Habitat and habitat conditions
    # Fire response
    # Fire history
    # Vegetation class
    # Associated species: mostly empty, flora
    # mgmt actions required
    # comments
    # DRF permit no
    # Plant count
    # TaxonSpecimenEncounter
    # TaxonSampleEncounter
    # VoucherSpecimen
    # File attachments

    # COM ENC
    # Survey: often no survey as most fauna enc are opportunistic
    # Threats
    # Habitat and habitat conditions
    # Fire history
    # Vegetation class

    # Associated species: mostly empty, flora
    # mgmt actions required
    # comments
    # DRF permit no
    # TaxonSpecimenEncounter
    # TaxonSampleEncounter


class AssociatedSpeciesObservation(ObservationGroup):
    """Observation of an associated species."""

    taxon = models.ForeignKey(
        Taxon,
        on_delete=models.CASCADE,
        related_name="associated_species")

    class Meta:
        """Class options."""

        verbose_name = "Associated Species"
        verbose_name_plural = "Associated Species"

    def __str__(self):
        """The unicode representation."""
        return u"Encounter {0} Obs {1}: Associated species {2}".format(
            self.encounter.pk, self.pk, self.taxon)


class FireHistoryObservation(ObservationGroup):
    """Evidence of past fire."""

    HMLN_DEFAULT = "NA"
    HMLN_CHOICES = (
        (HMLN_DEFAULT, "NA"),
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    )

    last_fire_date = models.DateField(
        verbose_name=_("Date of last fire"),
        blank=True, null=True,
        help_text=_("The estimated date of the last fire, if evident."))

    fire_intensity = models.CharField(
        verbose_name=_("Fire intensity"),
        max_length=100,
        default=HMLN_DEFAULT,
        choices=HMLN_CHOICES,
        help_text=_(
            "Estimated intensity of last fire on a scale from High to Low, "
            "or NA if no evidence of past fires."
        ),
    )

    class Meta:
        """Class options."""

        verbose_name = "Fire History"
        verbose_name_plural = "Fire Histories"

    def __str__(self):
        """The unicode representation."""
        return u"Encounter {0} Obs {1}: Fire on {2}, intensity {3}".format(
            self.encounter.pk,
            self.pk,
            self.last_fire_date.strftime("%d/%m/%Y"),
            self.get_fire_intensity_display())
