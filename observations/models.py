"""Observation models.

These models support opportunistic encounters with stranded, dead, injured,
nesting turtles and possibly other wildlife, such as cetaceans and pinnipeds.

An Encounter (or subclass) is an event where a person records some information
about a thing in the physical world. An Encounter is the generic base class,
and a subclass may be specific to a defined category of thing (e.g. the
TurtleNestEncounter class is specific to records about turtle nests and tracks).

An Encounter can have zero or more Observations associated with it. An Observation
(or subclass) is used to record an observation that was taken during the encounter
event (e.g. one encounter with a nesting turtle might result in observations about
the turtle's morphometrics, physical damage, and nesting success).
"""
from datetime import timedelta
from dateutil import tz
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.gis.db import models
from django.template import loader
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.safestring import mark_safe
from django_fsm import FSMField, transition
from django_fsm_log.decorators import fsm_log_by, fsm_log_description
from django_fsm_log.models import StateLog
import itertools
import logging
from polymorphic.models import PolymorphicModel
from slugify import slugify
import urllib

from wastd.utils import LegacySourceMixin, QualityControlMixin, UrlsMixin
from users.models import User, Organisation
from . import lookups

LOGGER = logging.getLogger("turtles")


def encounter_media(instance, filename):
    """Return an upload file path for an encounter media attachment.
    """
    return "encounter/{}/{}".format(instance.encounter.source_id, filename)


def campaign_media(instance, filename):
    """Return an upload file path for a campaign media attachment.
    Deprecated method, but required for migrations.
    """
    return "campaign/{}/{}".format(instance.campaign.id, filename)


def survey_media(instance, filename):
    """Return an upload path for survey media.
    """
    if not instance.survey.id:
        instance.survey.save()
    return "survey/{}/{}".format(instance.survey.id, filename)


class Area(models.Model):
    """An area with a polygonal extent.

    This model accommodates anything with a polygonal extent, providing:

    * Area type (to classify different kinds of areas)
    * Area name must be unique within area type
    * Polygonal extent of the area

    Some additional fields are populated behind the scenes at each save and
    serve to cache low churn, high use content:

    * centroid: useful for spatial analysis and location queries
    * northern extent: useful to sort by latitude
    * as html: an HTML map popup
    """
    AREATYPE_MPA = "MPA"
    AREATYPE_LOCALITY = "Locality"
    AREATYPE_SITE = "Site"
    AREATYPE_DBCA_REGION = "Region"
    AREATYPE_DBCA_DISTRICT = "District"
    AREATYPE_CHOICES = (
        (AREATYPE_MPA, "MPA"),
        (AREATYPE_LOCALITY, "Locality"),
        (AREATYPE_SITE, "Site"),
        (AREATYPE_DBCA_REGION, "DBCA Region"),
        (AREATYPE_DBCA_DISTRICT, "DBCA District"),
    )

    area_type = models.CharField(
        max_length=300,
        default=AREATYPE_SITE,
        choices=AREATYPE_CHOICES,
        help_text="The area type.",
    )
    name = models.CharField(
        max_length=1000,
        help_text="The name of the area.",
    )
    w2_location_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="W2 Location Code",
        help_text="The location code under which this area is known to the WAMTRAM turtle tagging database.",
    )
    w2_place_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="W2 Place Code",
        help_text="The place code under which this area is known to the WAMTRAM turtle tagging database.",
    )
    centroid = models.PointField(
        srid=4326,
        editable=False,
        blank=True,
        null=True,
        help_text="The centroid is a simplified presentation of the Area.",
    )
    northern_extent = models.FloatField(
        verbose_name="Northernmost latitude",
        editable=False,
        blank=True,
        null=True,
        help_text="The northernmost latitude serves to sort areas.",
    )
    length_surveyed_m = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name="Surveyed length (m)",
        blank=True,
        null=True,
        help_text="The length of meters covered by a survey of this area. E.g., the meters of high water mark along a beach.",
    )
    length_survey_roundtrip_m = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name="Survey roundtrip (m)",
        blank=True,
        null=True,
        help_text="The total length of meters walked during an end to end survey of this area.",
    )
    as_html = models.TextField(
        verbose_name="HTML representation",
        blank=True,
        null=True,
        editable=False,
        help_text="The cached HTML representation for display purposes.",
    )
    geom = models.PolygonField(
        srid=4326,
        verbose_name="Location",
        help_text="The exact extent of the area as polygon in WGS84.",
    )

    class Meta:
        ordering = ("-northern_extent", "name")
        unique_together = ("area_type", "name")

    def save(self, *args, **kwargs):
        """Cache centroid and northern extent.
        """
        if not self.northern_extent:
            self.northern_extent = self.derived_northern_extent
        if not self.centroid:
            self.centroid = self.derived_centroid
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.area_type})"

    @property
    def derived_centroid(self):
        """The centroid, derived from the polygon."""
        return self.geom.centroid or None

    @property
    def derived_northern_extent(self):
        """The northern extent, derived from the polygon."""
        return self.geom.extent[3] or None

    def get_popup(self):
        """Generate HTML popup content.
        """
        t = loader.get_template("popup/{}.html".format(self._meta.model_name))
        c = dict(original=self)
        return mark_safe(t.render(c))

    @property
    def leaflet_title(self):
        """A title for leaflet map markers."""
        return self.__str__()

    @property
    def absolute_admin_url(self):
        """Return the absolute admin change URL.
        """
        return reverse("admin:{}_{}_change".format(self._meta.app_label, self._meta.model_name), args=[self.pk])

    @property
    def all_encounters_url(self):
        """All Encounters within this Area."""
        return "/admin/observations/encounter/?{0}__id__exact={1}".format(
            "site" if self.area_type == Area.AREATYPE_SITE else "area",
            self.pk,
        )

    @property
    def animal_encounters_url(self):
        """The admin URL for AnimalEncounters within this Area."""
        return "/admin/observations/animalencounter/?{0}__id__exact={1}".format(
            "site" if self.area_type == Area.AREATYPE_SITE else "area",
            self.pk,
        )


class Campaign(models.Model):
    """An endeavour of a team to a Locality within a defined time range.

    * Campaign are owned by an Organisation.
    * Campaign own all Surveys and Encounters within its area and time range.
    * Campaign can nominate other Organisations as viewers of their data.
    """
    destination = models.ForeignKey(
        Area,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="campaigns",
        help_text="The surveyed Locality.",
    )
    start_time = models.DateTimeField(
        verbose_name="Campaign start",
        blank=True,
        null=True,
        help_text="The Campaign start, shown as local time (no daylight savings), stored as UTC.",
    )
    end_time = models.DateTimeField(
        verbose_name="Campaign end",
        blank=True,
        null=True,
        help_text="The Campaign end, shown as local time (no daylight savings), stored as UTC.",
    )
    comments = models.TextField(
        blank=True,
        null=True,
        help_text="Comments about the Campaign.",
    )
    team = models.ManyToManyField(User, blank=True, related_name="campaign_team")
    owner = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        editable=True,
        blank=True,
        null=True,
        related_name="campaigns",
        help_text="The organisation that ran this Campaign owns all records (Surveys and Encounters).",
    )
    viewers = models.ManyToManyField(
        Organisation,
        related_name="shared_campaigns",
        blank=True,
        help_text="The nominated organisations are able to view the Campaign's records.",
    )

    class Meta:
        ordering = ("-start_time", "destination", "owner")

    def __str__(self):
        return "{} {} {} to {}".format(
            "-" if not self.owner else self.owner.label,
            "-" if not self.destination else self.destination.name,
            "na"
            if not self.start_time
            else self.start_time.astimezone(tz.tzlocal()).strftime("%Y-%m-%d"),
            "na"
            if not self.end_time
            else self.end_time.astimezone(tz.tzlocal()).strftime("%Y-%m-%d"),
        )

    @property
    def surveys(self):
        """Return a QuerySet of Surveys or None.

        If any of destination, start_time or end_time are empty, return None,
        else return Surveys within the Campaign's area and time range.
        """
        if self.destination and self.start_time and self.end_time:
            return Survey.objects.filter(
                site__geom__coveredby=self.destination.geom,
                start_time__gte=self.start_time,
                end_time__lte=self.end_time,
            )
        return None

    @property
    def orphaned_surveys(self):
        """Return Surveys that should be, but are not linked to this Campaign.

        This includes Surveys without a Campaign,
        and Surveys linked to another Campaign.
        We assume that Campaigns do not overlap.
        """
        if self.surveys:
            return self.surveys.exclude(campaign=self)
        return None

    @property
    def encounters(self):
        """Return the QuerySet of all Encounters within this Campaign."""
        if self.destination and self.start_time and self.end_time:
            return Encounter.objects.filter(
                where__coveredby=self.destination.geom,
                when__gte=self.start_time,
                when__lte=self.end_time,
            )
        return None

    @property
    def orphaned_encounters(self):
        """Return Encounters  that should be, but are not linked to this Campaign.

        This includes Encounters without a Campaign,
        and Encounters linked to another Campaign.
        We assume that Campaigns do not overlap.
        """
        if self.encounters:
            return self.encounters.exclude(campaign=self)
        return None

    def adopt_all_surveys_and_encounters(self):
        """Adopt all surveys and encounters in this Campaign."""
        no_svy = 0
        no_enc = 0
        if self.surveys:
            no_svy = self.surveys.update(campaign=self)
        if self.encounters:
            no_enc = self.encounters.update(campaign=self)
        LOGGER.info("Adopted {0} surveys and {1} encounters.".format(no_svy, no_enc))

    def adopt_all_orphaned_surveys_and_encounters(self):
        """Adopt all orphaned surveys and encounters in this Campaign."""
        no_svy = 0
        no_enc = 0
        if self.orphaned_surveys:
            no_svy = self.orphaned_surveys.update(campaign=self)
        if self.orphaned_encounters:
            no_enc = self.orphaned_encounters.update(campaign=self)
        LOGGER.info("Adopted {0} surveys and {1} encounters.".format(no_svy, no_enc))


