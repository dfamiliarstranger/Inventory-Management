from django.contrib import admin
from .models import InventoryTicket, Expense

# Define the Admin Class for Inventory Ticket
class InventoryTicketAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'product_type', 'product_size', 'product_unit', 'product_color', 'inventory_unit', 'quantity', 'reason', 'created_at']

    # Define methods to access Product information through Inventory
    def product_name(self, obj):
        return obj.inventory.product.name
    
    def product_type(self, obj):
        return obj.inventory.product.type  # Adjust field name based on actual Product model
    
    def product_size(self, obj):
        return obj.inventory.product.size  # Adjust field name based on actual Product model
    
    def product_unit(self, obj):
        return obj.inventory.product.unit  # Adjust field name based on actual Product model

    def product_color(self, obj):
        return obj.inventory.product.color  # Adjust field name based on actual Product model
    
    def inventory_unit(self, obj):
        return obj.inventory.unit
    
    # Provide admin ordering and descriptive names
    product_name.admin_order_field = 'inventory__product__name'
    product_name.short_description = 'Product Name'
    
    product_type.admin_order_field = 'inventory__product__type'
    product_type.short_description = 'Product Type'
    
    product_size.admin_order_field = 'inventory__product__size'
    product_size.short_description = 'Product Size'

    product_size.admin_order_field = 'inventory__product__unit'
    product_size.short_description = 'Product Unit'
    
    product_color.admin_order_field = 'inventory__product__color'
    product_color.short_description = 'Product Color'

    inventory_unit.admin_order_field = 'inventory__unit'
    inventory_unit.short_description = 'Inventory Unit'
class ExpensesAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'category', 'description', 'price']

# Register all models to the admin site
admin.site.register(InventoryTicket, InventoryTicketAdmin)
admin.site.register(Expense, ExpensesAdmin)
