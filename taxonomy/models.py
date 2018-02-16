# -*- coding: utf-8 -*-
"""Taxonomic models.

The models in this module maintain a plain copy of WACensus data as published by KMI Geoserver.
The data is to be inserted and updated via the BioSysTT API.
"""
from __future__ import unicode_literals, absolute_import

# import itertools
# import urllib
# import slugify
# from datetime import timedelta
# from dateutil import tz

# from django.core.urlresolvers import reverse
from django.db import models
# from django.db.models.signals import pre_delete, pre_save, post_save
# from django.dispatch import receiver
# from django.contrib.gis.db import models as geo_models
# from django.contrib.gis.db.models.query import GeoQuerySet
# from django.core.urlresolvers import reverse
# from rest_framework.reverse import reverse as rest_reverse
# from django.template import loader
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
# from django.utils.safestring import mark_safe

# from durationfield.db.models.fields.duration import DurationField
# from django.db.models.fields import DurationField
# from django_fsm import FSMField, transition
# from django_fsm_log.decorators import fsm_log_by
# from django_fsm_log.models import StateLog
# from polymorphic.models import PolymorphicModel

# from wastd.users.models import User


@python_2_unicode_compatible
class Taxon(models.Model):
    r"""Taxonomic Names from HBVnames.

    Each Taxon has a unique, never re-used, ``name_id``.

    Data are refreshed (overwritten) from
    `KMI HBVnames <https://kmi.dbca.wa.gov.au/geoserver/dpaw/ows?
    service=WFS&version=1.0.0&request=GetFeature
    &typeName=dpaw:herbie_hbvnames&maxFeatures=50&outputFormat=application%2Fjson>`_

    Example taxon:
    {
      "type": "Feature",
      "id": "herbie_hbvnames.fid-3032fae6_1619d7978c8_-6031",
      "geometry": null,
      "properties": {
        "ogc_fid": 0,
        "name_id": 20887,
        "kingdom_id": 3,
        "rank_id": 180,
        "rank_name": "Genus",
        "name1": "Paraceterach",
        "name2": null,
        "rank3": null,
        "name3": null,
        "rank4": null,
        "name4": null,
        "pub_id": 582,
        "vol_info": "75",
        "pub_year": 1947,
        "is_current": "Y",
        "origin": null,
        "naturalised_status": null,
        "naturalised_certainty": null,
        "is_eradicated": null,
        "naturalised_comments": null,
        "informal": null,
        "form_desc_yr": null,
        "form_desc_mn": null,
        "form_desc_dy": null,
        "comments": null,
        "added_by": "HERBIE",
        "added_on": "2004-12-09Z",
        "updated_by": "SUEC",
        "updated_on": "2010-02-03Z",
        "family_code": "008",
        "family_nid": 22721,
        "name": "Paraceterach",
        "author": "Copel.",
        "reference": "Gen.Fil.\n75\n(1947)",
        "editor": null,
        "vernacular": null,
        "all_vernaculars": null,
        "full_name": "Paraceterach\nCopel.",
        "linear_sequence": null,
        "md5_rowhash": "f3e900990365c28fc9d15fe5e4090aa1"
      }
    }
    """

    name_id = models.BigIntegerField(
        unique=True,
        verbose_name=_("Name ID"),
        help_text=_("WACensus Name ID"),
    )

    name = models.CharField(
        max_length=1000,
        blank=True, null=True,
        verbose_name=_("Name"),
        help_text=_("Taxonomic Name"),
    )

    full_name = models.CharField(
        max_length=1000,
        blank=True, null=True,
        verbose_name=_("Full Name"),
        help_text=_("Taxonomic Full Name"),
    )

    vernacular = models.CharField(
        max_length=1000,
        blank=True, null=True,
        verbose_name=_("Vernacular Name"),
        help_text=_("Vernacular Name"),
    )

    all_vernaculars = models.TextField(
        blank=True, null=True,
        verbose_name=_("All Vernacular Names"),
        help_text=_("All Vernacular Names"),
    )

    kingdom_id = models.BigIntegerField(
        # refactor: FK Kingdom
        blank=True, null=True,
        verbose_name=_("Kingdom ID"),
        help_text=_("WACensus Kingdom ID"),
    )

    family_code = models.CharField(
        max_length=1000,
        blank=True, null=True,
        verbose_name=_("Family Code"),
        help_text=_("Taxonomic Family Code"),
    )

    family_nid = models.BigIntegerField(
        # refactor: FK Family
        blank=True, null=True,
        verbose_name=_("Family ID"),
        help_text=_("WACensus Family Name ID"),
    )

    rank_id = models.BigIntegerField(
        blank=True, null=True,
        verbose_name=_("Rank ID"),
        help_text=_("WACensus Rank ID"),
    )

    rank_name = models.CharField(
        max_length=500,
        blank=True, null=True,
        verbose_name=_("Rank Name"),
        help_text=_("Taxonomic Rank Name"),
    )

    name1 = models.CharField(
        max_length=500,
        blank=True, null=True,
        verbose_name=_("Name 1"),
        help_text=_("Taxonomic Name 1"),
    )

    name2 = models.CharField(
        max_length=500,
        blank=True, null=True,
        verbose_name=_("Name 2"),
        help_text=_("Taxonomic Name 2"),
    )

    rank3 = models.CharField(
        max_length=500,
        blank=True, null=True,
        verbose_name=_("Rank 3"),
        help_text=_("Taxonomic Rank 3"),
    )

    name3 = models.CharField(
        max_length=500,
        blank=True, null=True,
        verbose_name=_("Name 3"),
        help_text=_("Taxonomic Name 3"),
    )

    rank4 = models.CharField(
        max_length=500,
        blank=True, null=True,
        verbose_name=_("Rank 4"),
        help_text=_("Taxonomic Rank 4"),
    )

    name4 = models.CharField(
        max_length=500,
        blank=True, null=True,
        verbose_name=_("Name 4"),
        help_text=_("Taxonomic Name 4"),
    )

    author = models.CharField(
        max_length=1000,
        blank=True, null=True,
        verbose_name=_("Author"),
        help_text=_("Taxonomic Author"),
    )

    editor = models.CharField(
        max_length=1000,
        blank=True, null=True,
        verbose_name=_("Editor"),
        help_text=_("Taxonomic Editor"),
    )

    reference = models.CharField(
        max_length=1000,
        blank=True, null=True,
        verbose_name=_("Reference"),
        help_text=_("Taxonomic Reference"),
    )

    pub_id = models.BigIntegerField(
        blank=True, null=True,
        verbose_name=_("Publication ID"),
        help_text=_("WACensus Publication ID"),
    )

    vol_info = models.CharField(
        max_length=500,
        blank=True, null=True,
        verbose_name=_("Name 4"),
        help_text=_("Taxonomic Name 4"),
    )

    pub_year = models.IntegerField(
        blank=True, null=True,
        verbose_name=_("Publication Year"),
        help_text=_("WACensus Publication Year"),
    )

    #    "form_desc_yr": null,
    #    "form_desc_mn": null,
    #    "form_desc_dy": null,

    is_current = models.NullBooleanField(
        blank=True, null=True,
        verbose_name=_("Is name current?"),
        help_text=_("WACensus currency status"),
    )

    #    "origin": null,
    #    "naturalised_status": null,
    #    "naturalised_certainty": null,
    #    "is_eradicated": null,
    #    "naturalised_comments": null,
    #    "informal": null,

    #    "comments": null,
    #    "added_by": "HERBIE",
    #    "added_on": "2004-12-09Z",
    #    "updated_by": "SUEC",
    #    "updated_on": "2010-02-03Z",

    #    "linear_sequence": null,
    #    "md5_rowhash": "f3e900990365c28fc9d15fe5e4090aa1"

    class Meta:
        """Class options."""

        ordering = ["kingdom_id", "family_nid", "name_id"]
        verbose_name = "Taxon"
        verbose_name_plural = "Taxa"
        # get_latest_by = "added_on"

    def __str__(self):
        """The full taxonomic name."""
        return "[{0}] {1}".format(self.name_id, self.full_name)

    def taxonomic_synonyms(self):
        """TODO Return all taxonomic synonyms."""
        return self.__str__()

    def nomenclatural_synonyms(self):
        """TODO Return all nonenclatural synonyms."""
        return self.__str__()

    def current_names(self):
        """TODO Return all current name(s)."""
        return self.__str__()

# TODO: class Xrefs (taxonomic events)
# TODO: class Parents (taxonomic parents)
# TODO: class ParaphyleticGroups
