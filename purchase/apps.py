# purchase/apps.py
from django.apps import AppConfig

class PurchaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'purchase'

    def ready(self):
        print("Purchase app ready")  # Debug statement
        import purchase.signals  # Import signals module when the app is ready

