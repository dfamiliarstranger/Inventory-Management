# Generated by Django 4.2 on 2024-05-08 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0029_alter_customer_name_alter_supplier_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=10, null=True)),
            ],
        ),
    ]