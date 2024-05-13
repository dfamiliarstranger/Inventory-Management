# Generated by Django 4.2 on 2024-05-13 12:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0045_stock_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket_Records',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_size', models.IntegerField()),
                ('product_type', models.CharField(blank=True, max_length=30, null=True)),
                ('action', models.TextField()),
                ('quantity', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_at', models.DateField(blank=True, null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
