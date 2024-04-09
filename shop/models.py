from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone


class Product(models.Model):
    class TypeMis(models.TextChoices):
        GORYCHI = 'GORYCHI', ('горячее')
        LAPSHA = 'LAPSHA', ('лапша')
        SALATI = 'SALATI', ('салаты')
        ZAKUZKI = 'ZAKUZKI', ('закуски')
        NAPITKI = 'NAPITKI', ('напитки ')

    name = models.CharField(max_length=255, verbose_name='Наименование товара')
    type_mis = models.CharField(max_length=50,choices=TypeMis.choices, default=TypeMis.GORYCHI, verbose_name='Вид товара')
    code = models.CharField(max_length=255, verbose_name='Код товара')
    price = models.DecimalField(max_digits=20, decimal_places=0, verbose_name='Цена')
    Discount = models.DecimalField(max_digits=20, decimal_places=0, null=True, blank=True, verbose_name='Скидка в %')
    image_url = models.URLField(blank=True, null=True, verbose_name='url изображения')
    image = models.ImageField('Изображение', upload_to='img', null=True, blank=True)
    note = models.TextField(blank=True, null=True, verbose_name='записка')
    time = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['pk']
        verbose_name_plural = 'Товары'

    def __str__(self):
        return f'{self.name} - {self.price}'


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    amount = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, verbose_name='Cумма')
    time = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')
    

    class Meta:
        ordering = ['pk']
        verbose_name_plural = 'Платеж'

    def __str__(self):
        return f'{self.user} - {self.amount}'

    @staticmethod
    def get_balance(user: User):
        amount = Payment.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum']
        return amount or Decimal(0)


class Order(models.Model):
    STATUS_CART = 'Корзина'
    STATUS_WAITING_FOR_PAYMENT = 'Ожидает платежа'
    STATUS_PAID = 'Оплачено'
    STATUS_CHOICES = [
        (STATUS_CART, 'Корзина'),
        (STATUS_WAITING_FOR_PAYMENT, 'Ожидает платежа'),
        (STATUS_PAID, 'Оплачено')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    # items = models.ManyToManyField(OrderItem, related_name='orders')
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_CART, verbose_name="Cтатус")
    amount = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, verbose_name="Cумма")
    creation_time = models.DateTimeField(auto_now_add=True)
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, blank=True, null=True, verbose_name='Платеж')
    pickup = models.CharField(max_length=100, blank=True, verbose_name='Cамовывоз')
    time_samo = models.CharField(max_length=50, blank=True, verbose_name='Время самовывоза')
    location = models.CharField(max_length=100, blank=True, verbose_name="Улица")
    home = models.CharField(max_length=50, blank=True, verbose_name="Дом")
    podezd = models.CharField(max_length=50,  blank=True, verbose_name="Подъезд")
    etaj = models.CharField(max_length=50, blank=True, verbose_name="Этаж")
    kvartir = models.CharField(max_length=30, blank=True, verbose_name="Квартира/офис")
    domofon = models.CharField(max_length=30, blank=False, verbose_name="Удобный способ оплаты")
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')
    file = models.FileField('Файл', upload_to='file', null=True, blank=True)
    time = models.DateTimeField(default=timezone.now, verbose_name='Время заказа')
    phone = models.CharField(max_length=100, blank=False, verbose_name="Телефон")



    class Meta:
        ordering = ['pk']
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.user} - {self.amount} - {self.status}'

    @staticmethod
    def get_cart(user: User):
        cart = Order.objects.filter(user=user,
                                    status=Order.STATUS_CART
                                    ).first()
        if cart and (timezone.now() - cart.creation_time).days > 2:
            cart.delete()
            cart = None

        if not cart:
            cart = Order.objects.create(user=user,
                                        status=Order.STATUS_CART,
                                        amount=0)
        return cart

    def get_amount(self):
        amount = Decimal(0)
        for item in self.orderitem_set.all():
            amount += item.amount
        return amount

    def make_order(self):
        items = self.orderitem_set.all()
        if items and self.status == Order.STATUS_CART:
            self.status = Order.STATUS_WAITING_FOR_PAYMENT
            self.save()
            auto_payment_unpaid_orders(self.user)

    @staticmethod
    def get_amount_of_unpaid_orders(user: User):
        amount = Order.objects.filter(user=user,
                                      status=Order.STATUS_WAITING_FOR_PAYMENT,
                                      ).aggregate(Sum('amount'))['amount__sum']
        return amount or Decimal(0)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Товар')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    price = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='Цена')
    discount = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name='Скидка в рублях')
    image = models.ImageField('Изображение', upload_to='img', null=True, blank=True)

    class Meta:
        ordering = ['pk']
        verbose_name_plural = 'Элемент заказа'

    def __str__(self):
        return f'{self.product} - {self.order}'

    @property
    def amount(self):
        return self.quantity * (self.price - self.discount)


@transaction.atomic()
def auto_payment_unpaid_orders(user: User):
    unpaid_orders = Order.objects.filter(user=user,
                                         status=Order.STATUS_WAITING_FOR_PAYMENT)
    for order in unpaid_orders:
        if Payment.get_balance(user) < order.amount:
            break
        order.payment = Payment.objects.all().last()
        order.status = Order.STATUS_PAID
        order.save()
        Payment.objects.create(user=user,
                               amount=-order.amount)


@receiver(post_save, sender=OrderItem)
def recalculate_order_amount_after_save(sender, instance, **kwargs):
    order = instance.order
    order.amount = order.get_amount()
    order.save()


@receiver(post_delete, sender=OrderItem)
def recalculate_order_amount_after_delete(sender, instance, **kwargs):
    order = instance.order
    order.amount = order.get_amount()
    order.save()


@receiver(post_save, sender=Payment)
def auto_payment(sender, instance, **kwargs):
    user = instance.user
    auto_payment_unpaid_orders(user)