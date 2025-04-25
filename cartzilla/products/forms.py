from django import forms
from .models import Product, Review, Category, BargainRequest


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'image', 'category', 'allow_bargain', 'min_price']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['min_price'].required = False


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }


class BargainRequestForm(forms.ModelForm):
    class Meta:
        model = BargainRequest
        fields = ['offered_price']


class CounterOfferForm(forms.ModelForm):
    class Meta:
        model = BargainRequest
        fields = ['counter_price']