from django.apps import AppConfig


class MonitoringApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api.v1.monitoring"
    verbose_name = "監控 API"
