# Generated by Django 4.2 on 2024-07-15 07:01

from django.db import migrations, models
import django.db.models.deletion
import shortuuid.django_fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0006_alter_product_quantity'),
    ]

    operations = [
        migrations.CreateModel(
            name='Old_Stock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10)),
                ('unit', models.DecimalField(decimal_places=2, max_digits=10)),
                ('oid', shortuuid.django_fields.ShortUUIDField(alphabet=None, length=5, max_length=13, prefix='old-stk-', unique=True)),
                ('created_at', models.DateTimeField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product')),
            ],
        ),
    ]
