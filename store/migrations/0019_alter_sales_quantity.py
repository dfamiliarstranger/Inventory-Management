# Generated by Django 4.2 on 2024-05-04 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0018_sales'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sales',
            name='quantity',
            field=models.IntegerField(max_length=5),
        ),
    ]