class Survey(QualityControlMixin, UrlsMixin, models.Model):
    """A visit to one site by a team of field workers collecting data.
    """
    campaign = models.ForeignKey(
        Campaign,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text="The overarching Campaign instigating this Survey is automatically linked when a Campaign is saved.",
    )
    source = models.CharField(
        max_length=300,
        verbose_name="Data source",
        default=lookups.SOURCE_DEFAULT,
        choices=lookups.SOURCE_CHOICES,
        help_text="Where was this record captured initially?",
    )
    source_id = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name="Source ID",
        help_text="The ID of the start point in the original source.",
    )
    device_id = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name="Device ID",
        help_text="The ID of the recording device, if available.",
    )
    area = models.ForeignKey(
        Area,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Surveyed area",
        related_name="survey_area",
        help_text="The general area this survey took place in.",
    )
    site = models.ForeignKey(
        Area,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Surveyed site",
        help_text="The surveyed site, if known.",
    )
    transect = models.LineStringField(
        srid=4326,
        blank=True,
        null=True,
        verbose_name="Transect line",
        help_text="The surveyed path as LineString in WGS84, optional. E.g. automatically captured by form Track Tally.",
    )
    reporter = models.ForeignKey(
        User,
        on_delete=models.SET_DEFAULT,
        default=settings.ADMIN_USER,
        related_name="reported_surveys",
        verbose_name="Recorded by",
        blank=True,
        null=True,
        help_text="The person who captured the start point, ideally this person also recoreded the encounters and end point.",
    )
    start_location = models.PointField(
        srid=4326,
        blank=True,
        null=True,
        verbose_name="Survey start point",
        help_text="The start location as point in WGS84.",
    )
    start_location_accuracy_m = models.FloatField(
        verbose_name="Start location accuracy (m)",
        null=True,
        blank=True,
        help_text="The accuracy of the supplied start location in metres, if given.",
    )
    start_time = models.DateTimeField(
        verbose_name="Survey start time",
        blank=True,
        null=True,
        help_text="""The datetime of entering the site, shown as local time (no daylight savings), stored as UTC.
        The time of 'feet in the sand, start recording encounters'.""",
    )
    # NOTE: don't use this field, use SurveyMediaAttachment
    start_photo = models.FileField(
        upload_to=survey_media,
        blank=True,
        null=True,
        max_length=500,
        verbose_name="Site photo start",
        help_text="Site conditions at start of survey.",
    )
    start_comments = models.TextField(
        verbose_name="Comments at start",
        blank=True,
        null=True,
        help_text="Describe any circumstances affecting data collection, e.g. days without surveys.",
    )
    end_source_id = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name="Source ID of end point",
        help_text="The ID of the record in the original source.",
    )
    end_device_id = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name="End device ID",
        help_text="The ID of the recording device which captured the end point, if available.",
    )
    end_location = models.PointField(
        srid=4326,
        blank=True,
        null=True,
        verbose_name="Survey end point",
        help_text="The end location as point in WGS84.",
    )
    end_location_accuracy_m = models.FloatField(
        verbose_name="End location accuracy (m)",
        null=True,
        blank=True,
        help_text="The accuracy of the supplied end location in metres, if given.",
    )
    end_time = models.DateTimeField(
        verbose_name="Survey end time",
        blank=True,
        null=True,
        help_text="""The datetime of leaving the site, shown as local time (no daylight savings), stored as UTC.
        The time of 'feet in the sand, done recording encounters.'""",
    )
    end_photo = models.FileField(
        upload_to=survey_media,
        blank=True,
        null=True,
        max_length=500,
        verbose_name="Site photo end",
        help_text="Site conditions at end of survey.",
    )
    end_comments = models.TextField(
        verbose_name="Comments at finish",
        blank=True,
        null=True,
        help_text="Describe any circumstances affecting data collection, e.g. days without surveys.",
    )
    production = models.BooleanField(
        default=True,
        verbose_name="Production run",
        help_text="Whether the survey is a real (production) survey, or a training survey.",
    )
    team = models.ManyToManyField(
        User,
        blank=True,
        related_name="survey_team",
        help_text="Additional field workers, apart from the reporter, who assisted with data collection.",
    )
    label = models.CharField(
        blank=True,
        null=True,
        max_length=500,
        help_text="A human-readable, self-explanatory label.",
    )

    class Meta:
        ordering = ("-start_time",)
        unique_together = ("source", "source_id")

    def __str__(self):
        return self.label or str(self.pk)

    def make_label(self):
        return "Survey {} of {} on {} from {} to {}".format(
            self.pk,
            "unknown site" if not self.site else self.site.name,
            "NA" if not self.start_time else self.start_time.astimezone(tz.tzlocal()).strftime("%d-%b-%Y"),
            "" if not self.start_time else self.start_time.astimezone(tz.tzlocal()).strftime("%H:%M"),
            "" if not self.end_time else self.end_time.astimezone(tz.tzlocal()).strftime("%H:%M %Z"),
        )

    def label_short(self):
        return "Survey {} of {}".format(self.pk, "unknown site" if not self.site else self.site.name)

    @property
    def as_html(self):
        t = loader.get_template("popup/survey.html")
        return mark_safe(t.render({"original": self}))

    @property
    def absolute_admin_url(self):
        """Return the absolute admin change URL.
        """
        return reverse("admin:{}_{}_change".format(self._meta.app_label, self._meta.model_name), args=[self.pk])

    def card_template(self):
        return "observations/survey_card.html"

    @property
    def start_date(self):
        """The calendar date of the survey's start time in the local timezone."""
        return self.start_time.astimezone(tz.tzlocal()).date()

    @property
    def duplicate_surveys(self):
        """A queryset of other surveys on the same date and site with intersecting durations."""
        return (
            Survey.objects.filter(site=self.site, start_time__date=self.start_date)
            .exclude(pk=self.pk)
            .exclude(start_time__gte=self.end_time)  # surveys starting after self
            .exclude(end_time__lte=self.start_time)  # surveys ending before self
        )

    @property
    def no_duplicates(self):
        """The number of duplicate surveys."""
        return self.duplicate_surveys.count()

    @property
    def has_duplicates(self):
        """Whether there are duplicate surveys."""
        return self.no_duplicates > 0

    def close_duplicates(self, actor=None):
        """Mark this Survey as the only production survey, others as training and adopt all Encounters.

        Data import of Surveys reconstructed from SVS and SVE, adjusting site bondaries,
        and previous import algorithms, can cause duplicate Surveys to be created.

        The QA operator needs to identify duplicates, mark each as "not production" (=training, testing, or duplicate),
        set this Survey as "production", then save each of them and set to "curated".

        Duplicate Surveys are recognized by an overlap of place and time. They can however extend longer individually,
        so that duplicates can contain Encounters outside the duration of the production Survey.
        The remaining production Survey needs to adjust its start and end time to include all Encounters of all closed
        duplicate surveys.

        The production Survey adopts all Encounters within its spatial bounds.
        Encounters outside its spatial bounds can occur if the Survey site was adjusted manually.
        These will be orphaned after this operation, and can be adopted either by saving an adjacent survey,
        or running "adopt orphaned encounters".
        """
        survey_pks = [survey.pk for survey in self.duplicate_surveys.all()] + [self.pk]
        all_encounters = Encounter.objects.filter(survey_id__in=survey_pks)
        curator = actor if actor else User.objects.get(pk=1)
        msg = "Closing {0} duplicate(s) of Survey {1} as {2}.".format(
            len(survey_pks) - 1, self.pk, curator
        )

        # All duplicate Surveys shall be closed (not production) and own no Encounters
        for d in self.duplicate_surveys.all():
            LOGGER.info("Closing Survey {0} with actor {1}".format(d.pk, curator))
            d.production = False
            d.save()
            if d.status != QualityControlMixin.STATUS_CURATED:
                d.curate(by=curator)
                d.save()
            for a in d.attachments.all():
                a.survey = self
                a.save()

        # From all Encounters (if any), adjust duration
        if all_encounters.count() > 0:
            earliest_enc = min([e.when for e in all_encounters])
            earliest_buffered = earliest_enc - timedelta(minutes=30)
            latest_enc = max([e.when for e in all_encounters])
            latest_buffered = latest_enc + timedelta(minutes=30)

            msg += " {0} combined Encounters were found from duplicates between {1} and {2}.".format(
                all_encounters.count(),
                earliest_enc.astimezone(tz.tzlocal()).strftime("%Y-%m-%d %H:%M %Z"),
                latest_enc.astimezone(tz.tzlocal()).strftime("%Y-%m-%d %H:%M %Z"),
            )
            if earliest_enc < self.start_time:
                msg += " Adjusted Survey start time from {0} to 30 mins before earliest Encounter, {1}.".format(
                    self.start_time.astimezone(tz.tzlocal()).strftime(
                        "%Y-%m-%d %H:%M %Z"
                    ),
                    earliest_buffered.astimezone(tz.tzlocal()).strftime(
                        "%Y-%m-%d %H:%M %Z"
                    ),
                )
                self.start_time = earliest_buffered
            if latest_enc > self.end_time:
                msg += " Adjusted Survey end time from {0} to 30 mins after latest Encounter, {1}.".format(
                    self.end_time.astimezone(tz.tzlocal()).strftime(
                        "%Y-%m-%d %H:%M %Z"
                    ),
                    latest_buffered.astimezone(tz.tzlocal()).strftime(
                        "%Y-%m-%d %H:%M %Z"
                    ),
                )
                self.end_time = latest_buffered

        # This Survey is the production survey owning all Encounters
        self.production = True
        self.save()
        if self.status != QualityControlMixin.STATUS_CURATED:
            self.curate(by=curator)
            self.save()

        # ...except cuckoo Encounters
        if all_encounters.count() > 0 and self.site is not None:
            cuckoo_encounters = all_encounters.exclude(where__coveredby=self.site.geom)
            for e in cuckoo_encounters:
                e.site = None
                e.survey = None
                e.save()
            msg += " Evicted {0} cuckoo Encounters observed outside the site.".format(
                cuckoo_encounters.count()
            )

        # Post-save runs claim_encounters
        self.save()
        LOGGER.info(msg)
        return msg

    @property
    def leaflet_title(self):
        return self.__str__()

    @property
    def guess_site(self):
        """Return the first site containing the start_location or None.
        """
        candidates = Area.objects.filter(area_type=Area.AREATYPE_SITE, geom__covers=self.start_location)
        return candidates.first() or None

    @property
    def guess_area(self):
        """Return the first locality containing the start_location or None.
        """
        candidates = Area.objects.filter(area_type=Area.AREATYPE_LOCALITY, geom__covers=self.start_location)
        return candidates.first() or None


class SurveyEnd(models.Model):
    """A visit to one site by a team of field workers collecting data.
    TODO: deprecate this model (consolidate into Survey).
    """
    source = models.CharField(
        max_length=300,
        verbose_name="Data source",
        default=lookups.SOURCE_DEFAULT,
        choices=lookups.SOURCE_CHOICES,
        help_text="Where was this record captured initially?",
    )
    source_id = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name="Source ID",
        help_text="The ID of the start point in the original source.",
    )
    device_id = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name="Device ID",
        help_text="The ID of the recording device, if available.",
    )
    reporter = models.ForeignKey(
        User,
        on_delete=models.SET_DEFAULT,
        default=settings.ADMIN_USER,
        verbose_name="Recorded by",
        blank=True,
        null=True,
        help_text="The person who captured the start point, ideally this person also recoreded the encounters and end point.",
    )
    site = models.ForeignKey(
        Area,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Surveyed site",
        help_text="The surveyed site, if known.",
    )
    end_location = models.PointField(
        srid=4326,
        blank=True,
        null=True,
        verbose_name="Survey end point",
        help_text="The end location as point in WGS84.",
    )
    end_time = models.DateTimeField(
        verbose_name="Survey end time",
        blank=True,
        null=True,
        help_text="The datetime of leaving the site, shown as local time (no daylight savings), stored as UTC. The time of 'feet in the sand, done recording encounters.'",
    )
    end_photo = models.FileField(
        upload_to=survey_media,
        max_length=500,
        verbose_name="Site photo end",
        help_text="Site conditions at end of survey.",
    )
    end_comments = models.TextField(
        verbose_name="Comments at finish",
        blank=True,
        null=True,
        help_text="Describe any circumstances affecting data collection, e.g. days without surveys.",
    )

    class Meta:
        ordering = ("end_location", "end_time")
        unique_together = ("source", "source_id")

    def __str__(self):
        return "SurveyEnd {} at {} on {}".format(
            self.pk,
            "na" if not self.site else self.site,
            "na" if not self.end_time else self.end_time.isoformat(),
        )


