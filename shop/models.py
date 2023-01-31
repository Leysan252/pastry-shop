from decimal import Decimal

from PIL import Image
import io
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.db import models, transaction
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.datetime_safe import datetime
from django.utils.timezone import now


class Product(models.Model):
    type_p = models.CharField(max_length=255, verbose_name='product_type')
    name = models.CharField(max_length=255, verbose_name='product_name')
    price = models.DecimalField(max_digits=20, decimal_places=2)
    unit = models.CharField(max_length=255, blank=True, null=True)
    image_file = models.ImageField(upload_to='images/')
    note = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return f'{self.name}-{self.price}'


class Reviews(models.Model):
    name_r = models.CharField(max_length=255, verbose_name='rev_name')
    email_r = models.CharField(max_length=255, verbose_name='rev_email')
    number = models.CharField(max_length=12, validators=[MinLengthValidator(12)], blank=False)
    message = models.TextField()
    image_r = models.ImageField(upload_to='reviews/', blank=True)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return f'{self.name_r}'


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    time = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return f'{self.user}-{self.amount}'

    @staticmethod
    def get_balance(user: User):
        amount = Payment.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum']
        return amount or Decimal(0)


class Order(models.Model):
    STATUS_CART = '1_cart'
    STATUS_WAITING_FOR_PAYMENT = '2_waiting_for_payment'
    STATUS_PAID = '3_paid'
    STATUS_CHOICES = [
        (STATUS_CART, 'cart'),
        (STATUS_WAITING_FOR_PAYMENT, 'waiting_for_payment'),
        (STATUS_PAID, 'paid')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # items = models.ManyToManyField(OrderItem, related_name='orders')
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_CART)
    amount = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    adress = models.CharField(max_length=255, verbose_name='adress', null=True, blank=True)
    date_del = models.CharField(max_length=255, verbose_name='date_del', null=True, blank=True)
    type_del = models.CharField(max_length=255, verbose_name='type_del', null=True, blank=True)
    decor = models.ImageField(upload_to='decor/', blank=True)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return f'{self.user}-{self.amount} -  {self.status}'

    @staticmethod
    def get_cart(user: User):
        cart = Order.objects.filter(user=user,
                                    status=Order.STATUS_CART).first()

        if cart and (timezone.now() - cart.creation_time).days > 7:
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
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    discount = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return f'{self.product}-{self.price}'

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
                               amount=order.amount)


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
