# Generated by Django 4.2 on 2024-05-13 18:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0046_ticket_records'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket_records',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.stock'),
        ),
    ]
