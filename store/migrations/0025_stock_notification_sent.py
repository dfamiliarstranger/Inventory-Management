# Generated by Django 4.2 on 2024-05-07 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0024_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='notification_sent',
            field=models.BooleanField(default=False),
        ),
    ]
