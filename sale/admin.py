from django.contrib import admin
from .models import Customer, Inventory, Sale

# Register your models here.

class SaleAdmin(admin.ModelAdmin):
    list_display = [
        'product_name', 'product_type', 'product_size', 'product_color', 
        'customer', 'quantity', 'unit', 'price', 'total', 'pid', 'created_at'
    ]

    # Assuming `Inventory` model represents `Product` and has these fields.
    def product_name(self, obj):
        return obj.product.name  # Replace 'product' with the correct field if needed.

    def product_type(self, obj):
        return obj.product.type

    def product_size(self, obj):
        return f"{obj.product.size} {obj.product.unit}"

    def product_color(self, obj):
        return obj.product.color

    # Setting short descriptions and admin order fields for each property
    product_name.admin_order_field = 'product__name'
    product_name.short_description = 'Product Name'
    
    product_type.admin_order_field = 'product__type'
    product_type.short_description = 'Product Type'

    product_size.admin_order_field = 'product__size'
    product_size.short_description = 'Product Size'

    product_color.admin_order_field = 'product__color'
    product_color.short_description = 'Product Color'


class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'mobile_1', 'mobile_2', 'email', 'contact_info']


admin.site.register(Sale, SaleAdmin)
admin.site.register(Customer, CustomerAdmin)
