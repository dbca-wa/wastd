# -*- coding: utf-8 -*-
"""Conservation models."""
from __future__ import absolute_import, unicode_literals

# import itertools
# import urllib
# import slugify
from datetime import datetime
# from dateutil import tz
import logging

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models as geo_models
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
# from django.contrib.gis.db import models as geo_models
# from django.contrib.gis.db.models.query import GeoQuerySet
from django.urls import reverse
# from rest_framework.reverse import reverse as rest_reverse
# from django.template import loader
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
# from polymorphic.models import PolymorphicModel
# from durationfield.db.models.fields.duration import DurationField
# from django.db.models.fields import DurationField
from django_fsm import FSMIntegerField, transition
from django_fsm_log.decorators import fsm_log_by
from taxonomy.models import Community, Taxon

from wastd.users.models import User
from shared.models import UrlsMixin, CodeLabelDescriptionMixin, ObservationAuditMixin

# from django.utils.safestring import mark_safe

# from django_fsm_log.models import StateLog


logger = logging.getLogger(__name__)


def fileattachment_media(instance, filename):
    """Return an upload path for fileattachment media."""
    return 'attachment/{0}/{1}/{2}'.format(instance.content_type, instance.object_id, filename)


@python_2_unicode_compatible
class FileAttachment(models.Model):
    """A generic file attachment to any model."""

    attachment = models.FileField(upload_to=fileattachment_media)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    title = models.CharField(
        blank=True, null=True,
        max_length=500,
        verbose_name=_("Title"),
        help_text=_("A self-explanatory title for the file attachment."))

    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name=_("Author"),
        related_name="conservation_fileattachments",
        blank=True, null=True,
        help_text=_("The person who authored and endorsed this file."))

    current = models.BooleanField(
        db_index=True,
        default=True,
        verbose_name=_("Is current"),
        help_text=_("Whether this file is current or an archived version."),)

    confidential = models.BooleanField(
        db_index=True,
        default=True,
        verbose_name=_("Is confidential"),
        help_text=_("Whether this file is confidential or "
                    "can be released to the public."),)

    def __str__(self):
        """The full name."""
        return "{0} {1}".format(self.title, self.author)


# -----------------------------------------------------------------------------
# Conservation (Management) Threats and Actions
@python_2_unicode_compatible
class ConservationThreatCategory(CodeLabelDescriptionMixin, models.Model):
    """A conservation management threat category."""

    class Meta:
        """Class opts."""

        verbose_name = "Conservation Threat Category"
        verbose_name_plural = "Conservation Threat Categories"


@python_2_unicode_compatible
class ConservationThreat(UrlsMixin, ObservationAuditMixin, models.Model):
    """A conservation threat is a potentially damaging event against a taxon or community.

    The conservation threat can pertain to:

    * an entire species,
    * an entire community,
    * any combination of species and communities
      (as per multi-species management plans),
    * a management / recovery / interim recovery plan,
    * an individual occurrence (fauna site, flora population
      or subpopulation, TEC pr PEC boundary), or
    * a subset of occurrences as indicated by a multipolygon.

    The conservation threat is specified by:

    * a threat category, and
    * threat causes.
    """

    EHMLNN_DEFAULT = "NA"
    EHMLNN_NIL = "nil"
    EHMLNN_LOW = "low"
    EHMLNN_MEDIUM = "medium"
    EHMLNN_HIGH = "high"
    EHMLNN_EXTREME = "extreme"
    EHMLNN_CHOICES = (
        (EHMLNN_DEFAULT, _("NA")),
        (EHMLNN_NIL, _("Nil")),
        (EHMLNN_LOW, _("Low")),
        (EHMLNN_MEDIUM, _("Medium")),
        (EHMLNN_HIGH, _("High")),
        (EHMLNN_EXTREME, _("Extreme")),
    )

    LMSN_DEFAULT = "NA"
    LSMN_SHORT = "short-term"
    LSMN_MEDIUM = "medium-term"
    LSMN_LONG = "long-term"
    LMSN_CHOICES = (
        (LMSN_DEFAULT, _("NA")),
        (LSMN_SHORT, _("(S)hort term: Within 12 months")),
        (LSMN_MEDIUM, _("(M)edium term: Within 1 to 5 years")),
        (LSMN_LONG, _("(L)ong term: after 5 years")),
    )
    # Pertains to
    taxa = models.ManyToManyField(
        Taxon,
        blank=True,
        verbose_name=_("Taxa"),
        help_text=_("All taxa this conservation threat pertains to."),
    )

    communities = models.ManyToManyField(
        Community,
        blank=True,
        verbose_name=_("Communities"),
        help_text=_("All communities this conservation threat pertains to."),
    )

    document = models.ForeignKey(
        "Document",
        blank=True, null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Plan document"),
        help_text=_("The document in which this conservation threat is specified."),
    )

    target_area = geo_models.MultiPolygonField(
        srid=4326,
        blank=True, null=True,
        verbose_name=_("Target Area"),
        help_text=_("If this action pertains to only some but not all occurrences, "
                    "indicate the target area(s) here. This management action will "
                    "be automatically affiliated with all intersecting occurrence areas."),
    )

    occurrence_area_code = models.CharField(
        max_length=1000,
        blank=True, null=True,
        verbose_name=_("Occurence area code"),
        help_text=_("The known code for the occurrence area this "
                    "conservation threat pertains to, e.g. a Fauna site, "
                    "a Flora (sub)population ID, or a TEC/PEC boundary name."),
    )

    # Threat
    category = models.ForeignKey(
        ConservationThreatCategory,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Threat category"),
        help_text=_("Choose the overarching category."),
    )

    cause = models.TextField(
        blank=True, null=True,
        verbose_name=_("Threat cause"),
        help_text=_("Describe the threat cause or agent."),
    )

    area_affected_percent = models.DecimalField(
        max_digits=3,
        decimal_places=0,
        blank=True, null=True,
        verbose_name=_("Area affected [%]"),
        help_text=_("The estimated percentage (0-100) of the "
                    "specified occurrence area affected by this threat."),
    )

    current_impact = models.CharField(
        verbose_name=_("Current Impact"),
        max_length=100,
        default=EHMLNN_DEFAULT,
        choices=EHMLNN_CHOICES,
        help_text=_("Current impact of threat on specified subjects."),
    )

    potential_impact = models.CharField(
        verbose_name=_("Potential Impact"),
        max_length=100,
        default=EHMLNN_DEFAULT,
        choices=EHMLNN_CHOICES,
        help_text=_("Potential impact of threat on specified subjects."),
    )

    potential_onset = models.CharField(
        verbose_name=_("Potential Onset"),
        max_length=100,
        default=LMSN_DEFAULT,
        choices=LMSN_CHOICES,
        help_text=_("Potential onset of threat on specified subjects."),
    )

    class Meta:
        """Class opts."""

        verbose_name = "Conservation Threat"
        verbose_name_plural = "Conservation Threats"
        ordering = ["category", "cause", ]
        index_together = [
            ["document", "occurrence_area_code"],
        ]
        card_template = 'conservation/includes/conservationthreat_card.html'

    def __str__(self):
        """The full name."""
        return "[{0}] {1}".format(self.category, self.cause)


@python_2_unicode_compatible
class ConservationActionCategory(CodeLabelDescriptionMixin, models.Model):
    """A conservation management action category."""

    class Meta:
        """Class opts."""

        verbose_name = "Conservation Action Category"
        verbose_name_plural = "Conservation Action Categories"


