from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("product/", views.product, name="product"),
    path("forgotpass/", views.forgot, name="forgotpass"),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/shipping/', views.checkout_shipping, name='checkout_shipping'),
    path('checkout/process_order/', views.process_order, name='process_order'),
    path("category/", views.category, name="category"),
    path("cart/", views.cart, name="cart"),
    path("register/", views.register, name="register"),
    path('updateitem/', views.updateitem, name='updateitem'),
    path('processOrder/', views.processOrder, name='processOrder'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path("order-success/", views.order_success, name="order_success"),
]
