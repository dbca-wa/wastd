# -*- coding: utf-8 -*-
"""
    Opportunistic sighting of stranded/encountered dead or injured wildlife.

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
    * [flipper, pit, sat] tag observation
    * disposal actions

"""
from __future__ import unicode_literals, absolute_import

# from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.gis.db import models as geo_models
from polymorphic.models import PolymorphicModel
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from wastd.users.models import User


# Encounter models -----------------------------------------------------------#
@python_2_unicode_compatible
class Encounter(PolymorphicModel, geo_models.Model):
    """The base Encounter class knows when, where, who.

    When: Datetime of encounter, stored in UTC, entered and displayed in local
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

    as_html = models.TextField(
        verbose_name=_("HTML representation"),
        blank=True, null=True, editable=False,
        help_text=_("The cached HTML representation for display purposes."),)

    class Meta:
        """Class options."""

        ordering = ["when", "where"]
        verbose_name = "Encounter"
        verbose_name_plural = "Encounters"
        get_latest_by = "when"

    def __str__(self):
        """The unicode representation."""
        return "Encounter {0} on {1} by {2}".format(self.pk, self.when, self.who)

    def save(self, *args, **kwargs):
        """Cache the HTML representation in `as_html`."""
        self.as_html = self.make_html()
        super(Encounter, self).save(*args, **kwargs)

    @property
    def wkt(self):
        """Return the point coordinates as Well Known Text (WKT)."""
        return self.where.wkt

    @property
    def observer_html(self):
        """An HTML string of metadata"""
        tpl = '<div class="popup"><i class="fa fa-{0}"></i>&nbsp;{1}</div>'
        return mark_safe(
            tpl.format("calendar", self.when.strftime('%d/%m/%Y %H:%M:%S %Z')) +
            tpl.format("user", self.who.name))

    @property
    def observation_html(self):
        """An HTML string of Observations"""
        return "".join([o.as_html for o in self.observation_set.all()])

    def make_html(self):
        """Create an HTML representation."""
        return mark_safe("<h4>Encounter</h4>{0}{1}".format(
            self.observer_html, self.observation_html))


@python_2_unicode_compatible
class AnimalEncounter(Encounter):
    """The encounter of an animal of a species in a certain state of health
    and behaviour.
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
        ('unidentified', 'Unidentified species'),)

    SEX_CHOICES = (
        ("male", "male"),
        ("female", "female"),
        ("unknown", "unknown sex"),)

    MATURITY_CHOICES = (
        ("hatchling", "hatchling"),
        ("juvenile", "juvenile"),
        ("adult", "adult"),
        ("unknown", "unknown maturity"),)

    species = models.CharField(
        max_length=300,
        verbose_name=_("Species"),
        choices=SPECIES_CHOICES,
        default="unidentified",
        help_text=_("The species of the animal."),)

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

    class Meta:
        """Class options."""

        ordering = ["when", "where"]
        verbose_name = "Animal Encounter"
        verbose_name_plural = "Animal Encounters"
        get_latest_by = "when"

    def __str__(self):
        """The unicode representation."""
        return "AnimalEncounter {0} on {1} by {2} of {3}, {4} {5} {6}".format(
            self.pk,
            self.when.strftime('%d/%m/%Y %H:%M:%S %Z'),
            self.who.name,
            self.get_species_display(),
            self.get_health_display(),
            self.get_maturity_display(),
            self.get_sex_display())

    def save(self, *args, **kwargs):
        """Cache the HTML representation in `as_html`."""
        self.as_html = self.make_html()
        super(AnimalEncounter, self).save(*args, **kwargs)

    @property
    def animal_html(self):
        """An HTML string of Observations"""
        return mark_safe('<h4>{0}</h4><i class="fa fa-heartbeat"></i>&nbsp;{1} {2} {3}'.format(
            self.get_species_display(),
            self.get_health_display(),
            self.get_maturity_display(),
            self.get_sex_display()))

    def make_html(self):
        """Create an HTML representation."""
        return mark_safe("{0}{1}{2}".format(
            self.animal_html, self.observer_html, self.observation_html))


# Observation models ---------------------------------------------------------#
@python_2_unicode_compatible
class Observation(PolymorphicModel, models.Model):
    """The Observation base class."""
    encounter = models.ForeignKey(
        Encounter,
        blank=True, null=True,
        verbose_name=_("Encounter"),
        help_text=("The Encounter during which the observation was made"),)

    def __str__(self):
        """The unicode representation."""
        return "Obs {0} for {1}".format(self.pk, self.encounter.__str__())

    @property
    def as_html(self):
        """An HTML representation."""
        return mark_safe('<div class="popup">{0}</div>'.format(self.__str__()))