@python_2_unicode_compatible
class ConservationAction(UrlsMixin, models.Model):
    """A conservation action is an intended conservation management measure.

    The conservation action can pertain to:

    * an entire species,
    * an entire community,
    * any combination of species and communities
      (as per multi-species management plans),
    * a management / recovery / interim recovery plan,
    * an individual occurrence (fauna site, flora population
      or subpopulation, TEC pr PEC boundary), or
    * a subset of occurrences as indicated by a multipolygon.

    The conservation action intent is specified by:

    * an action category, and
    * implementation instructions.

    The partial or complete implementation is documented by:

    * instructions,
    * completion date,
    * expenditure.

    A conservation action has an implicit life cycle:

    * new - no implementation notes,
    * stale - implementation notes, but no changes in current fiscal year,
    * in progress - implementation notes, changed in current fiscal year,
    * complete - completion date set.

    Attachments can be added to capture e.g. communication records with stakeholders,
    reports on implementation outcomes and any other supporting information.
    """

    STATUS_NEW = 10
    STATUS_STALE = 20
    STATUS_INPROGRESS = 30
    STATUS_COMPLETED = 40

    STATUS_CHOICES = (
        (STATUS_NEW, "New"),
        (STATUS_STALE, "Stale"),
        (STATUS_INPROGRESS, "In progress"),
        (STATUS_COMPLETED, "Completed"),
    )

    # Pertains to
    taxa = models.ManyToManyField(
        Taxon,
        blank=True,
        verbose_name=_("Taxa"),
        help_text=_("All taxa this conservation action pertains to."),
    )

    communities = models.ManyToManyField(
        Community,
        blank=True,
        verbose_name=_("Communities"),
        help_text=_("All communities this conservation action pertains to."),
    )

    document = models.ForeignKey(
        "Document",
        blank=True, null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Plan document"),
        help_text=_("The document in which this conservation action is specified."),
    )

    target_area = geo_models.MultiPolygonField(
        srid=4326,
        blank=True, null=True,
        verbose_name=_("Target Area"),
        help_text=_("If this action pertains to only some but not all occurrences, "
                    "indicate the target area(s) here. This conservation action will "
                    "be automatically affiliated with all intersecting occurrence areas."),
    )

    occurrence_area_code = models.CharField(
        max_length=1000,
        blank=True, null=True,
        verbose_name=_("Occurence area code"),
        help_text=_("The known code for the occurrence area this "
                    "conservation action pertains to, either a Fauna site, "
                    "a Flora (sub)population ID, or a TEC/PEC boundary name."),
    )

    # Intent
    category = models.ForeignKey(
        ConservationActionCategory,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Managment action category"),
        help_text=_("Choose the overarching category."),
    )

    instructions = models.TextField(
        blank=True, null=True,
        verbose_name=_("Instructions"),
        help_text=_("Details on the intended implementation."),
    )

    # Implementation
    implementation_notes = models.TextField(
        blank=True, null=True,
        verbose_name=_("Implementation notes"),
        help_text=_("Add notes as appropriate once the implementation is in progress. "
                    "Separate progress from different fiscal years in paragraphs. "
                    "If this conservation action requires several separate activities, "
                    "consider reporting a them separately as conservation activities."),
    )

    completion_date = models.DateField(
        blank=True, null=True,
        verbose_name=_("Completion date"),
        help_text=_("Set once the action is completed."),
    )

    expenditure = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        blank=True, null=True,
        verbose_name=_("Expenditure"),
        help_text=_("The running tally of budget expended as sum of reported activities."),
    )

    status = models.PositiveIntegerField(
        verbose_name=_("Status"),
        default=STATUS_NEW,
        choices=STATUS_CHOICES,
        help_text=_("Completion status."), )

    attachments = GenericRelation(FileAttachment, object_id_field="object_id")

    class Meta:
        """Class opts."""

        verbose_name = "Conservation Action"
        verbose_name_plural = "Conservation Actions"
        ordering = ["status", "completion_date", "category", ]
        index_together = [
            ["status", "completion_date", "category", ],
            ["document", "occurrence_area_code"],
        ]
        card_template = 'conservation/includes/conservationaction_card.html'

    def __str__(self):
        """The full name."""
        return "[{0}] {1}".format(self.category, self.instructions)

    # -------------------------------------------------------------------------
    # django-fsm QA status
    def get_status(self):
        """Return a string indicating the progress status.

        * If completion date exists and in the past: completed
        * If cons activities added: in progress
        * If impl notes added: in progress
        * else: new.
        """
        if self.completion_date and self.completion_date <= timezone.now().date():
            return ConservationAction.STATUS_COMPLETED
        elif self.conservationactivity_set.count() > 0:
            return ConservationAction.STATUS_INPROGRESS
        elif self.implementation_notes:
            return ConservationAction.STATUS_INPROGRESS
        else:
            return ConservationAction.STATUS_NEW


@receiver(pre_save, sender=ConservationAction)
def update_status_cache(sender, instance, *args, **kwargs):
    """ConservationAction: Cache expensive lookups.

    * Derive status
    * Calculate total expenditure.
    """
    logger.info("[ConservationAction.update_status_cache] Deriving completion status.")
    if instance.completion_date and type(instance.completion_date) == datetime:
        instance.completion_date = instance.completion_date.date()
    instance.status = instance.get_status()
    instance.expenditure = instance.conservationactivity_set.aggregate(
        models.Sum('expenditure'))['expenditure__sum']


@python_2_unicode_compatible
class ConservationActivity(UrlsMixin, models.Model):
    """An implementation of a conservation management measure."""

    conservation_action = models.ForeignKey(
        ConservationAction,
        on_delete=models.CASCADE
    )

    implementation_notes = models.TextField(
        blank=True, null=True,
        verbose_name=_("Implementation notes"),
        help_text=_("Describe the executed work."),
    )

    completion_date = models.DateField(
        blank=True, null=True,
        verbose_name=_("Completion date"),
        help_text=_("The date on which this activity was completed."),
    )

    expenditure = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        blank=True, null=True,
        verbose_name=_("Expenditure"),
        help_text=_("The estimated cost of this activity."),
    )

    attachments = GenericRelation(FileAttachment, object_id_field="object_id")

    class Meta:
        """Class opts."""

        verbose_name = "Conservation Activity"
        verbose_name_plural = "Conservation Activities"

    def __str__(self):
        """The full name."""
        return "[{0}][{1}] {2}".format(
            self.conservation_action.category,
            self.completion_date.strftime("%d/%m/%Y") if self.completion_date else "in progress",
            self.implementation_notes)

    # -------------------------------------------------------------------------
    # URLs
    @property
    def absolute_admin_url(self):
        """Return the absolute admin change URL."""
        return self.conservation_action.absolute_admin_url

    def list_url(self):
        """ObsGroup list is not defined."""
        return self.conservation_action.get_absolute_url()

    def get_absolute_url(self):
        """Detail url."""
        return self.conservation_action.get_absolute_url()

    @classmethod
    def create_url(cls, conservation_action):
        """Create url. Required args: a conservation action instance."""
        return reverse('conservation:conservationactivity-create',
                       kwargs={'pk': conservation_action.pk})


@receiver(post_save, sender=ConservationActivity)
def update_consaction_caches(sender, instance, *args, **kwargs):
    """ConservationActivity: Update Conservation Action status and budget cache.

    * Derive status
    * Calculate total expenditure.
    """
    logger.info("[ConservationAction.update_caches] Updating cached fields.")
    instance.conservation_action.save()


# -----------------------------------------------------------------------------
# Conservation lists


