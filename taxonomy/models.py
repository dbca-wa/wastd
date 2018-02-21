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
class HbvGroup(models.Model):
    r"""Taxonomic groups.

    {//group
      "ogc_fid": 0,
      "class_id": "MONOCOT",
      "name_id": 828,
      "updated_by": "HERBIE",
      "updated_on": "2011-04-10Z",
      "rank_name": "Species",
      "name": "Eleocharis pallens",
      "md5_rowhash": "fa190f8247844ef8d2a94f73b961ed69"
    }
    """

    def __str__(self):
        """The full taxonomic name."""
        return ""


@python_2_unicode_compatible
class HbvFamily(models.Model):
    r"""Taxonomic nodes from Families and up from HBVFamilies.

    {
      "ogc_fid": 0,
      "name_id": 23206,
      "kingdom_id": 4,
      "rank_id": 140,
      "rank_name": "Family",
      "family_name": "Phragmopelthecaceae",
      "is_current": "Y",
      "informal": null,
      "comments": null,
      "family_code": "762",
      "linear_sequence": null,
      "order_nid": null,
      "order_name": null,
      "class_nid": null,
      "class_name": null,
      "division_nid": null,
      "division_name": null,
      "kingdom_name": "Fungi",
      "author": "L.Xavier",
      "editor": null,
      "reference":
        "Phragmopeltecaceae uma Nova Familia de Microascoliquens 42 (1976)",
      "supra_code": "LICHEN",
      "added_on": "2004-12-09Z",
      "updated_on": "2016-08-30Z",
      "md5_rowhash": "2b9aaba4c145701f540c40db4fde6071"
    }
    """

    def __str__(self):
        """The full taxonomic name."""
        return ""


@python_2_unicode_compatible
class HbvSpecies(models.Model):
    r"""Taxonomic species names.

    {
      "ogc_fid": 1,
      "name_id": 11724,
      "kingdom_id": 3,
      "rank_id": 240,
      "rank_name": "Variety",
      "family_code": "162",
      "family_nid": 34857,
      "genus": "Pultenaea",
      "species": "verruculosa",
      "infra_rank": "var.",
      "infra_name": "verruculosa",
      "infra_rank2": null,
      "infra_name2": null,
      "author": "Turcz.",
      "editor": null,
      "reference": null,
      "comments": null,
      "vernacular": null,
      "all_vernaculars": null,
      "species_name": "Pultenaea verruculosa var. verruculosa",
      "species_code": "PULVERVER",
      "is_current": "N",
      "naturalised": null,
      "naturalised_status": "N",
      "naturalised_certainty": null,
      "is_eradicated": null,
      "naturalised_comments": null,
      "informal": null,
      "added_on": "1991-12-31Z",
      "updated_on": "2004-12-09Z",
      "consv_code": null,
      "ranking": null,
      "linear_sequence": null,
      "md5_rowhash": "387d5ee88472d3f6f300f3b677ae475a"
    }
    """

    def __str__(self):
        """The full taxonomic name."""
        return ""


