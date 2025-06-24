import os
import uuid
from django.utils.timezone import now
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


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



    @property
    def imageURL(self):
        return self.image.url if self.image else ''

class Product(models.Model):
    name = models.CharField(max_length=200, null=True)
    price = models.FloatField()
    digital = models.BooleanField(default=False, null=True, blank=False)
    image = models.ImageField(null=True, blank=True, upload_to=getFileName)  # Primary display image
    is_featured = models.BooleanField(default=False)  # Add this line
    tagline = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100 ,blank=True, null=True)

    def __str__(self):
        return f'Product {self.name}'

    @property
    def imageURL(self):
        return self.image.url if self.image else ''
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=getFileName)

    def __str__(self):
        return f"Image for {self.product.name}"


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
    shipping_charge = models.FloatField(default=99.00)

    def __str__(self):
        return f"Order {self.id}"

    @property
    def get_total(self):
        if self.product and self.product.price:
            return self.product.price * self.quantity
        return 0 

    @property
    def get_cart_total(self):
        items_total = sum(item.get_total() for item in self.orderitem_set.all())
        return items_total 
    
    def get_cart_items(self):
        return sum([item.quantity for item in self.orderitem_set.all()])
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, default=0)
    quantity = models.IntegerField(default=1,blank=True)
    size = models.CharField(max_length=5, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def get_total(self):
        if self.product and self.product.price:
            return self.product.price * self.quantity
        return 0

    def __str__(self):
        product_name = self.product.name if self.product else "Deleted Product"
        return f"{product_name} x {self.quantity} ({self.size})"


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="shipping_addresses", default=0)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True) 
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=15, null=True)
    zipcode = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.first_name else "No Name"


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
   

    
class Banner(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200)
    button_text = models.CharField(max_length=50)
    image = models.ImageField(upload_to='banners/')
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
class FeaturedCategory(models.Model):
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='categories/')
    button_text = models.CharField(max_length=50, default='Shop Now')

    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    def get_link(self):
        return self.link_url or reverse('category')

    def __str__(self):
        return self.title    
        

class InstagramImage(models.Model):
    image = models.ImageField(upload_to='instagram/')
    alt_text = models.CharField(max_length=255, blank=True)
    active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.alt_text or f"Instagram Image {self.id}"
    
class Review(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1 to 5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}⭐)"

class SizeOption(models.Model):
    code = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return self.code

class ProductSize(models.Model):
    product = models.ForeignKey(Product, related_name='sizes', on_delete=models.CASCADE)
    size = models.ForeignKey(SizeOption, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('product', 'size')

    def __str__(self):
        return f"{self.product.name} - {self.size.code}"
    
