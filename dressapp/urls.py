from django.urls import path
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path("product/<int:pk>/", views.product, name="product"),
    path("forgotpass/", views.forgot, name="forgotpass"),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/shipping/', views.checkout_shipping, name='checkout_shipping'),
    path('checkout/process_order/', views.process_order, name='process_order'),
    path("category/", views.category, name="category"),
    path("cart/", views.cart, name="cart"),
    path("register/", views.register, name="register"),
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path('process-payment/', views.process_payment, name='process_payment'),
    path("order-success/", views.order_success, name="order_success"),
    path('profile/', login_required(views.profile), name='profile'),
    path("update-quantity-ajax/", views.update_quantity_ajax, name="update_quantity_ajax"),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('delete-cart-item/', views.delete_cart_item, name='delete_cart_item'),
    path('order/success/<str:order_number>/', views.order_success, name='order_success'),
    path('search-product/', views.search_results, name='search_redirect'),
    path('search-category/', views.category_from_search, name='category_from_search'),
    path('order-history/', views.order_history, name='order_history'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
]