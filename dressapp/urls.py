from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("product/<int:pk>/", views.product, name="product"),
    path("forgotpass/", views.forgot, name="forgotpass"),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/shipping/', views.checkout_shipping, name='checkout_shipping'),
    path('checkout/process_order/', views.process_order, name='process_order'),
    path("category/", views.category, name="category"),
    path("cart/", views.cart, name="cart"),
    path("register/", views.register, name="register"),
     path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path('processOrder/', views.processOrder, name='processOrder'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path("order-success/", views.order_success, name="order_success"),
    path('profile/', login_required(views.profile), name='profile'),
    path("update-quantity-ajax/", views.update_quantity_ajax, name="update_quantity_ajax"),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('delete-cart-item/', views.delete_cart_item, name='delete_cart_item'),
    path('order/success/<str:order_number>/', views.order_success, name='order_success'),
]
