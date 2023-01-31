from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, DeleteView

from .forms import *
from datetime import date


def fill_database(request):
    if request.method == 'POST' and request.user.is_staff:
        print("before")
        form_product = ProductForm(request.POST, request.FILES)

        print(f"{request.POST=}")
        if form_product.is_valid():
            print("++++++++++++++++++++++++++++++++++++")
            form_product.save()
            return redirect('index')
        else:
            messages.error(request, 'Форма заполнена неверно')
    return render(request, 'shop/fill_database.html')


def product_list(request):
    return render(request, 'shop/product_list.html')


@login_required(login_url='login')
def product_change(request, pk):
    sub = Product.objects.get(id=pk)
    form = Product(instance=sub)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=sub)
        if form.is_valid():
            form.save()
            redirect('index')
        else:
            messages.error(request, 'Форма заполнена неверно.')

    return render(request, 'shop/product_change.html', {'form': form})


def contact(request):
    if request.method == 'POST':
        print("before")
        form_reviews = ReviewsForm(request.POST, request.FILES)

        print(f"{request.POST=}")
        if form_reviews.is_valid():
            form_reviews.save()
            return redirect('index')
        else:
            print(form_reviews.errors)
            messages.error(request, 'Форма заполнена неверно')
    return render(request, 'shop/contact.html')


class ProductsListView(ListView):
    model = Product
    template_name = 'shop/products.html'


class ProductsDetailView(DetailView):
    model = Product
    template_name = 'shop/single.html'


@login_required(login_url=reverse_lazy('login'))
def add_item_to_cart(request, pk):
    if request.method == 'POST':
        quantity_form = AddQuantityForm(request.POST)
        if quantity_form.is_valid():
            quantity = quantity_form.cleaned_data['quantity']
            if quantity:
                cart = Order.get_cart(request.user)
                # product = Product.objects.get(pk=pk)
                product = get_object_or_404(Product, pk=pk)
                cart.orderitem_set.create(product=product,
                                          quantity=quantity,
                                          price=product.price)
                cart.save()
                return redirect('checkout')
        else:
            pass
    return redirect('products')


@login_required(login_url=reverse_lazy('login'))
def checkout(request):
    cart = Order.get_cart(request.user)
    items = cart.orderitem_set.all()
    context = {
        'cart': cart,
        'items': items,
    }
    if request.method == 'POST':
        print("before")
        form_reviews = ReviewsForm(request.POST, request.FILES)

        print(f"{request.POST=}")
        if form_reviews.is_valid():
            form_reviews.save()
            return redirect('index')
        else:
            print(form_reviews.errors)
            messages.error(request, 'Форма заполнена неверно')
    return render(request, 'shop/checkout.html', context)


@method_decorator(login_required, name='dispatch')
class CartDeleteItem(DeleteView):
    model = OrderItem
    template_name = 'shop/checkout.html'
    success_url = reverse_lazy('checkout')

    # Проверка доступа
    def get_queryset(self):
        qs = super().get_queryset()
        qs.filter(order__user=self.request.user)
        return qs


@login_required(login_url=reverse_lazy('login'))
def make_order(request):
    cart = Order.get_cart(request.user)
    cart.make_order()

    if request.method == 'POST':
        print("before")
        zakaz = OrderForm(request.POST, request.FILES)

        print(f"{request.POST=}")
        if zakaz.is_valid():
            print("++++++++++++++++++++++++++++++++++++")
            zakaz.save()
            return redirect('index')
        else:
            messages.error(request, 'Форма заполнена неверно')

    return redirect('checkout')
