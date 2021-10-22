# -*- coding: utf-8 -*-
"""Shared models."""
from __future__ import absolute_import, unicode_literals

# import itertools
import logging
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import options
# from django.template import loader, TemplateDoesNotExist
from django.urls import reverse
from django.utils.safestring import mark_safe  # noqa
from django.utils.translation import ugettext_lazy as _
# from durationfield.db.models.fields.duration import DurationField
# from django.db.models.fields import DurationField
from django_fsm import FSMField, transition
from django_fsm_log.decorators import fsm_log_by

# from wastd.users.models import User

# import urllib
# import slugify
# from datetime import timedelta
# from dateutil import tz

# from django.utils.safestring import mark_safe

# from django_fsm_log.models import StateLog
# from polymorphic.models import PolymorphicModel


logger = logging.getLogger(__name__)

# Instantiated models --------------------------------------------------------#


# Abstract models ------------------------------------------------------------#
class CodeLabelDescriptionMixin(models.Model):
    """A Mixin providing code, label and description."""

    code = models.SlugField(
        max_length=500,
        unique=True,
        verbose_name=_("Code"),
        help_text=_("A unique, url-safe code."),
    )

    label = models.CharField(
        blank=True, null=True,
        max_length=500,
        verbose_name=_("Label"),
        help_text=_("A human-readable, self-explanatory label."),
    )

    description = models.TextField(
        blank=True, null=True,
        verbose_name=_("Description"),
        help_text=_("A comprehensive description."),
    )

    class Meta:
        """Class opts."""

        abstract = True
        ordering = ["code", ]

    def __str__(self):
        """The full name."""
        return self.label

    # -------------------------------------------------------------------------
    # URLs
    @property
    def absolute_admin_url(self):
        """Return the absolute admin change URL."""
        return reverse('admin:{0}_{1}_change'.format(
            self._meta.app_label, self._meta.model_name), args=[self.pk])


# For RenderMixin: add Meta fields
options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('card_template', 'latex_template')


class RenderMixin(models.Model):
    """A mixin providing a rendered representation as card, as popup and as latex.

    Model options are made accessible as property self.opts.
    This allows to include e.g. the path to a template, such as ``card_template``.

    Helper functions ``as_card``, ``as_latex`` render the model
    through the respective templates and return the HTML or Latex source code as safe string.

    The template are expected at

    Provides a standard template path ``<app_label>/{card, latex}/model_name.{html,tex}``.
    Use in templates with

    {% include object.card_template %}
    """

    class Meta:
        """Class opts."""

        abstract = True

    @property
    def opts(self):
        """Return model options."""
        return self._meta

    # def do_render(self, template_type="cards", path=None):
    #     """Render a template to a safe string."""
    #     if path is None:
    #         if getattr(self.opts, "card_template", None):
    #             path = self.opts.card_template
    #         else:
    #             path = "{0}/{1}/{2}.html".format(
    #                 self.opts.app_label,
    #                 template_type,
    #                 self.opts.model_name)
    #     try:
    #         template = loader.get_template(path)
    #     except TemplateDoesNotExist:
    #         msg = "Missing template {0} for {1}".format(path, self.__str__())
    #         return mark_safe(msg)
    #     return mark_safe(template.render({"object": self}))

    # @property
    # def as_card(self, path=None):
    #     """Return as rendered HTML card."""
    #     return self.do_render(template_type="cards", path=path)

    # @property
    # def as_latex(self, path=None):
    #     """Return as Latex source."""
    #     return self.do_render(template_type="latex", path=path)

    @property
    def card_template(self):
        """The standard card template path is app_label/cards/model_name.html."""
        return "{0}/cards/{1}.html".format(
            self.opts.app_label,
            self.opts.model_name)

    @property
    def latex_template(self):
        """The standard latex template path is app_label/latex/model_name.html."""
        return "{0}/latex/{1}.html".format(
            self.opts.app_label,
            self.opts.model_name)


class UrlsMixin(models.Model):
    """Mixin class to add absolute admin, list, update and detail urls.

    To use, inherit from UrlsMixin and define a custom get_absolute_url(),
    plus any of list/create/update url not following the standard
    {app}:{model}-{action}(**pk) scheme defined in the methods in this mixin.

    This mixin provides the following URLs:

    * absolute_admin_url()
    * get_absolute_url() - available in templates as object.get_absolute_url
    * list_url (classmethod)
    * create_url (classmethod)
    * update_url
    """

    class Meta:
        """Class opts."""

        abstract = True

    # -------------------------------------------------------------------------
    # URLs
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

    @classmethod
    def create_url(cls):
        """Create url. Default: app:model-create."""
        return reverse('{0}:{1}-create'.format(
            cls._meta.app_label, cls._meta.model_name))

    @property
    def update_url(self):
        """Update url. Default: app:model-update(**pk)."""
        return reverse('{0}:{1}-update'.format(
            self._meta.app_label, self._meta.model_name),
            kwargs={'pk': self.pk})


