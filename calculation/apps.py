from django.apps import AppConfig

class CalculationConfig(AppConfig):
    name='calculation'
    def ready(self):
        from calculation import signals