# Generated by Django 4.2 on 2024-06-06 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0056_remove_stockitem_bottle_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockitem',
            name='price',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='stockitem',
            name='total',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
    ]