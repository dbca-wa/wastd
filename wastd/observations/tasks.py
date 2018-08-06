# -*- coding: utf-8 -*-
"""Tasks for WAStD."""
from background_task import background
import logging
import sys
from django.utils import timezone
from wastd.observations.utils import allocate_animal_names, save_all_odka, import_all_odka

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
    reload(sys)
    sys.setdefaultencoding('UTF8')
    save_all_odka(path="data/odka")
    import_all_odka(path="data/odka")
