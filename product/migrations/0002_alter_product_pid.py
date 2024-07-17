# Generated by Django 4.2 on 2024-07-13 12:19

from django.db import migrations
import shortuuid.django_fields


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='pid',
            field=shortuuid.django_fields.ShortUUIDField(alphabet=None, length=5, max_length=9, prefix='pdt-', unique=True),
        ),
    ]