class SurveyMediaAttachment(LegacySourceMixin, models.Model):
    """A media attachment to a Survey, e.g. start or end photos.
    """
    MEDIA_TYPE_CHOICES = (
        ("data_sheet", "Data sheet"),
        ("communication", "Communication record"),
        ("photograph", "Photograph"),
        ("other", "Other"),
    )

    survey = models.ForeignKey(
        Survey,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attachments",
        help_text="The Survey this attachment belongs to.",
    )
    media_type = models.CharField(
        max_length=300,
        verbose_name="Attachment type",
        choices=MEDIA_TYPE_CHOICES,
        default="photograph",
        help_text="What is the attached file about?",
    )
    title = models.CharField(
        max_length=300,
        verbose_name="Attachment name",
        blank=True,
        null=True,
        help_text="Give the attachment a representative name.",
    )
    attachment = models.FileField(
        upload_to=survey_media,
        max_length=500,
        verbose_name="File attachment",
        help_text="Upload the file.",
    )

    def __str__(self):
        return f"Media {self.pk}: {self.title}"

    @property
    def filepath(self):
        """The path to attached file."""
        try:
            fpath = force_str(self.attachment.file)
        except BaseException:
            fpath = None
        return fpath

    @property
    def thumbnail(self):
        if self.attachment:
            return mark_safe(
                '<a href="{0}" target="_" rel="nofollow" '
                'title="Click to view full screen in new browser tab">'
                '<img src="{0}" alt="{1} {2}" style="height:100px;"></img>'
                "</a>".format(
                    self.attachment.url, self.get_media_type_display(), self.title
                )
            )
        else:
            return ""


class Encounter(PolymorphicModel, UrlsMixin, models.Model):
    """The base Encounter class.

    * When: Datetime of encounter, stored in UTC, entered and displayed in local
      timezome.
    * Where: Point in WGS84.
    * Who: The observer has to be a registered system user.
    * Source: The previous point of truth for the record.
    * Source ID: The ID of the encounter at the previous point of truth. This
      can be a corporate file number, a database primary key, and likely is
      prefixed or post-fixed. Batch imports can (if they use the ID consistently)
      use the ID to identify previously imported records and avoid duplication.

    A suggested naming standard for paper records is
    ``<prefix><date><running-number>``, with possible

    * prefix indicates data type (stranding, tagging, nest obs etc)
    * date is reversed Y-m-d
    * a running number caters for multiple records of the same prefix and date

    These Paper record IDs should be recorded on the original paper forms
    (before scanning), used as file names for the PDF'd scans, and typed into
    WAStD.

    The QA status can only be changed through transition methods, not directly.
    Changes to the QA status, as wells as versions of the data are logged to
    preserve the data lineage.
    """
    LOCATION_DEFAULT = "1000"
    LOCATION_ACCURACY_CHOICES = (
        ("10", "GPS reading at exact location (10 m)"),
        (LOCATION_DEFAULT, "Site centroid or place name (1 km)"),
        ("10000", "Rough estimate (10 km)"),
    )

    ENCOUNTER_STRANDING = "stranding"
    ENCOUNTER_TAGGING = "tagging"
    ENCOUNTER_INWATER = "inwater"
    ENCOUNTER_NEST = "nest"
    ENCOUNTER_TRACKS = "tracks"
    ENCOUNTER_TAG = "tag-management"
    ENCOUNTER_LOGGER = "logger"
    ENCOUNTER_OTHER = "other"

    ENCOUNTER_TYPES = (
        (ENCOUNTER_STRANDING, "Stranding"),
        (ENCOUNTER_TAGGING, "Tagging"),
        (ENCOUNTER_NEST, "Nest"),
        (ENCOUNTER_TRACKS, "Tracks"),
        (ENCOUNTER_INWATER, "In water"),
        (ENCOUNTER_TAG, "Tag Management"),
        (ENCOUNTER_LOGGER, "Logger"),
        (ENCOUNTER_OTHER, "Other"),
    )

    LEAFLET_ICON = {
        ENCOUNTER_STRANDING: "circle-exclamation",
        ENCOUNTER_TAGGING: "tags",
        ENCOUNTER_NEST: "home",
        ENCOUNTER_TRACKS: "paw",
        ENCOUNTER_TAG: "cog",
        ENCOUNTER_INWATER: "water",
        ENCOUNTER_LOGGER: "tablet",
        ENCOUNTER_OTHER: "circle-question",
    }

    LEAFLET_COLOUR = {
        ENCOUNTER_STRANDING: "darkred",
        ENCOUNTER_TAGGING: "blue",
        ENCOUNTER_INWATER: "blue",
        ENCOUNTER_NEST: "green",
        ENCOUNTER_TRACKS: "cadetblue",
        ENCOUNTER_TAG: "darkpuple",
        ENCOUNTER_LOGGER: "orange",
        ENCOUNTER_OTHER: "purple",
    }

    STATUS_NEW = "new"
    STATUS_IMPORTED = "imported"
    STATUS_MANUAL_INPUT = "manual input"
    STATUS_PROOFREAD = "proofread"
    STATUS_CURATED = "curated"
    STATUS_PUBLISHED = "published"
    STATUS_FLAGGED = "flagged"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = (
        (STATUS_NEW, "New"),
        (STATUS_IMPORTED, "Imported"),
        (STATUS_MANUAL_INPUT, "Manual input"),
        (STATUS_PROOFREAD, "Proofread"),
        (STATUS_CURATED, "Curated"),
        (STATUS_PUBLISHED, "Published"),
        (STATUS_FLAGGED, "Flagged"),
        (STATUS_REJECTED, "Rejected"),
    )

    STATUS_LABELS = {
        STATUS_NEW: "secondary",
        STATUS_IMPORTED: "secondary",
        STATUS_MANUAL_INPUT: "secondary",
        STATUS_PROOFREAD: "warning",
        STATUS_CURATED: "success",
        STATUS_PUBLISHED: "info",
        STATUS_FLAGGED: "warning",
        STATUS_REJECTED: "danger",
    }

    status = FSMField(default=STATUS_NEW, choices=STATUS_CHOICES, verbose_name="QA Status")
    campaign = models.ForeignKey(
        Campaign,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text="The overarching Campaign instigating this Encounter is automatically linked when a Campaign saved.",
    )
    survey = models.ForeignKey(
        Survey,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The survey during which this encounter happened.",
    )
    area = models.ForeignKey(
        Area,  # Always an Area of type 'Locality'.
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="encounter_area",
        help_text="The general area this encounter took place in.",
    )
    site = models.ForeignKey(
        Area,  # Always an Area of type 'Site'.
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Surveyed site",
        related_name="encounter_site",
        help_text="The surveyed site, if known.",
    )
    source = models.CharField(
        max_length=300,
        db_index=True,
        verbose_name="Data source",
        default=lookups.SOURCE_DEFAULT,
        choices=lookups.SOURCE_CHOICES,
        help_text="Where was this record captured initially?",
    )
    source_id = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name="Source ID",
        help_text="The ID of the record in the original source, or a newly allocated ID if left blank. Delete and save to regenerate this ID.",
    )
    where = models.PointField(
        srid=4326,
        verbose_name="Observed at",
        help_text="The observation location as point in WGS84",
    )
    when = models.DateTimeField(
        db_index=True,
        verbose_name="Observed on",
        help_text="The observation datetime, shown as local time (no daylight savings), stored as UTC.",
    )
    location_accuracy = models.CharField(
        max_length=300,
        verbose_name="Location accuracy class (m)",
        default=LOCATION_DEFAULT,
        choices=LOCATION_ACCURACY_CHOICES,
        help_text="The source of the supplied location implies a rough location accuracy.",
    )
    location_accuracy_m = models.FloatField(
        verbose_name="Location accuracy (m)",
        null=True,
        blank=True,
        help_text="The accuracy of the supplied location in metres, if given.",
    )
    name = models.CharField(
        max_length=1000,
        editable=False,
        blank=True,
        null=True,
        verbose_name="Encounter Subject Identifer",
        help_text="""An automatically inferred read-only identifier for the encountered subject,
        e.g. in the case of AnimalEncounters, the animal's earliest associated tag ID.
        Encounters with the same identifer are encounters of the same subject (e.g. the same turtle).""",
    )
    observer = models.ForeignKey(
        User,
        on_delete=models.SET_DEFAULT,
        default=settings.ADMIN_USER,
        verbose_name="Observed by",
        related_name="encounters_observed",
        help_text="The person who encountered the subject, and executed any measurements. The observer is the source of measurement bias.",
    )
    reporter = models.ForeignKey(
        User,
        on_delete=models.SET_DEFAULT,
        default=settings.ADMIN_USER,
        verbose_name="Recorded by",
        related_name="encounters_reported",
        help_text="The person who wrote the initial data sheet in the field. The reporter is the source of handwriting and spelling errors.",
    )
    as_html = models.TextField(
        verbose_name="HTML representation",
        blank=True,
        null=True,
        editable=False,
        help_text="The cached HTML representation for display purposes.",
    )
    encounter_type = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        default=ENCOUNTER_OTHER,
        choices=ENCOUNTER_TYPES,
        help_text="The primary concern of this encounter.",
    )
    comments = models.TextField(
        blank=True,
        null=True,
        help_text="Comments",
    )

    class Meta:
        ordering = ("-when",)
        unique_together = ("source", "source_id")
        get_latest_by = "when"

    @property
    def opts(self):
        """Make _meta accessible from templates."""
        return self._meta

    def __str__(self):
        return f"Encounter {self.pk} on {self.when} by {self.observer}"

    @property
    def status_colour(self):
        """Return a Bootstrap4 CSS colour class for each status."""
        return self.STATUS_LABELS[self.status]
    
    @property
    def latitude(self):
        """Return the WGS 84 DD latitude."""
        return self.where.y

    @property
    def longitude(self):
        """Return the WGS 84 DD longitude."""
        return self.where.x

    # FSM transitions --------------------------------------------------------#
    def can_curate(self):
        """Return true if this record can be accepted."""
        return True

    # New|Imported|Manual input|Flagged -> Curated
    @fsm_log_by
    @fsm_log_description
    @transition(
        field=status,
        source=[STATUS_NEW, STATUS_IMPORTED, STATUS_MANUAL_INPUT, STATUS_FLAGGED],
        target=STATUS_CURATED,
        conditions=[can_curate],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Curate as trustworthy",
            explanation=("This record is deemed trustworthy."),
            notify=True,
            url_path="curate/",
            badge="badge-success",
        ),
    )
    def curate(self, by=None, description=None):
        """Accept record as trustworthy.

        Curated data is deemed trustworthy by a subject matter expert.
        Records can be marked as curated from new, proofread, or flagged.
        """
        return

    def can_flag(self):
        """Return true if curated status can be revoked."""
        return True

    # New|Imported|Manual input|Curated -> Flagged
    @fsm_log_by
    @fsm_log_description
    @transition(
        field=status,
        source=[STATUS_NEW, STATUS_IMPORTED, STATUS_MANUAL_INPUT, STATUS_CURATED],
        target=STATUS_FLAGGED,
        conditions=[can_flag],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Flag as not trustworthy",
            explanation=(
                "This record cannot be true. This record requires"
                " review by a subject matter expert."
            ),
            notify=True,
            url_path="flag/",
            badge="badge-warning",
        ),
    )
    def flag(self, by=None, description=None):
        """Flag as requiring review by a subject matter expert.
        """
        return

    def can_reject(self):
        """Return true if the record can be rejected as entirely wrong.
        """
        return True

    # New|Imported|Manual input|Flagged -> Rejected
    @fsm_log_by
    @fsm_log_description
    @transition(
        field=status,
        source=[STATUS_NEW, STATUS_IMPORTED, STATUS_MANUAL_INPUT, STATUS_FLAGGED],
        target=STATUS_REJECTED,
        conditions=[can_reject],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Reject as not trustworthy",
            explanation=("This record is confirmed wrong and not usable."),
            notify=True,
            url_path="reject/",
            badge="badge-danger",
        ),
    )
    def reject(self, by=None, description=None):
        """Confirm that a record is confirmed wrong and not usable.
        """
        return

    # Override create and update until we have front end forms
    @classmethod
    def create_url(cls):
        """Create url. Default: app:model-create."""
        return reverse(
            "admin:{}_{}_add".format(cls._meta.app_label, cls._meta.model_name)
        )

    @property
    def update_url(self):
        """Update url. Redirects to admin update URL, as we don't have a front end form yet."""
        return self.absolute_admin_url

    @property
    def absolute_admin_url(self):
        """Return the absolute admin change URL.
        """
        return reverse("admin:{}_{}_change".format(self._meta.app_label, self._meta.model_name), args=[self.pk])

    def get_curate_url(self):
        return reverse("observations:animalencounter-curate", kwargs={"pk": self.pk})

    def get_flag_url(self):
        return reverse("observations:animalencounter-flag", kwargs={"pk": self.pk})

    # -------------------------------------------------------------------------
    # Derived properties
    def can_change(self):
        # Returns True if editing this object is permitted, False otherwise.
        # Determined by the object's QA status.
        if self.status in [
            self.STATUS_NEW,
            self.STATUS_IMPORTED,
            self.STATUS_MANUAL_INPUT,
            self.STATUS_FLAGGED,
        ]:
            return True
        return False

    def card_template(self):
        return "observations/encounter_card.html"

    @property
    def leaflet_title(self):
        """A string for Leaflet map marker titles. Cache me as field."""
        return "{} {} {}".format(
            self.when.astimezone(tz.tzlocal()).strftime("%d-%b-%Y %H:%M:%S") if self.when else "",
            self.get_encounter_type_display(),
            self.name or "",
        ).strip()

    @property
    def leaflet_icon(self):
        """Return the Fontawesome icon class for the encounter type."""
        return Encounter.LEAFLET_ICON[self.encounter_type]

    @property
    def leaflet_colour(self):
        """Return the Leaflet.awesome-markers colour for the encounter type."""
        return Encounter.LEAFLET_COLOUR[self.encounter_type]

    @property
    def tx_logs(self):
        """A list of dicts of QA timestamp, status and operator."""
        return [
            dict(
                timestamp=log.timestamp.isoformat(),
                status=log.state,
                operator=log.by.name if log.by else None,
            )
            for log in StateLog.objects.for_(self)
        ]

    def get_encounter_type(self):
        """Placeholder function. Subclasses will include logic to set the encounter type.
        """
        return self.encounter_type

    @property
    def short_name(self):
        """A short, often unique, human-readable representation of the encounter.

        Slugified and dash-separated:

        * Date of encounter as YYYY-mm-dd
        * longitude in WGS 84 DD, rounded to 4 decimals (<10m),
        * latitude in WGS 84 DD, rounded to 4 decimals (<10m), (missing sign!!)
        * health,
        * maturity,
        * species.

        The short_name could be non-unique for encounters of multiple stranded
        animals of the same species and deadness.
        """
        return slugify(
            "-".join(
                [
                    self.when.astimezone(tz.tzlocal()).strftime("%Y-%m-%d %H:%M %Z"),
                    force_str(round(self.longitude, 4)).replace(".", "-"),
                    force_str(round(self.latitude, 4)).replace(".", "-"),
                ]
            )
        )

    @property
    def date(self):
        """Return the date component of Encounter.when."""
        return self.when.date()

    @property
    def date_string(self):
        """Return the date as string."""
        return str(self.when.date())

    @property
    def datetime(self):
        """Return the full datetime of the Encounter."""
        return self.when

    @property
    def season(self):
        """Return the season of the Encounter, the start year of the fiscal year.

        Calculated as the calendar year 180 days before the date of the Encounter.
        """
        return (self.when - relativedelta(months=6)).year

    @property
    def guess_site(self):
        """Return the first site containing `where`, or None.
        """
        candidates = Area.objects.filter(area_type=Area.AREATYPE_SITE, geom__covers=self.where)
        return candidates.first() or None

    @property
    def guess_area(self):
        """Return the first locality containing `where`, or None.
        """
        candidates = Area.objects.filter(area_type=Area.AREATYPE_LOCALITY, geom__covers=self.where)
        return candidates.first() or None

    def set_name(self, name):
        """Set the animal name to a given value."""
        self.name = name
        self.save()

    @property
    def inferred_name(self):
        """Return the inferred name from related new capture if existing.
        """
        return None

    def set_name_in_related_encounters(self, name):
        """Set the animal name in all related AnimalEncounters."""
        [a.set_name(name) for a in self.related_encounters]

    def set_name_and_propagate(self, name):
        """Set the animal name in this and all related Encounters."""
        # self.set_name(name)  # already contained in next line
        self.set_name_in_related_encounters(name)

    @property
    def related_encounters(self):
        """Return all Encounters with the same Animal.

        This algorithm collects all Encounters with the same animal by
        traversing an Encounter's TagObservations and their encounter histories.

        The algorithm starts with the Encounter (``self``) as initial
        known Encounter (``known_enc``), and ``self.tags`` as both initial known
        (``known_tags``) and new TagObs (``new_tags``).
        While there are new TagObs, a "while" loop harvests new encounters:

        * For each tag in ``new_tags``, retrieve the encounter history.
        * Combine and deduplicate the encounter histories
        * Remove known encounters and call this set of encounters ``new_enc``.
        * Add ``new_enc`` to ``known_enc``.
        * Combine and deduplicate all tags of all encounters in ``new_enc`` and
          call this set of TabObservations ``new_tags``.
        * Add ``new_tags`` to ``known_tags``.
        * Repeat the loop if the list of new tags is not empty.

        Finally, deduplicate and return ``known_enc``. These are all encounters
        that concern the same animal as this (self) encounter, as proven through
        the shared presence of TagObservations.
        """
        known_enc = [
            self,
        ]
        known_tags = list(self.tags)
        new_enc = []
        new_tags = self.tags
        show_must_go_on = True

        while show_must_go_on:
            new_enc = TagObservation.encounter_histories(new_tags, without=known_enc)
            known_enc.extend(new_enc)
            new_tags = Encounter.tag_lists(new_enc)
            known_tags += new_tags
            show_must_go_on = len(new_tags) > 0

        return list(set(known_enc))

    @property
    def tags(self):
        """Return a queryset of TagObservations."""
        return self.observation_set.instance_of(TagObservation)

    @property
    def flipper_tags(self):
        """Return a queryset of Flipper and PIT Tag Observations."""
        return self.observation_set.instance_of(TagObservation).filter(
            tagobservation__tag_type__in=["flipper-tag", "pit-tag"]
        )

    @property
    def primary_flipper_tag(self):
        """Return the TagObservation of the primary (by location in animal) flipper or PIT tag."""
        return self.flipper_tags.order_by("tagobservation__tag_location").first()

    @classmethod
    def tag_lists(cls, encounter_list):
        """Return the related tags of list of encounters.

        TODO double-check performance
        """
        return list(
            set(itertools.chain.from_iterable([e.tags for e in encounter_list]))
        )

    @property
    def is_new_capture(self):
        """Return whether the Encounter is a new capture (hint: never).

        Encounters can involve tags, but are never new captures.
        AnimalEncounters override this property, as they can be new captures.
        """
        return False

    # HTML popup -------------------------------------------------------------#
    

    def get_popup(self):
        """Generate HTML popup content."""
        t = loader.get_template("popup/{}.html".format(self._meta.model_name))
        return mark_safe(t.render({"original": self}))

    def get_report(self):
        """Generate an HTML report of the Encounter."""
        t = loader.get_template("reports/{}.html".format(self._meta.model_name))
        return mark_safe(t.render({"original": self}))
    
    @property
    def wkt(self):
        """Return the point coordinates as Well Known Text (WKT)."""
        return self.where.wkt
    
    @property
    def observation_set(self):
        """Manually implement the backwards relation to the Observation model."""
        return Observation.objects.filter(encounter=self)

    @property
    def latitude(self):
        """Return the WGS 84 DD latitude."""
        return self.where.y

    @property
    def longitude(self):
        """Return the WGS 84 DD longitude."""
        return self.where.x

    @property
    def crs(self):
        """Return the location CRS."""
        return self.where.srs.name

    @property
    def status_label(self):
        """Return the boostrap tag-* CSS label flavour for the QA status."""
        return QualityControlMixin.STATUS_LABELS[self.status]

    @property
    def photographs(self):
        """Return a queryset of all attached photographs.
        """
        return MediaAttachment.objects.filter(encounter=self, media_type="photograph")

    @property
    def as_html(self):
        """An HTML representation.
        """
        t = loader.get_template("popup/{}.html".format(self._meta.model_name))
        return mark_safe(t.render({"original": self}))


