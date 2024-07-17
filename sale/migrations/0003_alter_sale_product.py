# Generated by Django 4.2 on 2024-07-17 08:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0004_alter_purchase_supplier'),
        ('sale', '0002_alter_sale_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sale',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='purchase.inventory'),
        ),
    ]
