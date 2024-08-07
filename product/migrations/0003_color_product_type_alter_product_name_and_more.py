# Generated by Django 4.2 on 2024-07-13 12:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_alter_product_pid'),
    ]

    operations = [
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Product_type',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(choices=[('preform', 'Preform'), ('cap', 'Cap'), ('shrinkwrapper', 'Shrinkwrapper'), ('bottle', 'Bottle')], max_length=100),
        ),
        migrations.AlterField(
            model_name='product',
            name='unit',
            field=models.CharField(choices=[('grams', 'Grams'), ('kilogram', 'Kilogram'), ('millilitre', 'Millilitre'), ('centilitre', 'Centilitre'), ('litre', 'Litre')], max_length=20),
        ),
        migrations.AlterField(
            model_name='product',
            name='color',
            field=models.ForeignKey(blank=True, max_length=50, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='product.color'),
        ),
        migrations.AlterField(
            model_name='product',
            name='type',
            field=models.ForeignKey(max_length=50, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='product.product_type'),
        ),
    ]
