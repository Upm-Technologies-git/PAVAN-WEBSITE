import datetime
import json
import uuid

from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt


from .models import (
    Product, ContactUs, Customer, Order, OrderItem,
    ShippingAddress, Newsletter, Category
)

# Homepage

def index(request):
    return render(request, "index.html")

# Login View
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect("index")
        else:
            messages.error(request, "Bad credentials")
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

        if password != cpassword:
            messages.error(request, "Passwords do not match")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
        else:
            user = User.objects.create_user(username=email, email=email, password=password)
            user.first_name = firstname
            user.last_name = lastname
            user.save()
            Customer.objects.create(user=user)  # Ensure a Customer object is created
            messages.success(request, "Your account has been created successfully")
            return redirect("login")

    return render(request, "register.html")

# Product listing page
def product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "product.html", {"Product": product})

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

    return render(request, "checkout.html", {"items": items, "order": order})

# Shipping and Payment Pages
def checkout_shipping(request):
    return render(request, 'checkout-shipping.html')

def checkout_payment(request):
    return render(request, 'checkout-payment.html')

# Process Order from JS/AJAX
def process_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        order = Order.objects.create(
            customer_name=data['name'],
            email=data['email'],
            address=data['address'],
            city=data['city'],
            state=data['state'],
            zip_code=data['zip']
        )
        for item in data['items']:
            OrderItem.objects.create(
                order=order,
                product_name=item['name'],
                quantity=item['quantity'],
                price=item['price']
            )
        return JsonResponse({'message': 'Order placed successfully!'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

# Category Products
def category(request):
    products = Product.objects.all()
    return render(request, "category.html", {"products": products})

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

# AJAX Cart Update
def add_to_cart(request, product_id):
    customer = request.user.customer
    product = get_object_or_404(Product, id=product_id)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    order_item, created = OrderItem.objects.get_or_create(order=order, Product=product)

    if not created:
        order_item.quantity += 1
    order_item.save()

    messages.success(request, f"{product.name} added to cart!")
    return redirect("cart")

# Payment and Order Processing
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=403)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total()):
        order.complete = True
    order.save()

    if order.shipping:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment submitted..', safe=False)

# Payment Page
from django.utils.crypto import get_random_string

def process_payment(request):
    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        if payment_method == "checkoutPaymentCOD":
            order = Order.objects.create(
                customer=request.user.customer,
                order_number=get_random_string(10).upper(),
                payment_method="Cash on Delivery",
                status="Pending",
            )
            messages.success(request, "Your order has been placed successfully! Pay on delivery.")
            return redirect("order_success")

        messages.error(request, "Invalid payment method.")
        return redirect("checkout_payment")

    return redirect("checkout_payment")

# Success Page
def order_success(request):
    return render(request, "success.html")

# Utility: Generate Order Numbers
def update_order_numbers_view(request):
    orders = Order.objects.all()
    for order in orders:
        order.order_number = f"ORD-{now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        order.save()

    return HttpResponse('Order numbers updated successfully!')

@login_required
def profile(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')

        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # Ensure customer profile exists
        customer, created = Customer.objects.get_or_create(user=user)
        customer.phone = phone
        customer.save()

        messages.success(request, "Profile updated successfully!")

    return render(request, 'profile.html')

def product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "product.html", {"product": product})




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

        item_total = round(item.get_total, 2)
        order = item.order
        cart_total = round(order.get_cart_total, 2)
        return JsonResponse({'success': True, 'item_total': item_total, 'cart_total': cart_total})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@login_required
def update_cart_item(request, item_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_quantity = int(data.get('quantity'))
            order_item = OrderItem.objects.get(id=item_id, order__customer=request.user.customer, order__complete=False)

            order_item.quantity = new_quantity
            order_item.save()

            item_total = order_item.get_total
            cart_total = order_item.order.get_cart_total

            return JsonResponse({'item_total': item_total, 'cart_total': cart_total})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid method'}, status=405)