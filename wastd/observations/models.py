# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

# from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.gis.db import models as geo_models
from polymorphic.models import PolymorphicModel
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from wastd.users.models import User


# -----------------------------------------------------------------------------#
# Ancillary models
#
@python_2_unicode_compatible
class DistinguishingFeature(models.Model):
    """Distinguising Features.
    FEATURES_CHOICES = (
        ("damage-injury", "Obvious damage or injuries"),
        ("missing-limbs", "Missing limbs"),
        ("barnacles", "Barnacles"),
        ("algal-epiphytes-carapace", "Algal growth on carapace"),
        ("tagging-scars", "Tagging scars"),
        ("propeller-damage", "Propeller strike damage"),
        ("entanglement", "Entanglement in anthropogenic debris"),
        ("see-photo", "See attached photos"),)
    """
    name = models.CharField(
        max_length=300,
        verbose_name=_("Name"),
        help_text=_("A short name for the distinguising feature."),)

    description = models.TextField(
        verbose_name=_("Description"),
        blank=True, null=True,
        help_text=_("A description of the feature."),)

    class Meta:
        """Class options."""

        verbose_name = "Distinguishing Feature"
        verbose_name_plural = "Distinguishing Features"

    def __str__(self):
        """The unicode representation."""
        return self.name


# -----------------------------------------------------------------------------#
# Observation models
#
@python_2_unicode_compatible
class Observation(PolymorphicModel, geo_models.Model):
    """The base Observation class knows when, where, who.

    When: Datetime of observation, stored in UTC, entered and displayed in local
    timezome.
    Where: Point in WGS84.
    Who: The observer has to be a registered system user.
    """

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
        help_text=_("The observer has to be a registered system user"))

    class Meta:
        """Class options."""

        ordering = ["when", "where"]
        verbose_name = "Observation"
        verbose_name_plural = "Observations"
        get_latest_by = "when"

    def __str__(self):
        """The unicode representation."""
        return "Obs {0} on {1} by {2}".format(self.pk, self.when, self.who)

    @property
    def wkt(self):
        """Return the point coordinates as Well Known Text (WKT)."""
        return self.where.wkt


@python_2_unicode_compatible
class StrandingObservation(Observation):
    """Opportunistic sighting of stranded/encountered dead or injured wildlife.

    Species use a local name list, but should lookup a webservice.
    This Observation is generic for all species. Other Models can FK this Model
    to add species-specific measurements.

    Observer name / address / phone / email is captured with observer as system
    user.

    The combination of species and health determines subsequent measurements
    and actions:

    * [turtle, dugong, cetacean] damage observation
    * [turtle, dugong, cetacean] distinguished features
    * [taxon] morphometrics
    * tag observation
    """

    HEALTH_CHOICES = (
        ('alive', 'Alive, healthy'),
        ('alive-injured', 'Alive, injured'),
        ('alive-then-died', 'Initally alive, but died'),
        ('dead-edible', 'Dead, carcass edible'),
        ('dead-organs-intact', 'Dead, decomposed but organs intact'),
        ('dead-advanced', 'Dead, advanced decomposition'),
        ('dead-mummified', 'Dead, skin holding bones'),
        ('dead-disarticulated', 'Dead, no soft tissue remaining'),
        ('other', 'Other'),)

    SPECIES_CHOICES = (
        ('Natator depressus', 'Flatback turtle (Natator depressus)'),
        ('Chelonia mydas', 'Green turtle (Chelonia mydas)'),
        ('Eretmochelys imbricata', 'Hawksbill turtle (Eretmochelys imbricata)'),
        ('Caretta caretta', 'Loggerhead turtle (Caretta caretta)'),
        ('Lepidochelys olivacea', 'Olive Ridley turtle (Lepidochelys olivacea)'),
        ('Dermochelys coriacea', 'Leatherback turtle (Dermochelys coriacea)'),
        ('unidentified', 'Unidentified'),)

    species = models.CharField(
        max_length=300,
        verbose_name=_("Species"),
        choices=SPECIES_CHOICES,
        help_text=_("The species of the animal."),)

    health = models.CharField(
        max_length=300,
        verbose_name=_("Health status"),
        choices=HEALTH_CHOICES,
        help_text=_("On a scale from the Fresh Prince of Bel Air to 80s Hair "
                    "Metal: how dead and decomposed is the animal?"),)

    behaviour = models.TextField(
        verbose_name=_("Behaviour"),
        blank=True, null=True,
        help_text=_("Notes on condition or behaviour if alive."),)

    features = models.ManyToManyField(
        DistinguishingFeature,
        blank=True,
        help_text=_("Select any observed distinguishing features."),)

    management_actions = models.TextField(
        verbose_name=_("Management Actions"),
        blank=True, null=True,
        help_text=_("Managment actions taken. Keep updating as appropriate."),)

    comments = models.TextField(
        verbose_name=_("Comments"),
        blank=True, null=True,
        help_text=_("Any other comments or notes."),)

    def __str__(self):
        """The unicode representation."""
        return "StrandingObs {0} on {1} by {2} of {3}".format(
            self.pk, self.when, self.who, self.get_species_display())


