
from django.apps import AppConfig


class AppCustomZentlibConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_custom_zenith'

    def ready(self):
        # Importa os signals quando o app estiver pronto
        import app_custom_zenith.signals