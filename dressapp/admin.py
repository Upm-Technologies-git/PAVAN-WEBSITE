from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Customer, Product, Order, OrderItem, ShippingAddress,
    Newsletter, ContactUs, Category,Banner,FeaturedCategory,InstagramImage,ProductImage
)

# Inline for order items inside the order detail page
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['Product', 'quantity', 'get_total']
    can_delete = False

# Inline for shipping address inside the order detail page
class ShippingInline(admin.StackedInline):
    model = ShippingAddress
    extra = 0
    readonly_fields = ['address', 'city', 'state', 'zipcode', 'date_added']
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'status', 'complete', 'payment_method', 'transaction_id', 'date_ordered', 'get_cart_total']
    list_filter = ['status', 'complete', 'date_ordered']
    search_fields = ['order_number', 'transaction_id', 'customer__name']
    readonly_fields = ['order_number', 'transaction_id', 'date_ordered', 'get_cart_total', 'get_cart_items']
    inlines = [OrderItemInline, ShippingInline]

    def get_cart_total(self, obj):
        return f"₹{obj.get_cart_total:.2f}"
    get_cart_total.short_description = 'Total Amount'

    def get_cart_items(self, obj):
        return obj.get_cart_items
    get_cart_items.short_description = 'Total Items'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['Product', 'order', 'quantity', 'get_total']
    search_fields = ['Product__name', 'order__order_number']
    readonly_fields = ['get_total']

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'order', 'address', 'city', 'state', 'zipcode', 'date_added']
    search_fields = ['customer__name', 'order__order_number', 'city', 'state']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'email', 'phone']
    search_fields = ['name', 'email', 'phone', 'user__username']

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3  # You can set to 5 or more
    readonly_fields = ['preview']

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" style="object-fit: cover;" />', obj.image.url)
        return "-"
    preview.short_description = "Preview"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'digital', 'image_tag']
    search_fields = ['name']
    readonly_fields = ['image_tag']
    inlines = [ProductImageInline]
    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" />', obj.image.url)
        return "-"
    image_tag.short_description = 'Main Image'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'digital', 'image_tag']
    search_fields = ['name']
    readonly_fields = ['image_tag']

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" />', obj.image.url)
        return "-"
    image_tag.short_description = 'Image'

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['username', 'email']
    search_fields = ['username', 'email']

@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ['firstname', 'lastname', 'email', 'message']
    search_fields = ['firstname', 'lastname', 'email']

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'active']
    list_editable = ['order', 'active']
    search_fields = ['title', 'subtitle']


@admin.register(FeaturedCategory)
class FeaturedCategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'subtitle', 'order', 'active']
    list_filter = ['active']
    ordering = ['order']

@admin.register(InstagramImage)
class InstagramImageAdmin(admin.ModelAdmin):
    list_display = ['alt_text', 'active', 'order']
    list_editable = ['active', 'order']