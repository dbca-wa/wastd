# -*- coding: utf-8 -*-
"""Conservation models."""
from __future__ import unicode_literals, absolute_import

# import itertools
# import urllib
# import slugify
# from datetime import timedelta
# from dateutil import tz
# import logging

# from django.core.urlresolvers import reverse
from django.db import models
# from django.db.models.signals import pre_save, post_save
# from django.dispatch import receiver
# from django.contrib.gis.db import models as geo_models
# from django.contrib.gis.db.models.query import GeoQuerySet
# from django.core.urlresolvers import reverse
# from rest_framework.reverse import reverse as rest_reverse
# from django.template import loader
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
# from django.utils.safestring import mark_safe

# from polymorphic.models import PolymorphicModel
# from durationfield.db.models.fields.duration import DurationField
# from django.db.models.fields import DurationField
from django_fsm import FSMField  # , transition
# from django_fsm_log.decorators import fsm_log_by
# from django_fsm_log.models import StateLog

from taxonomy.models import Taxon, Community


@python_2_unicode_compatible
class ConservationList(models.Model):
    """A Conservation List like BCA, EPBC, RedList."""

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
        verbose_name=_("Applies to WA"),
        help_text=_("Whether this list is applicable internationally."),
    )

    class Meta:
        """Class opts."""

        verbose_name = "Conservation List"
        verbose_name_plural = "Conservation Lists"

    def __str__(self):
        """The full name."""
        return self.code


@python_2_unicode_compatible
class ConservationCategory(models.Model):
    """A Conservation Category like CR, EN, VU."""

    conservation_list = models.ForeignKey(
        ConservationList,
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

    class Meta:
        """Class opts."""

        unique_together = ("conservation_list", "code")
        verbose_name = "Conservation Category"
        verbose_name_plural = "Conservation Categories"

    def __str__(self):
        """The full name."""
        return self.code


@python_2_unicode_compatible
class ConservationCriterion(models.Model):
    """A Conservation Criterion like A4a."""

    conservation_list = models.ForeignKey(
        ConservationList,
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

    class Meta:
        """Class opts."""

        unique_together = ("conservation_list", "code")
        verbose_name = "Conservation Criterion"
        verbose_name_plural = "Conservation Criteria"

    def __str__(self):
        """The full name."""
        return self.code


@python_2_unicode_compatible
class Gazettal(models.Model):
    """The allocation of a ConservationCategory.

    Approval state is tracked as django-fsm field.
    ConservationCategory can change during approval process.
    Inheritance can override transitions.

    Documents are attached as MediaAttachments.

    Some conservation categories are mutually exclusiver than others.
    To prevent invalid combinations of ConservationCategories,
    the transition to Gazettal.STATUS_GAZETTED must take care of
    closing just the mutually exclusive ones.
    """

    STATUS_PROPOSED = 0
    STATUS_IN_EXPERT_REVIEW = 10
    STATUS_IN_PUBLIC_REVIEW = 20
    STATUS_IN_PANEL_REVIEW = 30
    STATUS_IN_BM_REVIEW = 40
    STATUS_IN_DIV_REVIEW = 50
    STATUS_IN_DG_REVIEW = 60
    STATUS_IN_MIN_REVIEW = 70
    STATUS_GAZETTED = 80
    STATUS_INACVITE = 90

    APPROVAL_STATUS = (
        (STATUS_PROPOSED, "Proposed"),
        (STATUS_IN_EXPERT_REVIEW, "In review with experts"),
        (STATUS_IN_PUBLIC_REVIEW, "In review with public"),
        (STATUS_IN_PANEL_REVIEW, "In review with panel"),
        (STATUS_IN_BM_REVIEW, "In review with Branch Manager"),
        (STATUS_IN_DIV_REVIEW, "In review with Division Director"),
        (STATUS_IN_DG_REVIEW, "In review with Director General"),
        (STATUS_IN_MIN_REVIEW, "In review with Minister"),
        (STATUS_GAZETTED, "Gazetted"),
        (STATUS_INACVITE, "Inactive"),
    )

    # Conservation status
    category = models.ForeignKey(
        ConservationCategory,
        verbose_name=_("Conservation Category"),
        help_text=_("The Conservation Category can change during the approval process."),
    )

    criteria = models.ManyToManyField(
        ConservationCriterion,
        verbose_name=_("Conservation Criteria"),
        help_text=_("The Conservation Criteria form the reason for the choice of conservation category."),
    )

    # is_s5 = models.BooleanField(
    #     db_index=True,
    #     default=False,
    #     verbose_name=_("Conservation Category S5"),
    #     help_text=_("Whether this Gazettal includes Conservation Category S5 (Migratory Bird)."),
    # )

    # is_m1 = models.BooleanField(
    #     db_index=True,
    #     default=False,
    #     verbose_name=_("Conservation Category M1"),
    #     help_text=_("Whether this Gazettal includes Conservation Category M1."),
    # )

    # is_m2 = models.BooleanField(
    #     db_index=True,
    #     default=False,
    #     verbose_name=_("Conservation Category M2"),
    #     help_text=_("Whether this Gazettal includes Conservation Category M2."),
    # )

    # is_m3 = models.BooleanField(
    #     db_index=True,
    #     default=False,
    #     verbose_name=_("Conservation Category M3"),
    #     help_text=_("Whether this Gazettal includes Conservation Category M3."),
    # )

    # is_m4 = models.BooleanField(
    #     db_index=True,
    #     default=False,
    #     verbose_name=_("Conservation Category M4"),
    #     help_text=_("Whether this Gazettal includes Conservation Category M4."),
    # )

    # Approval status
    status = FSMField(
        choices=APPROVAL_STATUS,
        default=STATUS_PROPOSED,
        db_index=True,
        verbose_name=_("Approval status"),
        help_text=_("The approval status of the Gazettal."),
    )

    # Approval milestones
    proposed_on = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("Proposed on"),
        help_text=_("The date and time this Gazettal was proposed on."),
    )

    gazetted_on = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("Gazetted on"),
        help_text=_("The date and time this Gazettal was gazetted on."),
    )

    deactivated_on = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("Deactivated on"),
        help_text=_("The date and time this Gazettal was deactivated on, most likely superseded by another Gazettal."),
    )

    review_due = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("Review due date"),
        help_text=_("The date and time this Gazettal should be reviewed."),
    )

    # Approval process log
    comments = models.TextField(
        blank=True, null=True,
        verbose_name=_("Comments"),
        help_text=_("Append comments on approval process as appropriate."),
    )

    class Meta:
        """Class opts."""

        abstract = True

    def __str__(self):
        """The full name."""
        return self.pk


@python_2_unicode_compatible
class TaxonGazettal(Gazettal):
    """The Gazettal of a ConservationCategory against a Taxon.

    There can only be one Gazettal per scope.
    Transition to "gazetted" shall close any other Gazettals of same scope.
    """

    taxon = models.ForeignKey(Taxon)

    def __str__(self):
        """The full name."""
        return self.pk

    class Meta:
        """Class opts."""

        verbose_name = "Taxon Gazettal"
        verbose_name_plural = "Taxon Gazettals"


@python_2_unicode_compatible
class CommunityGazettal(Gazettal):
    """The Gazettal of a ConservationCategory against a Community."""

    community = models.ForeignKey(Community)

    class Meta:
        """Class opts."""

        verbose_name = "Community Gazettal"
        verbose_name_plural = "Community Gazettals"

    def __str__(self):
        """The full name."""
        return self.pk