@python_2_unicode_compatible
class MediaAttachment(Observation):
    """A media attachment to an Encounter."""

    MEDIA_TYPE_CHOICES = (
        ('data_sheet', 'Original data sheet'),
        ('photograph', 'Photograph'),
        ('other', 'Other'),)

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
        upload_to='attachments/%Y/%m/%d/',
        verbose_name=_("File attachment"),
        help_text=_("Upload the file"),)

    def __str__(self):
        """The unicode representation."""
        return "Media {0} {1} for {2}".format(
            self.pk, self.title, self.encounter.__str__())

    @property
    def as_html(self):
        """An HTML representation."""
        tpl = ('<div class="popup"><i class="fa fa-film"></i>'
               '&nbsp;<a href="{0}" target="_">{1}</a></div>')
        return mark_safe(tpl.format(self.attachment.url, self.title))


@python_2_unicode_compatible
class DistinguishingFeatureObservation(Observation):
    """DistinguishingFeature observation."""

    OBSERVATION_CHOICES = (
        ("na", "Not observed"),
        ("absent", "Confirmed absent"),
        ("present", "Confirmed present"),)

    OBSERVATION_ICONS = {
        "na": "fa fa-question-circle-o",
        "absent": "fa fa-times",
        "present": "fa fa-check"}

    PHOTO_CHOICES = (
        ("na", "Not applicable"),
        ("see photos", "See attached photos for details"),)

    PHOTO_ICONS = {
        "na": "fa fa-question-circle-o",
        "see photos": "fa fa-check"}

    damage_injury = models.CharField(
        max_length=300,
        verbose_name=_("Obvious damage or injuries"),
        choices=OBSERVATION_CHOICES,
        default="na",
        help_text=_(""),)

    missing_limbs = models.CharField(
        max_length=300,
        verbose_name=_("Missing limbs"),
        choices=OBSERVATION_CHOICES,
        default="na",
        help_text=_(""),)

    barnacles = models.CharField(
        max_length=300,
        verbose_name=_("Barnacles"),
        choices=OBSERVATION_CHOICES,
        default="na",
        help_text=_(""),)

    algal_growth = models.CharField(
        max_length=300,
        verbose_name=_("Algal growth on carapace"),
        choices=OBSERVATION_CHOICES,
        default="na",
        help_text=_(""),)

    tagging_scars = models.CharField(
        max_length=300,
        verbose_name=_("Tagging scars"),
        choices=OBSERVATION_CHOICES,
        default="na",
        help_text=_(""),)

    propeller_damage = models.CharField(
        max_length=300,
        verbose_name=_("Propeller strike damage"),
        choices=OBSERVATION_CHOICES,
        default="na",
        help_text=_(""),)

    entanglement = models.CharField(
        max_length=300,
        verbose_name=_("Entanglement"),
        choices=OBSERVATION_CHOICES,
        default="na",
        help_text=_("Entanglement in anthropogenic debris"),)

    see_photo = models.CharField(
        max_length=300,
        verbose_name=_("See attached photos"),
        choices=PHOTO_CHOICES,
        default="na",
        help_text=_("More relevant detail in attached photos"),)

    comments = models.TextField(
        verbose_name=_("Comments"),
        blank=True, null=True,
        help_text=_("Further comments on distinguising features."),)

    def __str__(self):
        """The unicode representation."""
        return "Distinguishing Features {0} of {1}".format(
            self.pk, self.encounter.__str__())

    @property
    def as_html(self):
        """An HTML representation."""
        tpl = ('<div class="popup"><i class="fa fa-eye"></i>&nbsp;{0}'
               '&nbsp<i class="{1}"></i></div>')
        return mark_safe(
            tpl.format("Damage", self.OBSERVATION_ICONS[self.damage_injury]) +
            tpl.format("Missing Limbs", self.OBSERVATION_ICONS[self.missing_limbs]) +
            tpl.format("Barnacles", self.OBSERVATION_ICONS[self.barnacles]) +
            tpl.format("Algal growth", self.OBSERVATION_ICONS[self.algal_growth]) +
            tpl.format("Tagging scars", self.OBSERVATION_ICONS[self.tagging_scars]) +
            tpl.format("Propeller damage", self.OBSERVATION_ICONS[self.propeller_damage]) +
            tpl.format("Entanglement", self.OBSERVATION_ICONS[self.entanglement]) +
            tpl.format("More in photos", self.PHOTO_ICONS[self.see_photo]))


@python_2_unicode_compatible
class DisposalObservation(Observation):
    """Disposal of a dead animal."""

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
        return "Disposal {0} of {1}".format(
            self.pk, self.encounter.__str__())

    @property
    def as_html(self):
        """An HTML representation."""
        tpl = '<div class="popup"><i class="fa fa-trash"></i>&nbsp;{0}</div>'
        return mark_safe(tpl.format(self.management_actions))


