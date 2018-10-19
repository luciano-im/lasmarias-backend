from django.apps import AppConfig


class AppConfig(AppConfig):
    name = 'app'

    # In ready function import signals to be prepared to be fired since app is loaded
    def ready(self):
        import app.signals
