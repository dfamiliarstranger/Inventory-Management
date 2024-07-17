from decimal import Decimal
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Sale, Inventory

print("Signals module loaded")

@receiver(post_save, sender=Sale)
def deduct_inventory_on_sale(sender, instance, created, **kwargs):
    print(f"Sale created: {instance}")  # Debug statement
    if created:
        inventory = Inventory.objects.get(product=instance.product)
        
        inventory.unit -= Decimal(instance.unit)
        inventory.save()

@receiver(pre_delete, sender=Sale)
def return_inventory_on_sale_delete(sender, instance, **kwargs):
    print(f"Sale deleted: {instance}")  # Debug statement
    inventory = Inventory.objects.get(product=instance.product)
    
    inventory.unit += Decimal(instance.unit)
    inventory.save()
