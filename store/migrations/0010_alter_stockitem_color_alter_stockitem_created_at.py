# Generated by Django 4.2 on 2024-04-20 12:49

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_alter_stockitem_cap_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockitem',
            name='color',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='stockitem',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