class ObservationAuditMixin(models.Model):
    """Mixin class to track observer and observation date."""

    encountered_on = models.DateTimeField(
        verbose_name=_("Encountered on"),
        blank=True, null=True,
        db_index=True,
        help_text=_("The datetime of the original encounter, "
                    "entered in the local time zone GMT+08 (Perth/Australia)."))

    encountered_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        verbose_name=_("Encountered by"),
        blank=True, null=True,
        help_text=_("The person who experienced the original encounter. "
                    "DBCA staff have to visit this site to create a new profile. "
                    "Add User profiles for external people through the data curation portal."))

    class Meta:
        """Class opts."""

        abstract = True


def make_source_id():
    """Return a new uuid1."""
    return uuid.uuid1()

class LegacySourceMixin(models.Model):
    """Mixin class for Legacy source and source_id.

    Using this class allows a model to preserve a link to a legacy source.
    This is useful to make a data import repeatable by identifying which records
    to overwrite.
    """

    SOURCE_MANUAL_ENTRY = 0
    SOURCE_PAPER_DATASHEET = 1
    SOURCE_DIGITAL_CAPTURE_ODK = 2
    SOURCE_PARTIAL_SURVEY = 3
    SOURCE_THREATENED_FAUNA = 10
    SOURCE_THREATENED_FLORA = 11
    SOURCE_THREATENED_COMMUNITIES = 12
    SOURCE_THREATENED_COMMUNITIES_BOUNDARIES = 13
    SOURCE_THREATENED_COMMUNITIES_BUFFERS = 14
    SOURCE_THREATENED_COMMUNITIES_SITES = 15
    SOURCE_WAMTRAM2 = 20
    SOURCE_NINGALOO_TURTLE_PROGRAM = 21
    SOURCE_BROOME_TURTLE_PROGRAM = 22
    SOURCE_PORT_HEDLAND_TURTLE_PROGRAM = 23
    SOURCE_GNARALOO_TURTLE_PROGRAM = 24
    SOURCE_ECO_BEACH_TURTLE_PROGRAM = 25
    SOURCE_CETACEAN_STRANDINGS = 30
    SOURCE_PINNIPED_STRANDINGS = 31

    SOURCES = (
        (SOURCE_MANUAL_ENTRY, 'Direct entry'),
        (SOURCE_PAPER_DATASHEET, 'Manual entry from paper datasheet'),
        (SOURCE_DIGITAL_CAPTURE_ODK, 'Digital data capture (ODK)'),
        (SOURCE_PARTIAL_SURVEY, 'Partial survey'),
        (SOURCE_THREATENED_FAUNA, 'Threatened Fauna'),
        (SOURCE_THREATENED_FLORA, 'Threatened Flora'),
        (SOURCE_THREATENED_COMMUNITIES, 'Threatened Communities'),
        (SOURCE_THREATENED_COMMUNITIES_BOUNDARIES, 'Threatened Communities Boundaries'),
        (SOURCE_THREATENED_COMMUNITIES_BUFFERS, 'Threatened Communities Buffers'),
        (SOURCE_THREATENED_COMMUNITIES_SITES, 'Threatened Communities Sites'),
        (SOURCE_WAMTRAM2, "Turtle Tagging Database WAMTRAM2"),
        (SOURCE_NINGALOO_TURTLE_PROGRAM, "Ningaloo Turtle Program"),
        (SOURCE_BROOME_TURTLE_PROGRAM, "Broome Turtle Program"),
        (SOURCE_PORT_HEDLAND_TURTLE_PROGRAM, "Pt Hedland Turtle Program"),
        (SOURCE_GNARALOO_TURTLE_PROGRAM, "Gnaraloo Turtle Program"),
        (SOURCE_ECO_BEACH_TURTLE_PROGRAM, "Eco Beach Turtle Program"),
        (SOURCE_CETACEAN_STRANDINGS, "Cetacean Strandings Database"),
        (SOURCE_PINNIPED_STRANDINGS, "Pinniped Strandings Database"),
    )

    source = models.PositiveIntegerField(
        verbose_name=_("Data Source"),
        default=SOURCE_MANUAL_ENTRY,
        choices=SOURCES,
        help_text=_("Where was this record captured initially?"), )

    source_id = models.CharField(
        max_length=1000,
        default=make_source_id,
        verbose_name=_("Source ID"),
        help_text=_("The ID of the record in the original source, "
                    "if available, or a randomly generated UUID1."), )

    class Meta:
        """Class opts."""

        abstract = True
        unique_together = ("source", "source_id")


