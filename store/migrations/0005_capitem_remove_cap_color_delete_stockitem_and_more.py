# Generated by Django 4.2 on 2024-04-04 15:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_stockitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='CapItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.CharField(max_length=5)),
                ('price', models.IntegerField()),
                ('total', models.DecimalField(decimal_places=2, max_digits=5)),
                ('color', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='cap',
            name='color',
        ),
        migrations.DeleteModel(
            name='StockItem',
        ),
        migrations.AddField(
            model_name='capitem',
            name='cap',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.cap'),
        ),
    ]
