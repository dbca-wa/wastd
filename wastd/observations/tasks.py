# -*- coding: utf-8 -*-
"""Tasks for WAStD."""
from background_task import background
import logging
import os
from django.conf import settings
from django.utils import timezone
from wastd.observations.utils import (
    allocate_animal_names, save_all_odka, import_all_odka, reconstruct_missing_surveys)

logger = logging.getLogger(__name__)


@background(queue="admin-tasks", schedule=timezone.now())
def update_names():
    """Update cached names on Encounters and Loggers and reconstructs Surveys."""
    logger.info("[wastd.observations.tasks.update_names] Start updating names...")
    surveys, names, loggers = allocate_animal_names()
    msg = ("[wastd.observations.tasks.update_names] {0} surveys reconstructed, "
           "{1} animal names reconstructed, {2} logger names set".format(
               len(surveys), len(names), len(loggers)))
    logger.info(msg)


@background(queue="admin-tasks", schedule=timezone.now())
def import_odka():
    """Download and import new ODKA submissions."""
    path = os.path.join(settings.MEDIA_ROOT, "odka")
    os.makedirs(path, exist_ok=True)
    save_all_odka(path=path)
    import_all_odka(path=path)
    reconstruct_missing_surveys()