class AnimalEncounter(Encounter):
    """The encounter of an animal of a species.

    Extends the base Encounter class with:

    * taxonomic group (choices), can be used to filter remaining form choices
    * species (choices)
    * sex (choices)
    * maturity (choices)
    * health (choices)
    * activity (choices)
    * behaviour (free text)
    * habitat (choices)
    """
    taxon = models.CharField(
        max_length=300,
        verbose_name="Taxonomic group",
        choices=lookups.TAXON_CHOICES,
        default=lookups.TAXON_CHOICES_DEFAULT,
        help_text="The taxonomic group of the animal.",
    )
    species = models.CharField(
        max_length=300,
        choices=lookups.SPECIES_CHOICES,
        default=lookups.NA_VALUE,
        help_text="The species of the animal.",
    )
    sex = models.CharField(
        max_length=300,
        choices=lookups.SEX_CHOICES,
        default=lookups.NA_VALUE,
        help_text="The animal's sex.",
    )
    maturity = models.CharField(
        max_length=300,
        choices=lookups.MATURITY_CHOICES,
        default=lookups.NA_VALUE,
        help_text="The animal's maturity.",
    )
    health = models.CharField(
        max_length=300,
        verbose_name="Health status",
        choices=lookups.HEALTH_CHOICES,
        default=lookups.NA_VALUE,
        help_text="The animal's physical health",
    )
    activity = models.CharField(
        max_length=300,
        choices=lookups.ACTIVITY_CHOICES,
        default=lookups.NA_VALUE,
        help_text="The animal's activity at the time of observation.",
    )
    behaviour = models.TextField(
        verbose_name="Condition and behaviour",
        blank=True,
        null=True,
        help_text="Notes on condition or behaviour.",
    )
    habitat = models.CharField(
        max_length=500,
        choices=lookups.HABITAT_CHOICES,
        default=lookups.NA_VALUE,
        help_text="The habitat in which the animal was encountered.",
    )
    sighting_status = models.CharField(
        max_length=300,
        choices=lookups.SIGHTING_STATUS_CHOICES,
        default=lookups.NA_VALUE,
        help_text="The status is inferred automatically based on whether and where this animal was processed and identified last.",
    )
    sighting_status_reason = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        help_text="The rationale for the inferred sighting status.",
    )
    identifiers = models.TextField(
        blank=True,
        null=True,
        help_text="""A space-separated list of all identifers ever recorded as associated with this animal.
        This list includes identifiers recorded only in earlier or later encounters.""",
    )
    datetime_of_last_sighting = models.DateTimeField(
        verbose_name="Last seen on",
        blank=True,
        null=True,
        help_text="""The observation datetime of this animal's last sighting, shown as local time
        (no daylight savings), stored as UTC. Blank if the animal has never been seen before.""",
    )
    site_of_last_sighting = models.ForeignKey(
        Area,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="encounter_last_sighting",
        verbose_name="Last seen at",
        help_text="The Site in which the animal was encountered last.",
    )
    site_of_first_sighting = models.ForeignKey(
        Area,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="encounter_first_sighting",
        verbose_name="First seen at",
        help_text="The Site in which the animal was encountered first.",
    )
    nesting_event = models.CharField(  # TODO rename to nesting_success
        max_length=300,
        verbose_name="Nesting success",
        choices=lookups.NESTING_SUCCESS_CHOICES,
        default=lookups.NA_VALUE,
        help_text="What indication of nesting success was observed?",
    )
    nesting_disturbed = models.CharField(
        max_length=300,
        choices=lookups.OBSERVATION_CHOICES,
        default=lookups.NA_VALUE,
        help_text="Was the nesting interrupted? If so, specify disturbance in comments.",
    )
    laparoscopy = models.BooleanField(
        max_length=300,
        verbose_name="Laparoscopy conducted",
        default=False,
        help_text="Was the animal's sex and maturity determined through laparoscopy?",
    )
    checked_for_injuries = models.CharField(
        max_length=300,
        choices=lookups.OBSERVATION_CHOICES,
        default=lookups.NA_VALUE,
        help_text="Was the animal checked for injuries, were any found?",
    )
    scanned_for_pit_tags = models.CharField(
        max_length=300,
        verbose_name="Scanned for PIT tags",
        choices=lookups.OBSERVATION_CHOICES,
        default=lookups.NA_VALUE,
        help_text="Was the animal scanned for PIT tags, were any found?",
    )
    checked_for_flipper_tags = models.CharField(
        max_length=300,
        choices=lookups.OBSERVATION_CHOICES,
        default=lookups.NA_VALUE,
        help_text="Was the animal checked for flipper tags, were any found?",
    )
    cause_of_death = models.CharField(
        max_length=300,
        choices=lookups.CAUSE_OF_DEATH_CHOICES,
        default=lookups.NA_VALUE,
        help_text="If dead, is the case of death known?",
    )
    cause_of_death_confidence = models.CharField(
        max_length=300,
        choices=lookups.CONFIDENCE_CHOICES,
        default=lookups.NA_VALUE,
        help_text="What is the cause of death, if known, based on?",
    )

    def __str__(self):
        tpl = "AnimalEncounter {} on {} by {} of {}, {} {} {} on {}"
        return tpl.format(
            self.pk,
            self.when.astimezone(tz.tzlocal()).strftime("%Y-%m-%d %H:%M %Z"),
            self.observer.name,
            self.get_species_display(),
            self.get_health_display(),
            self.get_maturity_display(),
            self.get_sex_display(),
            self.get_habitat_display(),
        )

    def get_encounter_type(self):
        """Infer the encounter type.

        AnimalEncounters are either in water, tagging or stranding encounters.
        If the animal is dead (at various decompositional stages), a stranding
        is assumed.
        In water captures happen if the habitat is in the list of aquatic
        habitats.
        Remaining encounters are assumed to be taggings, as other encounters are
        excluded. Note that an animal encountered in water, or even a dead
        animal (whether that makes sense or not) can also be tagged.
        """
        # Return any existing type, if set.
        if self.encounter_type:
            return self.encounter_type

        if self.nesting_event in lookups.NESTING_PRESENT:
            return Encounter.ENCOUNTER_TAGGING
        elif self.health in lookups.DEATH_STAGES:
            return Encounter.ENCOUNTER_STRANDING
        elif self.habitat in lookups.HABITAT_WATER:
            # This will ignore inwater encounters without habitat
            return Encounter.ENCOUNTER_INWATER
        else:
            # Not stranding or in water, fall back to 'other'
            return Encounter.ENCOUNTER_OTHER

    @property
    def short_name(self):
        """A short, often unique, human-readable representation of the encounter.

        Slugified and dash-separated:

        * Date of encounter as YYYY-mm-dd
        * longitude in WGS 84 DD, rounded to 4 decimals (<10m),
        * latitude in WGS 84 DD, rounded to 4 decimals (<10m), (missing sign!!)
        * health,
        * maturity,
        * species,
        * name if available (requires "update names" and tag obs)

        The short_name could be non-unique for encounters of multiple stranded
        animals of the same species and deadness.
        """
        nameparts = [
            self.when.astimezone(tz.tzlocal()).strftime("%Y-%m-%d %H:%M %Z"),
            force_str(round(self.longitude, 4)).replace(".", "-"),
            force_str(round(self.latitude, 4)).replace(".", "-"),
            self.health,
            self.maturity,
            self.sex,
            self.species,
        ]
        if self.name is not None:
            nameparts.append(self.name)
        return slugify("-".join(nameparts))


    @property
    def is_stranding(self):
        """Return whether the Encounters is stranding or tagging.

        If the animal is not "alive", it's a stranding encounter, else it's a
        tagging encounter.
        """
        return self.health != "alive"

    @property
    def is_new_capture(self):
        """Return whether this Encounter is a new capture.

        New captures are named after their primary flipper tag.
        An Encounter is a new capture if there are:

        * no associated TagObservations of ``is_recapture`` status
        * at least one associated TabObservation of ``is_new`` status
        """
        new_tagobs = set([x for x in self.flipper_tags if x.is_new])
        old_tagobs = set([x for x in self.flipper_tags if x.is_recapture])
        has_new_tagobs = len(new_tagobs) > 0
        has_old_tagobs = len(old_tagobs) > 0
        return has_new_tagobs and not has_old_tagobs

    def get_absolute_url(self):
        return reverse("observations:animalencounter-detail", kwargs={"pk": self.pk})

    def get_card_title(self):
        title = "{} {} {}".format(
            self.get_health_display(),
            self.get_maturity_display().lower(),
            self.get_species_display(),
        )
        if self.sighting_status != "na":
            title += " {self.get_sighting_status_display()}"
        return title

    def card_template(self):
        return "observations/animalencounter_card.html"

    def get_tag_observations(self):
        """Return a queryset of TagObservations.
        """
        return self.observation_set.instance_of(TagObservation)

    def get_tag_serials(self):
        """Return a comma-separated list of tag serials observed during this encounter.
        """
        tag_observations = self.get_tag_observations()
        if tag_observations:
            return ", ".join([tag.name for tag in tag_observations])
        else:
            return ""


