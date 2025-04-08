from django.contrib import admin
from .models import PS_Inventory, PS_Production, PS_RawMaterialReceipt

# Register models without custom admin classes

admin.site.register(PS_Production)

# Register model with a custom admin class
@admin.register(PS_RawMaterialReceipt)
class RawMaterialReceiptAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'quantity_in_bags', 'quantity_in_units', 'amount', 'date_received')
    list_filter = ('date_received', 'customer')
    search_fields = ('customer__name', 'product__name')
@admin.register(PS_Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'product', 'quantity_in_units', 'quantity_in_bags')

