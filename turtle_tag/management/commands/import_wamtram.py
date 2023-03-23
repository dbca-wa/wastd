from django.core.management.base import BaseCommand
from turtle_tag.utils import import_wamtram


class Command(BaseCommand):
    help = 'Imports WAMTRAM data (idempotent)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-reload',
            action='store_false',
            help='Skip import of existing WAMTRAM records',
            dest='reload',
        )

    def handle(self, *args, **options):
        import_wamtram(reload=options['reload'])
