# Generated by Django 4.2 on 2024-05-08 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0025_stock_notification_sent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockitem',
            name='created_at',
            field=models.DateField(blank=True, null=True),
        ),
    ]