# Generated by Django 4.2 on 2024-04-20 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_alter_stockitem_color_alter_stockitem_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockitem',
            name='total',
            field=models.DecimalField(decimal_places=2, max_digits=20),
        ),
    ]