@python_2_unicode_compatible
class HbvTaxon(models.Model):
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
        "full_name": "Paraceterach\nCopel.",
        "author": "Copel.",
        "reference": "Gen.Fil.\n75\n(1947)",
        "editor": null,
        "vernacular": null,
        "all_vernaculars": null,
        "linear_sequence": null,
        "md5_rowhash": "f3e900990365c28fc9d15fe5e4090aa1"
      }
    }
    """

    name_id = models.BigIntegerField(
        unique=True,
        verbose_name=_("Name ID"),
        help_text=_("WACensus Name ID, formerly known as Taxon ID. "
                    "Assigned by WACensus."),
    )

    name = models.CharField(
        max_length=1000,
        blank=True, null=True,
        verbose_name=_("Name"),
        help_text=_(
            "Full taxonomic name without author. Different concepts "
            "(defined by different authors) can have identical names."),
    )

    full_name = models.CharField(
        max_length=1000,
        blank=True, null=True,
        verbose_name=_("Full Name"),
        help_text=_(
            "Full taxonomic name including author. Different concepts "
            "(defined by different authors) will have different Full Names."),
    )

    vernacular = models.CharField(
        max_length=1000,
        blank=True, null=True,
        verbose_name=_("Preferred Vernacular Name"),
        help_text=_("Preferred Vernacular Name."),
    )

    all_vernaculars = models.TextField(
        blank=True, null=True,
        verbose_name=_("All Vernacular Names"),
        help_text=_("All Vernacular Names in order of preference."),
    )

    kingdom_id = models.BigIntegerField(
        # refactor: FK Kingdom
        # default: request.user.default_kingdom
        blank=True, null=True,
        verbose_name=_("Kingdom ID"),
        help_text=_("WACensus Kingdom ID."),
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
        help_text=_("WACensus Taxonomic Rank ID."),
    )

    rank_name = models.CharField(
        max_length=500,
        blank=True, null=True,
        verbose_name=_("Rank Name"),
        help_text=_("WACensus Taxonomic Rank Name."),
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

    form_desc_yr = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_("Described on (year)"),
        help_text=_("Year of first description."),
    )

    form_desc_mn = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_("Described on (month)"),
        help_text=_("Month of first description."),
    )

    form_desc_dy = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_("Described on (day)"),
        help_text=_("Day of first description."),
    )

    is_current = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_("Is name current?"),
        help_text=_("WACensus currency status."),
    )

    origin = models.CharField(
        max_length=1000,
        blank=True, null=True,
        verbose_name=_("Origin"),
        help_text=_("Origin."),
    )

    naturalised_status = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_("Naturalisation status"),
        help_text=_("Naturalisation status."),
    )

    naturalised_certainty = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_("Naturalisation certainty"),
        help_text=_("Naturalisation certainty."),
    )

    naturalised_comments = models.TextField(
        blank=True, null=True,
        verbose_name=_("Naturalisation comments"),
        help_text=_("Naturalisation comments."),
    )

    is_eradicated = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_("Is eradicated?"),
        help_text=_("Whether taxon is eradicated or not."),
    )

    informal = models.CharField(
        max_length=500,
        blank=True, null=True,
        verbose_name=_("Name approval status"),
        help_text=_("The approval status indicates whether a taxonomic name"
                    " is a phrase name (PN), manuscript name (MS) or published (blank)."),
    )

    comments = models.TextField(
        blank=True, null=True,
        verbose_name=_("Comments"),
        help_text=_("Comments are words to clarify things."),
    )

    added_by = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_("Added by"),
        help_text=_("The person or system who added this record to WACensus."),
    )

    added_on = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_("WACensus added on"),
        help_text=_("Date on which this record was added to WACensus."),
    )

    updated_by = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_("Updated by"),
        help_text=_("The person or system who updated this record last in WACensus."),
    )

    updated_on = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_("WACensus updated on"),
        help_text=_("Date on which this record was updated in WACensus."),
    )

    #    "linear_sequence": null,
    linear_sequence = models.TextField(
        blank=True, null=True,
        verbose_name=_("Linear sequence"),
        help_text=_(""),
    )

    #    "md5_rowhash": "f3e900990365c28fc9d15fe5e4090aa1"
    md5_rowhash = models.CharField(
        max_length=500,
        blank=True, null=True,
        verbose_name=_("GeoServer MD5 rowhash"),
        help_text=_("An MD5 hash of the record, used to indicate updates."),
    )

    ogc_fid = models.CharField(
        max_length=500,
        blank=True, null=True,
        verbose_name=_("GeoServer OGC FeatureID"),
        help_text=_("The OCG Feature ID of the record, used to identify the record."),
    )

    class Meta:
        """Class options."""

        ordering = ["kingdom_id", "family_nid", "name_id"]
        verbose_name = "HBV Taxon"
        verbose_name_plural = "HBV Taxa"
        # get_latest_by = "added_on"

    def __str__(self):
        """The full taxonomic name."""
        return "[{0}] {1} ({2})".format(
            self.name_id,
            self.full_name,
            self.vernacular or "")

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


@python_2_unicode_compatible
class HbvXrefs(models.Model):
    r"""Taxonomic operations on name IDs.

    {//xrefs
      "ogc_fid": 0,
      "xref_id": 1,
      "old_name_id": 8288,
      "new_name_id": null,
      "xref_type": "EXC",
      "active": "Y",
      "authorised_by": null,
      "authorised_on": "        ",
      "comments": null,
      "added_on": "1990-12-03Z",
      "updated_on": null,
      "md5_rowhash": "8a0bb19a2dad98dbe92dbc0caad58eb9"
    }
    """

    def __str__(self):
        """The full taxonomic name."""
        return ""

# TODO: class Parents (taxonomic parents)
# TODO: class ParaphyleticGroups
