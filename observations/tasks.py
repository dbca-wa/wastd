from django.conf import settings
import logging
import os

from observations import utils, models

LOGGER = logging.getLogger("turtles")


def update_names():
    """Update cached names on Encounters and reconstructs Surveys."""
    msg = "[observations.tasks.update_names] Start updating names..."
    LOGGER.info(msg)
    encs = utils.reconstruct_animal_names()
    msg = "[observations.tasks.update_names] " "{} animal names reconstructed. ".format(
        len(encs)
    )
    LOGGER.info(msg)


def resave_surveys():
    """Re-save Surveys."""
    msg = "[observations.tasks.resave_surveys] Start re-saving Surveys..."
    LOGGER.info(msg)
    surveys = [s.save() for s in models.Survey.objects.all()]
    msg = "[observations.tasks.resave_surveys] {0} surveys reconstructed".format(
        len(surveys)
    )
    LOGGER.info(msg)


def import_odka():
    """Download and import new ODKA submissions."""
    path = os.path.join(settings.MEDIA_ROOT, "odka")
    os.makedirs(path, exist_ok=True)
    utils.save_all_odka(path=path)
    utils.import_all_odka(path=path)
    utils.reconstruct_missing_surveys()


def reconstruct_surveys():
    """Reconstruct missing surveys."""
    utils.reconstruct_missing_surveys()
