from django.db.models.signals import post_save, post_delete
from django.db.models import F
from django.dispatch import receiver
from .models import Production
from purchase.models import Inventory

print(" Production Signals module loaded")

@receiver(post_save, sender=Production)
def update_inventory_on_production_save(sender, instance, created, **kwargs):
    if created:
        # Update inventory for preforms
        preform_inventory = Inventory.objects.get(pk=instance.preform_product.pk)
        preform_inventory.unit = F('unit') - instance.used_preforms
        preform_inventory.save()

        # Update inventory for produced bottles
        bottle_inventory, created = Inventory.objects.get_or_create(
            product=instance.produced_bottle_product,
            defaults={'unit': 0}
        )
        if not created:
            bottle_inventory.unit = F('unit') + instance.produced_bottles
        else:
            bottle_inventory.unit = instance.produced_bottles
        bottle_inventory.save()


@receiver(post_delete, sender=Production)
def reverse_inventory_on_delete(sender, instance, **kwargs):
    # Reverse inventory for preforms
    preform_inventory = Inventory.objects.get(pk=instance.preform_product.pk)
    preform_inventory.unit = F('unit') + instance.used_preforms
    preform_inventory.save()

    # Reverse inventory for produced bottles
    bottle_inventory = Inventory.objects.get(product=instance.produced_bottle_product)
    bottle_inventory.unit = F('unit') - instance.produced_bottles
    bottle_inventory.save()
