from django.apps import AppConfig


class ObservationsConfig(AppConfig):
    name = "observations"
    verbose_name = "Observations"

    def ready(self):
        # Import module signals.
        from observations import signals
