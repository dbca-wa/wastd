# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

# from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.gis.db import models as geo_models
from polymorphic.models import PolymorphicModel
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from wastd.users.models import User


# Ancillary models -----------------------------------------------------------#
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


# Observation models ---------------------------------------------------------#
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
        help_text=_("The observation datetime, shown here as local time, "
                    "stored as UTC."))
    where = geo_models.PointField(
        srid=4326,
        verbose_name=_("Observed at"),
        help_text=_("The observation location as point in WGS84"))
    who = models.ForeignKey(
        User,
        verbose_name=_("Observed by"),
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

    @property
    def tag_html(self):
        """An HTML string of associated TagObservations"""
        return "".join(["<p>{0}</p>".format(t.__str__())
                        for t in self.tagobservation_set.all()])

    @property
    def popupContent(self):
        """HTML for a map popup."""
        return mark_safe(
            "<h3>Observation</h3>{0}<p>{1} reported by {2}<p>".format(
                self.tag_html, self.when.strftime('%d/%m/%Y %H:%M:%S'), self.who))


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
        ('alive', 'Alive (healthy)'),
        ('alive-injured', 'Alive (injured)'),
        ('alive-then-died', 'Initally alive (but died)'),
        ('dead-edible', 'Dead (carcass edible)'),
        ('dead-organs-intact', 'Dead (decomposed but organs intact)'),
        ('dead-advanced', 'Dead (advanced decomposition)'),
        ('dead-mummified', 'Mummified (dead, skin holding bones)'),
        ('dead-disarticulated', 'Disarticulated (dead, no soft tissue remaining)'),
        ('other', 'Other'),)

    SPECIES_CHOICES = (
        ('Natator depressus', 'Flatback turtle (Natator depressus)'),
        ('Chelonia mydas', 'Green turtle (Chelonia mydas)'),
        ('Eretmochelys imbricata', 'Hawksbill turtle (Eretmochelys imbricata)'),
        ('Caretta caretta', 'Loggerhead turtle (Caretta caretta)'),
        ('Lepidochelys olivacea', 'Olive Ridley turtle (Lepidochelys olivacea)'),
        ('Dermochelys coriacea', 'Leatherback turtle (Dermochelys coriacea)'),
        ('unidentified', 'Unidentified Species'),)

    species = models.CharField(
        max_length=300,
        verbose_name=_("Species"),
        choices=SPECIES_CHOICES,
        help_text=_("The species of the animal."),)

    health = models.CharField(
        max_length=300,
        verbose_name=_("Health status"),
        choices=HEALTH_CHOICES,
        default="alive",
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

    @property
    def popupContent(self):
        """HTML for a map popup."""
        return mark_safe(
            "<h3>{0}</h3><p>{1}</p>{2}<p>seen on {3} reported by {4}<p>".format(
                self.get_species_display(), self.get_health_display(),
                self.tag_html, self.when.strftime('%d/%m/%Y %H:%M:%S'),
                self.who.name))


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
        ("unknown", "Unknown Sex"),)

    MATURITY_CHOICES = (
        ("hatchling", "Hatchling"),
        ("juvenile", "Juvenile"),
        ("adult", "Adult"),
        ("unknown", "Unknown Maturity"),)

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
        help_text=_("The Curved Carapace Length in millimetres."),)

    curved_carapace_length_accuracy = models.CharField(
        max_length=300,
        default="unknown",
        verbose_name=_("Curved Carapace Length Accuracy"),
        choices=ACCURACY_CHOICES,
        help_text=_("The measurement type as indication of accuracy."),)

    curved_carapace_width_mm = models.PositiveIntegerField(
        verbose_name=_("Curved Carapace Width (mm)"),
        blank=True, null=True,
        help_text=_("Curved Carapace Width in millimetres."),)

    curved_carapace_width_accuracy = models.CharField(
        max_length=300,
        default="unknown",
        verbose_name=_("Curved Carapace Width Accuracy"),
        choices=ACCURACY_CHOICES,
        help_text=_("The measurement type as indication of accuracy."),)

    tail_length_mm = models.PositiveIntegerField(
        verbose_name=_("Tail Length (mm)"),
        blank=True, null=True,
        help_text=_("The Tail Length, measured from carapace in millimetres."),)

    tail_length_accuracy = models.CharField(
        max_length=300,
        default="unknown",
        verbose_name=_("Tail Length Accuracy"),
        choices=ACCURACY_CHOICES,
        help_text=_("The measurement type as indication of accuracy."),)

    maximum_head_width_mm = models.PositiveIntegerField(
        verbose_name=_("Maximum Head Width (mm)"),
        blank=True, null=True,
        help_text=_("The Maximum Head Width in millimetres."),)

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

    @property
    def popupContent(self):
        """HTML for a map popup."""
        return mark_safe(
            "<h3>{0}</h3><p>{1} {4} {5}</p>{6}<p>seen on {2} reported by {3}<p>".format(
                self.get_species_display(), self.get_health_display(),
                self.when.strftime('%d/%m/%Y %H:%M:%S'), self.who,
                self.get_maturity_display(), self.get_sex_display(),
                self.tag_html))


