from django.contrib import admin
from.models import Cap, Notification,  Preform_type, Customer, Supplier, StockItem, Stock, Production, Sales, Color, Ticket_Records
# Register your models here.

admin.site.register(Cap)
# admin.site.register(Bottle)

admin.site.register(Preform_type)
admin.site.register(Supplier)
admin.site.register(Customer)
admin.site.register(StockItem)
admin.site.register(Stock)
admin.site.register(Production)
admin.site.register(Sales)
admin.site.register(Notification)
admin.site.register(Color)
admin.site.register(Ticket_Records)

