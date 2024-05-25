from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('profile/', views.profile_view, name="profile"),
    path('register/', views.register_view.as_view(), name="register"),


    path("add/<str:product_name>/", views.add_to_cart, name="add_to_cart"),
    path("remove/<str:product_name>/", views.remove_from_cart, name="remove_from_cart"),
    path('cart/', views.cart_detail, name="cart_detail"),
    path('otchet/', views.otchet, name='otchet'),

    path('order/<str:order_number>', views.view_order, name='order'),
    # path('return-product/<str:order_number>', views.view_return_product, name='return-product'),

    path('orders_detail/', views.orders_detail, name="orders_detail"),
    path('add_new_item/', views.add_new_item, name="add_new_item"),
]
