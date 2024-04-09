from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from shop import views

urlpatterns = [
    path('shop/', views.ProductsListView.as_view(), name='shop'),
    path('cart_view/', views.cart_view, name='cart_view'),
    path('detail/<int:pk>/',views.ProductsDetailView.as_view(), name='shop_detail'),
    path('add-item-to-cart/<int:pk>', views.add_item_to_cart, name='add_item_to_cart'),
    path('delete_item/<int:pk>', views.CartDeleteItem.as_view(), name='cart_delete_item'),
    path('make-order/', views.make_order, name='make_order'),
    path('shoping_payment/', views.shoping_payment, name='shoping_payment'),
    path('shop/<str:type_mis>/', views.ProductsListView.as_view(), name='products_by_category'),
    path('search/', views.ProductsSearchView.as_view(), name='search_results'),
]