class TurtleNestEncounter(Encounter):
    """The encounter of turtle nest during its life cycle.
    May represent a track with no nest, and track & nest, or a nest with no track.

    The observations are assumed to follow DBCA protocol.
    TurtleNestEncouters by third parties can be recorded, but related
    observations cannot if they don't follow DBCA protocol.

    Stages:

    * false crawl (aborted nesting attempt)
    * new (turtle is present, observed during nesting/tagging)
    * fresh (morning after, observed during track count)
    * predated (nest and eggs destroyed by predator)
    * hatched (eggs hatched)
    """
    nest_age = models.CharField(
        max_length=300,
        verbose_name="Age",
        choices=lookups.NEST_AGE_CHOICES,
        default=lookups.NEST_AGE_DEFAULT,
        help_text="The track or nest age.",
    )
    nest_type = models.CharField(
        max_length=300,
        verbose_name="Type",
        choices=lookups.NEST_TYPE_CHOICES,
        default=lookups.NEST_TYPE_DEFAULT,
        help_text="The track or nest type.",
    )
    species = models.CharField(
        max_length=300,
        choices=lookups.TURTLE_SPECIES_CHOICES,
        default=lookups.TURTLE_SPECIES_DEFAULT,
        help_text="The species of the animal which created the track or nest.",
    )
    habitat = models.CharField(
        max_length=500,
        choices=lookups.BEACH_POSITION_CHOICES,
        default=lookups.NA_VALUE,
        help_text="The habitat in which the track or nest was encountered.",
    )
    disturbance = models.CharField(
        max_length=300,
        verbose_name="Evidence of predation or disturbance",
        choices=lookups.OBSERVATION_CHOICES,
        default=lookups.NA_VALUE,
        help_text="Is there evidence of predation or other disturbance?",
    )
    nest_tagged = models.CharField(
        max_length=300,
        verbose_name="Nest tag present",
        choices=lookups.OBSERVATION_CHOICES,
        default=lookups.NA_VALUE,
        help_text="Was a nest tag applied, re-sighted, or otherwise encountered?",
    )
    logger_found = models.CharField(
        max_length=300,
        verbose_name="Logger present",
        choices=lookups.OBSERVATION_CHOICES,
        default=lookups.NA_VALUE,
        help_text="Was a data logger deployed, retrieved, or otherwise encountered?",
    )
    eggs_counted = models.CharField(
        max_length=300,
        verbose_name="Nest excavated and eggs counted",
        choices=lookups.OBSERVATION_CHOICES,
        default=lookups.NA_VALUE,
        help_text="Was the nest excavated and were turtle eggs counted?",
    )
    hatchlings_measured = models.CharField(
        max_length=300,
        choices=lookups.OBSERVATION_CHOICES,
        default=lookups.NA_VALUE,
        help_text="Were turtle hatchlings encountered and their morphometrics measured?",
    )
    fan_angles_measured = models.CharField(
        max_length=300,
        verbose_name="Hatchling emergence recorded",
        choices=lookups.OBSERVATION_CHOICES,
        default=lookups.NA_VALUE,
        help_text="Were hatchling emergence track fan angles recorded?",
    )

    def __str__(self):
        return f"{self.pk}: {self.get_nest_type_display()}, {self.get_nest_age_display().lower()}, {self.get_species_display()}"

    def get_encounter_type(self):
        # Return any existing type, if set.
        if self.encounter_type:
            return self.encounter_type

        if self.nest_type in ["successful-crawl", "nest", "hatched-nest"]:
            return Encounter.ENCOUNTER_NEST
        else:
            return Encounter.ENCOUNTER_TRACKS

    @property
    def short_name(self):
        """A short, often unique, human-readable representation of the encounter.

        Slugified and dash-separated:

        * Date of encounter as YYYY-mm-dd
        * longitude in WGS 84 DD, rounded to 4 decimals (<10m),
        * latitude in WGS 84 DD, rounded to 4 decimals (<10m), (missing sign!!)
        * nest age (type),
        * species,
        * name if available (requires "update names" and tag obs)

        The short_name could be non-unique.
        """
        nameparts = [
            self.when.astimezone(tz.tzlocal()).strftime("%Y-%m-%d %H:%M %Z"),
            force_str(round(self.longitude, 4)).replace(".", "-"),
            force_str(round(self.latitude, 4)).replace(".", "-"),
            self.nest_age,
            self.species,
        ]
        if self.name is not None:
            nameparts.append(self.name)
        return slugify("-".join(nameparts))

    @property
    def inferred_name(self):
        """Return the first NestTag name or None."""
        nest_tag = self.observation_set.instance_of(NestTagObservation).first()
        if nest_tag:
            return nest_tag.name
        else:
            return None

    def get_absolute_url(self):
        return reverse(
            "observations:turtlenestencounter-detail", kwargs={"pk": self.pk}
        )

    def get_curate_url(self):
        return reverse("observations:turtlenestencounter-curate", kwargs={"pk": self.pk})

    def get_flag_url(self):
        return reverse("observations:turtlenestencounter-flag", kwargs={"pk": self.pk})

    def card_template(self):
        return "observations/turtlenestencounter_card.html"

    def get_nest_observation(self):
        """A turtle nest encounter should be associated with 0-1 nest observation objects.
        Returns the related turtle nest observation or None.
        """
        observation = self.observation_set.instance_of(TurtleNestObservation).first()
        return observation

    def get_nesttag_observation(self):
        """A turtle nest encounter should be associated with 0-1 NestTagObservation objects.
        Returns the related NestTagObservation or None.
        """
        
        observation = self.observation_set.instance_of(NestTagObservation).first()
        return observation

    def get_hatchling_emergence_observation(self):
        """A turtle nest encounter should be associated with 0-1 TurtleHatchlingEmergenceObservation objects.
        Returns the related TurtleHatchlingEmergenceObservation or None.
        """
        observation = self.observation_set.instance_of(TurtleHatchlingEmergenceObservation).first()
        return observation


