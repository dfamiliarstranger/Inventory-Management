from django.db import models
from shortuuid.django_fields import ShortUUIDField
from product.models import Product
from decimal import Decimal


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    mobile_1 = models.CharField(max_length=100)
    mobile_2 = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=50)
    contact_info = models.TextField()
    sid = ShortUUIDField(unique=True, length=3, prefix="spp-")

    def __str__(self):
        return self.name

class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    pid = ShortUUIDField(unique=True, length=5, prefix="pur-")
    created_at = models.DateTimeField()

    def __str__(self):
        return f"Purchase {self.pid} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        self.unit = self.product.quantity * Decimal(self.quantity)
        super().save(*args, **kwargs)

class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    unit = models.DecimalField(max_digits=10, decimal_places=2)
    

    def __str__(self):
        return f"{self.product.name} - {self.unit}"
 
    class Meta:
   
        verbose_name_plural = "Inventory"