@python_2_unicode_compatible
class ConservationList(models.Model):
    """A Conservation List like BCA, EPBC, RedList."""

    APPROVAL_IMMEDIATE = 10
    APPROVAL_PANEL = 20
    APPROVAL_DIRECTOR = 25
    APPROVAL_MINISTER = 30

    APPROVAL_LEVELS = (
        (APPROVAL_IMMEDIATE, 'Immediate'),
        (APPROVAL_PANEL, 'Panel'),
        (APPROVAL_DIRECTOR, 'Director'),
        (APPROVAL_MINISTER, 'Minister'),
    )

    code = models.CharField(
        max_length=500,
        unique=True,
        verbose_name=_("Code"),
        help_text=_("A Conservation List code."),
    )

    label = models.CharField(
        blank=True, null=True,
        max_length=500,
        verbose_name=_("Label"),
        help_text=_("An explanatory label."),
    )

    description = models.TextField(
        blank=True, null=True,
        verbose_name=_("Description"),
        help_text=_("A comprehensive description."),
    )

    active_from = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("Active from"),
        help_text=_("The date and time from which this list is current."),
    )

    active_to = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("Active to"),
        help_text=_("The date and time from which this list is non-current."),
    )

    scope_wa = models.BooleanField(
        db_index=True,
        default=False,
        verbose_name=_("Applies to WA"),
        help_text=_("Whether this list is applicable state-wide."),
    )

    scope_cmw = models.BooleanField(
        db_index=True,
        default=False,
        verbose_name=_("Applies to Commonwealth"),
        help_text=_("Whether this list is applicable nation-wide."),
    )

    scope_intl = models.BooleanField(
        db_index=True,
        default=False,
        verbose_name=_("Applies Internationally"),
        help_text=_("Whether this list is applicable internationally."),
    )

    scope_species = models.BooleanField(
        db_index=True,
        default=False,
        verbose_name=_("Applies to Species"),
        help_text=_("Whether this list is applicable to individual species."),
    )

    scope_communities = models.BooleanField(
        db_index=True,
        default=False,
        verbose_name=_("Applies to Communities"),
        help_text=_("Whether this list is applicable to ecological communities."),
    )

    approval_level = models.PositiveIntegerField(
        verbose_name=_("Approval Level"),
        default=APPROVAL_MINISTER,
        choices=APPROVAL_LEVELS,
        help_text=_("What is the highest required approval instance for this list?"), )

    class Meta:
        """Class opts."""

        verbose_name = "Conservation List"
        verbose_name_plural = "Conservation Lists"
        ordering = ["-active_from", ]

    def __str__(self):
        """The full name."""
        return self.code

    # -------------------------------------------------------------------------
    # URLs
    @property
    def absolute_admin_url(self):
        """Return the absolute admin change URL."""
        return reverse('admin:{0}_{1}_change'.format(
            self._meta.app_label, self._meta.model_name), args=[self.pk])


@python_2_unicode_compatible
class ConservationCategory(models.Model):
    """A Conservation Category like CR, EN, VU."""

    conservation_list = models.ForeignKey(
        ConservationList,
        on_delete=models.CASCADE,
        verbose_name=_("Conservation List"),
        help_text=_("The conservation list this code is described in."),
    )

    code = models.CharField(
        max_length=500,
        verbose_name=_("Code"),
        help_text=_("A category code, unique within its conservation list."),
    )

    label = models.CharField(
        blank=True, null=True,
        max_length=500,
        verbose_name=_("Label"),
        help_text=_("An explanatory label."),
    )

    description = models.TextField(
        blank=True, null=True,
        verbose_name=_("Description"),
        help_text=_("A comprehensive description."),
    )

    rank = models.PositiveIntegerField(
        verbose_name=_("Rank"),
        blank=True, null=True,
        help_text=_("Display order, lowest number goes first."), )

    current = models.BooleanField(
        db_index=True,
        default=True,
        verbose_name=_("Is current"),
        help_text=_("Whether this category should be shown for "
                    "new conservatin listings."),
    )

    class Meta:
        """Class opts."""

        unique_together = ("conservation_list", "code")
        ordering = ["conservation_list", "rank"]
        verbose_name = "Conservation Category"
        verbose_name_plural = "Conservation Categories"

    def __str__(self):
        """The full name."""
        return "[{0}] {1}".format(self.conservation_list.code, self.code)

    # -------------------------------------------------------------------------
    # URLs
    @property
    def absolute_admin_url(self):
        """Return the absolute admin change URL."""
        return reverse('admin:{0}_{1}_change'.format(
            self._meta.app_label, self._meta.model_name), args=[self.pk])


@python_2_unicode_compatible
class ConservationCriterion(models.Model):
    """A Conservation Criterion like A4a."""

    conservation_list = models.ForeignKey(
        ConservationList,
        on_delete=models.CASCADE,
        verbose_name=_("Conservation List"),
        help_text=_("The conservation list this code is described in."),
    )

    code = models.CharField(
        max_length=500,
        verbose_name=_("Code"),
        help_text=_("A criterion code, unique within its conservation list."),
    )

    label = models.CharField(
        blank=True, null=True,
        max_length=500,
        verbose_name=_("Label"),
        help_text=_("An explanatory label."),
    )

    description = models.TextField(
        blank=True, null=True,
        verbose_name=_("Description"),
        help_text=_("A comprehensive description."),
    )

    rank = models.PositiveIntegerField(
        verbose_name=_("Rank"),
        blank=True, null=True,
        help_text=_("Display order, lowest number goes first."), )

    class Meta:
        """Class opts."""

        unique_together = ("conservation_list", "code")
        ordering = ["conservation_list", "rank"]
        verbose_name = "Conservation Criterion"
        verbose_name_plural = "Conservation Criteria"

    def __str__(self):
        """The full name."""
        return "[{0}] {1}".format(self.conservation_list.code, self.code)

    # -------------------------------------------------------------------------
    # URLs
    @property
    def absolute_admin_url(self):
        """Return the absolute admin change URL."""
        return reverse('admin:{0}_{1}_change'.format(
            self._meta.app_label, self._meta.model_name), args=[self.pk])


class ActiveGazettalManager(models.Manager):
    """Custom Gazettal manager to return only active Gazettals."""

    def get_queryset(self):
        """Return only active Gazettals."""
        return super().get_queryset().filter(status=Gazettal.STATUS_EFFECTIVE)


