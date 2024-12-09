# Generated by Django 5.1.1 on 2024-12-09 17:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender', models.CharField(choices=[('USER', 'User'), ('BOT', 'Bot')], max_length=4)),
                ('message', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Component',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('category', models.CharField(choices=[('CPU', 'Processor'), ('RAM', 'Memory'), ('SSD', 'Storage'), ('SCREEN', 'Display'), ('GPU', 'Graphics Card')], max_length=20)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('lead_time_days', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='receipts/')),
                ('merchant_name', models.CharField(max_length=200, null=True)),
                ('date', models.DateField(null=True)),
                ('document_number', models.CharField(max_length=100, null=True)),
                ('total_items', models.IntegerField(null=True)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('tax', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('payment_method', models.CharField(max_length=100, null=True)),
                ('payment_status', models.CharField(max_length=50, null=True)),
                ('raw_json', models.JSONField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('country', models.CharField(max_length=50)),
                ('reliability_score', models.FloatField(default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='Laptop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_name', models.CharField(max_length=100)),
                ('production_date', models.DateField()),
                ('production_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('selling_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('units_produced', models.IntegerField()),
                ('components', models.ManyToManyField(to='my_app.component')),
            ],
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('warehouse_location', models.CharField(max_length=100)),
                ('laptop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='my_app.laptop')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('PROCESSING', 'Processing'), ('SHIPPED', 'Shipped'), ('DELIVERED', 'Delivered')], default='PENDING', max_length=20)),
                ('delivery_date', models.DateField(blank=True, null=True)),
                ('laptop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='my_app.laptop')),
            ],
        ),
        migrations.CreateModel(
            name='AdditionalCharge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=200)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('receipt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='additional_charges', to='my_app.receipt')),
            ],
        ),
        migrations.CreateModel(
            name='ReceiptItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('quantity', models.IntegerField()),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('receipt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='my_app.receipt')),
            ],
        ),
        migrations.AddField(
            model_name='component',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='my_app.supplier'),
        ),
    ]
