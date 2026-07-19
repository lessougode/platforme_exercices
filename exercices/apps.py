from django.apps import AppConfig


class ExercicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'exercices'
    verbose_name = "Exercices"

    def ready(self):
        import exercices.signals  # noqa
