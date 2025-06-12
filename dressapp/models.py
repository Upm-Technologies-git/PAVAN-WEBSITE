import os
import uuid
from django.utils.timezone import now
from django.db import models
from django.contrib.auth.models import User

# Function to generate file names dynamically
def getFileName(instance, filename):
    base, ext = os.path.splitext(filename)
    return f"uploads/{instance.__class__.__name__}/{now().strftime('%Y%m%d%H%M%S')}{ext}"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.CharField(max_length=200, unique=True, null=True)

    def __str__(self):
        return self.user.username 

class Product(models.Model):
    name = models.CharField(max_length=200, null=True)
    price = models.FloatField()
    digital = models.BooleanField(default=False, null=True, blank=False)
    image = models.ImageField(null=True, blank=True, upload_to=getFileName)

    def __str__(self):
        return f'Product {self.name}'

    @property
    def imageURL(self):
        return self.image.url if self.image else ''


class Order(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ]

    customer = models.ForeignKey('Customer', on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    transaction_id = models.CharField(max_length=200, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)

    def __str__(self):
        return f"Order {self.id}"

    @property
    def get_cart_total(self):
        total = sum([item.get_total for item in self.orderitem_set.all()])
        return total

    @property
    def get_cart_items(self):
        return sum(item.quantity for item in self.orderitem_set.all())

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    Product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, default=0)
    quantity = models.IntegerField(default=1, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OrderItem {self.Product} ({self.quantity})"

    @property
    def get_total(self):
        return self.Product.price * self.quantity

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="shipping_addresses", default=0)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address if self.address else "No Address"

class Newsletter(models.Model):
    username = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=254, null=True, unique=True)

    def __str__(self):
        return f'User {self.username or "Anonymous"}'

class ContactUs(models.Model):
    firstname = models.CharField(max_length=100, null=True)
    lastname = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=254, null=True)
    message = models.TextField(null=True)

    def __str__(self):
        return f'User {self.firstname or "Anonymous"}'
   
class Category(models.Model):
    name = models.CharField(max_length=200, null=True)
    price = models.FloatField()
    digital = models.BooleanField(default=False, null=True, blank=False)
    image = models.ImageField(null=True, blank=True, upload_to=getFileName)

    def __str__(self):
        return f'Category {self.name}'

    @property
    def imageURL(self):
        return self.image.url if self.image else ''
    
