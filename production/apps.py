from django.apps import AppConfig


class ProductionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'production'



    def ready(self):
        print("Production app ready")  # Debug statement
        import production.signals  # Import signals module when the app is ready

