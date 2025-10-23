from django.shortcuts import render, redirect, get_object_or_404
from .cart import Cart
from store.models import Product
from django.http import JsonResponse

def cart_summary(request):
    cart = Cart(request)
    cart_products = cart.get_products
    return render(request, 'cart_summary.html', {'cart_products':cart_products})

def cart_add(request):
    # get the cart 
    cart = Cart(request)
    # test for POST
    if request.POST.get('action') == 'post':
        # get what we need
        product_id = int(request.POST.get('product_id'))
        # search for the product in DB
        product = get_object_or_404(Product, id=product_id)
        # save to session 
        cart.add(product=product)

        #  get cart Quantity 
        cart_quantity = cart.__len__()

        #return response
        # response = JsonResponse({'Product Name: ': product.name})
        response = JsonResponse({'qty: ': cart_quantity})
        return response


def cart_update(request):
    pass

def cart_delete(request):
    pass

