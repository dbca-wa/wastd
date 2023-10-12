from django.core.management.base import BaseCommand
from turtle_tags.utils import import_wamtram


class Command(BaseCommand):
    help = "Imports WAMTRAM database (idempotent for existing records)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reload",
            action="store_true",
            help="Re-import existing WAMTRAM records",
            dest="reload",
        )

    def handle(self, *args, **options):
        if "reload" in options:
            reload = options["reload"]
        else:
            reload = False

        import_wamtram(reload=reload)