class Observation(PolymorphicModel, LegacySourceMixin, models.Model):
    """The Observation base class for encounter observations.

    Everything happens somewhere, at a time, to someone, and someone records it.
    Therefore, an Observation must happen during an Encounter.
    """

    encounter = models.ForeignKey(
        Encounter,
        on_delete=models.CASCADE,
        related_name="observations",
        help_text="The Encounter during which the observation was made",
    )

    def __str__(self):
        return f"Observation {self.pk} for {self.encounter}"

    @property
    def point(self):
        """Return the encounter location."""
        return self.encounter.where

    @property
    def as_html(self):
        """An HTML representation."""
        t = loader.get_template("popup/{}.html".format(self._meta.model_name))
        return mark_safe(t.render({"original": self}))

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
    def latitude(self):
        """The encounter's latitude."""
        return self.encounter.where.y or ""

    @property
    def longitude(self):
        """The encounter's longitude."""
        return self.encounter.where.x or ""

    def datetime(self):
        """The encounter's timestamp."""
        return self.encounter.when or ""

    @property
    def absolute_admin_url(self):
        """Return the absolute admin change URL.
        """
        return reverse("admin:{}_{}_change".format(self._meta.app_label, self._meta.model_name), args=[self.pk])


class MediaAttachment(Observation):
    """A media attachment to an Encounter.
    """
    MEDIA_TYPE_CHOICES = (
        ("data_sheet", "Data sheet"),
        ("communication", "Communication record"),
        ("photograph", "Photograph"),
        ("other", "Other"),
    )

    media_type = models.CharField(
        max_length=300,
        verbose_name="Attachment type",
        choices=MEDIA_TYPE_CHOICES,
        default="photograph",
        help_text="What is the attached file about?",
    )

    title = models.CharField(
        max_length=300,
        verbose_name="Attachment name",
        blank=True,
        null=True,
        help_text="Give the attachment a representative name",
    )

    attachment = models.FileField(
        upload_to=encounter_media,
        max_length=500,
        verbose_name="File attachment",
        help_text="Upload the file",
    )

    def __str__(self):
        return f"Media attachment {self.pk} for encounter {self.encounter.pk}: {self.attachment.name}"

    @property
    def filepath(self):
        """The path to attached file."""
        try:
            fpath = force_str(self.attachment.file)
        except BaseException:
            fpath = None
        return fpath

    @property
    def thumbnail(self):
        if self.attachment:
            return mark_safe(
                '<a href="{0}" target="_" rel="nofollow" '
                'title="Click to view full screen in new browser tab">'
                '<img src="{0}" alt="{1} {2}" style="height:100px;"></img>'
                "</a>".format(
                    self.attachment.url, self.get_media_type_display(), self.title
                )
            )
        else:
            return ""


class TagObservation(Observation):
    """An Observation of an identifying tag on an observed entity.

    The identifying tag can be a flipper tag on a turtle, a PIT tag,
    a satellite tag, a whisker ID from a picture of a pinniped,
    a genetic fingerprint or similar.

    The tag has its own life cycle through stages of production, delivery,
    affiliation with an animal, repeated sightings and disposal.

    The life cycle stages will vary between tag types.

    A TagObservation will find the tag in exactly one of the life cycle stages.

    The life history of each tag can be reconstructed from the sum of all of its
    TagObservations.

    As TagObservations can sometimes occur without an Observation of an animal,
    the FK to Observations is optional.

    Flipper Tag Status as per WAMTRAM:

    * # = tag attached new, number NA, need to double-check number
    * P, p: re-sighted as attached to animal, no actions taken or necessary
    * do not use: 0L, A2, M, M1, N
    * AE = A1
    * P_ED = near flipper edge, might fall off soon
    * PX = tag re-sighted, but operator could not read tag ID
      (e.g. turtle running off)
    * RQ = tag re-sighted, tag was "insecure", but no action was recorded

    Recaptured tags: Need to record state (open, closed, tip locked or not)
    as feedback to taggers to improve their tagging technique.

    PIT tag status:

    * applied and did read OK
    * applied and did not read (but still inside and might read later on)

    Animal Name:
    All TagObservations of one animal are linked by shared encounters or
    shared tag names. The earliest associated flipper tag name is used as the
    animal's name, and transferred onto all related TagObservations.
    """
    tag_type = models.CharField(
        max_length=300,
        choices=lookups.TAG_TYPE_CHOICES,
        default="flipper-tag",
        help_text="What kind of tag is it?",
    )
    tag_location = models.CharField(
        max_length=300,
        choices=lookups.TURTLE_BODY_PART_CHOICES,
        default=lookups.BODY_PART_DEFAULT,
        help_text="Where is the tag attached?",
    )
    name = models.CharField(
        max_length=1000,
        verbose_name="Tag ID",
        help_text="The ID/serial number of the tag",
        db_index=True,
    )
    status = models.CharField(
        max_length=300,
        verbose_name="Tag status",
        choices=lookups.TAG_STATUS_CHOICES,
        default=lookups.TAG_STATUS_DEFAULT,
        help_text="The status this tag was after the encounter.",
    )
    handler = models.ForeignKey(
        User,
        on_delete=models.SET_DEFAULT,
        default=settings.ADMIN_USER,
        blank=True,
        null=True,
        verbose_name="Handled by",
        related_name="tag_handler",
        help_text="The person in physical contact with the tag",
    )
    recorder = models.ForeignKey(
        User,
        on_delete=models.SET_DEFAULT,
        default=settings.ADMIN_USER,
        blank=True,
        null=True,
        verbose_name="Recorded by",
        related_name="tag_recorder",
        help_text="The person who records the tag observation",
    )
    comments = models.TextField(
        blank=True,
        null=True,
        help_text="Any other comments or notes.",
    )

    def __str__(self):
        return "{} {} {} on {}".format(
            self.get_tag_type_display(),
            self.name,
            self.get_status_display(),
            self.get_tag_location_display(),
        )

    @classmethod
    def encounter_history(cls, tagname):
        """Return the related encounters of all TagObservations of a given tag name."""
        return list(set([t.encounter for t in cls.objects.filter(name=tagname)]))

    @classmethod
    def encounter_histories(cls, tagname_list, without=[]):
        """Return the related encounters of all tag names.
        """
        return [
            encounter
            for encounter in list(
                set(
                    itertools.chain.from_iterable(
                        [TagObservation.encounter_history(t.name) for t in tagname_list]
                    )
                )
            )
            if encounter not in without
        ]

    @property
    def is_new(self):
        """Return whether the TagObservation is the first association with the animal.
        """
        return self.status == lookups.TAG_STATUS_APPLIED_NEW

    @property
    def is_recapture(self):
        """Return whether the TabObservation is a recapture."""
        return self.status in lookups.TAG_STATUS_RESIGHTED

    @property
    def history_url(self):
        """The list view of all observations of this tag."""
        cl = reverse("admin:observations_tagobservation_changelist")
        return "{0}?q={1}".format(cl, urllib.parse.quote_plus(self.name))


class NestTagObservation(Observation):
    """Turtle Nest Tag Observation.

    TNTs consist of three components, which are all optional:

    * flipper_tag_id: The primary flipper tag ID of the nesting turtle
    * date_nest_laid: The calendar (not turtle) date of nest creation
    * tag_label: Any extra nest label if other two components not available

    Naming scheme:

    * Uppercase and remove whitespace from flipper tag ID
    * date nest laid: YYYY-mm-dd
    * Uppercase and remove whitespace from tag label
    * Join all with "_"

    E.g.: WA1234_2017-12-31_M1
    """
    status = models.CharField(
        max_length=300,
        verbose_name="Tag status",
        choices=lookups.NEST_TAG_STATUS_CHOICES,
        default=lookups.TAG_STATUS_DEFAULT,
        help_text="The status this tag was seen in, or brought into.",
    )
    flipper_tag_id = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name="Flipper tag ID",
        help_text="The primary flipper tag ID of the nesting turtle if available.",
    )
    date_nest_laid = models.DateField(
        blank=True,
        null=True,
        help_text="The calendar (not turtle) date of nest creation.",
    )
    tag_label = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        help_text="Any extra nest label if other two components are not available.",
    )
    comments = models.TextField(
        blank=True,
        null=True,
        help_text="Any other comments or notes.",
    )

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    @property
    def history_url(self):
        """The list view of all observations of this tag."""
        cl = reverse("admin:observations_nesttagobservation_changelist")
        if self.flipper_tag_id:
            return "{0}?q={1}".format(cl, urllib.parse.quote_plus(self.flipper_tag_id))
        else:
            return cl

    @property
    def name(self):
        """Return the nest tag name according to the naming scheme."""
        return "_".join(
            [
                ("" if not self.flipper_tag_id else self.flipper_tag_id)
                .upper()
                .replace(" ", ""),
                "" if not self.date_nest_laid else str(self.date_nest_laid),
                "" if not self.tag_label else self.tag_label.upper().replace(" ", ""),
            ]
        )


class ManagementAction(Observation):
    """
    Management actions following an AnimalEncounter.

    E.g, disposal, rehab, euthanasia.
    """

    management_actions = models.TextField(
        blank=True,
        null=True,
        help_text="Managment actions taken. Keep updating as appropriate.",
    )
    comments = models.TextField(
        blank=True,
        null=True,
        help_text="Any other comments or notes.",
    )

    def __str__(self):
        return f"Management action {self.pk} of {self.encounter}"


class TurtleMorphometricObservation(Observation):
    """Morphometric measurements of a turtle.
    """
    curved_carapace_length_mm = models.PositiveIntegerField(
        verbose_name="Curved carapace length max (mm)",
        blank=True,
        null=True,
        help_text="The curved carapace length (max) in millimetres.",
    )
    curved_carapace_length_accuracy = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        choices=lookups.ACCURACY_CHOICES,
        verbose_name="Curved carapace length (max) accuracy",
        help_text="The expected measurement accuracy.",
    )
    curved_carapace_length_min_mm = models.PositiveIntegerField(
        verbose_name="Curved carapace length min (mm)",
        blank=True,
        null=True,
        help_text="The curved carapace length (min) in millimetres.",
    )
    curved_carapace_length_min_accuracy = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        choices=lookups.ACCURACY_CHOICES,
        verbose_name="Curved carapace length accuracy",
        help_text="The expected measurement accuracy.",
    )
    straight_carapace_length_mm = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Straight carapace length (mm)",
        help_text="The straight carapace length in millimetres.",
    )
    straight_carapace_length_accuracy = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        choices=lookups.ACCURACY_CHOICES,
        verbose_name="Straight carapace length accuracy",
        help_text="The expected measurement accuracy.",
    )
    curved_carapace_width_mm = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Curved carapace width (mm)",
        help_text="Curved carapace width in millimetres.",
    )
    curved_carapace_width_accuracy = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        choices=lookups.ACCURACY_CHOICES,
        verbose_name="Curved carapace width (mm)",
        help_text="The expected measurement accuracy.",
    )
    tail_length_carapace_mm = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Tail length from carapace (mm)",
        help_text="The tail length in millimetres, measured from carapace to tip.",
    )
    tail_length_carapace_accuracy = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        choices=lookups.ACCURACY_CHOICES,
        verbose_name="Tail length from carapace accuracy",
        help_text="The expected measurement accuracy.",
    )
    tail_length_vent_mm = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Tail length from vent (mm)",
        help_text="The tail length in millimetres, measured from vent to tip.",
    )
    tail_length_vent_accuracy = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        choices=lookups.ACCURACY_CHOICES,
        verbose_name="Tail Length Accuracy",
        help_text="The expected measurement accuracy.",
    )
    tail_length_plastron_mm = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Tail length from plastron (mm)",
        help_text="The tail length in millimetres, measured from plastron to tip.",
    )
    tail_length_plastron_accuracy = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        choices=lookups.ACCURACY_CHOICES,
        verbose_name="Tail length from plastron accuracy",
        help_text="The expected measurement accuracy.",
    )
    maximum_head_width_mm = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Maximum head width (mm)",
        help_text="The maximum head width in millimetres.",
    )
    maximum_head_width_accuracy = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        choices=lookups.ACCURACY_CHOICES,
        verbose_name="Maximum head width accuracy",
        help_text="The expected measurement accuracy.",
    )
    maximum_head_length_mm = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Maximum head length (mm)",
        help_text="The maximum head length in millimetres.",
    )
    maximum_head_length_accuracy = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        choices=lookups.ACCURACY_CHOICES,
        verbose_name="Maximum head length accuracy",
        help_text="The expected measurement accuracy.",
    )
    body_depth_mm = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Body depth (mm)",
        help_text="The body depth, plastron to carapace, in millimetres.",
    )
    body_depth_accuracy = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        choices=lookups.ACCURACY_CHOICES,
        verbose_name="Body depth accuracy",
        help_text="The expected measurement accuracy.",
    )
    body_weight_g = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Body weight (g)",
        help_text="The body weight in grams (1000 g = 1kg).",
    )
    body_weight_accuracy = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        choices=lookups.ACCURACY_CHOICES,
        verbose_name="Body weight accuracy",
        help_text="The expected measurement accuracy.",
    )
    handler = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="morphometric_handler",
        verbose_name="Measured by",
        help_text="The person conducting the measurements.",
    )
    recorder = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="morphometric_recorder",
        verbose_name="Recorded by",
        help_text="The person recording the measurements.",
    )

    def __str__(self):
        return "Turtle morphometrics {}: CCL {} CCW {} for encounter {}".format(
            self.pk,
            self.curved_carapace_length_mm,
            self.curved_carapace_width_mm,
            self.encounter.pk,
        )