@python_2_unicode_compatible
class Gazettal(models.Model):
    """The allocation of a ConservationCategory.

    Approval state is tracked as django-fsm field.
    ConservationCategory can change during approval process.
    Inheritance can override transitions.

    Documents are attached as MediaAttachments.

    Some conservation categories are mutually exclusiver than others.
    To prevent invalid combinations of ConservationCategories,
    the transition to Gazettal.STATUS_EFFECTIVE must take care of
    closing just the mutually exclusive ones.
    """

    STATUS_PROPOSED = 0
    STATUS_IN_EXPERT_REVIEW = 10
    STATUS_IN_PUBLIC_REVIEW = 20
    STATUS_IN_PANEL_REVIEW = 30
    STATUS_IN_BM_REVIEW = 40
    STATUS_IN_DIR_REVIEW = 50
    STATUS_IN_DG_REVIEW = 60
    STATUS_IN_MIN_REVIEW = 70
    STATUS_EFFECTIVE = 80
    STATUS_CLOSED = 90
    STATUS_REJECTED = 100

    APPROVAL_STATUS = (
        (STATUS_PROPOSED, "Proposed"),
        (STATUS_IN_EXPERT_REVIEW, "In review with experts"),
        (STATUS_IN_PUBLIC_REVIEW, "In review with public"),
        (STATUS_IN_PANEL_REVIEW, "In review with panel"),
        (STATUS_IN_BM_REVIEW, "In review with Branch Manager"),
        (STATUS_IN_DIR_REVIEW, "In review with Division Director"),
        (STATUS_IN_DG_REVIEW, "In review with Director General"),
        (STATUS_IN_MIN_REVIEW, "In review with Minister"),
        (STATUS_EFFECTIVE, "Listed"),
        (STATUS_CLOSED, "De-listed"),
        (STATUS_REJECTED, "Rejected"),
    )

    SOURCE_MANUAL_ENTRY = 0
    SOURCE_THREATENED_FAUNA = 1
    SOURCE_THREATENED_FLORA = 2
    SOURCE_THREATENED_COMMUNITIES = 3

    SOURCES = (
        (SOURCE_MANUAL_ENTRY, 'Manual entry'),
        (SOURCE_THREATENED_FAUNA, 'Threatened Fauna'),
        (SOURCE_THREATENED_FLORA, 'Threatened Flora'),
        (SOURCE_THREATENED_COMMUNITIES, 'Threatened Communities'),
    )

    SCOPE_WESTERN_AUSTRALIA = 0
    SCOPE_COMMONWEALTH = 1
    SCOPE_INTERNATIONAL = 2
    SCOPE_ACTION_PLAN = 3

    SCOPES = (
        (SCOPE_WESTERN_AUSTRALIA, 'WA'),
        (SCOPE_COMMONWEALTH, 'CWTH'),
        (SCOPE_INTERNATIONAL, 'IUCN'),
        (SCOPE_ACTION_PLAN, 'AP'),
    )

    source = models.PositiveIntegerField(
        verbose_name=_("Data Source"),
        default=SOURCE_MANUAL_ENTRY,
        choices=SOURCES,
        help_text=_("Where was this record captured initially?"), )

    source_id = models.CharField(
        max_length=1000,
        blank=True, null=True,
        verbose_name=_("Source ID"),
        help_text=_("The ID of the record in the original source, if available."), )

    scope = models.PositiveIntegerField(
        verbose_name=_("Scope"),
        default=SCOPE_WESTERN_AUSTRALIA,
        choices=SCOPES,
        help_text=_("In which legislation does this Gazettal apply?"), )

    # Conservation status
    category = models.ManyToManyField(
        ConservationCategory,
        blank=True,
        verbose_name=_("Conservation Categories"),
        help_text=_("The Conservation Categories can change during the approval process."
                    " Some combinations are valid, some are not."),
    )

    criteria = models.ManyToManyField(
        ConservationCriterion,
        blank=True,
        verbose_name=_("Conservation Criteria"),
        help_text=_("The Conservation Criteria form the reason "
                    "for the choice of conservation categories."),
    )

    # Approval status
    status = FSMIntegerField(
        choices=APPROVAL_STATUS,
        default=STATUS_PROPOSED,
        db_index=True,
        verbose_name=_("Approval status"),
        help_text=_("The approval status of the Conservation Listing."),
    )

    # Approval milestones
    proposed_on = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("Proposed on"),
        help_text=_("The date and time this Conservation Listing was proposed on."),
    )

    effective_from = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("Effective from"),
        help_text=_("The date printed on the Departmental Gazettal notice "
                    "containing this Conservation Listing."),
    )

    effective_to = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("Effective to"),
        help_text=_("The date and time this Conservation Listing was de-listed or "
                    "otherwise ceased to be in effect."),
    )

    last_reviewed_on = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("Last reviewed on"),
        help_text=_("The date and time this Conservation Listing was last reviewed."),
    )

    review_due = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("Review due date"),
        help_text=_("The date and time this Conservation Listing should be reviewed."),
    )

    # Approval process log
    comments = models.TextField(
        blank=True, null=True,
        verbose_name=_("Comments"),
        help_text=_("Append comments on approval process as appropriate."),
    )

    # Cache fields
    category_cache = models.TextField(
        blank=True, null=True,
        verbose_name=_("Category list"),
        help_text=_("An auto-generated list of conservation categories."),
    )

    criteria_cache = models.TextField(
        blank=True, null=True,
        verbose_name=_("Criteria list"),
        help_text=_("An auto-generated list of conservation criteria."),
    )

    label_cache = models.TextField(
        blank=True, null=True,
        verbose_name=_("Gazettal label"),
        help_text=_("An auto-generated label for the Conservation Listing."),
    )

    objects = models.Manager()
    active = ActiveGazettalManager()

    class Meta:
        """Class opts."""

        abstract = True

    def __str__(self):
        """The full name."""
        return unicode(self.pk)

    # -------------------------------------------------------------------------
    # URLs
    @property
    def absolute_admin_url(self):
        """Return the absolute admin change URL."""
        return reverse('admin:{0}_{1}_change'.format(
            self._meta.app_label, self._meta.model_name), args=[self.pk])

    @property
    def absolute_admin_add_url(self):
        """Return the absolute admin add URL."""
        return reverse('admin:{0}_{1}_add'.format(
            self._meta.app_label, self._meta.model_name))

    # -------------------------------------------------------------------------
    # Derived properties
    @property
    def build_category_cache(self):
        """Build a string of all attached categories."""
        return ", ".join([c.__str__() for c in self.category.all()])

    @property
    def build_criteria_cache(self):
        """Build a string of all attached criteria."""
        return ", ".join([c.code for c in self.criteria.all()])

    @property
    def build_label_cache(self):
        """Return the category and criteria cache."""
        return "{0} {1}".format(
            self.get_scope_display(),
            self.build_category_cache
        ).strip()

    @property
    def max_approval_level(self):
        """Return the highest required approval level of all categories."""
        try:
            return max([c.conservation_list.approval_level
                        for c in self.category.all()])
        except ValueError:
            return 0

    @property
    def is_active(self):
        """Return True if status currently in effect."""
        return self.status == Gazettal.STATUS_EFFECTIVE

    # ------------------------------------------------------------------------#
    # Django-FSM transitions
    # ALL -> STATUS_PROPOSED -------------------------------------------------#
    def can_recall_to_proposed(self):
        """Allow always to reset to the initial status."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source=[STATUS_IN_EXPERT_REVIEW,
                STATUS_IN_PUBLIC_REVIEW,
                STATUS_IN_PANEL_REVIEW,
                STATUS_IN_BM_REVIEW,
                STATUS_IN_DIR_REVIEW,
                STATUS_IN_DG_REVIEW,
                STATUS_IN_MIN_REVIEW,
                STATUS_EFFECTIVE,
                STATUS_CLOSED,
                STATUS_REJECTED],
        target=STATUS_PROPOSED,
        conditions=[can_recall_to_proposed],
        # permission='conservation.can_recall_to_proposed'
    )
    def recall_to_proposed(self):
        """Reset a new Gazettal to status "new" (proposed).

        This transition allows to reset any Gazettal to status "new"
        (before any endorsement) to start over freshly.
        This operation is equivalent to starting a new Gazettal.

        Source: all but STATUS_PROPOSED
        Target: STATUS_PROPOSED
        Permissions: staff
        Gatecheck: can_recall_to_proposed (pass)
        """
        logger.info("[Gazettal status] recall_to_proposed")

    # STATUS_PROPOSED -> STATUS_IN_EXPERT_REVIEW -----------------------------#
    def can_submit_for_expert_review(self):
        """Require if any categories are of min approval level APPROVAL_PANEL."""
        return self.max_approval_level >= ConservationList.APPROVAL_PANEL

    @fsm_log_by
    @transition(
        field=status,
        source=STATUS_PROPOSED,
        target=STATUS_IN_EXPERT_REVIEW,
        conditions=[can_submit_for_expert_review],
        # permission='conservation.can_submit_for_expert_review'
    )
    def submit_for_expert_review(self):
        """Submit a new Gazettal for expert review.

        Source: STATUS_PROPOSED
        Target: STATUS_IN_EXPERT_REVIEW
        Permissions: curators
        Gatecheck: At least one category requires panel approval
        """
        logger.info("[Gazettal status] submit_for_expert_review")

    # PROPOSED / IN_EXPERT_REVIEW -> STATUS_IN_PUBLIC_REVIEW -----------------#
    def can_submit_for_public_review(self):
        """Only categories of max approval level APPROVAL_PANEL require this step."""
        return self.max_approval_level >= ConservationList.APPROVAL_PANEL

    @fsm_log_by
    @transition(
        field=status,
        source=[STATUS_PROPOSED, STATUS_IN_EXPERT_REVIEW],
        target=STATUS_IN_PUBLIC_REVIEW,
        conditions=[can_submit_for_public_review],
        # permission='conservation.can_submit_for_expert_review'
    )
    def submit_for_public_review(self):
        """Submit a new Gazettal for public review.

        Source: STATUS_PROPOSED, STATUS_IN_EXPERT_REVIEW
        Target: STATUS_IN_PUBLIC_REVIEW
        Permissions: curators
        Gatecheck: At least one category requires panel approval
        """
        logger.info("[Gazettal status] submit_for_public_review")

    # STATUS_PROPOSED, STATUS_IN_EXPERT_REVIEW, STATUS_IN_PUBLIC_REVIEW ->
    # STATUS_IN_PANEL_REVIEW  ------------------------------------------------#
    def can_submit_for_panel_review(self):
        """Only categories of max approval level APPROVAL_PANEL require this step."""
        return self.max_approval_level >= ConservationList.APPROVAL_PANEL

    @fsm_log_by
    @transition(
        field=status,
        source=[STATUS_PROPOSED, STATUS_IN_EXPERT_REVIEW, STATUS_IN_PUBLIC_REVIEW],
        target=STATUS_IN_PANEL_REVIEW,
        conditions=[can_submit_for_panel_review],
        # permission='conservation.can_submit_for_panel_review'
    )
    def submit_for_panel_review(self):
        """Submit a new Gazettal for panel review.

        A proposed review can optionally go to an expert, to the public,
        or go directly for panel review.

        Source: STATUS_PROPOSED, STATUS_IN_EXPERT_REVIEW, STATUS_IN_PUBLIC_REVIEW
        Target: STATUS_IN_PANEL_REVIEW
        Permissions: curators
        Gatecheck: At least one category requires panel approval
        """
        logger.info("[Gazettal status] submit_for_panel_review")

    # STATUS_IN_PANEL_REVIEW -> STATUS_IN_BM_REVIEW --------------------------#
    def can_submit_for_bm_review(self):
        """Only categories of approval level APPROVAL_MINISTER require this step."""
        return self.max_approval_level == ConservationList.APPROVAL_MINISTER

    @fsm_log_by
    @transition(
        field=status,
        source=STATUS_IN_PANEL_REVIEW,
        target=STATUS_IN_BM_REVIEW,
        conditions=[can_submit_for_panel_review],
        # permission='conservation.submit_for_bm_review'
    )
    def submit_for_bm_review(self):
        """Submit a new Gazettal for Branch Manager review once panel endorses.

        Source: STATUS_IN_PANEL_REVIEW
        Target: STATUS_IN_BM_REVIEW
        Permissions: curators
        Gatecheck: At least one category requires ministerial approval
        """
        logger.info("[Gazettal status] submit_for_bm_review")

    # STATUS_IN_BM_REVIEW -> STATUS_IN_DIR_REVIEW ----------------------------#
    def can_submit_for_dir_review(self):
        """Only categories of approval level APPROVAL_MINISTER require this step."""
        return self.max_approval_level == ConservationList.APPROVAL_MINISTER

    @fsm_log_by
    @transition(
        field=status,
        source=STATUS_IN_BM_REVIEW,
        target=STATUS_IN_DIR_REVIEW,
        conditions=[can_submit_for_dir_review],
        # permission='conservation.can_submit_for_dir_review'
    )
    def submit_for_director_review(self):
        """Submit a new Gazettal for Dir BCS review once BM endorses.

        Source: STATUS_IN_BM_REVIEW
        Target: STATUS_IN_DIR_REVIEW
        Permissions: curators
        Gatecheck: At least one category requires ministerial approval
        """
        logger.info("[Gazettal status] submit_for_director_review")

    # STATUS_IN_DIR_REVIEW -> STATUS_IN_DG_REVIEW ----------------------------#
    def can_submit_for_dg_review(self):
        """Only categories of approval level APPROVAL_MINISTER require this step."""
        return self.max_approval_level == ConservationList.APPROVAL_MINISTER

    @fsm_log_by
    @transition(
        field=status,
        source=STATUS_IN_DIR_REVIEW,
        target=STATUS_IN_DG_REVIEW,
        conditions=[can_submit_for_dg_review],
        # permission='conservation.can_submit_for_dg_review'
    )
    def submit_for_director_general_review(self):
        """Submit a new Gazettal for DG review once Director endorses.

        Source: STATUS_IN_DIR_REVIEW
        Target: STATUS_IN_DG_REVIEW
        Permissions: curators
        Gatecheck: At least one category requires ministerial approval
        """
        logger.info("[Gazettal status] submit_for_director_general_review")

    # STATUS_IN_DG_REVIEW -> STATUS_IN_MIN_REVIEW ----------------------------#
    def can_submit_for_minister_review(self):
        """Only categories of approval level APPROVAL_MINISTER require this step."""
        return self.max_approval_level == ConservationList.APPROVAL_MINISTER

    @fsm_log_by
    @transition(
        field=status,
        source=STATUS_IN_DG_REVIEW,
        target=STATUS_IN_MIN_REVIEW,
        conditions=[can_submit_for_minister_review],
        # permission='conservation.can_submit_for_dg_review'
    )
    def submit_for_minister_review(self):
        """Submit a new Gazettal for DG review once Director endorses.

        Source: STATUS_IN_DG_REVIEW
        Target: STATUS_IN_MIN_REVIEW
        Permissions: curators
        Gatecheck: At least one category requires ministerial approval
        """
        logger.info("[Gazettal status] submit_for_minister_review")

    # ALL -> STATUS_EFFECTIVE -------------------------------------------------#
    def can_mark_gazetted(self):
        """Gatecheck for mark_gazetted."""
        return True

    # @fsm_log_by
    # @transition(
    #     field=status,
    #     source='*',
    #     target=STATUS_EFFECTIVE,
    #     conditions=[can_mark_gazetted],
    #     # permission='conservation.can_mark_gazetted'
    # )
    # def mark_gazetted(self):
    #     """Mark a conservation listing as gazetted.

    #     This transition allows any source status to fast-track any Gazettal.

    #     Source: all but STATUS_EFFECTIVE
    #     Target: STATUS_EFFECTIVE
    #     Permissions: curators
    #     Gatecheck: can_mark_gazetted (pass)
    #     """
    #     logger.info("[Gazettal status] you should override this method to "
    #                 "close other Tax/ComGazettals in same scope.")

    # STATUS_* -> STATUS_CLOSED ----------------------------------------------#
    def can_mark_delisted(self):
        """Gatecheck for mark_delisted."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source=[STATUS_PROPOSED,
                STATUS_IN_EXPERT_REVIEW,
                STATUS_IN_PUBLIC_REVIEW,
                STATUS_IN_PANEL_REVIEW,
                STATUS_IN_BM_REVIEW,
                STATUS_IN_DIR_REVIEW,
                STATUS_IN_DG_REVIEW,
                STATUS_IN_MIN_REVIEW,
                STATUS_EFFECTIVE],
        target=STATUS_CLOSED,
        conditions=[can_mark_delisted],
        # permission='conservation.can_mark_delisted'
    )
    def mark_delisted(self, by=None):
        """Mark a conservation listing as de-listed.

        This can either happen if a new conservation listing is gazetted,
        or if a conservation listing is de-listed without a superseding new listing.

        Source: all
        Target: STATUS_CLOSED
        Permissions: curators
        Gatecheck: can_mark_delisted (pass)
        """
        logger.info("[Gazettal status] mark_delisted")

    # STATUS_* -> STATUS_CLOSED ----------------------------------------------#
    def can_mark_rejected(self):
        """Gatecheck for mark_rejected."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source=[STATUS_PROPOSED,
                STATUS_IN_EXPERT_REVIEW,
                STATUS_IN_PUBLIC_REVIEW,
                STATUS_IN_PANEL_REVIEW,
                STATUS_IN_BM_REVIEW,
                STATUS_IN_DIR_REVIEW,
                STATUS_IN_DG_REVIEW,
                STATUS_IN_MIN_REVIEW],
        target=STATUS_REJECTED,
        conditions=[can_mark_rejected],
        # permission='conservation.can_mark_rejected'
    )
    def mark_rejected(self):
        """Mark a conservation listing as rejected.

        This can happen in any review stage.

        Source: all review stages
        Target: STATUS_REJECTED
        Permissions: curators
        Gatecheck: can_mark_rejected (pass)
        """
        logger.info("[Gazettal status] mark_rejected")

    # end Django-FSM
    # ------------------------------------------------------------------------#


