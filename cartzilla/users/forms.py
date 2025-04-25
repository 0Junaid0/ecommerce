from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Customer, Seller


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    account_type = forms.ChoiceField(choices=[('customer', 'Customer'), ('seller', 'Seller')])

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'account_type']


class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['address']


class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ['details']


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']