# Generated by Django 4.2 on 2024-07-16 01:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0003_alter_inventory_options_alter_inventory_unit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='purchase.supplier'),
        ),
    ]
