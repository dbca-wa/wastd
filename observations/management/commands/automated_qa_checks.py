from django.core.management.base import BaseCommand
import logging

from observations.models import (
    Encounter,
    TurtleNestEncounter,
    TurtleNestDisturbanceObservation,
    TurtleNestDisturbanceTallyObservation,
    TURTLE_SPECIES_DEFAULT,
    NEST_TYPE_TRACK_UNSURE,
    NEST_AGE_DEFAULT,
)
from users.models import User


class Command(BaseCommand):
    help = 'Runs automated QA/QC checks and flags records for curation'

    def handle(self, *args, **options):
        logger = logging.getLogger('wastd')
        logger.info('Running automated QA/QC checks and flagging records for curation')
        system_user = User.objects.get(pk=1)

        # Check: Any turtle nest encounter with uncertain species.
        # FIXME: STATUS_NEW may change to STATUS_IMPORTED.
        nest_encounters = TurtleNestEncounter.objects.filter(species=TURTLE_SPECIES_DEFAULT, status=Encounter.STATUS_NEW)
        if nest_encounters:
            logger.info(f'Flagging {nest_encounters.count()} turtle nest encounters for curation due to uncertain species')
        for enc in nest_encounters:
            enc.flag(by=system_user, description='Flagged by automated checks due to uncertain species')
            enc.save()

        # Check: Any turtle nest encounter with uncertain nesting outcome.
        # FIXME: STATUS_NEW may change to STATUS_IMPORTED.
        nest_encounters = TurtleNestEncounter.objects.filter(nest_type=NEST_TYPE_TRACK_UNSURE, status=Encounter.STATUS_NEW)
        if nest_encounters:
            logger.info(f'Flagging {nest_encounters.count()} turtle nest encounters for curation due to uncertain nesting outcome')
        for enc in nest_encounters:
            enc.flag(by=system_user, description='Flagged by automated checks due to uncertain nesting outcome')
            enc.save()

        # Check: Any turtle nest encounter with uncertain nest age.
        # FIXME: STATUS_NEW may change to STATUS_IMPORTED.
        nest_encounters = TurtleNestEncounter.objects.filter(nest_age=NEST_AGE_DEFAULT, status=Encounter.STATUS_NEW)
        if nest_encounters:
            logger.info(f'Flagging {nest_encounters.count()} turtle nest encounters for curation due to uncertain nest age')
        for enc in nest_encounters:
            enc.flag(by=system_user, description='Flagged by automated checks due to uncertain nest age')
            enc.save()

        # Check: Any turtle nest encounter marked as uncertain for predation.
        nest_encounters = set()
        for obs in TurtleNestDisturbanceObservation.objects.filter(disturbance_cause="unknown"):
            if isinstance(obs.encounter, TurtleNestEncounter):
                nest_encounters.add(obs.encounter)
        for obs in TurtleNestDisturbanceTallyObservation.objects.filter(disturbance_cause="unknown"):
            if isinstance(obs.encounter, TurtleNestEncounter):
                nest_encounters.add(obs.encounter)
        pks = [enc.pk for enc in nest_encounters]
        # Convert back to a queryset
        nest_encounters = TurtleNestEncounter.objects.filter(pk__in=pks, status=Encounter.STATUS_NEW)
        if nest_encounters:
            logger.info(f'Flagging {nest_encounters.count()} turtle nest encounters for curation due to uncertain predation')
        for enc in nest_encounters:
            enc.flag(by=system_user, description='Flagged by automated checks due to uncertain predation')
            enc.save()

        logger.info('Automated QA/QC checks completed')