class HatchlingMorphometricObservation(Observation):
    """Morphometric measurements of a hatchling at a TurtleNestEncounter.
    """
    straight_carapace_length_mm = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Straight carapace length (mm)",
        help_text="The straight carapace length in millimetres.",
    )
    straight_carapace_width_mm = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Straight carapace width (mm)",
        help_text="The straight carapace width in millimetres.",
    )
    body_weight_g = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Body weight (g)",
        help_text="The body weight in grams (1000 g = 1kg).",
    )

    def __str__(self):
        return f"{self.pk} Hatchling SCL {self.straight_carapace_length_mm} mm, SCW {self.straight_carapace_width_mm} mm, Wt {self.body_weight_g} g"


class TurtleDamageObservation(Observation):
    """Observations of turtle damage or injuries.
    """
    body_part = models.CharField(
        max_length=300,
        default="whole-turtle",
        verbose_name="Affected body part",
        choices=lookups.TURTLE_BODY_PART_CHOICES,
        help_text="The body part affected by the observed damage.",
    )
    damage_type = models.CharField(
        max_length=300,
        default="minor-trauma",
        choices=lookups.DAMAGE_TYPE_CHOICES,
        help_text="The type of the damage.",
    )
    damage_age = models.CharField(
        max_length=300,
        default="healed-entirely",
        choices=lookups.DAMAGE_AGE_CHOICES,
        help_text="The age of the damage.",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="A description of the damage.",
    )

    def __str__(self):
        return "{}: {} {}".format(
            self.get_body_part_display(),
            self.get_damage_age_display(),
            self.get_damage_type_display(),
        )


class TurtleNestObservation(Observation):
    """Turtle nest observation

    This model supports data sheets for:

    * Turtle nest observation during tagging
    * Turtle nest excavation after hatching

    Egg count is done as total, plus categories of nest contents following
    "Determining Clutch Size and Hatching Success, Jeffrey D. Miller,
    Research and Management Techniques for the Conservation of Sea Turtles,
    IUCN Marine Turtle Specialist Group, 1999.
    """
    eggs_laid = models.BooleanField(
        verbose_name="Did the turtle lay eggs?",
        default=False,
    )
    egg_count = models.PositiveIntegerField(
        verbose_name="Total number of eggs laid",
        blank=True,
        null=True,
        help_text="The total number of eggs laid as observed during tagging.",
    )
    no_egg_shells = models.PositiveIntegerField(
        verbose_name="Egg shells (S)",
        blank=True,
        null=True,
        help_text="The number of empty shells counted which were more than 50 percent complete.",
    )
    no_live_hatchlings_neck_of_nest = models.PositiveIntegerField(
        verbose_name="Live hatchlings in neck of nest",
        blank=True,
        null=True,
        help_text="The number of live hatchlings in the neck of the nest.",
    )
    no_live_hatchlings = models.PositiveIntegerField(
        verbose_name="Live hatchlings in nest (L)",
        blank=True,
        null=True,
        help_text="The number of live hatchlings left among shells excluding those in neck of nest.",
    )
    no_dead_hatchlings = models.PositiveIntegerField(
        verbose_name="Dead hatchlings (D)",
        blank=True,
        null=True,
        help_text="The number of dead hatchlings that have left" " their shells.",
    )
    no_undeveloped_eggs = models.PositiveIntegerField(
        verbose_name="Undeveloped eggs (UD)",
        blank=True,
        null=True,
        help_text="The number of unhatched eggs with no obvious embryo.",
    )
    no_unhatched_eggs = models.PositiveIntegerField(
        verbose_name="Unhatched eggs (UH)",
        blank=True,
        null=True,
        help_text="The number of unhatched eggs with obvious, not yet full term, embryo.",
    )
    no_unhatched_term = models.PositiveIntegerField(
        verbose_name="Unhatched term (UHT)",
        blank=True,
        null=True,
        help_text="The number of unhatched, apparently full term, embryo in egg or pipped with small amount of external yolk material.",
    )
    no_depredated_eggs = models.PositiveIntegerField(
        verbose_name="Depredated eggs (P)",
        blank=True,
        null=True,
        help_text="The number of open, nearly complete shells containing egg residue.",
    )
    nest_depth_top = models.PositiveIntegerField(
        verbose_name="Nest depth (top) mm",
        blank=True,
        null=True,
        help_text="The depth of sand above the eggs in mm.",
    )
    nest_depth_bottom = models.PositiveIntegerField(
        verbose_name="Nest depth (bottom) mm",
        blank=True,
        null=True,
        help_text="The depth of the lowest eggs in mm.",
    )
    sand_temp = models.FloatField(
        verbose_name="Sand temperature",
        blank=True,
        null=True,
        help_text="The sand temperature in degree Celsius.",
    )
    air_temp = models.FloatField(
        verbose_name="Air temperature",
        blank=True,
        null=True,
        help_text="The air temperature in degree Celsius.",
    )
    water_temp = models.FloatField(
        verbose_name="Water temperature",
        blank=True,
        null=True,
        help_text="The water temperature in degree Celsius.",
    )
    egg_temp = models.FloatField(
        verbose_name="Egg temperature",
        blank=True,
        null=True,
        help_text="The egg temperature in degree Celsius.",
    )
    comments = models.TextField(
        blank=True,
        null=True,
        help_text="Any other comments or notes.",
    )

    def __str__(self):
        return f"Nest Obs {self.egg_count} eggs, hatching succ {self.hatching_success}, emerg succ {self.emergence_success}"

    @property
    def no_emerged(self):
        """The number of hatchlings leaving or departed from nest is S-(L+D)."""
        return (
            (self.no_egg_shells or 0)
            - (self.no_live_hatchlings or 0)
            - (self.no_dead_hatchlings or 0)
        )

    @property
    def egg_count_calculated(self):
        """The calculated egg count from nest excavations.

        Calculated as:

        no_egg_shells + no_undeveloped_eggs + no_unhatched_eggs +
        no_unhatched_term + no_depredated_eggs
        """
        return (
            (self.no_egg_shells or 0)
            + (self.no_undeveloped_eggs or 0)
            + (self.no_unhatched_eggs or 0)
            + (self.no_unhatched_term or 0)
            + (self.no_depredated_eggs or 0)
        )

    @property
    def hatching_success(self):
        """Return the hatching success as percentage [0..100].

        Formula after Miller 1999::

            Hatching success = 100 * no_egg_shells / (
                no_egg_shells + no_undeveloped_eggs + no_unhatched_eggs +
                no_unhatched_term + no_depredated_eggs)
        """
        if self.egg_count_calculated == 0:
            return
        else:
            return round(100 * (self.no_egg_shells or 0) / self.egg_count_calculated, 1)

    @property
    def emergence_success(self):
        """Return the emergence success as percentage [0..100].

        Formula after Miller 1999::

            Emergence success = 100 *
                (no_egg_shells - no_live_hatchlings - no_dead_hatchlings) / (
                no_egg_shells + no_undeveloped_eggs + no_unhatched_eggs +
                no_unhatched_term + no_depredated_eggs)
        """
        if self.egg_count_calculated == 0:
            return
        else:
            return round(
                100
                * (
                    (self.no_egg_shells or 0)
                    - (self.no_live_hatchlings or 0)
                    - (self.no_dead_hatchlings or 0)
                )
                / self.egg_count_calculated,
                1,
            )


class TurtleNestDisturbanceObservation(Observation):
    """Turtle nest disturbance observations.

    Disturbance can be a result of:

    * Predation
    * Disturbance by other turtles
    * Environmental disturbance (cyclones, tides)
    * Anthropogenic disturbance (vehicle damage, poaching, research, harvest)

    Disturbance severity can range from negligible disturbance to total destruction.

    Disturbance cause contains a training category to mark training or test records.
    """

    NEST_VIABILITY_CHOICES = (
        ("negligible", "negligible disturbance"),
        ("partly", "nest partly destroyed"),
        ("completely", "nest completely destroyed"),
        (lookups.NA_VALUE, "nest in indeterminate condition"),
    )

    disturbance_cause = models.CharField(
        max_length=300,
        choices=lookups.NEST_DAMAGE_CHOICES,
        help_text="The cause of the disturbance.",
    )
    disturbance_cause_confidence = models.CharField(
        max_length=300,
        verbose_name="Disturbance cause choice confidence",
        choices=lookups.CONFIDENCE_CHOICES,
        default=lookups.NA_VALUE,
        help_text="What is the choice of disturbance cause based on?",
    )
    disturbance_severity = models.CharField(
        max_length=300,
        choices=NEST_VIABILITY_CHOICES,
        default=lookups.NA_VALUE,
        help_text="The impact of the disturbance on nest viability.",
    )
    comments = models.TextField(
        blank=True,
        null=True,
        help_text="Any other comments or notes.",
    )

    def __str__(self):
        return f"{self.pk}: Nest disturbance {self.disturbance_severity} by {self.disturbance_cause}"


class TurtleTrackObservation(Observation):
    """Observation measurements for measurements of the track of a (normally) unidentified
    turtle species.
    """
    max_track_width_front = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Maximum distance between sand touched by front flippers, measured in mm.",
    )
    max_track_width_rear = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Maximum distance between sand touched by rear flippers, measured in mm.",
    )
    carapace_drag_width = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Carapace drag width, measured in mm.",
    )
    step_length = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Distance with front flipper marks, measured in mm",
    )
    tail_pokes = models.CharField(
        blank=True,
        null=True,
        max_length=300,
        choices=lookups.TAIL_POKE_CHOICES,
        help_text="Are regular dips in the middle of the track present?",
    )

    def __str__(self):
        return f"Track front width {self.max_track_width_front} mm"


