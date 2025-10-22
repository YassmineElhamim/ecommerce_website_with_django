from django.shortcuts import render, redirect, get_object_or_404
from .cart import Cart
from store.models import Product
from django.http import JsonResponse

def cart_summary(request):
    return render(request, 'cart_summary.html', {})

def cart_add(request):
    pass

def cart_update(request):
    pass

def cart_delete(request):
    pass

