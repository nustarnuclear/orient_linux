from django.apps import AppConfig

class TragopanConfig(AppConfig):
    name='tragopan'
    def ready(self):
        from tragopan import signals
