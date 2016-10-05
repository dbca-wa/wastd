# -*- coding: utf-8 -*-
"""Observation untilities."""
from wastd.observations.models import AnimalEncounter, LoggerEncounter


def allocate_animal_names():
    """Reconstruct names of Animals from their first allocated Flipper Tag.

    Names are inferred as the first ever allocated flipper tag ID and written
    to each Encounter. Note this can include non-AnimalEncounters, such as
    incidents of tag returns, post-mortem necropsies and other incidentes related
    to an absent animal.

    Algorithm:

    * Find list of new captures (AnimalEncounters with at least one newly
      allocated FlipperTag and no other existing, resighted tags)
    * For each new capture, get the primary flipper tag name as animal name
    * Set the animal name of this and all related Encounters
    """
    ae = [a.set_name_and_propagate(a.primary_flipper_tag.name)
          for a in AnimalEncounter.objects.all() if a.is_new_capture]
    le = [a.set_name_and_propagate(a.primary_flipper_tag.name)
          for a in LoggerEncounter.objects.all() if a.is_new_capture]
    return ae + le
