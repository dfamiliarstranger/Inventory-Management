from django.db import models
from shortuuid.django_fields import ShortUUIDField
from decimal import Decimal
from product.models import Product


# Create your models here.
class Old_Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.DecimalField(max_digits=10, decimal_places=2)
    oid = ShortUUIDField(unique=True, length=5, prefix="old-stk-")
    created_at = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Old Stock {self.oid} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        if self.product.quantity and self.product.quantity != 0:
            self.quantity = Decimal(self.unit) / Decimal(self.product.quantity)
        else:
            self.quantity = Decimal(0)
        super().save(*args, **kwargs)


