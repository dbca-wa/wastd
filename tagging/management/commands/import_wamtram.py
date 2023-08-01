from django.core.management.base import BaseCommand
from tagging.utils import import_wamtram


class Command(BaseCommand):
    help = 'Imports WAMTRAM data (idempotent)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reload',
            action='store_true',
            help='Re-import existing WAMTRAM records',
            dest='reload',
        )

    def handle(self, *args, **options):
        reload = False
        if 'reload' in options:
            reload = options['reload']

        import_wamtram(reload=reload)
