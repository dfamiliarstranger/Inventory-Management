# Generated by Django 4.2 on 2024-07-24 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sale', '0004_alter_sale_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sale',
            name='created_at',
            field=models.DateTimeField(),
        ),
    ]
