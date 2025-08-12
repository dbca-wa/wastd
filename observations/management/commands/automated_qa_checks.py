from django.core.management.base import BaseCommand
import itertools
import logging

from observations.lookups import (
    TURTLE_SPECIES_DEFAULT,
    NEST_TYPE_TRACK_UNSURE,
    NEST_AGE_DEFAULT,
)
from observations.models import (
    Area,
    Encounter,
    TurtleNestEncounter,
    TrackTallyObservation,
    TurtleNestDisturbanceObservation,
    TurtleNestDisturbanceTallyObservation,
    AnimalEncounter,
)
from users.models import User

class Command(BaseCommand):
    help = 'Runs automated QA/QC checks to flag records for manual curation as needed'

    def handle(self, *args, **options):
        logger = logging.getLogger('turtles')
        logger.info('Running automated QA/QC checks and flagging records for curation')
        
        system_user = User.objects.get(pk=1)
        unknown_user = User.objects.get_or_create(name='Unknown user', username='unknown_user')[0]

        # Check: Any TurtleNestEncounter with a site label containing the term "training".
        nest_encounters = TurtleNestEncounter.objects.filter(site__name__icontains="training", status=Encounter.STATUS_IMPORTED)
        if nest_encounters:
            logger.info(f'Flagging {nest_encounters.count()} turtle nest encounters for curation due to site containing "Training"')
        for enc in nest_encounters:
            enc.flag(by=system_user, description='Flagged for curation by automated checks due to site containing "Training"')
            enc.save()

        # Check: Any TurtleNestEncounter with a site label containing the term "testing".
        nest_encounters = TurtleNestEncounter.objects.filter(site__name__icontains="testing", status=Encounter.STATUS_IMPORTED)
        if nest_encounters:
            logger.info(f'Flagging {nest_encounters.count()} turtle nest encounters for curation due to site containing "testing"')
        for enc in nest_encounters:
            enc.flag(by=system_user, description='Flagged for curation by automated checks due to site containing "testing"')
            enc.save()

        # Check: Any turtle nest encounter with uncertain species.
        nest_encounters = TurtleNestEncounter.objects.filter(species=TURTLE_SPECIES_DEFAULT, status=Encounter.STATUS_IMPORTED)
        if nest_encounters:
            logger.info(f'Flagging {nest_encounters.count()} turtle nest encounters for curation due to uncertain species')
        for enc in nest_encounters:
            enc.flag(by=system_user, description='Flagged for curation by automated checks due to uncertain species')
            enc.save()

        # Check: Any turtle nest encounter using 'test' species.
        for species in ["corolla-corolla", "test-turtle"]:
            nest_encounters = TurtleNestEncounter.objects.filter(species=species, status=Encounter.STATUS_IMPORTED)
            if nest_encounters:
                logger.info(f'Flagging {nest_encounters.count()} turtle nest encounters for curation due to test species type')
            for enc in nest_encounters:
                enc.flag(by=system_user, description='Flagged for curation by automated checks due to test species type')
                enc.save()

        # Check: Any turtle nest encounter with uncertain nesting outcome.
        nest_encounters = TurtleNestEncounter.objects.filter(nest_type=NEST_TYPE_TRACK_UNSURE, status=Encounter.STATUS_IMPORTED)
        if nest_encounters:
            logger.info(f'Flagging {nest_encounters.count()} turtle nest encounters for curation due to uncertain nesting outcome')
        for enc in nest_encounters:
            enc.flag(by=system_user, description='Flagged for curation by automated checks due to uncertain nesting outcome')
            enc.save()

        # Check: Any turtle nest encounter with uncertain nest age.
        nest_encounters = TurtleNestEncounter.objects.filter(nest_age="unknown", status=Encounter.STATUS_IMPORTED)
        if nest_encounters:
            logger.info(f'Flagging {nest_encounters.count()} turtle nest encounters for curation due to uncertain nest age')
        for enc in nest_encounters:
            enc.flag(by=system_user, description='Flagged for curation by automated checks due to uncertain nest age')
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
        nest_encounters = TurtleNestEncounter.objects.filter(pk__in=pks, status=Encounter.STATUS_IMPORTED)
        if nest_encounters:
            logger.info(f'Flagging {nest_encounters.count()} turtle nest encounters for curation due to uncertain predation')
        for enc in nest_encounters:
            enc.flag(by=system_user, description='Flagged for curation by automated checks due to uncertain predation')
            enc.save()

        # Check: Any records with the following species at any of the following areas.
        # Species: Leatherback, Loggerhead, Olive Ridley
        # Areas: Delambre Island, Thevenard Island, Port Hedland, Rosemary Island, Eco Beach, Barrow Island, Mundabullangana
        localities = [
            "Delambre Island",
            "Thevenard Island",
            "Port Hedland",
            "Rosemary Island",
            "Eco Beach",
            "Barrow Island",
            "Mundabullangana",
        ]
        species_list = [
            ("dermochelys-coriacea", "Dermochelys coriacea (Leatherback turtle)"),
            ("caretta-caretta", "Caretta caretta (Loggerhead turtle)"),
            ("lepidochelys-olivacea", "Lepidochelys olivacea (Olive ridley turtle)"),
        ]

        for el in itertools.product(localities, species_list):
            locality = Area.objects.get(name=el[0], area_type="Locality")
            areas = Area.objects.filter(geom__coveredby=locality.geom)
            species = el[1][0]
            species_name = el[1][1]

            for area in areas:
                nest_encounters = TurtleNestEncounter.objects.filter(area=area, species=species, status=Encounter.STATUS_IMPORTED)
                if nest_encounters:
                    logger.info(f'Flagging {nest_encounters.count()} turtle nest encounters for curation: {species_name} at {area.name}')
                for enc in nest_encounters:
                    enc.flag(by=system_user, description=f'Flagged for curation by automated checks: {species_name} at {area.name}')
                    enc.save()

                nest_encounters = set()
                for obs in TrackTallyObservation.objects.filter(encounter__area=area, species=species):
                    if isinstance(obs.encounter, TurtleNestEncounter):
                        nest_encounters.add(obs.encounter)
                for obs in TurtleNestDisturbanceTallyObservation.objects.filter(encounter__area=area, species=species):
                    if isinstance(obs.encounter, TurtleNestEncounter):
                        nest_encounters.add(obs.encounter)
                pks = [enc.pk for enc in nest_encounters]
                # Convert back to a queryset
                nest_encounters = TurtleNestEncounter.objects.filter(pk__in=pks, status=Encounter.STATUS_IMPORTED)
                if nest_encounters:
                    logger.info(f'Flagging {nest_encounters.count()} turtle nest encounters for curation: {species_name} at {area.name}')
                for enc in nest_encounters:
                    enc.flag(by=system_user, description=f'Flagged for curation by automated checks: {species_name} at {area.name}')
                    enc.save()

        # Check: Any records with the following species at any of the following areas.
        # Species: Leatherback, Olive Ridley
        # Areas: Ningaloo
        localities = [
            "Ningaloo",
        ]
        species_list = [
            ("dermochelys-coriacea", "Dermochelys coriacea (Leatherback turtle)"),
            ("lepidochelys-olivacea", "Lepidochelys olivacea (Olive ridley turtle)"),
        ]

        for el in itertools.product(localities, species_list):
            locality = Area.objects.get(name=el[0], area_type="Locality")
            areas = Area.objects.filter(geom__coveredby=locality.geom)
            species = el[1][0]
            species_name = el[1][1]

            for area in areas:
                # TurtleNestEncounter objects
                nest_encounters = TurtleNestEncounter.objects.filter(area=area, species=species, status=Encounter.STATUS_IMPORTED)
                if nest_encounters:
                    logger.info(f'Flagging {nest_encounters.count()} turtle nest encounters for curation: {species_name} at {area.name}')
                for enc in nest_encounters:
                    enc.flag(by=system_user, description=f'Flagged for curation by automated checks: {species_name} at {area.name}')
                    enc.save()

                # Observations linked to TurtleNestEncounter objects.
                nest_encounters = set()
                for obs in TrackTallyObservation.objects.filter(encounter__area=area, species=species):
                    if isinstance(obs.encounter, TurtleNestEncounter):
                        nest_encounters.add(obs.encounter)
                for obs in TurtleNestDisturbanceTallyObservation.objects.filter(encounter__area=area, species=species):
                    if isinstance(obs.encounter, TurtleNestEncounter):
                        nest_encounters.add(obs.encounter)
                pks = [enc.pk for enc in nest_encounters]
                # Convert back to a queryset
                nest_encounters = TurtleNestEncounter.objects.filter(pk__in=pks, status=Encounter.STATUS_IMPORTED)
                if nest_encounters:
                    logger.info(f'Flagging {nest_encounters.count()} turtle nest encounters for curation: {species_name} at {area.name}')
                for enc in nest_encounters:
                    enc.flag(by=system_user, description=f'Flagged for curation by automated checks: {species_name} at {area.name}')
                    enc.save()

        # Check: imported Turtle Nest Encounters with 'Unknown user' as the reporter.
        nest_encounters = TurtleNestEncounter.objects.filter(status=Encounter.STATUS_IMPORTED, reporter=unknown_user)
        if nest_encounters:
            logger.info(f'Flagging {nest_encounters.count()} turtle nest encounters for curation due to unknown reporter')
        for enc in nest_encounters:
            enc.flag(by=system_user, description='Flagged for curation by automated checks due to unknown reporter')
            enc.save()

        # Mark remaining TurtleNestEncounter objects with status == Imported as imported (passed QA/QC checks).
        nest_encounters = TurtleNestEncounter.objects.filter(status=Encounter.STATUS_IMPORTED)
        if nest_encounters:
            logger.info(f'Marking {nest_encounters.count()} imported turtle nest encounters as curated (passed QA/QC checks)')
        for enc in nest_encounters:
            enc.curate(by=system_user, description=f'Curated by automated QA/QC (passed all checks)')
            enc.save()

        # Check: imported Animal Encounters with 'Unknown user' as the reporter.
        animal_encounters = AnimalEncounter.objects.filter(status=Encounter.STATUS_IMPORTED, reporter=unknown_user)
        if animal_encounters:
            logger.info(f'Flagging {animal_encounters.count()} animal encounters for curation due to unknown reporter')
        for enc in animal_encounters:
            enc.flag(by=system_user, description='Flagged for curation by automated checks due to unknown reporter')
            enc.save()

        logger.info('Automated QA/QC checks completed')
