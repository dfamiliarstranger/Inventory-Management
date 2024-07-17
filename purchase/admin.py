from django.contrib import admin
from .models import Supplier, Purchase, Inventory

class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['product','supplier','quantity','unit', 'price', 'total', 'pid', 'created_at']

class InventoryAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'product_type', 'product_size', 'product_color', 'unit']

    def product_name(self, obj):
        return obj.product.name

    def product_type(self, obj):
        return obj.product.type  # Assuming your Product model has a 'category' field

    def product_size(self, obj):
        return obj.product.size  # Assuming your Product model has a 'price' field
    
    def product_color(self, obj):
        return obj.product.color  # Assuming your Product model has a 'price' field

    product_name.admin_order_field = 'product__name'  # Allows column to be sortable by product's name
    product_name.short_description = 'Product Name'  # Renames the column header

    product_type.admin_order_field = 'product__type'
    product_type.short_description = 'Product Type'

    product_size.admin_order_field = 'product__size'
    product_size.short_description = 'Product size'

    product_color.admin_order_field = 'product__color'
    product_color.short_description = 'Product color'


admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(Supplier)
admin.site.register(Inventory, InventoryAdmin)