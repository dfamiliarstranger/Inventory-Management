# Generated by Django 4.2 on 2024-07-17 10:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0006_inventory_quantity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inventory',
            name='quantity',
        ),
    ]
