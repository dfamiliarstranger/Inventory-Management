from django.contrib import admin
from .models import Production, Product, Inventory

class ProductionAdmin(admin.ModelAdmin):
    list_display = [
        'preform_product_name', 'preform_product_type', 'preform_product_size', 'preform_product_color',
        'bottle_product_name', 'bottle_product_type', 'bottle_product_size', 'bottle_product_color',
        'used_preforms', 'defective_preforms', 'produced_bottles', 'defective_bottles', 'production_date'
    ]

    def preform_product_name(self, obj):
        return obj.preform_product.product.name

    def preform_product_type(self, obj):
        return obj.preform_product.product.type

    def preform_product_size(self, obj):
        return f"{obj.preform_product.product.size} {obj.preform_product.product.unit}"

    def preform_product_color(self, obj):
        return obj.preform_product.product.color

    def bottle_product_name(self, obj):
        return obj.produced_bottle_product.name

    def bottle_product_type(self, obj):
        return obj.produced_bottle_product.type

    def bottle_product_size(self, obj):
        return f"{obj.produced_bottle_product.size} {obj.produced_bottle_product.unit}"

    def bottle_product_color(self, obj):
        return obj.produced_bottle_product.color

    # Short descriptions and order fields
    preform_product_name.admin_order_field = 'preform_product__product__name'
    preform_product_name.short_description = 'Preform Product Name'
    
    preform_product_type.admin_order_field = 'preform_product__product__type'
    preform_product_type.short_description = 'Preform Product Type'

    preform_product_size.admin_order_field = 'preform_product__product__size'
    preform_product_size.short_description = 'Preform Product Size'

    preform_product_color.admin_order_field = 'preform_product__product__color'
    preform_product_color.short_description = 'Preform Product Color'

    bottle_product_name.admin_order_field = 'produced_bottle_product__name'
    bottle_product_name.short_description = 'Bottle Product Name'
    
    bottle_product_type.admin_order_field = 'produced_bottle_product__type'
    bottle_product_type.short_description = 'Bottle Product Type'

    bottle_product_size.admin_order_field = 'produced_bottle_product__size'
    bottle_product_size.short_description = 'Bottle Product Size'

    bottle_product_color.admin_order_field = 'produced_bottle_product__color'
    bottle_product_color.short_description = 'Bottle Product Color'

admin.site.register(Production, ProductionAdmin)
