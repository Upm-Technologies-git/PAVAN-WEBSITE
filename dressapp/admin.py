from django.contrib import admin
from .models import *

# Register your models here.
class customeradmin(admin.ModelAdmin):
    list_display = ("email","name")
    list_filter = ("name",)

admin.site.register(Customer, customeradmin)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(Newsletter)
admin.site.register(ContactUs)
admin.site.register(Category)