from django.apps import AppConfig

import apps.goals.signals as goalsignal


class GoalsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.goals"

    def ready(self):
        goalsignal
