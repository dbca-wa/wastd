# -*- coding: utf-8 -*-
"""Tasks for WAStD."""
from background_task import background
import logging
import os
from django.conf import settings
from django.utils import timezone
from sentry_sdk import capture_message
from wastd.observations.utils import (
    allocate_animal_names, save_all_odka, import_all_odka, reconstruct_missing_surveys)

logger = logging.getLogger(__name__)


@background(queue="admin-tasks", schedule=timezone.now())
def update_names():
    """Update cached names on Encounters and Loggers and reconstructs Surveys."""
    msg = "[wastd.observations.tasks.update_names] Start updating names..."
    logger.info(msg)
    capture_message(msg, level="info")
    surveys, names, loggers = allocate_animal_names()
    msg = ("[wastd.observations.tasks.update_names] {0} surveys reconstructed, "
           "{1} animal names reconstructed, {2} logger names set. "
           "Task successfully finished.".format(
               len(surveys), len(names), len(loggers)))
    logger.info(msg)
    capture_message(msg, level="info")


@background(queue="admin-tasks", schedule=timezone.now())
def import_odka():
    """Download and import new ODKA submissions."""
    capture_message("[wastd.observations.tasks.import_odka] Starting ODKA import.", level="info")
    path = os.path.join(settings.MEDIA_ROOT, "odka")
    os.makedirs(path, exist_ok=True)
    save_all_odka(path=path)
    capture_message("[wastd.observations.tasks.import_odka] ODKA submissions downloaded.", level="info")
    import_all_odka(path=path)
    capture_message("[wastd.observations.tasks.import_odka] ODKA submissions imported.", level="info")
    reconstruct_missing_surveys()
    capture_message(
        "[wastd.observations.tasks.import_odka] "
        "ODKA surveys reconstructed, task successfully finished.", level="info")
