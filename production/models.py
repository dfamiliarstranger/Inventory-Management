from django.db import models
from django.db.models import F
from purchase.models import Inventory
from product.models import Product
# Create your models here.


class Production(models.Model):
    preform_product = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        limit_choices_to={'product__name': 'preform'},
        related_name='preform_productions'
    )
    produced_bottle_product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        limit_choices_to={'name': 'bottle'},
        related_name='bottle_productions'
    )
    used_preforms = models.PositiveIntegerField(default=0)
    defective_preforms = models.PositiveIntegerField(default=0)
    produced_bottles = models.PositiveIntegerField(default=0)
    defective_bottles = models.PositiveIntegerField(default=0)
    production_date = models.DateTimeField()

    def __str__(self):
        return f"Production on {self.production_date}"

