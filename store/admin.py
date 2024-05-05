from django.contrib import admin
from.models import Cap, Bottle, Preform, Preform_type, Customer, Supplier, StockItem, Stock, Production, Sales
# Register your models here.

admin.site.register(Cap)
admin.site.register(Bottle)
admin.site.register(Preform)
admin.site.register(Preform_type)
admin.site.register(Supplier)
admin.site.register(Customer)
admin.site.register(StockItem)
admin.site.register(Stock)
admin.site.register(Production)
admin.site.register(Sales)

