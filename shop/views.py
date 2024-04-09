from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, DeleteView
from shop.forms import AddQuantityForm, OrderUserView, FileFormView
from shop.models import Product, Order, OrderItem
from django.views.generic import TemplateView
from .models import auto_payment_unpaid_orders
from django import template
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST


class ProductsSearchView(ListView):
    model = Product
    template_name = 'shop/search_results.html' 

    def get_queryset(self):
        query = self.request.GET.get('query')
        if query:
            return Product.objects.filter(name__icontains=query)
        return Product.objects.none()  # Возвращаем пустой запрос

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('query', '')
        return context


class ProductsListView(ListView):
    model = Product
    template_name = 'shop/shop.html'
    ordering = ["-time"]
    paginate_by = 6 
    context_object_name = 'products'
    paginate_by = 6
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['load_more'] = self.paginate_by 
        return context
    
    #Этот код проверяет, есть ли предыдущая страница (), и если она есть, он создает новую кнопку, которая ссылается на первую страницу ().page_obj.has_previous"?page=1&load_more={{ load_more }}"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['load_more'] = self.request.GET.get('load_more', '')
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        type_mis = self.kwargs.get('type_mis', None)
        if type_mis:
            queryset = queryset.filter(type_mis=type_mis)
        return queryset


def shoping_payment(request):
    return render(request, 'shoping_payment.html')


class ProductsDetailView(DetailView):
    model = Product
    template_name = 'shop/shop-details.html'


@login_required(login_url=reverse_lazy('login'))
@require_POST
def add_item_to_cart(request, pk):
    quantity_form = AddQuantityForm(request.POST)
    if quantity_form.is_valid():
        quantity = quantity_form.cleaned_data['quantity']
        cart = Order.get_cart(request.user)
        product = get_object_or_404(Product, pk=pk)
        cart.orderitem_set.create(product=product, quantity=quantity, price=product.price)
        cart.save()
        
        cart_items = cart.orderitem_set.all()
        cart_count = sum(item.quantity for item in cart_items)

        return JsonResponse({"status": "success", "message": "Товар успешно добавлен в корзину", "cart_count": cart_count})
    else:
        return JsonResponse({"status": "error", "message": "Произошла ошибка при добавлении товара в корзину"})


@login_required(login_url=reverse_lazy('login'))
def cart_view(request):
    cart = Order.get_cart(request.user)
    items = cart.orderitem_set.all()
    delivery_form = OrderUserView()
    file_form = FileFormView()
    context = {
        'cart': cart,
        'items': items,
        'form': delivery_form,
        'file_form': file_form,
    }

    if request.method == 'POST':
        cart = Order.get_cart(request.user)
        cart.status = Order.STATUS_WAITING_FOR_PAYMENT
        # доставка
        cart.phone = request.POST.get('phone')  
        cart.location = request.POST.get('location')
        cart.home = request.POST.get('home')
        cart.podezd = request.POST.get('podezd')
        cart.etaj = request.POST.get('etaj')
        cart.kvartir = request.POST.get('kvartir')
        cart.domofon = request.POST.get('domofon')
        cart.comment = request.POST.get('comment')
        # самовывез
        cart.time_samo = request.POST.get('time_samo')
        cart.save()
        auto_payment_unpaid_orders(cart.user)
        return redirect('resultat')

    return render(request, 'shop/cart.html', context)



@method_decorator(login_required, name='dispatch')
class CartDeleteItem(DeleteView):
    model = OrderItem
    template_name = 'shop/cart.html'
    success_url = reverse_lazy('cart_view')

    # Проверка доступа
    def get_queryset(self):
        qs = super().get_queryset()
        qs.filter(order__user=self.request.user)
        return qs


@login_required(login_url=reverse_lazy('login'))
def make_order(request):
    cart = Order.get_cart(request.user)
    cart.make_order()
    return redirect('shop')