@python_2_unicode_compatible
class TaxonGazettal(Gazettal):
    """The Gazettal of a ConservationCategory against a Taxon.

    There can only be one Gazettal per scope.
    Transition to "gazetted" shall close any other Gazettals of same scope.
    """

    taxon = models.ForeignKey(Taxon,
                              on_delete=models.CASCADE,
                              related_name="taxon_gazettal")

    class Meta:
        """Class opts."""

        verbose_name = "Taxon Conservation Listing"
        verbose_name_plural = "Taxon Conservation Listings"

    def __str__(self):
        """The full name."""
        return "{0} {1} {2} {3}".format(
            self.get_scope_display(),
            self.taxon,
            self.category_cache,
            self.criteria_cache
        ).strip()

    # -------------------------------------------------------------------------
    # URLs
    @property
    def absolute_admin_url(self):
        """Return the absolute admin change URL."""
        return reverse('admin:{0}_{1}_change'.format(
            self._meta.app_label, self._meta.model_name), args=[self.pk])

    def get_absolute_url(self):
        """Detail url."""
        return self.taxon.get_absolute_url()

    # -------------------------------------------------------------------------
    # Transitions
    @fsm_log_by
    @transition(
        field='status',
        source=[Gazettal.STATUS_PROPOSED,
                Gazettal.STATUS_IN_EXPERT_REVIEW,
                Gazettal.STATUS_IN_PUBLIC_REVIEW,
                Gazettal.STATUS_IN_PANEL_REVIEW,
                Gazettal.STATUS_IN_BM_REVIEW,
                Gazettal.STATUS_IN_DIR_REVIEW,
                Gazettal.STATUS_IN_DG_REVIEW,
                Gazettal.STATUS_IN_MIN_REVIEW,
                Gazettal.STATUS_CLOSED],
        target=Gazettal.STATUS_EFFECTIVE,
        # conditions=[Gazettal.can_mark_gazetted],
        # permission='conservation.can_mark_gazetted'
    )
    def mark_gazetted(self):
        """Mark a conservation listing as gazetted.

        This transition allows any source status to fast-track any Gazettal.

        Source: all but STATUS_EFFECTIVE
        Target: STATUS_EFFECTIVE
        Permissions: curators
        Gatecheck: can_mark_gazetted (pass)
        """
        logger.info("[Taxon Gazettal] mark_gazetted should now mark older "
                    "Gazettals as de-listed.")
        # TODO fsm_log_by request.user if coming from request
        [gazettal.mark_delisted() for gazettal in
         self.taxon.taxon_gazettal.filter(
            scope=self.scope,
            status=Gazettal.STATUS_EFFECTIVE
        ).exclude(pk=self.pk)]
        # TODO: set fsm_log_by


