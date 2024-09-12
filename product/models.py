from django.db import models
from shortuuid.django_fields import ShortUUIDField

# Create your models here.
class Product_type(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Color(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    PRODUCT_NAME = (
    ("preform", "Preform"),
    ("cap", "Cap"),
    ("shrinkwrapper", "Shrinkwrapper"),
    ("bottle", "Bottle"),
    )

    PRODUCT_UNIT = (
    ("g", "g"),
    ("kg", "Kg"),
    ("mm", "mm"),
    ("cl", "Cl"),
    ("l", "L"),
    ("ml", "ml"),
    )

    name = models.CharField(max_length=100, choices=PRODUCT_NAME)
    type = models.ForeignKey(Product_type, null=True, on_delete=models.SET_NULL, related_name='products', blank=True) 
    size = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    color = models.ForeignKey(Color, null=True, blank=True, on_delete=models.SET_NULL, related_name='products')
    unit = models.CharField(max_length=20, choices=PRODUCT_UNIT)  # e.g., 'kg', 'liters', 'pieces'
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    pid = ShortUUIDField(unique=True, length=5, prefix="pdt-")

    def __str__(self):
        return self.name

