from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
import logging

from wastd.utils import sanitize_tag_label
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
from .utils import claim_encounters


LOGGER = logging.getLogger("turtles")


@receiver(post_save, sender=Campaign)
def campaign_post_save(sender, instance, *args, **kwargs):
    """Campaign: Claim Surveys and Encounters."""
    instance.adopt_all_surveys_and_encounters()
    msg = "Campaign {} has adopted {} surveys and {} encounters.".format(
        instance, instance.surveys.count(), instance.encounters.count()
    )
    LOGGER.info(msg)


@receiver(post_save, sender=Survey)
def survey_post_save(sender, instance, *args, **kwargs):
    """Survey: claim encounters if not a training survey.
    """
    if instance.production and instance.start_time and instance.end_time and instance.site:
        claim_encounters(instance)


@receiver(pre_delete, sender=Encounter)
def encounter_pre_delete(sender, instance, **kwargs):
    """Delete Observations before deleting an Encounter.
    See https://github.com/django-polymorphic/django-polymorphic/issues/34
    """
    for observation in instance.observation_set.all():
        observation.delete()


@receiver(pre_save, sender=Encounter)
@receiver(pre_save, sender=AnimalEncounter)
@receiver(pre_save, sender=TurtleNestEncounter)
@receiver(pre_save, sender=LineTransectEncounter)
def encounter_pre_save(sender, instance, *args, **kwargs):
    """Encounter pre_save: calculate expensive lookups.

    Bulk updates or bulk creates will bypass these to be reconstructed later.

    * source_id: Set from short_name if empty
    * area and site: Inferred from location (where) if empty
    * encounter_type: Always from instance.get_encounter_type()
    * as_html: Always set from get_popup()
    """
    # If the encounter doesn't have a source_id
    if not instance.source_id:
        instance.source_id = instance.short_name
    # This is slow, use set_name() instead in bulk
    if not instance.name and instance.inferred_name:
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
    if instance.encounter.status == Encounter.STATUS_NEW and not instance.encounter.name:
        instance.encounter.name = instance.name
        instance.encounter.save()
