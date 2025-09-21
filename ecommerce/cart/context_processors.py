from .cart import Cart

def cart(request):
    # return default data from cart
    return {'cart' : Cart(request)}