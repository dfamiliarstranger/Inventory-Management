# oldstock_app/signals.py
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Old_Stock
from decimal import Decimal
from purchase.models import Inventory


print("Old Stock module loaded")
@receiver(post_save, sender=Old_Stock)
def update_inventory(sender, instance, created, **kwargs):
    if created:
        inventory, created = Inventory.objects.get_or_create(
            product=instance.product,
            defaults={'unit': instance.unit}
        )
        if not created:
            inventory.unit += Decimal(instance.unit)
            inventory.save()

@receiver(pre_delete, sender=Old_Stock)
def reverse_inventory(sender, instance, **kwargs):
    inventory = Inventory.objects.get(product=instance.product)
   
    inventory.unit -= instance.unit
    inventory.save()