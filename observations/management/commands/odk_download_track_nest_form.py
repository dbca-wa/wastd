from django.core.management.base import BaseCommand
import logging
from observations.odk import import_turtle_track_or_nest, import_site_visit_start, import_site_visit_end
from wastd.odk import get_auth_headers


class Command(BaseCommand):
    help = 'Runs ETL scripts to download submissions related to Turtle Track/Nest survey data from ODK'

    def add_arguments(self, parser):
        parser.add_argument(
            '--duration',
            action='store',
            default=8,
            type=int,
            help='Duration (hours) within which surveys should try to automatically link and claim orphan encounters',
            dest='duration',
        )

    def handle(self, *args, **options):
        logger = logging.getLogger('turtles')
        logger.info("Downloading auth headers")
        auth_headers = get_auth_headers()

        logger.info('Downloading data from Turtle Track or Nest form')
        import_turtle_track_or_nest(auth_headers=auth_headers)

        logger.info('Downloading data from Site Visit Start form')
        import_site_visit_start(auth_headers=auth_headers)

        logger.info('Downloading data from Site Visit End form, linking encounters')
        import_site_visit_end(duration_hr=options['duration'], auth_headers=auth_headers)
