# Generated by Django 4.2 on 2024-05-13 06:16

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0044_remove_production_excesses_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
