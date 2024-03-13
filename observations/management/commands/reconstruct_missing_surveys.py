from django.core.management.base import BaseCommand
from observations.utils import reconstruct_missing_surveys


class Command(BaseCommand):
    help = '''Find Encounters with missing survey but existing site,
group by date and site, aggregate datetime ("when") into earliest and latest record,
buffer earliest and latest record by given minutes (default: 30),
create a Survey with aggregated data.'''

    def add_arguments(self, parser):
        parser.add_argument(
            '--buffer-minutes',
            action='store',
            default=30,
            type=int,
            help='Number of minutes to buffer start and end time for a reconstructed survey',
            dest='buffer_mins',
        )

    def handle(self, *args, **options):
        reconstruct_missing_surveys(options['buffer_mins'])
