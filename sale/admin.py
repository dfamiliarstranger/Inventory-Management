from django.contrib import admin
from .models import Customer, Inventory, Sale
# Register your models here.

class SaleAdmin(admin.ModelAdmin):
    list_display = ['product','customer','quantity','unit', 'price', 'total', 'pid', 'created_at']

class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'mobile_1', 'mobile_2', 'email', 'contact_info']


admin.site.register(Sale, SaleAdmin)
admin.site.register(Customer, CustomerAdmin)