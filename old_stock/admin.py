from django.contrib import admin
from .models import Old_Stock
from decimal import Decimal

# Register your models here.


class Old_StockAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'product_type', 'product_size', 'product_color', 'unit', 'quantity','oid']
    readonly_fields = ('quantity',)
    

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

    def save_model(self, request, obj, form, change):
        if obj.product.quantity and obj.product.quantity != 0:
            obj.quantity = Decimal(obj.unit) / Decimal(obj.product.quantity)
        else:
            obj.quantity = Decimal(0)
        super().save_model(request, obj, form, change)



admin.site.register(Old_Stock, Old_StockAdmin)

