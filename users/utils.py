import logging
from .models import User

LOGGER = logging.getLogger("turtles")


def transfer_user(old, new):
    """Merge one :model:`users.User` profile into another.

    This function has side effects:
    * It updates all FK and M2M from one user to another.
    * It updates the new User.aliases with the username,
      name, and aliases of the old User.
    * It marks the old User profile as "inactive". (Should it delete? Implications for ETL and user mapping!)
    * It sends LOGGER.info messages.

    Arguments:

    * ``old`` :model:`users.User` The user to be closed.
    * ``new`` :model:`users.User` The user to be retained.

    Return:

    * ``msg`` <str> A summary message.
    """
    # Gate checks ------------------------------------------------------------#
    if old == new:
        msg = (
            "Same user, nothing to do. "
            "Only two different user profiles can be merged."
        )
        LOGGER.info(msg)
        return msg

    # ------------------------------------------------------------------------#
    # Stocktake before merge
    msg = (
        "User profile closed: {} with "
        "{} Encounters observed, {} Encounters reported, "
        "{} Surveys started, {} Survey Ends recorded, {} Surveys teamed, "
        "{} morph recorded, {} morph handled, "
        "{} tags recorded, {} tags handled, "
        "{} revisions, {} statelogs. "
        "User profile retained: {} with "
        "{} Encounters observed, {} Encounters reported, "
        "{} Surveys started, {} Survey Ends recorded, {} Surveys teamed, "
        "{} morph recorded, {} morph handled, "
        "{} tags recorded, {} tags handled, "
        "{} revisions, {} statelogs. ".format(
            old,
            old.encounters_reported.count(),
            old.encounters_observed.count(),
            old.reported_surveys.count(),
            old.surveyend_set.count(),
            old.survey_team.count(),
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
            new.survey_team.count(),
            new.morphometric_recorder.count(),
            new.morphometric_handler.count(),
            new.tag_recorder.count(),
            new.tag_handler.count(),
            new.revision_set.count(),
            new.statelog_set.count(),
        )
    )

    # ------------------------------------------------------------------------#
    # Transfer FK and M2M
    # Alternatively, one could use the model API to programmatically find FKs
    for x in old.encounters_reported.all():
        x.reporter = new
        x.save()

    for x in old.encounters_observed.all():
        x.observer = new
        x.save()

    for x in old.reported_surveys.all():
        x.reporter = new
        x.save()

    for x in old.surveyend_set.all():
        x.reporter = new
        x.save()

    for x in old.morphometric_recorder.all():
        x.recorder = new
        x.save()

    for x in old.morphometric_handler.all():
        x.handler = new
        x.save()

    for x in old.tag_recorder.all():
        x.recorder = new
        x.save()

    for x in old.tag_handler.all():
        x.handler = new
        x.save()

    for x in old.revision_set.all():
        x.user = new
        x.save()

    for x in old.statelog_set.all():
        x.by_id = new.id
        x.save()

    for svy in old.survey_team.all():
        svy.team.remove(old)
        svy.team.add(new)
        svy.save()

    # ------------------------------------------------------------------------#
    # Transfer old user details to new user
    # Old username, name, aliases merged with new aliases and deduplicated
    new_aliases = (
        list(map(str.strip, new.aliases.split(","))) if new.aliases != "" else list()
    )
    old_aliases = (
        list(map(str.strip, old.aliases.split(","))) if old.aliases != "" else list()
    )
    old_details = [old.username, old.name]
    combined_aliases = list(set(new_aliases + old_aliases + old_details))
    new.aliases = ", ".join([x for x in combined_aliases if x != ""])
    new.is_active = True  # So we can revert an incorrect User merge

    # Role is too messy to deduplicate
    if old.role and old.role != "":
        if not new.role:
            new.role = ""
        new.role += old.role

    if not new.affiliation and old.affiliation and old.affiliation != "":
        new.affiliation += old.affiliation

    if not new.email and old.email:
        new.email = old.email

    if not new.phone and old.phone:
        new.phone = old.phone

    new.save()

    # ------------------------------------------------------------------------#
    # Mark the old user profile as inactive
    old.is_active = False
    old.is_staff = False
    old.is_superuser = False
    old.aliases = ""
    old.role = ""
    old.affiliation = ""
    old.save()

    # ------------------------------------------------------------------------#
    # Stocktake after merge
    new = User.objects.get(pk=new.pk)  # Load fresh state from DB
    msg += (
        "After merge: {} now has "
        "{} Encounters observed, {} Encounters reported, "
        "{} Surveys started, {} Survey Ends recorded, {} Surveys teamed, "
        "{} morph recorded, {} morph handled, "
        "{} tags recorded, {} tags handled, "
        "{} revisions, {} statelogs. ".format(
            new,
            new.encounters_reported.count(),
            new.encounters_observed.count(),
            new.reported_surveys.count(),
            new.surveyend_set.count(),
            new.survey_team.count(),
            new.morphometric_recorder.count(),
            new.morphometric_handler.count(),
            new.tag_recorder.count(),
            new.tag_handler.count(),
            new.revision_set.count(),
            new.statelog_set.count(),
        )
    )

    LOGGER.info(msg)
    return msg


