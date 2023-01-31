from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.views.generic import TemplateView

from konditer import settings
from shop import views

urlpatterns = [
    path('fill_database/', views.fill_database, name='fill_database'),
    path('', views.ProductsListView.as_view(), name='products'),
    path('checkout/', views.checkout, name='checkout'),
    path('contact/', views.contact, name='contact'),
    path('product_list/', views.product_list, name='product_list'),
    path('product_change/', views.product_change, name='product_change'),
    path('single/<int:pk>/',
         views.ProductsDetailView.as_view(), name='single'),
    path('add-item-to-cart/<int:pk>', views.add_item_to_cart, name='add_item_to_cart'),
    path('delete_item/<int:pk>', views.CartDeleteItem.as_view(), name='cart_delete_item'),
    path('make_order/', views.make_order, name='make_order'),
]
