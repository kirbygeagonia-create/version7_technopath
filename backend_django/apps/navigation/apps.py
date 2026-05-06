from django.apps import AppConfig


class NavigationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.navigation'
    verbose_name = 'Navigation'

    def ready(self):
        import apps.navigation.signals  # noqa: F401
