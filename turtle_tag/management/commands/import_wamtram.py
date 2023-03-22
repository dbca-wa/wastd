from django.core.management.base import BaseCommand
from turtle_tag.utils import import_wamtram


class Command(BaseCommand):
    help = 'Imports WAMTRAM data (idempotent)'

    def handle(self, *args, **options):
        import_wamtram()
