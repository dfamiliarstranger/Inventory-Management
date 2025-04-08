from django.db import models
from django.db.models import F
from sale.models import Customer
from purchase.models import Product

from django.utils.timezone import now
# Create your models here.


# Inventory Model
class PS_Inventory(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='inventory')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, limit_choices_to={'name': 'preform'})
    quantity_in_bags = models.PositiveIntegerField(default=0)
    quantity_in_units = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} for {self.customer.name}"    

# Model to receive raw materials
class PS_RawMaterialReceipt(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, limit_choices_to={'name': 'preform'})
    quantity_in_bags = models.PositiveIntegerField()
    quantity_in_units = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_received = models.DateTimeField(default=now)

    def save(self, *args, **kwargs):
        # Update inventory
        inventory, created = PS_Inventory.objects.get_or_create(customer=self.customer, product=self.product)
        inventory.quantity_in_bags += self.quantity_in_bags
        inventory.quantity_in_units += self.quantity_in_units
        inventory.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Received {self.quantity_in_units} {self.product.name} from {self.customer.name}"

# Production Model
class PS_Production(models.Model):
    preform_product = models.ForeignKey(
        PS_Inventory,
        on_delete=models.CASCADE,
        related_name='preform_productions'
    )
    produced_bottle_product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        limit_choices_to={'name': 'bottle'},
        related_name='ps_bottle_productions'
    )
    used_preforms = models.PositiveIntegerField(default=0)
    defective_preforms = models.PositiveIntegerField(default=0)
    produced_bottles = models.PositiveIntegerField(default=0)
    defective_bottles = models.PositiveIntegerField(default=0)
    production_date = models.DateTimeField(default=now)

    def save(self, *args, **kwargs):
        # Deduct from inventory
        if self.preform_product.quantity_in_units >= self.used_preforms:
            self.preform_product.quantity_in_units -= self.used_preforms
            self.preform_product.save()
            super().save(*args, **kwargs)
        else:
            raise ValueError("Not enough preforms in inventory")

    def __str__(self):
        return f"Production on {self.production_date}"
