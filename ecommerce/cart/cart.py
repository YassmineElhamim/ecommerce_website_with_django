from store.models import Product

class Cart():
    def __init__(self, request):
        self.session = request.session

        # Get current session key if exist 
        cart = self.session.get('session_key')

        # If the user is new, no session key if it exists
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}


        # Make sure cart is available on all pages 
        self.cart = cart


# ________________________________________________________________


    def add(self, product, quantity=1):
        product_id = str(product.id)

        if product_id in self.cart:
            self.cart[product_id]['quantity'] +=quantity
        else:
            self.cart[product_id] = {'price': str(product.price), 'quantity': quantity}

        self.session.modified = True

    @property
    def item_count(self):
        return sum(item.get('quantity', 1) for item in self.cart.values())

    def get_items(self):
        items=[]
        for product_id, data in self.cart.items():
            product = Product.objects.get(id=int(product_id))
            items.append({
                'product': product,
                'quantity': data.get('quantity',1),
                'total_price': float(data.get('price',0))*data.get('quantity',1)

            })
        return items
