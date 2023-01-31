from django.forms import ModelForm, forms

from .models import *


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })


class ReviewsForm(ModelForm):
    class Meta:
        model = Reviews
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(ReviewsForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })


class AddQuantityForm(ModelForm):
    class Meta:
        model = OrderItem
        fields = ['quantity']


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