def change_user_for_area(old, new, area):
    """Transfer all data within one area to another user.

    This function has side effects:
    * It updates all FK and M2M from one user to another for a subset of data.
    * It sends LOGGER.info messages.

    Arguments:

    * ``old`` :model:`users.User` The user which was incorrectly assigned.
    * ``new`` :model:`users.User` The user to transfer the data to.
    * ``area`` :model:`observations.Area` The Area of type Locality in which to transfer data from old to new user.

    The relevant data is linked via FKs from User and Area.

    Return:

    * ``msg`` <str> A summary message.
    """

    # Gate checks ------------------------------------------------------------#
    if old == new:
        msg = (
            "Same user, nothing to do. "
            "If you wanted to transfer data from one to another user, "
            "choose two different users."
        )
        LOGGER.info(msg)
        return msg

    if not area:
        msg = "No area selected, nothing to do. " "A locality is required."
        LOGGER.info(msg)
        return msg

    # ------------------------------------------------------------------------#
    # Stocktake before transfer
    msg = (
        "Data transferred from User {} to {} in Area {}. "
        "{} Encounters observed, {} Encounters reported, "
        "{} Surveys started, {} Surveys teamed, "
        "{} morph recorded, {} morph handled, "
        "{} tags recorded, {} tags handled.".format(
            old,
            new,
            area,
            old.encounters_reported.filter(area=area).count(),
            old.encounters_observed.filter(area=area).count(),
            old.reported_surveys.filter(area=area).count(),
            old.survey_team.filter(area=area).count(),
            old.morphometric_recorder.filter(encounter__area=area).count(),
            old.morphometric_handler.filter(encounter__area=area).count(),
            old.tag_recorder.filter(encounter__area=area).count(),
            old.tag_handler.filter(encounter__area=area).count(),
        )
    )

    # ------------------------------------------------------------------------#
    # Transfer FK and M2M
    # Alternatively, one could use the model API to programmatically find FKs
    for x in old.encounters_reported.filter(area=area):
        x.reporter = new
        x.save()

    for x in old.encounters_observed.filter(area=area):
        x.observer = new
        x.save()

    for x in old.reported_surveys.filter(area=area):
        x.reporter = new
        x.save()

    for x in old.morphometric_recorder.filter(encounter__area=area):
        x.recorder = new
        x.save()

    for x in old.morphometric_handler.filter(encounter__area=area):
        x.handler = new
        x.save()

    for x in old.tag_recorder.filter(encounter__area=area):
        x.recorder = new
        x.save()

    for x in old.tag_handler.filter(encounter__area=area):
        x.handler = new
        x.save()

    for svy in old.survey_team.filter(area=area):
        svy.team.remove(old)
        svy.team.add(new)
        svy.save()

    LOGGER.info(msg)
    return msg