@python_2_unicode_compatible
class TurtleStrandingObservation(StrandingObservation):
    """Opportunistic sighting of stranded/encountered dead or injured turtle.

    Default stranding measurements, plus:

    * Sex
    * Maturity
    * Morphometrics
    """

    ACCURACY_CHOICES = (
        ("unknown", "Unknown"),
        ("estimated", "Estimated"),
        ("measured", "Measured"),)

    SEX_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
        ("unknown", "Unknown"),)

    MATURITY_CHOICES = (
        ("hatchling", "Hatchling"),
        ("juvenile", "Juvenile"),
        ("adult", "Adult"),
        ("unknown", "Unknown"),)

    sex = models.CharField(
        max_length=300,
        default="unknown",
        verbose_name=_("Sex"),
        choices=SEX_CHOICES,
        help_text=_("The animal's sex."),)

    maturity = models.CharField(
        max_length=300,
        default="unknown",
        verbose_name=_("Maturity"),
        choices=MATURITY_CHOICES,
        help_text=_("The animal's maturity."),)

    curved_carapace_length_mm = models.PositiveIntegerField(
        verbose_name=_("Curved Carapace Length (mm)"),
        blank=True, null=True,
        help_text=_(""),)

    curved_carapace_length_accuracy = models.CharField(
        max_length=300,
        default="unknown",
        verbose_name=_("Curved Carapace Length Accuracy"),
        choices=ACCURACY_CHOICES,
        help_text=_("The measurement type as indication of accuracy."),)

    curved_carapace_width_mm = models.PositiveIntegerField(
        verbose_name=_("Curved Carapace Width (mm)"),
        blank=True, null=True,
        help_text=_(""),)

    curved_carapace_width_accuracy = models.CharField(
        max_length=300,
        default="unknown",
        verbose_name=_("Curved Carapace Width Accuracy"),
        choices=ACCURACY_CHOICES,
        help_text=_("The measurement type as indication of accuracy."),)

    tail_length_mm = models.PositiveIntegerField(
        verbose_name=_("Tail Length (mm)"),
        blank=True, null=True,
        help_text=_("Measured from carapace"),)

    tail_length_accuracy = models.CharField(
        max_length=300,
        default="unknown",
        verbose_name=_("Tail Length Accuracy"),
        choices=ACCURACY_CHOICES,
        help_text=_("The measurement type as indication of accuracy."),)

    maximum_head_width_mm = models.PositiveIntegerField(
        verbose_name=_("Maximum Head Width (mm)"),
        blank=True, null=True,
        help_text=_(""),)

    maximum_head_width_accuracy = models.CharField(
        max_length=300,
        default="unknown",
        verbose_name=_("Maximum Head Width Accuracy"),
        choices=ACCURACY_CHOICES,
        help_text=_("The measurement type as indication of accuracy."),)

    def __str__(self):
        """The unicode representation."""
        return "TurtleStrandingObs {0} on {1} by {2} of {3}".format(
            self.pk, self.when, self.who, self.get_species_display())


# -----------------------------------------------------------------------------#
# Child models of Observations
#
@python_2_unicode_compatible
class MediaAttachment(models.Model):
    """A media attachment to an Observation."""

    MEDIA_TYPE_CHOICES = (
        ('data_sheet', 'Original data sheet'),
        ('photograph', 'Photograph'),
        ('other', 'Other'),)

    observation = models.ForeignKey(
        Observation,
        verbose_name=_("Observation"),
        help_text=("Which Observation does this attachment relate to?"),)

    media_type = models.CharField(
        max_length=300,
        verbose_name=_("Attachment type"),
        blank=True, null=True,
        choices=MEDIA_TYPE_CHOICES,
        help_text=_("What is the attached file about?"),)

    title = models.CharField(
        max_length=300,
        verbose_name=_("Attachment name"),
        blank=True, null=True,
        help_text=_("Give the attachment a representative name"),)

    attachment = models.FileField(
        upload_to='media/%Y/%m/%d/',
        verbose_name=_("File attachment"),
        help_text=_("Upload the file"),)

    def __str__(self):
        """The unicode representation."""
        return self.title