class QualityControlMixin(models.Model):
    """Mixin class for QA status levels with django-fsm transitions.

    Upcoming work: permissions https://github.com/dbca-wa/wastd/issues/291
    Related: https://github.com/dbca-wa/wastd/issues/299
    """

    STATUS_NEW = 'new'
    STATUS_PROOFREAD = 'proofread'
    STATUS_CURATED = 'curated'
    STATUS_PUBLISHED = 'published'
    STATUS_FLAGGED = 'flagged'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = (
        (STATUS_NEW, _("New")),
        (STATUS_PROOFREAD, _("Proofread")),
        (STATUS_CURATED, _("Curated")),
        (STATUS_PUBLISHED, _("Published")),
        (STATUS_FLAGGED, _("Flagged")),
        (STATUS_REJECTED, _("Rejected")),
    )

    STATUS_LABELS = {
        STATUS_NEW: "secondary",
        STATUS_PROOFREAD: "warning",
        STATUS_CURATED: "success",
        STATUS_PUBLISHED: "info",
        STATUS_FLAGGED: "warning",
        STATUS_REJECTED: "danger",
    }

    status = FSMField(
        default=STATUS_NEW,
        choices=STATUS_CHOICES,
        verbose_name=_("QA Status"))

    class Meta:
        """Class opts."""

        abstract = True

    @property
    def status_colour(self):
        """Return a Bootstrap4 CSS colour class for each status."""
        return self.STATUS_LABELS[self.status]


# FSM transitions --------------------------------------------------------#
    def can_proofread(self):
        """Return true if this document can be proofread."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source=STATUS_NEW,
        target=STATUS_PROOFREAD,
        conditions=[can_proofread],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Submit for QA",
            explanation=("Submit this record as a faithful representation of the "
                         "data source for QA to become an accepted record."),
            notify=True,)
    )
    def proofread(self, by=None):
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

    @fsm_log_by
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
    def require_proofreading(self, by=None):
        """Mark encounter as having typos, requiring more proofreading.

        Proofreading compares the attached data sheet with entered values.
        If a discrepancy to the data sheet is found, proofreading is required.
        """
        return

    def can_curate(self):
        """Return true if this record can be accepted."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source=[STATUS_NEW, STATUS_PROOFREAD, STATUS_FLAGGED],
        target=STATUS_CURATED,
        conditions=[can_curate],
        # permission=lambda instance, user: user in instance.all_permitted,

        custom=dict(
            verbose="Accept as trustworthy",
            explanation=("This record is deemed trustworthy."),
            notify=True,)
    )
    def curate(self, by=None):
        """Accept record as trustworthy.

        Curated data is deemed trustworthy by a subject matter expert.
        Records can be marked as curated from new, proofread, or flagged.
        """
        return

    def can_flag(self):
        """Return true if curated status can be revoked."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source=STATUS_CURATED,
        target=STATUS_FLAGGED,
        conditions=[can_flag],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Flag as not trustworthy",
            explanation=("This record cannot be true. This record requires"
                         " review by a subject matter expert."),
            notify=True,)
    )
    def flag(self, by=None):
        """Flag as requiring changes to data.

        Curated data is deemed trustworthy by a subject matter expert.
        Revoking curation flags data for requiring changes by an expert.
        """
        return

    def can_reject(self):
        """Return true if the record can be rejected as entirely wrong."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source=[STATUS_PROOFREAD, STATUS_CURATED, STATUS_FLAGGED],
        target=STATUS_REJECTED,
        conditions=[can_flag],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Confirm as not trustworthy",
            explanation=("This record is confirmed wrong and not trustworthy."),
            notify=True,)
    )
    def reject(self, by=None):
        """Confirm that a record is not trustworthy and beyond repair."""
        return


    def can_reset(self):
        """Return true if the record QA status can be reset."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source=STATUS_REJECTED,
        target=STATUS_NEW,
        conditions=[can_reset],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Reset QA status",
            explanation=("The QA status of this record needs to be reset."),
            notify=True,)
    )
    def reset(self, by=None):
        """Reset the QA status of a record to NEW.

        This allows a record to be brought into the desired QA status.
        """
        return

    def can_publish(self):
        """Return true if this document can be published."""
        return True

    @fsm_log_by
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
    def publish(self, by=None):
        """Mark encounter as ready to be published.

        Published data has been deemed fit for release by the data owner.
        """
        return

    def can_embargo(self):
        """Return true if encounter can be embargoed."""
        return True

    @fsm_log_by
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
    def embargo(self, by=None):
        """Mark encounter as NOT ready to be published.

        Published data has been deemed fit for release by the data owner.
        Embargoed data is marked as curated, but not ready for release.
        """
        return
