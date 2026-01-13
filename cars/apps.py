from django.apps import AppConfig


class CarsConfig(AppConfig):
    name = 'cars'
    verbose_name = 'Gestão de Carros'

    def ready(self):
        import cars.signals  # noqa: F401
