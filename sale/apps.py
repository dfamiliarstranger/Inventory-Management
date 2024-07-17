from django.apps import AppConfig


class SaleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sale'

    def ready(self):
        print("Sale app ready")  # Debug statement
        import sale.signals  # Import signals module when the app is ready

