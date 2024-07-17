from django.contrib import admin
from.models import Product, Color, Product_type

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name','type','color','size', 'color', 'unit', 'quantity', 'pid']
    
    


admin.site.register(Product, ProductAdmin)
admin.site.register(Product_type)
admin.site.register(Color)


