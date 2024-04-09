from .models import OrderItem, Order

def cart_items(request):
    if request.user.is_authenticated:
        cart_items = OrderItem.objects.filter(order__user=request.user, order__status=Order.STATUS_CART)
        cart_count = cart_items.count()
    else:
        cart_count = 0
    return {'cart_count': cart_count}