import datetime
import json
import uuid
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from .forms import ReviewForm
from django.db.models import Avg
from django.views.decorators.cache import never_cache
import re
from collections import namedtuple
from .models import (
    Product, ContactUs, Customer, Order, OrderItem,
    ShippingAddress, Newsletter,  Banner, FeaturedCategory, InstagramImage,Review,SizeOption,ProductSize
)

# Homepage

def index(request):
    banners = Banner.objects.filter(active=True).order_by('order')
    featured_categories = FeaturedCategory.objects.filter(active=True).order_by('order')
    featured_products = Product.objects.filter(is_featured=True)
    instagram_images = InstagramImage.objects.filter(active=True).order_by('order')
    return render(request, "index.html", {
        'banners': banners,
        'featured_categories': featured_categories,
        'featured_products': featured_products,
        'instagram_images': instagram_images,
    })

# Login View
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, "Please enter both email and password.")
            return redirect("login")

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect("index")
            else:
                messages.error(request, "Invalid email or password.")
        except User.DoesNotExist:
            messages.error(request, "Email not registered.")

        return redirect("login")

    return render(request, "login.html")

# Register View
def register(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')

        if not all([firstname, lastname, email, password, cpassword]):
            messages.error(request, "All fields are required.")
        elif password != cpassword:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        else:
            user = User.objects.create_user(username=email, email=email, password=password)
            user.first_name = firstname
            user.last_name = lastname
            user.save()
            Customer.objects.create(user=user)
            messages.success(request, "Your account has been created successfully.")
            return redirect("login")

    return render(request, "register.html")

# Product Detail

def product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:10]
    reviews = Review.objects.filter(product=product).order_by('-rating', '-created_at')
    review_form = ReviewForm()
    average_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    average_rating = round(average_rating, 1)

    # Fetch ProductSize availability
    product_sizes = ProductSize.objects.filter(product=product).select_related('size')
    available_sizes = {ps.size.code: ps.is_available for ps in product_sizes}

    # Build enhanced size list with availability
    SizeDisplay = namedtuple('SizeDisplay', ['code', 'is_available'])
    sizes = [
        SizeDisplay(size.code, available_sizes.get(size.code, False))
        for size in SizeOption.objects.all()
    ]

    if request.method == 'POST':
        if request.user.is_authenticated:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.user = request.user
                review.product = product
                review.save()
                return redirect('product', pk=product.pk)
        else:
            return redirect('login')

    return render(request, 'product.html', {
        'product': product,
        'sizes': sizes,  # now has .code and .is_available
        'related_products': related_products,
        'reviews': reviews,
        'average_rating': average_rating,
        'review_form': review_form,
    })

# Forgot Password View
def forgot(request):
    return render(request, "forgotten-password.html")

# Checkout View
def checkout(request):
    order = None
    items = []

    if request.user.is_authenticated:
        try:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            items = order.orderitem_set.all()
        except Customer.DoesNotExist:
            messages.error(request, "No customer profile found.")
            customer = None  # safely define customer as None if not found
    else:
        customer = None

    return render(request, "checkout.html", {"items": items, "order": order})

# Shipping and Payment Pages
def checkout_shipping(request):
    return render(request, 'checkout-shipping.html')

def checkout_payment(request):
    return render(request, 'checkout-payment.html')

# Cart View
def cart(request):
    order = None
    items = []
    if request.user.is_authenticated:
        try:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            items = order.orderitem_set.all()
        except Customer.DoesNotExist:
            messages.error(request, "No customer profile found.")

    return render(request, "cart.html", {"items": items, "order": order})

# Add to Cart
@login_required(login_url='login')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    size = request.POST.get("size") or request.GET.get("size", "")

    try:
        customer = request.user.customer
        order, _ = Order.objects.get_or_create(customer=customer, complete=False)

        if not size:
            messages.error(request, "Please select a size.")
            return redirect("product", product.id)

        # ✅ size included in lookup
        order_item, created = OrderItem.objects.get_or_create(order=order, product=product, size=size)

        if not created:
            order_item.quantity += 1

        order_item.save()
        messages.success(request, f"{product.name} ({size}) added to cart!")
    except Customer.DoesNotExist:
        messages.error(request, "Customer profile not found.")

    return redirect("cart")


