# Generated by Django 4.2 on 2024-05-13 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0047_alter_ticket_records_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket_records',
            name='quantity',
            field=models.IntegerField(),
        ),
    ]