from django.shortcuts import render, redirect, get_object_or_404
from .cart import Cart
from store.models import Product
from django.http import JsonResponse

def cart_summary(request):
    cart= Cart(request)
    cart_items = cart.get_items()
    return render(request, 'cart_summary.html', {'cart_items':cart_items})
    

def cart_add(request):
    # get the cart 
    cart = Cart(request)
    # test for POST 
    if request.POST.get('action') == 'post' :
        # get stuff
        product_id = request.POST.get('product_id')
        if not product_id:
            return JsonResponse({'error': 'No product_id'}, status=400)
        product = get_object_or_404(Product, id=int(product_id))
        cart.add(product=product, quantity=1)
        return JsonResponse({'product_name': product.name})
        return JsonResponse({'error': 'Invalid request'}, status=400)
        return response

def cart_update(request):
    pass

def cart_delete(request):
    pass

