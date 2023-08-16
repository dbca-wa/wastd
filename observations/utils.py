import logging
from datetime import timedelta
import pandas

from .models import (
    Area,
    Survey,
    Encounter,
)

LOGGER = logging.getLogger("turtles")


def guess_site(survey):
    """Return the first Area containing the start_location or None.
    """
    if not survey.start_location:
        return None
    else:
        return Area.objects.filter(area_type=Area.AREATYPE_SITE, geom__covers=survey.start_location).first()


def guess_area(survey):
    """Return the first Area containing the start_location or None.
    """
    if not survey.start_location:
        return None
    else:
        return Area.objects.filter(area_type=Area.AREATYPE_LOCALITY, geom__covers=survey.start_location).first()


def claim_encounters(survey):
    """For a Survey, update any 'orphan' Encounters within the same site and the same
    start & end times to be associated with that survey.
    """
    encounters = Encounter.objects.filter(
        survey__isnull=True,
        where__coveredby=survey.site.geom,
        when__gte=survey.start_time,
        when__lte=survey.end_time,
    )
    if encounters:
        encounters.update(survey=survey, site=survey.site)


def reconstruct_missing_surveys(buffer_mins=30):
    """Create missing surveys.

    Find Encounters with missing survey but existing site,
    group by date and site, aggregate datetime ("when") into earliest and latest record,
    buffer earliest and latest record by given minutes (default: 30),
    create a Survey with aggregated data.

    Crosstab: See pandas
    """
    encounters_no_survey = Encounter.objects.exclude(site=None).filter(survey=None)
    LOGGER.info("Found {} orphans Encounters without survey".format(encounters_no_survey.count()))
    LOGGER.info("Inferring missing survey data...")
    tne_all = [[t.site.id, t.when.date(), t.when, t.reporter] for t in encounters_no_survey]
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
            "Missing Survey on {} at {} by {} from {}-{}".format(
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
    LOGGER.info("Created {} surveys to adopt {} orphaned Encounters.".format(len(missing_surveys), encounters_no_survey.count()))

    encounters_no_survey = Encounter.objects.exclude(site=None).filter(survey=None)
    LOGGER.info("Remaining Encounters without survey: {}".format(encounters_no_survey.count()))

    return None
