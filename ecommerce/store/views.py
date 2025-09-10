from django.shortcuts import render
from .models import Product



def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products':products})

def products(request):
    return render(request, 'products.html', {})
