# my_app/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
import json

class User(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )



class Receipt(models.Model):
    image = models.ImageField(upload_to='receipts/')
    merchant_name = models.CharField(max_length=200, null=True)
    date = models.DateField(null=True)
    document_number = models.CharField(max_length=100, null=True)
    total_items = models.IntegerField(null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tax = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    payment_method = models.CharField(max_length=100, null=True)
    payment_status = models.CharField(max_length=50, null=True)
    raw_json = models.JSONField(null=True)  # Store complete JSON response
    created_at = models.DateTimeField(auto_now_add=True)

class ReceiptItem(models.Model):
    receipt = models.ForeignKey(Receipt, related_name='items', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

class AdditionalCharge(models.Model):
    receipt = models.ForeignKey(Receipt, related_name='additional_charges', on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=50)
    reliability_score = models.FloatField(default=0.0)
    
    def __str__(self):
        return self.name

class Component(models.Model):
    CATEGORY_CHOICES = [
        ('CPU', 'Processor'),
        ('RAM', 'Memory'),
        ('SSD', 'Storage'),
        ('SCREEN', 'Display'),
        ('GPU', 'Graphics Card'),
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    lead_time_days = models.IntegerField()
    
    def __str__(self):
        return f"{self.name} ({self.category})"

class Laptop(models.Model):
    model_name = models.CharField(max_length=100)
    components = models.ManyToManyField(Component)
    production_date = models.DateField()
    production_cost = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    units_produced = models.IntegerField()
    
    def __str__(self):
        return self.model_name

class Inventory(models.Model):
    laptop = models.ForeignKey(Laptop, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)
    warehouse_location = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.laptop.model_name} - {self.quantity} units"

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
    ]
    
    laptop = models.ForeignKey(Laptop, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    delivery_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.laptop.model_name}"


class ChatMessage(models.Model):
    SENDER_CHOICES = [
        ('USER', 'User'),
        ('BOT', 'Bot'),
    ]
    
    sender = models.CharField(max_length=4, choices=SENDER_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']