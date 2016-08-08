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
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from polymorphic.models import PolymorphicModel
from django_fsm import FSMField, transition
import urllib

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
    STATUS_NEW = 'new'
    STATUS_PROOFREAD = 'proofread'
    STATUS_CURATED = 'curated'
    STATUS_PUBLISHED = 'published'

    STATUS_CHOICES = (
        (STATUS_NEW, _("New")),
        (STATUS_PROOFREAD, _("Proofread")),
        (STATUS_CURATED, _("Curated")),
        (STATUS_PUBLISHED, _("Published"))
        )

    STATUS_LABELS = {
        STATUS_NEW: "danger",
        STATUS_PROOFREAD: "warning",
        STATUS_CURATED: "info",
        STATUS_PUBLISHED: "success"
        }

    status = FSMField(
        default=STATUS_NEW,
        choices=STATUS_CHOICES,
        verbose_name=_("QA Status"))

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

    # FSM transitions --------------------------------------------------------#
    def can_proofread(self):
        """Return true if this document can be proofread."""
        return True

    @transition(
        field=status,
        source=STATUS_NEW,
        target=STATUS_PROOFREAD,
        conditions=[can_proofread],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Mark as proofread",
            explanation=("This record is a faithful representation of the "
                         "data sheet."),
            notify=True,)
        )
    def proofread(self):
        """Mark encounter as proof-read.

        Proofreading compares the attached data sheet with entered values.
        Proofread data is deemed a faithful representation of original data
        captured on a paper field data collection form, or stored in a legacy
        system.
        """
        return

    def can_require_proofreading(self):
        """Return true if this document can be proofread."""
        return True

    @transition(
        field=status,
        source=STATUS_PROOFREAD,
        target=STATUS_NEW,
        conditions=[can_require_proofreading],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Require proofreading",
            explanation=("This record deviates from the data source and "
                         "requires proofreading."),
            notify=True,)
        )
    def require_proofreading(self):
        """Mark encounter as having typos, requiring more proofreading.

        Proofreading compares the attached data sheet with entered values.
        If a discrepancy to the data sheet is found, proofreading is required.
        """
        return

    def can_curate(self):
        """Return true if this document can be marked as curated."""
        return True

    @transition(
        field=status,
        source=STATUS_PROOFREAD,
        target=STATUS_CURATED,
        conditions=[can_curate],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Mark as trustworthy",
            explanation=("This record is deemed trustworthy."),
            notify=True,)
        )
    def curate(self):
        """Mark encounter as curated.

        Curated data is deemed trustworthy by a subject matter expert.
        """
        return

    def can_revoke_curated(self):
        """Return true if curated status can be revoked."""
        return True

    @transition(
        field=status,
        source=STATUS_CURATED,
        target=STATUS_PROOFREAD,
        conditions=[can_revoke_curated],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Flag",
            explanation=("This record cannot be true. This record requires"
                         " review by a subject matter expert."),
            notify=True,)
        )
    def flag(self):
        """Flag as requiring changes to data.

        Curated data is deemed trustworthy by a subject matter expert.
        Revoking curation flags data for requiring changes by an expert.
        """
        return

    def can_publish(self):
        """Return true if this document can be published."""
        return True

    @transition(
        field=status,
        source=STATUS_CURATED,
        target=STATUS_PUBLISHED,
        conditions=[can_publish],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Publish",
            explanation=("This record is fit for release."),
            notify=True,)
        )
    def publish(self):
        """Mark encounter as ready to be published.

        Published data has been deemed fit for release by the data owner.
        """
        return

    def can_embargo(self):
        """Return true if encounter can be embargoed."""
        return True

    @transition(
        field=status,
        source=STATUS_PUBLISHED,
        target=STATUS_CURATED,
        conditions=[can_embargo],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Embargo",
            explanation=("This record is not fit for release."),
            notify=True,)
        )
    def embargo(self):
        """Mark encounter as NOT ready to be published.

        Published data has been deemed fit for release by the data owner.
        Embargoed data is marked as curated, but not ready for release.
        """
        return

    # HTML display -----------------------------------------------------------#
    @property
    def wkt(self):
        """Return the point coordinates as Well Known Text (WKT)."""
        return self.where.wkt

    @property
    def status_html(self):
        """An HTML div indicating the QA status."""
        tpl = '<div class="popup"><span class="tag tag-{0}">{1}</span></div>'
        return tpl.format(Encounter.STATUS_LABELS[self.status],
                          self.get_status_display())

    @property
    def absolute_admin_url(self):
        """Return the absolute admin change URL."""
        return reverse('admin:{0}_{1}_change'.format(
            self._meta.app_label, self._meta.model_name), args=[self.pk])

    @property
    def admin_url_html(self):
        """An HTML div with a link to the admin change_view."""
        tpl = ('<div class="popup">&nbsp;<a href={0} target="_">'
               '<i class="fa fa-pencil"></i></a></div>')
        return tpl.format(self.absolute_admin_url)

    @property
    def observer_html(self):
        """An HTML string of metadata."""
        tpl = '<div class="popup"><i class="fa fa-{0}"></i>&nbsp;{1}</div>'
        return mark_safe(
            tpl.format("calendar", self.when.strftime('%d/%m/%Y %H:%M:%S %Z')) +
            tpl.format("user", self.who.name))

    @property
    def observation_html(self):
        """An HTML string of Observations."""
        return "".join([o.as_html for o in self.observation_set.all()])

    def make_html(self):
        """Create an HTML representation."""
        tpl = '<h4>Encounter</h4>{0}{1}{2}{4}'
        return mark_safe(tpl.format(self.observer_html, self.observation_html,
                                    self.admin_url_html, self.status_html))


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
        ('other', 'Other'), )

    SPECIES_CHOICES = (
        ('Natator depressus', 'Flatback turtle (Natator depressus)'),
        ('Chelonia mydas', 'Green turtle (Chelonia mydas)'),
        ('Eretmochelys imbricata', 'Hawksbill turtle (Eretmochelys imbricata)'),
        ('Caretta caretta', 'Loggerhead turtle (Caretta caretta)'),
        ('Lepidochelys olivacea', 'Olive Ridley turtle (Lepidochelys olivacea)'),
        ('Dermochelys coriacea', 'Leatherback turtle (Dermochelys coriacea)'),
        ('Corolla corolla', 'Hatchback turtle (Corolla corolla)'),
        ('unidentified', 'Unidentified species'), )

    SEX_CHOICES = (
        ("male", "male"),
        ("female", "female"),
        ("unknown", "sex not determined or not examined"),
        ("intersex", "hermaphrodite or intersex"), )

    MATURITY_CHOICES = (
        ("juvenile", "juvenile"),
        # ("unweaned", "unweaned immature juvenile"),
        # ("weaned", "weaned immature juvenile"),
        ("adult", "adult"),
        ("unknown", "unknown maturity"), )

    ACTIVITY_CHOICES = (
        ("arriving", "arriving"),
        ("digging-body-pit", "digging body pit"),
        ("excavating-egg-chamber", "excavating egg chamber"),
        ("laying-eggs", "laying eggs"),
        ("filling-in-egg-chamber", "filling in egg chamber"),
        ("returning-to-water", "returning to water"),
        ("other", "other activity"),
        ("unknown", "unknown activity"), )

    species = models.CharField(
        max_length=300,
        verbose_name=_("Species"),
        choices=SPECIES_CHOICES,
        default="unidentified",
        help_text=_("The species of the animal."), )

    sex = models.CharField(
        max_length=300,
        default="unknown",
        verbose_name=_("Sex"),
        choices=SEX_CHOICES,
        help_text=_("The animal's sex."), )

    maturity = models.CharField(
        max_length=300,
        default="unknown",
        verbose_name=_("Maturity"),
        choices=MATURITY_CHOICES,
        help_text=_("The animal's maturity."), )

    health = models.CharField(
        max_length=300,
        verbose_name=_("Health status"),
        choices=HEALTH_CHOICES,
        default="alive",
        help_text=_("On a scale from the Fresh Prince of Bel Air to 80s Hair "
                    "Metal: how dead and decomposed is the animal?"), )

    activity = models.CharField(
        max_length=300,
        default="unknown",
        verbose_name=_("Activity"),
        choices=ACTIVITY_CHOICES,
        help_text=_("The animal's activity at the time of observation."), )

    behaviour = models.TextField(
        verbose_name=_("Behaviour"),
        blank=True, null=True,
        help_text=_("Notes on condition or behaviour if alive."), )

    class Meta:
        """Class options."""

        ordering = ["when", "where"]
        verbose_name = "Animal Encounter"
        verbose_name_plural = "Animal Encounters"
        get_latest_by = "when"

    def __str__(self):
        """The unicode representation."""
        tpl = "AnimalEncounter {0} on {1} by {2} of {3}, {4} {5} {6}"
        return tpl.format(
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
        tpl = '<h4>{0}</h4><i class="fa fa-heartbeat"></i>&nbsp;{1} {2} {3}'
        return mark_safe(
            tpl.format(self.get_species_display(), self.get_health_display(),
                       self.get_maturity_display(), self.get_sex_display()))

    def make_html(self):
        """Create an HTML representation."""
        tpl = "{0}{1}{2}{3}{4}"
        return mark_safe(tpl.format(self.animal_html, self.observer_html,
                                    self.observation_html, self.admin_url_html,
                                    self.status_html))


@python_2_unicode_compatible
class TurtleEncounter(AnimalEncounter):
    """The encounter of an animal of a species in a certain state of health
    and behaviour.

    TODO: StrandNet activity.
    TODO: StandNet carcass / health condition, freshness of injury > HEALTH_CHOICES
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
        ('Corolla corolla', 'Hatchback turtle (Corolla corolla)'),
        ('unidentified', 'Unidentified species'),)

    SEX_CHOICES = (
        ("male", "male"),
        ("female", "female"),
        ("unknown", "sex not determined or not examined"),
        ("intersex", "hermaphrodite or intersex"), )

    MATURITY_CHOICES = (
        ("hatchling", "hatchling"),
        ("juvenile", "juvenile"),
        ("adult", "adult"),
        ("unknown", "unknown maturity"), )

    ACTIVITY_CHOICES = (
        ("arriving", "arriving"),
        ("digging-body-pit", "digging body pit"),
        ("excavating-egg-chamber", "excavating egg chamber"),
        ("laying-eggs", "laying eggs"),
        ("filling-in-egg-chamber", "filling in egg chamber"),
        ("returning-to-water", "returning to water"),
        ("other", "other activity"),
        ("unknown", "unknown activity"), )

    class Meta:
        """Class options."""

        ordering = ["when", "where"]
        verbose_name = "Turtle Encounter"
        verbose_name_plural = "Turtle Encounters"
        get_latest_by = "when"

    def __str__(self):
        """The unicode representation."""
        tpl = "TurtleEncounter {0} on {1} by {2} of {3}, {4} {5} {6}"
        return tpl.format(
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
        super(TurtleEncounter, self).save(*args, **kwargs)

    @property
    def animal_html(self):
        """An HTML string of Observations"""
        tpl = '<h4>{0}</h4><i class="fa fa-heartbeat"></i>&nbsp;{1} {2} {3}'
        return mark_safe(
            tpl.format(self.get_species_display(), self.get_health_display(),
                       self.get_maturity_display(), self.get_sex_display()))

    def make_html(self):
        """Create an HTML representation."""
        tpl = "{0}{1}{2}{3}{4}"
        return mark_safe(tpl.format(self.animal_html, self.observer_html,
                                    self.observation_html, self.admin_url_html,
                                    self.status_html))


# Observation models ---------------------------------------------------------#
@python_2_unicode_compatible
class Observation(PolymorphicModel, models.Model):
    """The Observation base class for encounter observations."""

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

    @property
    def observation_name(self):
        """Model name."""
        return self.polymorphic_ctype.model


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
class TagObservation(Observation):
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

    As TagObservations can sometimes occur without an Observation of an animal, the
    FK to Observations is optional.
    """

    TYPE_CHOICES = (
        ('flipper-tag', 'Flipper Tag'),
        ('pit-tag', 'PIT Tag'),
        ('satellite-tag', 'Satellite Tag'),
        ('physical-sample', 'Physical Sample'),
        ('biopsy-sample', 'Biopsy Sample'),
        ('genetic-fingerprint', 'Genetic Fingerprint'),
        ('whisker-id', 'Whisker ID'),
        ('other', 'Other'),)

    STATUS_CHOICES = (
        ('ordered', 'ordered from manufacturer'),
        ('produced', 'produced by manufacturer'),
        ('delivered', 'delivered to HQ'),
        ('allocated', 'allocated to field team'),
        ('attached', 'attached new to an animal'),
        ('recaptured', 're-sighted as attached to animal'),
        ('detached', 'taken off an animal'),
        ('found', 'found detached'),
        ('returned', 'returned to HQ'),
        ('decommissioned', 'decommissioned from active tag pool'),
        ('destroyed', 'destroyed'),
        ('observed', 'observed in any other context, see comments'), )

    SIDE_CHOICES = (
        ("L", "left front flipper"),
        ("R", "right front flipper"),
        ("C", "carapace"),
        ("N", "neck"),
        ("O", "other, see comments"), )

    POSITION_CHOICES = (
        ("1", "1st scale from body/head"),
        ("2", "2nd scale from body/head"),
        ("3", "3rd scale from body/head"),
        ("O", "other, see comments"), )

    tag_type = models.CharField(
        max_length=300,
        verbose_name=_("Tag type"),
        choices=TYPE_CHOICES,
        default="flipper-tag",
        help_text=_("What kind of tag is it?"),)

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
        return "{0} {1} {2} on {3}, {4}".format(
            self.get_tag_type_display(),
            self.name, self.get_status_display(),
            self.get_side_display(), self.get_position_display())

    @property
    def history_url(self):
        """The list view of all observations of this tag."""
        cl = reverse("admin:observations_tagobservation_changelist")
        return "{0}?q={1}".format(cl, urllib.quote_plus(self.name))

    @property
    def as_html(self):
        """An HTML representation."""
        tpl = ('<div class="popup"><i class="fa fa-tag"></i>&nbsp;{0}&nbsp;'
               '<a href={1} target="_" class="btn btn-sm">'
               '<i class="fa fa-history"></i></a></div>')
        return mark_safe(tpl.format(self.__str__(), self.history_url))


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

    scanned_for_pit_tags = models.CharField(
        max_length=300,
        verbose_name=_("Scanned for PIT tags"),
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
            tpl.format("PIT tags scanned", self.OBSERVATION_ICONS[self.scanned_for_pit_tags]) +
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
        "measured": "fa fa-balance-scale"}

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
class TurtleNestingObservation(Observation):
    """Nesting-related measurements of a turtle."""

    BEACH_POSITION_CHOICES = (
        ("below-hwm", "below high water mark"),
        ("above-hw", "above high water mark, below dune"),
        ("dune-edge", "edge of dune, beginning of spinifex"),
        ("in-dune", "inside dune, spinifex"), )

    nest_position = models.CharField(
        max_length=300,
        default="unknown",
        verbose_name=_("Beach position"),
        choices=BEACH_POSITION_CHOICES,
        help_text=_("The position of the nest on the beach."),)

    eggs_laid = models.BooleanField(
        verbose_name=_("Did the turtle lay eggs?"),
        default=False,
        help_text=_("Did round, white objects leave the turtle's butt?"),)

    egg_count = models.PositiveIntegerField(
        verbose_name=_("Number of eggs laid"),
        blank=True, null=True,
        help_text=_("The number of eggs laid."),)

    def __str__(self):
        """The unicode representation."""
        return "Turtle Nesting {0} for {1}".format(
            self.pk, self.encounter)

# NestObs
# Turtle activity when tagged
# EggsObs
# Turtle damage obs - vs dist feat
# Hatched Nest Obs
# Nest obs Ningaloo
# Track obs (false crawl) Ningaloo