@python_2_unicode_compatible
class TurtleMorphometricObservation(Observation):
    """Morphometric measurements of a turtle."""

    ACCURACY_CHOICES = (
        ("unknown", "Unknown"),
        ("estimated", "Estimated"),
        ("measured", "Measured"),)

    ACCURACY_ICONS = {
        "unknown": "fa fa-question-circle-o",
        "estimated": "fa fa-comment-o",
        "measured": "fa fa-balance-scale"
    }

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

    curved_carapace_notch_mm = models.PositiveIntegerField(
        verbose_name=_("Curved Carapace Notch (mm)"),
        blank=True, null=True,
        help_text=_("The Curved Carapace Notch in millimetres."),)

    curved_carapace_notch_accuracy = models.CharField(
        max_length=300,
        default="unknown",
        verbose_name=_("Curved Carapace Notch Accuracy"),
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
        return "Turtle Morphometrics {0} for {1}".format(
            self.pk, self.encounter)

    @property
    def as_html(self):
        """An HTML representation."""
        tpl = ('<div class="popup"><i class="fa fa-bar-chart"></i>&nbsp;{0}'
               '&nbsp;{1}&nbsp;mm&nbsp;<i class="{2}"></i></div>')
        return mark_safe(
            tpl.format("CCL", self.curved_carapace_length_mm,
                       self.ACCURACY_ICONS[self.curved_carapace_length_accuracy]) +
            tpl.format("CCN", self.curved_carapace_notch_mm,
                       self.ACCURACY_ICONS[self.curved_carapace_notch_accuracy]) +
            tpl.format("CCW", self.curved_carapace_width_mm,
                       self.ACCURACY_ICONS[self.curved_carapace_width_accuracy]) +
            tpl.format("TL", self.tail_length_mm,
                       self.ACCURACY_ICONS[self.tail_length_accuracy]) +
            tpl.format("HW", self.maximum_head_width_mm,
                       self.ACCURACY_ICONS[self.maximum_head_width_accuracy])
            )


@python_2_unicode_compatible
class FlipperTagObservation(Observation):
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

    # TYPE_CHOICES = (
    #     ('flipper-tag', 'Flipper Tag'),
    #     ('pit-tag', 'PIT Tag'),
    #     ('satellite-tag', 'Satellite Tag'),
    #     ('physical-sample', 'Physical Sample'),
    #     ('genetic-fingerprint', 'Genetic Fingerprint'),
    #     ('whisker-id', 'Whisker ID'),
    #     ('other', 'Other'),)
    """

    STATUS_CHOICES = (
        ('ordered', 'ordered from manufacturer'),
        ('produced', 'produced by manufacturer'),
        ('delivered', 'delivered to HQ'),
        ('allocated', 'allocated to field team'),
        ('attached', 'attached new to an animal'),
        ('recaptured', 're-sighted as attached to animal'),
        ('detached', 'raken off an animal'),
        ('found', 'found detached'),
        ('returned', 'returned to HQ'),
        ('decommissioned', 'decommissioned from active tag pool'),
        ('destroyed', 'destroyed'),
        ('observed', 'observed in any other context, see comments'),)

    SIDE_CHOICES = (
        ("L", "left front flipper"),
        ("R", "right front flipper"))

    POSITION_CHOICES = (
        ("1", "1st scale from body"),
        ("2", "2nd scale from body"),
        ("3", "3rd scale from body"))

    side = models.CharField(
        max_length=300,
        verbose_name=_("Tag side"),
        choices=SIDE_CHOICES,
        default="L",
        help_text=_("Is the tag on the left or right front flipper?"),)

    position = models.CharField(
        max_length=300,
        verbose_name=_("Tag position"),
        choices=POSITION_CHOICES,
        default="1",
        help_text=_("Counting from inside, to which flipper scale is the "
                    "tag attached?"),)

    name = models.CharField(
        max_length=1000,
        verbose_name=_("Tag ID"),
        help_text=_("The ID of a tag must be unique within the tag type."),)

    status = models.CharField(
        max_length=300,
        verbose_name=_("Tag status"),
        choices=STATUS_CHOICES,
        default="recaptured",
        help_text=_("The status this tag was seen in, or brought into."),)

    comments = models.TextField(
        verbose_name=_("Comments"),
        blank=True, null=True,
        help_text=_("Any other comments or notes."),)

    def __str__(self):
        """The unicode representation."""
        return "Flipper Tag {0} {1} on {2}, {3}".format(
            self.name, self.get_status_display(),
            self.get_side_display(), self.get_position_display())

    @property
    def as_html(self):
        """An HTML representation."""
        tpl = '<div class="popup"><i class="fa fa-tag"></i>&nbsp;{0}</div>'
        return mark_safe(tpl.format(self.__str__()))


# NestObs
# Turtle activity when tagged
# EggsObs
# Turtle damage obs - vs dist feat
# Hatched Nest Obs
# Nest obs Ningaloo
# Track obs (false crawl) Ningaloo
