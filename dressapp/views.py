import datetime
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, login as auth_login
from .models import Product,ContactUs, Customer, Order, OrderItem, ShippingAddress, Newsletter,Category
from django.utils.timezone import now
from django.http import HttpResponse
import uuid

# Create your views here.
def index(request):
    context = {}
    return render(request, "index.html",context=context)

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


def register(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')

        if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists")
        else:
            myuser = User.objects.create_user(username=email, email=email, password=password)
            myuser.first_name = firstname
            myuser.last_name = lastname
            myuser.save()
            messages.success(request, "Your account has been created successfully")
            return redirect("login")

    
    return render(request, "register.html")


def product(request):
    category = Category.objects.all()
    context = {'Category':category}
    return render(request, "product.html", context=context)

def forgot(request):
    context = {}
    return render(request, "forgotten-password.html", context=context)

def checkout(request):
    order = None  # Initialize order to ensure it is always defined
    items = []
    if request.user.is_authenticated:  # Use request.user instead of request.User
        customer = request.user.customer  # Assuming a one-to-one relationship
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()  # Ensure this matches the related name

    context = {'items': items, 'order': order}
    return render(request, "checkout.html", context=context)


def checkout_shipping(request):
    return render(request, 'checkout-shipping.html')

def checkout_payment(request):
    return render(request, 'checkout-payment.html')

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

from .models import Product  # Ensure you import the model correctly

def category(request):
    products = Product.objects.all()  # Model names are Capitalized
    context = {'products': products}
    return render(request, "category.html", context=context)


def cart(request):
    
    order = None  # Initialize order to ensure it is always defined
    items = []
    if request.user.is_authenticated:  # Use request.user instead of request.User
        customer = request.user.customer  # Assuming a one-to-one relationship
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()  # Ensure this matches the related name

    context = {'items': items, 'order': order}
    return render(request, "cart.html", context=context)

def updateitem(request):
    customer = request.user.customer
    productID = request.POST.get('productID')
    action = request.POST.get('action')
    
    product = get_object_or_404(product, id=productID)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1) 

    orderItem.save()
    
    if orderItem.quantity <= 0:
        orderItem.delete()
    
    return JsonResponse("Item is added", safe=False)

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)

def process_payment(request):
    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        if payment_method == "checkoutPaymentCOD":
            order = Order.objects.create(
                user=request.user,  # Assumes a logged-in user
                order_number=get_random_string(10).upper(),
                payment_method="Cash on Delivery",
                status="Pending",
            )
            messages.success(request, "Your order has been placed successfully! Pay on delivery.")
            return redirect("order_success")  # Redirect to order success page

        messages.error(request, "Invalid payment method.")
        return redirect("checkout_payment")  # Redirect back to payment page

    return redirect("checkout_payment")

def order_success(request):
    return render(request, "success.html")

def update_order_numbers_view(request):
    orders = Order.objects.all()
    for order in orders:
        order.order_number = f"ORD-{now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        order.save()
    
    return HttpResponse('Order numbers updated successfully!')
