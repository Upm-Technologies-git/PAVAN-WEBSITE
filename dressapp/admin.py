from django.contrib import admin
from django.utils.html import format_html
from .forms import ProductAdminForm
from .models import (
    Customer, Product, Order, OrderItem, ShippingAddress,
    Newsletter, ContactUs,Banner,FeaturedCategory,InstagramImage,ProductImage,Review,ProductSize,SizeOption
)

# Inline for order items inside the order detail page
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ['product', 'quantity', 'size', 'get_total', 'product_image']
    readonly_fields = ['product', 'quantity', 'size', 'get_total', 'product_image']
    extra = 0

    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = "Total"

    def product_image(self, obj):
        if obj.product and obj.product.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit:contain;"/>', obj.product.image.url
            )
        return "No Image"
    product_image.short_description = "Image"

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
    readonly_fields = ['order_number', 'transaction_id', 'date_ordered', 'get_cart_total', 'get_cart_items','shipping_charge']
    inlines = [OrderItemInline, ShippingInline]

    def get_cart_total(self, obj):
        return f"₹{float(obj.get_cart_total) +99:.2f}"
    get_cart_total.short_description = 'Total Amount'

    def get_cart_items(self, obj):
        return obj.get_cart_items()  
    get_cart_items.short_description = 'Total Items'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(complete=True)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'order', 'quantity', 'get_total']
    search_fields = ['product__name', 'order__order_number']
    readonly_fields = ['product', 'quantity', 'get_total']

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'address', 'city', 'state', 'zipcode', 'phone', 'date_added')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'email', 'phone']
    search_fields = ['name', 'email', 'phone', 'user__username']

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    readonly_fields = ['preview']

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" style="object-fit: cover;" />', obj.image.url)
        return "-"
    preview.short_description = "Preview"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ['name', 'price', 'digital', 'image_tag']
    search_fields = ['name']
    readonly_fields = ['image_tag']
    inlines = [ProductImageInline]

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" />', obj.image.url)
        return "-"
    image_tag.short_description = 'Main Image'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        selected_sizes = form.cleaned_data.get('new_sizes')
        if selected_sizes is None:
            selected_sizes = SizeOption.objects.none()

        for size in SizeOption.objects.all():
            ps_obj, created = ProductSize.objects.get_or_create(product=obj, size=size)
            if size in selected_sizes:
                ps_obj.is_available = True
            else:
                ps_obj.is_available = False
            ps_obj.save()

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

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'comment', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'product__name', 'comment')

@admin.register(SizeOption)
class SizeOptionAdmin(admin.ModelAdmin):
    list_display = ['code']