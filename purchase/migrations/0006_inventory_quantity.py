# Generated by Django 4.2 on 2024-07-17 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0005_remove_inventory_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventory',
            name='quantity',
            field=models.DecimalField(decimal_places=2, default=32, max_digits=10),
            preserve_default=False,
        ),
    ]