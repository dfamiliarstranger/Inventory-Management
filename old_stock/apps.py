
from django.apps import AppConfig

class OldStockAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'old_stock'

    def ready(self):
        import old_stock.signals
