from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.db import transaction
from django.db.models import F
from decimal import Decimal
            #################   Products Table     ################

class Cap(models.Model):
    size = models.IntegerField()
    quantity_per_bag = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.size}"
    
class Preform_type(models.Model):
    name = models.CharField(max_length=30)
    size = models.DecimalField(max_digits=5, decimal_places=1)
    quantity_per_bag = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.name} {self.size}"
    

            #################   Clients Table     ################

class Contact(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

class Supplier(Contact):
    pass


class Customer(Contact):
    pass

class Color(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"
    
class Cap_name(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

class Stock(models.Model):
    name = models.CharField(max_length=100, null=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    cap_type = models.ForeignKey(Cap, on_delete=models.SET_NULL, null=True, blank=True)
    product_type = models.CharField(max_length=20, null=True, blank=True)
    bottle_type = models.CharField(max_length=20, null=True, blank=True)
    preform_type = models.ForeignKey(Preform_type, on_delete=models.SET_NULL, null=True, blank=True)
    unit = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_sent = models.BooleanField(default=False)
    quantity = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.color} - {self.product_type}"


class StockItem(models.Model):
    name = models.CharField(max_length=20, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True) 
    quantity = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    total = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    created_at = models.DateField(null=True, blank=True)
    cap_type = models.ForeignKey(Cap, on_delete=models.SET_NULL, null=True, blank=True)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    product_type = models.CharField(max_length=20, null=True, blank=True)
    preform_type = models.ForeignKey(Preform_type, on_delete=models.SET_NULL, null=True, blank=True)
    unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.unit:
            self.unit = self.calculate_unit()
        super().save(*args, **kwargs)

    def calculate_unit(self):
        if self.name == 'Preform' and self.preform_type:
            return self.preform_type.quantity_per_bag * self.quantity
        elif self.cap_type:
            return self.cap_type.quantity_per_bag * self.quantity
        return self.quantity


def update_inventory(add_stock_item):
    try:
        with transaction.atomic():
            inventory_item = Stock.objects.filter(
                name=add_stock_item.name,
                color=add_stock_item.color,
                product_type=add_stock_item.product_type,
                cap_type=add_stock_item.cap_type,
                preform_type=add_stock_item.preform_type,
            ).first()

            if inventory_item:
                # Update quantity and unit
                inventory_item.quantity = Decimal(inventory_item.quantity) + Decimal(add_stock_item.quantity)
                inventory_item.unit = Decimal(inventory_item.unit) + Decimal(add_stock_item.unit)
                inventory_item.save()
            else:
                Stock.objects.create(
                    name=add_stock_item.name,
                    color=add_stock_item.color,
                    product_type=add_stock_item.product_type,
                    cap_type=add_stock_item.cap_type,
                    preform_type=add_stock_item.preform_type,
                    quantity=add_stock_item.quantity,
                    unit=add_stock_item.unit
                )
    except Exception as e:
        # Handle exceptions
        print(f"An error occurred: {e}")
    

class Bottle(models.Model):
    created_at = models.DateField(null=True, blank=True)
    bottle_unit = models.CharField(max_length=30, null=True, blank=True)
    bottle_size = models.IntegerField()
    bottle_color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.bottle_size}ml {self.bottle_color} {self.bottle_unit}"

###################     Production Models     #####################
class Production(models.Model):
    product = models.ForeignKey(Stock, on_delete=models.CASCADE, null=True ) 
    product_quantity = models.IntegerField(null=True, blank=True)
    damages = models.IntegerField(null=True, blank=True)
    waste_bottle = models.IntegerField(null=True, blank=True)
    good_bottle = models.IntegerField()
    bottle_size = models.IntegerField()
    bottle_color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateField(null=True, blank=True)
    bottle_unit = models.CharField(max_length=30, null=True, blank=True)

 
class Sales(models.Model):
    product = models.ForeignKey(Stock, on_delete=models.CASCADE, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)  
    quantity = models.IntegerField()
    price = models.IntegerField()
    total = models.DecimalField(max_digits=20,decimal_places=2)
    created_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.product}"
    

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

class Ticket_Records(models.Model):
    product = models.ForeignKey(Stock, on_delete=models.CASCADE) 
    product_type = models.CharField(max_length=30, null=True, blank=True)
    action = models.TextField()
    quantity = models.IntegerField()
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Record for {self.product} created at {self.created_at}"
   


