# Generated by Django 4.2 on 2024-05-16 07:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0050_remove_ticket_records_product_size'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stock',
            name='notification_sent',
        ),
        migrations.DeleteModel(
            name='Preform',
        ),
    ]
