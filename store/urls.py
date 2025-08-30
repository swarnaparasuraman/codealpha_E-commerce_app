from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.product_list_view, name='product_list'),
    path('product/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('category/<slug:slug>/', views.category_products_view, name='category_products'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/', views.add_to_cart_view, name='add_to_cart'),
    path('update-cart-item/', views.update_cart_item_view, name='update_cart_item'),
    path('remove-from-cart/', views.remove_from_cart_view, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order-confirmation/<str:order_number>/', views.order_confirmation_view, name='order_confirmation'),
    path('order/<str:order_number>/', views.order_detail_view, name='order_detail'),
]
