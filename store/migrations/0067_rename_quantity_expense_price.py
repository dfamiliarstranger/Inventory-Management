# Generated by Django 4.2.7 on 2024-09-01 22:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0066_expense'),
    ]

    operations = [
        migrations.RenameField(
            model_name='expense',
            old_name='quantity',
            new_name='price',
        ),
    ]