class TurtleHatchlingEmergenceObservation(Observation):
    """Turtle hatchling emergence observation.

    Hatchling emergence observations can include:

    * Emergence time (if seen directly),
    * Fan angles of hatchling tracks forming a fan from nest to sea,
    * Emergence climate
    * Outliers present (if yes: TurtleHatchlingEmergenceOutlierObservation)
    * Light sources known and present (if yes: LightSourceObservation).
    """
    bearing_to_water_degrees = models.FloatField(
        verbose_name="Bearing to water",
        blank=True,
        null=True,
        help_text="Bearing captured with handheld compass.",
    )
    bearing_leftmost_track_degrees = models.FloatField(
        verbose_name="Leftmost track bearing of main fan",
        blank=True,
        null=True,
        help_text="Excluding outlier tracks, 5m from nest or at HWM. Bearing captured with handheld compass.",
    )
    bearing_rightmost_track_degrees = models.FloatField(
        verbose_name="Rightmost track bearing of main fan",
        blank=True,
        null=True,
        help_text="Excluding outlier tracks, 5m from nest or at HWM. Bearing captured with handheld compass.",
    )
    no_tracks_main_group = models.PositiveIntegerField(
        verbose_name="Number of tracks in main fan",
        blank=True,
        null=True,
        help_text="Exact count or best estimate.",
    )
    no_tracks_main_group_min = models.PositiveIntegerField(
        verbose_name="Min number of tracks in main fan",
        blank=True,
        null=True,
        help_text="Lowest estimate.",
    )
    no_tracks_main_group_max = models.PositiveIntegerField(
        verbose_name="Max number of tracks in main fan",
        blank=True,
        null=True,
        help_text="Highest estimate.",
    )
    outlier_tracks_present = models.CharField(
        max_length=300,
        choices=lookups.OBSERVATION_CHOICES,
        default=lookups.NA_VALUE,
    )
    path_to_sea_comments = models.TextField(
        verbose_name="Hatchling path to sea comments",
        blank=True,
        null=True,
        help_text="Any other comments or notes.",
    )
    hatchling_emergence_time_known = models.CharField(
        max_length=300,
        choices=(
            (lookups.NA_VALUE, "NA"),
            ("yes", "Yes"),
            ("no", "No"),
        ),
        default=lookups.NA_VALUE,
    )
    cloud_cover_at_emergence_known = models.CharField(
        max_length=300,
        choices=(
            (lookups.NA_VALUE, "NA"),
            ("yes", "Yes"),
            ("no", "No"),
        ),
        default=lookups.NA_VALUE,
    )
    light_sources_present = models.CharField(
        max_length=300,
        verbose_name="Light sources present during emergence",
        choices=lookups.OBSERVATION_CHOICES,
        default=lookups.NA_VALUE,
    )
    hatchling_emergence_time = models.DateTimeField(
        blank=True,
        null=True,
        help_text="The estimated time of hatchling emergence, stored as UTC and shown in local time.",
    )
    hatchling_emergence_time_accuracy = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name="Hatchling emergence time estimate accuracy",
        choices=lookups.TIME_ESTIMATE_CHOICES,
        default=lookups.NA_VALUE,
    )
    cloud_cover_at_emergence = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="If known, in eights.",
    )

    def __str__(self):
        return "Fan {} ({}-{}) tracks ({}-{} deg); water {} deg".format(
            self.no_tracks_main_group,
            self.no_tracks_main_group_min,
            self.no_tracks_main_group_max,
            self.bearing_leftmost_track_degrees,
            self.bearing_rightmost_track_degrees,
            self.bearing_to_water_degrees,
        )


class LightSourceObservation(Observation):
    """The observation of a light source during the emergence of hatchlings from a turtle nest.
    """
    bearing_light_degrees = models.FloatField(
        verbose_name="Bearing",
        blank=True,
        null=True,
        help_text="Bearing captured with handheld compass.",
    )
    light_source_type = models.CharField(
        max_length=300,
        choices=(
            (lookups.NA_VALUE, "NA"),
            ("natural", "Natural"),
            ("artificial", "Artificial"),
        ),
        default=lookups.NA_VALUE,
    )
    light_source_description = models.TextField(
        verbose_name="Comments",
        blank=True,
        null=True,
        help_text="Any other comments or notes.",
    )

    def __str__(self):
        return "Light source {} at {} deg: {}".format(
            self.get_light_source_type_display(),
            self.bearing_light_degrees,
            self.light_source_description or "",
        )


class TurtleHatchlingEmergenceOutlierObservation(Observation):
    """The observation of a hatchling emergence track outlier.
    """
    bearing_outlier_track_degrees = models.FloatField(
        verbose_name="Bearing",
        blank=True,
        null=True,
        help_text="Aim at track 5m from nest or high water mark. Bearing captured with handheld compass.",
    )
    outlier_group_size = models.PositiveIntegerField(
        verbose_name="Number of tracks in outlier group",
        blank=True,
        null=True,
    )
    outlier_track_comment = models.TextField(
        verbose_name="Comments",
        blank=True,
        null=True,
        help_text="Any other comments or notes.",
    )

    def __str__(self):
        return f"Outlier: {self.outlier_group_size} tracks at {self.bearing_outlier_track_degrees} deg."


class LoggerObservation(Observation):
    """A logger is observed during an Encounter.
    """
    LOGGER_TYPE_DEFAULT = "temperature-logger"
    LOGGER_TYPE_CHOICES = (
        (LOGGER_TYPE_DEFAULT, "Temperature Logger"),
        ("data-logger", "Data Logger"),
        ("ctd-data-logger", "Conductivity, Temperature, Depth SR Data Logger"),
    )

    LOGGER_STATUS_DEFAULT = "resighted"
    LOGGER_STATUS_NEW = "programmed"
    LOGGER_STATUS_CHOICES = (
        (LOGGER_STATUS_NEW, "programmed"),
        ("posted", "posted to field team"),
        ("deployed", "deployed in situ"),
        ("resighted", "resighted in situ"),
        ("retrieved", "retrieved in situ"),
        ("downloaded", "downloaded"),
    )

    logger_type = models.CharField(
        max_length=300,
        default=LOGGER_TYPE_DEFAULT,
        verbose_name="Type",
        choices=LOGGER_TYPE_CHOICES,
        help_text="The logger type.",
    )
    deployment_status = models.CharField(
        max_length=300,
        default=LOGGER_STATUS_DEFAULT,
        verbose_name="Status",
        choices=LOGGER_STATUS_CHOICES,
        help_text="The logger life cycle status.",
    )
    logger_id = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name="Logger ID",
        help_text="The ID of a logger must be unique within the tag type.",
    )
    comments = models.TextField(
        blank=True,
        null=True,
        help_text="Comments",
    )

    def __str__(self):
        if self.logger_id:
            return f"{self.logger_id} ({self.get_logger_type_display()})"
        else:
            return f"{self.get_logger_type_display()}"


class TissueSampleObservation(Observation):
    """A tissue sample extracted from an animal during an AnimalEncounter.
    """
    sample_type = models.CharField(
        max_length=128,
        default=lookups.TISSUE_SAMPLE_TYPE_DEFAULT,
        choices=lookups.TISSUE_SAMPLE_TYPE_CHOICES,
        help_text="The type of tissue in this sample",
    )
    serial = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        db_index=True,
        help_text="The ID/serial number of the sample",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="An optional description of the sample",
    )
    data = models.JSONField(default=dict, help_text="Sample analysis results")

    def __str__(self):
        if self.serial:
            return f"{self.get_sample_type_display()} - {self.serial}"
        else:
            self.get_sample_type_display()


# Line transect encounter classes


class LineTransectEncounter(Encounter):
    """Encounter with a line transect.

    An observer tallies (not individually georeferenced) observations along
    a line transect, while recording the transect route live and keeping the
    tally until the end of the transect.

    Although individually geo-referenced Encounters are preferable, this Encounter
    type supports tallies of abundant entities (like turtle tracks on a saturation
    beach), collected under time pressure.

    Examples:

    ODK form "Track Tally", providing per record:
    * One LineTransectEncounter with zero to many related:
    * TrackTallyObservation
    * TurtleNestDisturbanceTallyObservation
    """

    transect = models.LineStringField(
        srid=4326,
        dim=2,
        verbose_name="Transect line",
        help_text="The line transect as LineString in WGS84",
    )

    def __str__(self):
        return f"Line tx {self.pk}"

    def inferred_name(self):
        """Return an empty string."""
        return ""

    def get_encounter_type(self):
        """Infer the encounter type.

        If TrackTallyObservations are related, it's a track observation.

        TODO support other types of line transects when added
        """
        return Encounter.ENCOUNTER_TRACKS

    @property
    def short_name(self):
        """A short, often unique, human-readable representation of the encounter.

        Slugified and dash-separated:

        * Date of encounter as YYYY-mm-dd
        * longitude in WGS 84 DD, rounded to 4 decimals (<10m),
        * latitude in WGS 84 DD, rounded to 4 decimals (<10m), (missing sign!!)
        * nest age (type),
        * species,
        * name if available (requires "update names" and tag obs)

        The short_name could be non-unique.
        """
        nameparts = [
            self.when.astimezone(tz.tzlocal()).strftime("%Y-%m-%d %H:%M %Z"),
            force_str(round(self.longitude, 4)).replace(".", "-"),
            force_str(round(self.latitude, 4)).replace(".", "-"),
        ]
        if self.name is not None:
            nameparts.append(self.name)
        return slugify("-".join(nameparts))

    @property
    def latitude(self):
        """Return the WGS 84 DD latitude."""
        return self.where.y

    @property
    def longitude(self):
        """Return the WGS 84 DD longitude."""
        return self.where.x

    def card_template(self):
        return "observations/linetransectencounter_card.html"


class TrackTallyObservation(Observation):
    """Observation of turtle track tallies and signs of predation.
    """
    species = models.CharField(
        max_length=300,
        choices=lookups.TURTLE_SPECIES_CHOICES,
        default=lookups.TURTLE_SPECIES_DEFAULT,
        help_text="The species of the animal causing the track.",
    )
    nest_age = models.CharField(
        max_length=300,
        verbose_name="Age",
        choices=lookups.NEST_AGE_CHOICES,
        default=lookups.NEST_AGE_DEFAULT,
        help_text="The track or nest age.",
    )
    nest_type = models.CharField(
        max_length=300,
        verbose_name="Type",
        choices=lookups.NEST_TYPE_CHOICES,
        default=lookups.NEST_TYPE_DEFAULT,
        help_text="The track or nest type.",
    )
    tally = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="The sum of encountered tracks.",
    )

    def __str__(self):
        return f"TrackTally: {self.tally} {self.nest_age} {self.nest_type}s of {self.species}"


class TurtleNestDisturbanceTallyObservation(Observation):
    """Observation of turtle track tallies and signs of predation.
    """
    species = models.CharField(
        max_length=300,
        choices=lookups.TURTLE_SPECIES_CHOICES,
        default=lookups.TURTLE_SPECIES_DEFAULT,
        help_text="The species of the nesting animal.",
    )
    disturbance_cause = models.CharField(
        max_length=300,
        choices=lookups.NEST_DAMAGE_CHOICES,
        default=lookups.UNKNOWN_VALUE,
        help_text="The cause of the disturbance.",
    )
    no_nests_disturbed = models.PositiveIntegerField(
        verbose_name="Tally of nests disturbed",
        blank=True,
        null=True,
        help_text="The sum of damaged nests.",
    )
    no_tracks_encountered = models.PositiveIntegerField(
        verbose_name="Tally of disturbance signs",
        blank=True,
        null=True,
        help_text="The sum of signs, e.g. predator tracks.",
    )
    comments = models.TextField(
        blank=True,
        null=True,
        help_text="Any other comments or notes.",
    )

    def __str__(self):
        return f"Nest Damage Tally: {self.no_nests_disturbed} nests of {self.species} showing disturbance by {self.disturbance_cause}"
