from decimal import Decimal
from django.db.models.signals import post_save,  pre_delete
from django.dispatch import receiver
from .models import Purchase, Inventory

print("Signals module loaded")

@receiver(post_save, sender=Purchase)
def update_inventory(sender, instance, created, **kwargs):
    print(f"Purchase created: {instance}")  # Debug statement
    if created:
        inventory, created = Inventory.objects.get_or_create(
            product=instance.product,
            defaults={'unit': instance.unit}
        )
        if not created:
            inventory.unit += Decimal(instance.unit)
            inventory.save()



@receiver(pre_delete, sender=Purchase)
def reverse_inventory_on_delete(sender, instance, **kwargs):
    print(f"Purchase deleted: {instance}")  # Debug statement
    inventory = Inventory.objects.get(product=instance.product)
    inventory.unit -= Decimal(instance.unit)
    inventory.save()