# Child models of Observations -----------------------------------------------#
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
        choices=MEDIA_TYPE_CHOICES,
        default="other",
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

@python_2_unicode_compatible
class TagObservation(models.Model):
    """An Observation of an identifying tag on an observed entity.

    The identifying tag can be a flipper tag on a turtle, a PIT tag,
    a satellite tag, a barcode on a sample taken off an animal, a whisker ID
    from a picture of a pinniped, a genetic fingerprint or similar.

    The tag has its own life cycle through stages of production, delivery,
    affiliation with an animal, repeated sightings and disposal.

    The life cycle stages will vary between tag types.

    A TagObservation will find the tag in exactly one of the life cycle stages.

    The life history of each tag can be reconstructed from the sum of all of its
    TagObservations.

    As TagObservations can occur without an Observation of an animal, the
    FK to Observations is optional.
    """

    TYPE_CHOICES = (
        ('flipper-tag', 'Flipper Tag'),
        ('pit-tag', 'PIT Tag'),
        ('satellite-tag', 'Satellite Tag'),
        ('physical-sample', 'Physical Sample'),
        ('genetic-fingerprint', 'Genetic Fingerprint'),
        ('whisker-id', 'Whisker ID'),
        ('other', 'Other'),)

    STATUS_CHOICES = (
        ('ordered', 'Ordered from manufacturer'),
        ('produced', 'Produced by manufacturer'),
        ('delivered', 'Delivered to HQ'),
        ('allocated', 'Allocated to field team'),
        ('attached', 'Attached to an animal'),
        ('recaptured', 'Re-sighted as attached to animal'),
        ('detached', 'Taken off an animal'),
        ('found', 'Found detached'),
        ('returned', 'Returned to HQ'),
        ('decommissioned', 'Decommissioned from active tag pool'),
        ('destroyed', 'Destroyed'),
        ('observed', 'Observed in any other context, see comments'),)

    observation = models.ForeignKey(
        Observation,
        blank=True, null=True,
        verbose_name=_("Observation"),
        help_text=("During which Observation was this tag encountered?"),)

    type = models.CharField(
        max_length=300,
        verbose_name=_("Tag type"),
        choices=TYPE_CHOICES,
        default="flipper-tag",
        help_text=_("The Tag type."),)

    status = models.CharField(
        max_length=300,
        verbose_name=_("Tag status"),
        choices=STATUS_CHOICES,
        default="recaptured",
        help_text=_("The status this tag was seen in, or brought into."),)

    name = models.CharField(
        max_length=1000,
        verbose_name=_("Tag ID"),
        help_text=_("The ID of a tag must be unique within the tag type."),)

    comments = models.TextField(
        verbose_name=_("Comments"),
        blank=True, null=True,
        help_text=_("Any other comments or notes."),)

    def __str__(self):
        """The unicode representation."""
        return "{0} ({1})".format(self.name, self.get_status_display())
