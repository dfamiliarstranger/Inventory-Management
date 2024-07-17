from django.db import models
from shortuuid.django_fields import ShortUUIDField
from purchase.models import Inventory, Product
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.contrib import messages


class Customer(models.Model):
    name = models.CharField(max_length=100)
    mobile_1 = models.CharField(max_length=100)
    mobile_2 = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=50)
    contact_info = models.TextField()
    sid = ShortUUIDField(unique=True, length=3, prefix="cus-")

    def __str__(self): 
        return self.name

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    pid = ShortUUIDField(unique=True, length=5, prefix="sls-")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        # Ensure the product exists in the inventory and validate the sale
        inventory_item = Inventory.objects.get(product=self.product)
        if self.unit > inventory_item.unit:
            raise ValidationError('Not enough inventory to make this sale.')

    def save(self, *args, **kwargs):
        self.clean()  # Call the clean method to validate before saving
        
        # Calculate the quantity based on the unit
        unit = Decimal(self.unit)
        product_quantity = Decimal(self.product.quantity)
        self.quantity = unit / product_quantity

        # Update inventory
        inventory_item = Inventory.objects.get(product=self.product)
        inventory_item.unit -= self.unit
        inventory_item.save()

        # Calculate total price
        self.total = self.quantity * self.price

        super(Sale, self).save(*args, **kwargs)

    def __str__(self):
        return f"Sales {self.pid} - {self.customer}"