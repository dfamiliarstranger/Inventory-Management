# Generated by Django 4.2 on 2024-05-09 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0034_remove_stockitem_unit'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Bottle',
        ),
        migrations.AddField(
            model_name='stockitem',
            name='unit',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
