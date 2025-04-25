from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from products.models import Product

def home(request):
    products = Product.objects.all().order_by('-id')[:6]  # Latest 6 products
    return render(request, 'core/home.html', {'products': products})

def about(request):
    return render(request, 'core/about.html')