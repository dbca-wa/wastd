import logging
from datetime import timedelta
import pandas

from .models import (
    Area,
    Survey,
    Encounter,
    SurveyEnd,
)

LOGGER = logging.getLogger("turtles")


def guess_site(survey):
    """Return the first Area containing the start_location or None.
    """
    if not survey.start_location:
        return None
    else:
        return Area.objects.filter(
            area_type=Area.AREATYPE_SITE, geom__covers=survey.start_location
        ).first()


def guess_area(survey):
    """Return the first Area containing the start_location or None.
    """
    if not survey.start_location:
        return None
    else:
        return Area.objects.filter(
            area_type=Area.AREATYPE_LOCALITY,
            geom__covers=survey.start_location,
        ).first()


def claim_encounters(survey):
    """Update Encounters within this Survey to reference survey=self.
    """
    if survey.encounters:
        # Update the queryset of encounters covered by the survey site area, and
        # within the start_time and end_time of the survey.
        survey.encounters.update(survey=survey, site=survey.site)


def claim_end_points(survey):
    """Claim SurveyEnd.

    The first SurveyEnd with the matching site,
    and an end_time within six hours after start_time is used
    to set corresponding end_location, end_time, end_comments,
    end_photo and end_source_id.

    Since the end point could be taken with a different device (e.g.
    if primary device malfunctions), we will not filter down to
    the same device_id.

    If no SurveyEnd is found and no end_time is set, the end_time is set to
    start_time plus six hours. This should allow the survey to claim its Encounters.

    TODO we could be a bit cleverer and find the latest encounter on the same day and site.
    """
    se = SurveyEnd.objects.filter(
        site=survey.site,
        end_time__gte=survey.start_time,
        end_time__lte=survey.start_time + timedelta(hours=6),
    ).first()
    if se:
        survey.end_location = se.end_location
        survey.end_time = se.end_time
        survey.end_comments = se.end_comments
        survey.end_photo = se.end_photo
        survey.end_source_id = se.source_id
        survey.end_device_id = se.device_id
    else:
        if not survey.end_time:
            survey.end_time = survey.start_time + timedelta(hours=6)
            survey.end_comments = (
                "[NEEDS QA][Missing SiteVisitEnd] Survey end guessed."
            )
            LOGGER.info(
                "[Survey.claim_end_points] Missing SiteVisitEnd for Survey {}".format(survey)
            )


def reconstruct_missing_surveys(buffer_mins=30):
    """Create missing surveys.

    Find Encounters with missing survey but existing site,
    group by date and site, aggregate datetime ("when") into earliest and latest record,
    buffer earliest and latest record by given minutes (default: 30),
    create a Survey with aggregated data.

    Crosstab: See pandas
    """
    LOGGER.info("Rounding up the orphans...")
    tne = Encounter.objects.exclude(site=None).filter(survey=None)
    LOGGER.info("Found {} orphans witout survey.".format(tne.count()))
    LOGGER.info("Inferring missing survey data...")
    tne_all = [[t.site.id, t.when.date(), t.when, t.reporter] for t in tne]
    tne_idx = [[t[0], t[1]] for t in tne_all]
    tne_data = [[t[2], t[3]] for t in tne_all]
    idx = pandas.MultiIndex.from_tuples(tne_idx, names=["site", "date"])
    df = pandas.DataFrame(tne_data, index=idx, columns=["datetime", "reporter"])
    missing_surveys = pandas.pivot_table(
        df,
        index=["date", "site"],
        values=["datetime", "reporter"],
        aggfunc={"datetime": [min, max], "reporter": "first"},
    )
    LOGGER.info(
        "Creating {} missing surveys...".format(len(missing_surveys))
    )

    bfr = timedelta(minutes=buffer_mins)
    for idx, row in missing_surveys.iterrows():
        LOGGER.debug(
            "Missing Survey on {0} at {1} by {2} from {3}-{4}".format(
                idx[0],
                idx[1],
                row["reporter"]["first"],
                row["datetime"]["min"] - bfr,
                row["datetime"]["max"] + bfr,
            )
        )
        ste = Area.objects.get(id=idx[1])
        s = Survey.objects.create(
            source="reconstructed",
            site=ste,
            start_location=ste.centroid,
            start_time=row["datetime"]["min"] - bfr,
            end_time=row["datetime"]["max"] + bfr,
            end_location=ste.centroid,
            reporter=row["reporter"]["first"],
            start_comments="[QA][AUTO] Reconstructed by WAStD from Encounters without surveys.",
        )
        s.save()
    LOGGER.info("Created {} surveys to adopt {} orphaned Encounters.".format(len(missing_surveys), tne.count()))

    tne = Encounter.objects.exclude(site=None).filter(survey=None)
    LOGGER.info("Remaining orphans without survey: {}".format(tne.count()))

    return None
