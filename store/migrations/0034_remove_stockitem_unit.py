# Generated by Django 4.2 on 2024-05-09 09:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0033_production_bottle_unit_stock_unit_stockitem_unit_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stockitem',
            name='unit',
        ),
    ]
