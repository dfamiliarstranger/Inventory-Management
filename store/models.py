from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.db import transaction
from django.db.models import F
from decimal import Decimal
from purchase.models import Inventory            #################   Products Table     ################


class InventoryTicket(models.Model):
    REASON_CHOICES = [
        ('INCREASE', 'Increase'),
        ('DECREASE', 'Decrease'),
    ]

    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=10, choices=REASON_CHOICES)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.inventory.product.name} - {self.quantity} - {self.reason}"
    
class Expense(models.Model):
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)