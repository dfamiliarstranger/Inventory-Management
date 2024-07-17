# Generated by Django 4.2 on 2024-07-16 18:39

from django.db import migrations, models
import django.db.models.deletion
import shortuuid.django_fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('purchase', '0004_alter_purchase_supplier'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('mobile_1', models.CharField(max_length=100)),
                ('mobile_2', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.EmailField(max_length=50)),
                ('contact_info', models.TextField()),
                ('sid', shortuuid.django_fields.ShortUUIDField(alphabet=None, length=3, max_length=7, prefix='cus-', unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10)),
                ('unit', models.DecimalField(decimal_places=2, max_digits=10)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('pid', shortuuid.django_fields.ShortUUIDField(alphabet=None, length=5, max_length=9, prefix='sls-', unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sale.customer')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='purchase.inventory')),
            ],
        ),
    ]