@python_2_unicode_compatible
class CommunityGazettal(Gazettal):
    """The Gazettal of a ConservationCategory against a Community."""

    community = models.ForeignKey(Community,
                                  on_delete=models.CASCADE,
                                  related_name="community_gazettal")

    class Meta:
        """Class opts."""

        verbose_name = "Community Conservation Listing"
        verbose_name_plural = "Community Conservation Listings"

    def __str__(self):
        """The full name."""
        return "{0} {1} {2} {3}".format(
            self.get_scope_display(),
            self.community.code,
            self.category_cache,
            self.criteria_cache
        ).strip()

    # -------------------------------------------------------------------------
    # URLs
    @property
    def absolute_admin_url(self):
        """Return the absolute admin change URL."""
        return reverse('admin:{0}_{1}_change'.format(
            self._meta.app_label, self._meta.model_name), args=[self.pk])

    def get_absolute_url(self):
        """Detail url."""
        return self.community.get_absolute_url()

    # -------------------------------------------------------------------------
    # Transitions
    @fsm_log_by
    @transition(
        field='status',
        source=[Gazettal.STATUS_PROPOSED,
                Gazettal.STATUS_IN_EXPERT_REVIEW,
                Gazettal.STATUS_IN_PUBLIC_REVIEW,
                Gazettal.STATUS_IN_PANEL_REVIEW,
                Gazettal.STATUS_IN_BM_REVIEW,
                Gazettal.STATUS_IN_DIR_REVIEW,
                Gazettal.STATUS_IN_DG_REVIEW,
                Gazettal.STATUS_IN_MIN_REVIEW,
                Gazettal.STATUS_CLOSED],
        target=Gazettal.STATUS_EFFECTIVE,
        # conditions=[Gazettal.can_mark_gazetted],
        # permission='conservation.can_mark_gazetted'
    )
    def mark_gazetted(self):
        """Mark a conservation listing as gazetted.

        This transition allows any source status to fast-track any Gazettal.

        Source: all but STATUS_EFFECTIVE
        Target: STATUS_EFFECTIVE
        Permissions: curators
        Gatecheck: can_mark_gazetted (pass)
        """
        logger.info("[Community Gazettal] De-list previous "
                    "Gazettals in same scope.")
        [gazettal.mark_delisted() for gazettal in
         self.community.community_gazettal.filter(
            scope=self.scope,
            status=Gazettal.STATUS_EFFECTIVE
        ).exclude(pk=self.pk)]


@receiver(pre_save, sender=TaxonGazettal)
@receiver(pre_save, sender=CommunityGazettal)
def gazettal_caches(sender, instance, *args, **kwargs):
    """Gazettal: Cache expensive lookups."""
    if instance.pk:
        logger.info("[gazettal_caches] Updating cache fields.")
        instance.category_cache = instance.build_category_cache
        instance.criteria_cache = instance.build_criteria_cache
        instance.label_cache = instance.build_label_cache
    else:
        logger.info("[gazettal_caches] New Gazettal, re-save to populate caches.")


