from .models import User
import logging
logger = logging.getLogger(__name__)

def transfer_user(old, new):
    """Transfer all objects relating to a user to another user.

    Transfers all FK fields to User from old to new:

    * u.encounters_reported.all()
    * u.encounters_observed.all()
    * u.morphometric_handler.all()
    * u.morphometric_recorder.all()
    * u.tag_handler.all()
    * u.tag_recorder.all()
    * u.revision_set.all()
    * u.statelog_set.all()
    * u.expedition_team.all()
    * u.surveyend_set.all()
    * u.reported_surveys.all()
    * u.survey_team.all()
    * u.fileattachment_set.all()
    * u.document_set.all()
    """

    # TODO gate check for obj not found or old==new
    # survey team TODO

    msg = (
        "User profile closed: {} with "
        "{} Encounters observed, {} Encounters reported, "
        "{} Surveys started, {} Survey Ends recorded, "
        "{} morph recorded, {} morph handled, "
        "{} tags recorded, {} tags handled, "
        "{} revisions, {} statelogs. "
        "User profile retained: {} with"
        "{} Encounters observed, {} Encounters reported, "
        "{} Surveys started, {} Survey Ends recorded, "
        "{} morph recorded, {} morph handled, "
        "{} tags recorded, {} tags handled, "
        "{} revisions, {} statelogs. ".format(
        old,
        old.encounters_reported.count(),
        old.encounters_observed.count(),
        old.reported_surveys.count(),
        old.surveyend_set.count(),
        old.morphometric_recorder.count(),
        old.morphometric_handler.count(),
        old.tag_recorder.count(),
        old.tag_handler.count(),
        old.revision_set.count(),
        old.statelog_set.count(),
        new,
        new.encounters_reported.count(),
        new.encounters_observed.count(),
        new.reported_surveys.count(),
        new.surveyend_set.count(),
        new.morphometric_recorder.count(),
        new.morphometric_handler.count(),
        new.tag_recorder.count(),
        new.tag_handler.count(),
        new.revision_set.count(),
        new.statelog_set.count(),
        )
    )

    logger.info(msg)
    return msg


    # for x in old.encounters_reported.all():
    #     x.reporter = new
    #     x.save()

    # for x in old.encounters_reported.all():
    #     x.observer = new
    #     x.save()

    # for x in old.reported_surveys.all():
    #     x.reporter = new
    #     x.save()

    # for x in old.surveyend_set.all():
    #     x.reporter = new
    #     x.save()


