from datetime import timedelta
from dateutil import parser as dateparser
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
import logging

from shared.utils import sanitize_tag_label
from .models import (
    Campaign,
    Survey,
    Encounter,
    AnimalEncounter,
    TurtleNestEncounter,
    LineTransectEncounter,
    TagObservation,
    NestTagObservation,
)
from .utils import guess_site, guess_area, claim_encounters


LOGGER = logging.getLogger("turtles")


@receiver(post_save, sender=Campaign)
def campaign_post_save(sender, instance, *args, **kwargs):
    """Campaign: Claim Surveys and Encounters."""
    # Version 1
    instance.adopt_all_surveys_and_encounters()
    msg = "Campaign {0} has adopted {1} surveys and {2} encounters.".format(
        instance, instance.surveys.count(), instance.encounters.count()
    )
    LOGGER.info(msg)


@receiver(pre_save, sender=Survey)
def survey_pre_save(sender, instance, buffer_mins=30, initial_duration_hrs=6, *args, **kwargs):
    """Survey pre-save: sanity check and data cleaning.

    If a start or end time are given as string, they are parsed into a native datetime object.
    If site or area are blank, they will be guessed via spatial overlap with known locations.

    If the end time is not given or earlier than the start time (mostly due to data import errors), the
    end time will be adjusted to ``initial_duration_hrs`` after the start time.
    This will give the ``post_save`` signal an opportunity to ``claim_encounters``.

    If the end time is exactly ``initial_duration_hrs`` later than the start time, it
    will be adjusted to ``buffer_mins`` after the last encounter within.
    """
    msg = ""
    if type(instance.start_time) == str:
        instance.start_time = dateparser.parse(instance.start_time)
    if type(instance.end_time) == str:
        instance.end_time = dateparser.parse(instance.end_time)

    if not instance.site:
        instance.site = guess_site(instance)
    if not instance.area:
        instance.area = guess_area(instance)

    if not instance.end_time:
        instance.end_time = instance.start_time + timedelta(hours=initial_duration_hrs)
        msg += (
            "[signal.survey_pre_save] End time was missing, "
            "adjusted to {} hours after start time\n".format(initial_duration_hrs)
        )

    if instance.end_time < instance.start_time:
        instance.end_time = instance.start_time + timedelta(hours=initial_duration_hrs)
        msg += (
            "[signal.survey_pre_save] End time was before start time, "
            "adjusted to {} hours after start time\n".format(initial_duration_hrs)
        )

    # If the survey end_time is exactly `initial_duration_hrs` after start_time,
    # check to see if the survey has any encounters.
    # If so, change the survey end_time to the time of the last encounter (`when`) plus `buffer_mins`.
    if instance.end_time == instance.start_time + timedelta(hours=initial_duration_hrs):
        et = instance.end_time
        if instance.encounters:
            instance.end_time = instance.encounters.last().when + timedelta(minutes=buffer_mins)
            msg += (
                "[signal.survey_pre_save] End time adjusted from {} to {}, "
                "{} minutes after last of {} encounters."
            ).format(et, instance.end_time, buffer_mins, len(instance.encounters))

    if msg != "":
        instance.end_comments = (instance.end_comments or "") + msg
        LOGGER.info(msg)
    instance.label = instance.make_label


@receiver(post_save, sender=Survey)
def survey_post_save(sender, instance, *args, **kwargs):
    """Survey: Claim encounters.
    """
    claim_encounters(instance)
    if instance.encounters:
        LOGGER.info(f"[signal.survey_post_save] {instance} claimed Encounters {instance.encounters}")
    else:
        LOGGER.info(f"[signal.survey_post_save] {instance} claimed no Encounters")


@receiver(pre_delete, sender=Encounter)
def encounter_pre_delete(sender, instance, **kwargs):
    """Delete Observations before deleting an Encounter.

    See https://github.com/django-polymorphic/django-polymorphic/issues/34
    """
    for observation in instance.observation_set.all():
        LOGGER.info(f"[signal.encounter_pre_delete] Deleting {observation}")
        observation.delete()


@receiver(pre_save, sender=Encounter)
@receiver(pre_save, sender=AnimalEncounter)
@receiver(pre_save, sender=TurtleNestEncounter)
@receiver(pre_save, sender=LineTransectEncounter)
def encounter_pre_save(sender, instance, *args, **kwargs):
    """Encounter pre_save: calculate expensive lookups.

    Bulk updates or bulk creates will bypass these to be reconstructed later.

    * source_id: Set form short_name if empty
    * area and site: Inferred from location (where) if empty
    * encounter_type: Always from instance.get_encounter_type()
    * as_html /as_latex: Always set from get_popup() and get_latex()
    """
    if not instance.source_id:
        instance.source_id = instance.short_name
    # This is slow, use set_name() instead in bulk
    if (not instance.name) and instance.inferred_name:
        instance.name = instance.inferred_name
    if not instance.site:
        instance.site = instance.guess_site
    if not instance.area:
        instance.area = instance.guess_area
    instance.encounter_type = instance.get_encounter_type()
    instance.as_html = instance.get_popup()


@receiver(pre_save, sender=TagObservation)
def tagobservation_pre_save(sender, instance, *args, **kwargs):
    """TagObservation pre_save: sanitise tag_label, name Encounter after tag.
    """
    if instance.encounter.status == Encounter.STATUS_NEW and instance.name:
        instance.name = sanitize_tag_label(instance.name)


@receiver(pre_save, sender=NestTagObservation)
def nesttagobservation_pre_save(sender, instance, *args, **kwargs):
    """NestTagObservation pre_save: sanitise tag_label, name unnamed Encounter after tag.
    """
    if instance.encounter.status == Encounter.STATUS_NEW and instance.tag_label:
        instance.tag_label = sanitize_tag_label(instance.tag_label)
    if instance.encounter.status == Encounter.STATUS_NEW and instance.flipper_tag_id:
        instance.flipper_tag_id = sanitize_tag_label(instance.flipper_tag_id)
    if instance.encounter.status == Encounter.STATUS_NEW and (
        not instance.encounter.name
    ):
        instance.encounter.name = instance.name
        instance.encounter.save(
            update_fields=[
                "name",
            ]
        )
