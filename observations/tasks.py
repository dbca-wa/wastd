import logging
from observations import utils, models

LOGGER = logging.getLogger("turtles")


def update_names():
    """Update cached names on Encounters and reconstructs Surveys.
    """
    LOGGER.info("[observations.tasks.update_names] Start updating names...")
    encs = utils.reconstruct_animal_names()
    msg = "[observations.tasks.update_names] {} animal names reconstructed. ".format(len(encs))
    LOGGER.info(msg)


def resave_surveys():
    """Re-save Surveys in order to trigger the associated pre- and post-save singnals.
    """
    LOGGER.info("[observations.tasks.resave_surveys] Start re-saving Surveys...")
    surveys = [s.save() for s in models.Survey.objects.all()]
    msg = "[observations.tasks.resave_surveys] {0} surveys reconstructed".format(len(surveys))
    LOGGER.info(msg)


def reconstruct_surveys():
    """Reconstruct missing surveys.
    """
    utils.reconstruct_missing_surveys()