# Process Order
@csrf_exempt
@require_POST
def process_order(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'}, status=403)

    data = json.loads(request.body)
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    if order.get_cart_total == 0:
        return JsonResponse({'error': 'Cannot place order with total ₹0'}, status=400)

    order.user = request.user
    order.complete = True
    order.payment_method = "COD"
    order.transaction_id = str(datetime.datetime.now().timestamp())
    order.save()

    ShippingAddress.objects.create(
        customer=customer,
        order=order,
        first_name=data.get('first_name', ''),
        last_name=data.get('last_name', ''),
        address=data.get('address', ''),
        city=data.get('city', ''),
        state=data.get('state', ''),
        zipcode=data.get('zip', ''),
        phone=data.get('phone', '')
    )

    for item in data.get('items', []):
        product_id = item.get('product_id')
        quantity = item.get('quantity', 1)
        OrderItem.objects.get_or_create(
            order=order,
            product_id=product_id,
            defaults={'quantity': quantity}
        )

    return JsonResponse({'success': True, 'order_number': order.order_number})
# Payment Processing
def process_payment(request):
    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        if payment_method == "checkoutPaymentCOD":
            try:
                customer = request.user.customer
                order, created = Order.objects.get_or_create(customer=customer, complete=False)
                if order.get_cart_total == 0:
                    messages.error(request, "Cannot place order with total ₹0")
                    return redirect("checkout_payment")
                order.payment_method = "Cash on Delivery"
                order.status = "Pending"
                order.complete = True
                order.save()

                subject = f"New COD Order from {customer.name}"
                message = f"""
                A new order has been placed:

                Order Number: {order.order_number}
                Customer: {customer.name}
                Email: {request.user.email}
                Payment Method: {order.payment_method}
                Status: {order.status}
                Total Amount: ₹{order.get_cart_total:.2f}
                Date: {order.date_ordered.strftime('%Y-%m-%d %H:%M')}
                """

                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    ['wabiwabiclothing@gmail.com'],
                    fail_silently=False,
                )

                return render(request, "order-summary.html", {"order": order})
            except Customer.DoesNotExist:
                messages.error(request, "No customer profile found.")
                return redirect("checkout_payment")

        messages.error(request, "Invalid payment method.")
        order.shipping_charge = 99  # Set fixed shipping fee
        order.save()
    return redirect("checkout_payment")

# Success Page
def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'success.html', {'order': order})

# Profile Update
# Profile Update
@login_required
@never_cache
def profile(request):
    # Ensure the customer profile exists
    customer, created = Customer.objects.get_or_create(
        user=request.user,
        defaults={
            'name': f"{request.user.first_name} {request.user.last_name}".strip(),
            'email': request.user.email,
        }
    )

    orders = Order.objects.filter(customer=customer, complete=True).order_by('-date_ordered')

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')

        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        customer.name = f"{first_name} {last_name}".strip()
        customer.phone = phone
        customer.save()

        messages.success(request, "Profile updated successfully!")

    return render(request, 'profile.html', {"orders": orders})

# Quantity Update via AJAX
@csrf_exempt
@require_POST
def update_quantity_ajax(request):
    data = json.loads(request.body)
    item_id = data.get('item_id')
    quantity = int(data.get('quantity', 1))

    try:
        item = OrderItem.objects.get(id=item_id, order__customer=request.user.customer, order__complete=False)
        item.quantity = quantity
        item.save()

        return JsonResponse({
            'success': True,
            'item_total': round(item.get_total(), 2),
            'cart_total': round(item.order.get_cart_total, 2)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
@login_required
def update_cart_item(request, item_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity'))

            order_item = OrderItem.objects.get(id=item_id, order__customer=request.user.customer, order__complete=False)
            order_item.quantity = quantity
            order_item.save()

            return JsonResponse({
                'item_total': order_item.get_total,
                'cart_total': order_item.order.get_cart_total
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid method'}, status=405)

# Delete Cart Item
@csrf_exempt
def delete_cart_item(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        item_id = data.get('item_id')

        try:
            item = OrderItem.objects.get(id=item_id)
            item.delete()
            return JsonResponse({'success': True})
        except OrderItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item not found'})


def category(request):
    products = Product.objects.all()
    return render(request, "category.html", {"products": products})


def normalize(text):
    return re.sub(r'[^a-z0-9\s]', '', text.lower())

def search_results(request):
    query = request.GET.get('q', '').strip()
    normalized_query = normalize(query)

    matched_products = []
    if normalized_query:
        for product in Product.objects.all():
            if normalized_query in normalize(product.name):
                matched_products.append(product)

    if not matched_products:
        messages.error(request, "No product found matching your search.")
        return redirect('index')

    elif len(matched_products) == 1:
        return redirect('product', pk=matched_products[0].id)

    else:
        # Store matched product IDs and query in session for use in category view
        request.session['search_matched_ids'] = [product.id for product in matched_products]
        request.session['search_query'] = query
        return redirect('category_from_search')
    
@login_required
def category_from_search(request):
    ids = request.session.get('search_matched_ids', [])
    query = request.session.get('search_query', '')

    if not ids:
        messages.warning(request, "Search session expired.")
        return redirect('index')

    products = Product.objects.filter(id__in=ids).order_by('name')  # You can change sort here
    return render(request, 'category.html', {
        'products': products,
        'search_query': query,
        'filtered': True
    })

@login_required
def order_history(request):
    orders = Order.objects.filter(customer=request.user).order_by('-order_date')
    return render(request, 'order_history.html', {'orders': orders})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user.customer)

    if order.status != "Cancelled":
        order.status = "Cancelled"
        order.save()
        messages.success(request, f"Order #{order.order_number} has been cancelled.")

    return redirect('profile') 