# -----------------------------------------------------------------------------
# Documents
@python_2_unicode_compatible
class Document(models.Model):
    """A Document with attachments and approval workflow."""

    TYPE_RECOVERY_PLAN = 0
    TYPE_INTERIM_RECOVERY_PLAN = 5
    TYPE_MANAGEMENT_PLAN = 10
    TYPE_ANIMAL_ETHICS = 20
    TYPE_FAUNA_TRANSLOCATION = 30
    TYPE_SOP = 40

    TYPES = (
        (TYPE_RECOVERY_PLAN, 'Recovery Plan'),
        (TYPE_INTERIM_RECOVERY_PLAN, 'Interim Recovery Plan'),
        (TYPE_MANAGEMENT_PLAN, 'Management Plan'),
        (TYPE_ANIMAL_ETHICS, 'Animal Ethics Application'),
        (TYPE_FAUNA_TRANSLOCATION, 'Fauna Translocation Proposal'),
        (TYPE_SOP, 'Standard Operating Procedure'),
    )

    STATUS_PROPOSED = 0
    STATUS_IN_EXPERT_REVIEW = 10
    STATUS_IN_PUBLIC_REVIEW = 20
    STATUS_IN_PANEL_REVIEW = 30
    STATUS_IN_BM_REVIEW = 40
    STATUS_IN_REGIONAL_REVIEW = 45
    STATUS_IN_DIR_REVIEW = 50
    STATUS_IN_DG_REVIEW = 60
    STATUS_IN_MIN_REVIEW = 70
    STATUS_EFFECTIVE = 80
    STATUS_ADOPTED_COMMONWEALTH = 85
    STATUS_CLOSED = 90
    STATUS_REJECTED = 100

    APPROVAL_STATUS = (
        (STATUS_PROPOSED, "Proposed"),
        (STATUS_IN_BM_REVIEW, "In review with Branch Manager"),
        (STATUS_IN_REGIONAL_REVIEW, "In review with Regional Manager"),
        (STATUS_IN_DIR_REVIEW, "In review with Division Director"),
        (STATUS_IN_PUBLIC_REVIEW, "In review with public"),
        (STATUS_IN_DG_REVIEW, "In review with Director General"),
        (STATUS_IN_MIN_REVIEW, "In review with Minister"),
        (STATUS_EFFECTIVE, "Active"),
        (STATUS_CLOSED, "Closed"),
        (STATUS_REJECTED, "Rejected"),
    )

    SOURCE_MANUAL_ENTRY = 0
    SOURCE_THREATENED_FAUNA = 1
    SOURCE_THREATENED_FLORA = 2
    SOURCE_THREATENED_COMMUNITIES = 3

    SOURCES = (
        (SOURCE_MANUAL_ENTRY, 'Manual entry'),
        (SOURCE_THREATENED_FAUNA, 'Threatened Fauna'),
        (SOURCE_THREATENED_FLORA, 'Threatened Flora'),
        (SOURCE_THREATENED_COMMUNITIES, 'Threatened Communities'),
    )

    source = models.PositiveIntegerField(
        verbose_name=_("Data Source"),
        default=SOURCE_MANUAL_ENTRY,
        choices=SOURCES,
        help_text=_("Where was this record captured initially?"), )

    source_id = models.CharField(
        max_length=1000,
        blank=True, null=True,
        verbose_name=_("Source ID"),
        help_text=_("The ID of the record in the original source, if available."), )

    taxa = models.ManyToManyField(
        Taxon,
        blank=True,
        verbose_name=_("Taxa"),
        help_text=_("All taxa this document applies to."),
    )

    communities = models.ManyToManyField(
        Community,
        blank=True,
        verbose_name=_("Communities"),
        help_text=_("All communities this document applies to."),
    )

    document_type = models.PositiveIntegerField(
        verbose_name=_("Document Type"),
        choices=TYPES,
        default=TYPE_RECOVERY_PLAN,
        help_text=_("The document type governs the approval process."), )

    # Approval status
    status = FSMIntegerField(
        choices=APPROVAL_STATUS,
        default=STATUS_PROPOSED,
        db_index=True,
        verbose_name=_("Approval status"),
        help_text=_("The approval status of the Gazettal."),
    )

    effective_from = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("Effective from"),
        help_text=_("The date from which this document is effective from."),
    )

    effective_to = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("Effective to"),
        help_text=_("The date to which this document is effective to."),
    )

    effective_from_commonwealth = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("Adopted by Commonwealth on"),
        help_text=_("The date from which this document was adopted by the Commonwealth."),
    )

    effective_to_commonwealth = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("Retired by Commonwealth on"),
        help_text=_("The date on which this document was retired by the Commonwealth."),
    )

    review_due = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("Review due date"),
        help_text=_("The date and time this Document should be reviewed."),
    )

    last_reviewed_on = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("Last reviewed on"),
        help_text=_("The date and time this Conservation Listing was last reviewed."),
    )

    # year
    # number

    title = models.CharField(
        max_length=1000,
        verbose_name=_("Title"),
        help_text=_("A concise document title."),
    )

    comments = models.TextField(
        blank=True, null=True,
        verbose_name=_("Comments"),
        help_text=_("Optional comments on document approval and provenance."),
    )

    team = models.ManyToManyField(
        User,
        blank=True,
        verbose_name=_("Staff involved in the writing, approval, "
                       "or publication of this document."),
    )

    attachments = GenericRelation(FileAttachment, object_id_field="object_id")

    class Meta:
        """Class opts."""

        ordering = ["document_type", "title"]
        verbose_name = "Document"
        verbose_name_plural = "Documents"

    def __str__(self):
        """The full name."""
        return "[{0}] {1}".format(self.get_document_type_display(), self.title)

    # -------------------------------------------------------------------------
    # URLs
    # def get_absolute_url(self):
    #     """Detail url."""
    #     return "/"

    @property
    def absolute_admin_url(self):
        """Return the absolute admin change URL."""
        return reverse('admin:{0}_{1}_change'.format(
            self._meta.app_label, self._meta.model_name), args=[self.pk])

    # ------------------------------------------------------------------------#
    # Django-FSM transitions
    # ALL -> STATUS_PROPOSED -------------------------------------------------#
    def can_recall_to_proposed(self):
        """Allow always to reset to the initial status."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source=[STATUS_IN_EXPERT_REVIEW,
                STATUS_IN_PUBLIC_REVIEW,
                STATUS_IN_PANEL_REVIEW,
                STATUS_IN_BM_REVIEW,
                STATUS_IN_DIR_REVIEW,
                STATUS_IN_DG_REVIEW,
                STATUS_IN_MIN_REVIEW,
                STATUS_EFFECTIVE,
                STATUS_CLOSED,
                STATUS_REJECTED],
        target=STATUS_PROPOSED,
        conditions=[can_recall_to_proposed],
        # permission='conservation.can_recall_to_proposed'
    )
    def recall_to_proposed(self):
        """Reset a new Gazettal to status "new" (proposed).

        This transition allows to reset any Gazettal to status "new"
        (before any endorsement) to start over freshly.
        This operation is equivalent to starting a new Gazettal.

        Source: all but STATUS_PROPOSED
        Target: STATUS_PROPOSED
        Permissions: staff
        Gatecheck: can_recall_to_proposed (pass)
        """
        logger.info("[Gazettal status] recall_to_proposed")

    # STATUS_PROPOSED -> STATUS_IN_EXPERT_REVIEW -----------------------------#
    def can_submit_for_expert_review(self):
        """Require if any categories are of min approval level APPROVAL_PANEL."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source=STATUS_PROPOSED,
        target=STATUS_IN_EXPERT_REVIEW,
        conditions=[can_submit_for_expert_review],
        # permission='conservation.can_submit_for_expert_review'
    )
    def submit_for_expert_review(self):
        """Submit a new Gazettal for expert review.

        Source: STATUS_PROPOSED
        Target: STATUS_IN_EXPERT_REVIEW
        Permissions: curators
        Gatecheck: At least one category requires panel approval
        """
        logger.info("[Gazettal status] submit_for_expert_review")

    # PROPOSED / IN_EXPERT_REVIEW -> STATUS_IN_PUBLIC_REVIEW -----------------#
    def can_submit_for_public_review(self):
        """Only categories of max approval level APPROVAL_PANEL require this step."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source=[STATUS_PROPOSED, STATUS_IN_EXPERT_REVIEW],
        target=STATUS_IN_PUBLIC_REVIEW,
        conditions=[can_submit_for_public_review],
        # permission='conservation.can_submit_for_expert_review'
    )
    def submit_for_public_review(self):
        """Submit a new Gazettal for public review.

        Source: STATUS_PROPOSED, STATUS_IN_EXPERT_REVIEW
        Target: STATUS_IN_PUBLIC_REVIEW
        Permissions: curators
        Gatecheck: At least one category requires panel approval
        """
        logger.info("[Gazettal status] submit_for_public_review")

    # STATUS_PROPOSED, STATUS_IN_EXPERT_REVIEW, STATUS_IN_PUBLIC_REVIEW ->
    # STATUS_IN_PANEL_REVIEW  ------------------------------------------------#
    def can_submit_for_panel_review(self):
        """Only categories of max approval level APPROVAL_PANEL require this step."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source=[STATUS_PROPOSED, STATUS_IN_EXPERT_REVIEW, STATUS_IN_PUBLIC_REVIEW],
        target=STATUS_IN_PANEL_REVIEW,
        conditions=[can_submit_for_panel_review],
        # permission='conservation.can_submit_for_panel_review'
    )
    def submit_for_panel_review(self):
        """Submit a new Gazettal for panel review.

        A proposed review can optionally go to an expert, to the public,
        or go directly for panel review.

        Source: STATUS_PROPOSED, STATUS_IN_EXPERT_REVIEW, STATUS_IN_PUBLIC_REVIEW
        Target: STATUS_IN_PANEL_REVIEW
        Permissions: curators
        Gatecheck: At least one category requires panel approval
        """
        logger.info("[Gazettal status] submit_for_panel_review")

    # STATUS_IN_PANEL_REVIEW -> STATUS_IN_BM_REVIEW --------------------------#
    def can_submit_for_bm_review(self):
        """Only categories of approval level APPROVAL_MINISTER require this step."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source=STATUS_IN_PANEL_REVIEW,
        target=STATUS_IN_BM_REVIEW,
        conditions=[can_submit_for_panel_review],
        # permission='conservation.submit_for_bm_review'
    )
    def submit_for_bm_review(self):
        """Submit a new Gazettal for Branch Manager review once panel endorses.

        Source: STATUS_IN_PANEL_REVIEW
        Target: STATUS_IN_BM_REVIEW
        Permissions: curators
        Gatecheck: At least one category requires ministerial approval
        """
        logger.info("[Gazettal status] submit_for_bm_review")

    # STATUS_IN_BM_REVIEW -> STATUS_IN_DIR_REVIEW ----------------------------#
    def can_submit_for_dir_review(self):
        """Only categories of approval level APPROVAL_MINISTER require this step."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source=STATUS_IN_BM_REVIEW,
        target=STATUS_IN_DIR_REVIEW,
        conditions=[can_submit_for_dir_review],
        # permission='conservation.can_submit_for_dir_review'
    )
    def submit_for_director_review(self):
        """Submit a new Gazettal for Dir BCS review once BM endorses.

        Source: STATUS_IN_BM_REVIEW
        Target: STATUS_IN_DIR_REVIEW
        Permissions: curators
        Gatecheck: At least one category requires ministerial approval
        """
        logger.info("[Gazettal status] submit_for_director_review")

    # STATUS_IN_DIR_REVIEW -> STATUS_IN_DG_REVIEW ----------------------------#
    def can_submit_for_dg_review(self):
        """Only categories of approval level APPROVAL_MINISTER require this step."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source=STATUS_IN_DIR_REVIEW,
        target=STATUS_IN_DG_REVIEW,
        conditions=[can_submit_for_dg_review],
        # permission='conservation.can_submit_for_dg_review'
    )
    def submit_for_director_general_review(self):
        """Submit a new Gazettal for DG review once Director endorses.

        Source: STATUS_IN_DIR_REVIEW
        Target: STATUS_IN_DG_REVIEW
        Permissions: curators
        Gatecheck: At least one category requires ministerial approval
        """
        logger.info("[Gazettal status] submit_for_director_general_review")

    # STATUS_IN_DG_REVIEW -> STATUS_IN_MIN_REVIEW ----------------------------#
    def can_submit_for_minister_review(self):
        """Only categories of approval level APPROVAL_MINISTER require this step."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source=STATUS_IN_DG_REVIEW,
        target=STATUS_IN_MIN_REVIEW,
        conditions=[can_submit_for_minister_review],
        # permission='conservation.can_submit_for_dg_review'
    )
    def submit_for_minister_review(self):
        """Submit a new Gazettal for DG review once Director endorses.

        Source: STATUS_IN_DG_REVIEW
        Target: STATUS_IN_MIN_REVIEW
        Permissions: curators
        Gatecheck: At least one category requires ministerial approval
        """
        logger.info("[Gazettal status] submit_for_minister_review")

    # ALL -> STATUS_EFFECTIVE -------------------------------------------------#
    def can_mark_gazetted(self):
        """Gatecheck for mark_gazetted."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source='*',
        target=STATUS_EFFECTIVE,
        conditions=[can_mark_gazetted],
        # permission='conservation.can_mark_gazetted'
    )
    def mark_active(self):
        """Mark a Document as approved and active.

        This transition allows any source status to fast-track any Document.

        Source: all but STATUS_EFFECTIVE
        Target: STATUS_EFFECTIVE
        Permissions: curators
        Gatecheck: can_mark_gazetted (pass)
        """
        logger.info("[Gazettal status] you should override this method to "
                    "close other Tax/ComGazettals in same scope.")

    # STATUS_* -> STATUS_CLOSED ----------------------------------------------#
    def can_mark_delisted(self):
        """Gatecheck for mark_delisted."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source=[STATUS_PROPOSED,
                STATUS_IN_EXPERT_REVIEW,
                STATUS_IN_PUBLIC_REVIEW,
                STATUS_IN_PANEL_REVIEW,
                STATUS_IN_BM_REVIEW,
                STATUS_IN_DIR_REVIEW,
                STATUS_IN_DG_REVIEW,
                STATUS_IN_MIN_REVIEW,
                STATUS_EFFECTIVE],
        target=STATUS_CLOSED,
        conditions=[can_mark_delisted],
        # permission='conservation.can_mark_delisted'
    )
    def mark_closed(self):
        """Mark a Document as closed.

        Source: all
        Target: STATUS_CLOSED
        Permissions: curators
        Gatecheck: can_mark_delisted (pass)
        """
        logger.info("[Gazettal status] mark_inactive")

    # STATUS_EFFECTIVE -> STATUS_ADOPTED_COMMONWEALTH
    # TODO

    # STATUS_* -> STATUS_CLOSED ----------------------------------------------#
    def can_mark_rejected(self):
        """Gatecheck for mark_rejected."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source=[STATUS_PROPOSED,
                STATUS_IN_EXPERT_REVIEW,
                STATUS_IN_PUBLIC_REVIEW,
                STATUS_IN_PANEL_REVIEW,
                STATUS_IN_BM_REVIEW,
                STATUS_IN_DIR_REVIEW,
                STATUS_IN_DG_REVIEW,
                STATUS_IN_MIN_REVIEW],
        target=STATUS_REJECTED,
        conditions=[can_mark_rejected],
        # permission='conservation.can_mark_rejected'
    )
    def mark_rejected(self):
        """Mark a conservation listing as rejected.

        This can happen in any review stage.

        Source: all review stages
        Target: STATUS_REJECTED
        Permissions: curators
        Gatecheck: can_mark_rejected (pass)
        """
        logger.info("[Gazettal status] mark_rejected")

    # end Django-FSM
    # ------------------------------------------------------------------------#
