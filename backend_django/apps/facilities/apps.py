from django.apps import AppConfig


class FacilitiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.facilities'
    verbose_name = 'Facilities'

    def ready(self):
        """
        Import signals when the app is ready.
        This ensures facility change notifications are automatically created.
        """
        import apps.facilities.signals  # noqa
