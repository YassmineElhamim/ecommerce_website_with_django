from store.models import Product
from decimal import Decimal


class Cart():
    def __init__(self, request):
        self.session = request.session

        # Get current session key if exists
        cart = self.session.get('session_key')

        # If the user is new, no session key exists
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        # Make sure cart is available on all pages
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        
        Args:
            product: Product instance
            quantity: Number of items to add
            override_quantity: If True, set quantity instead of adding
        """
        product_id = str(product.id)

        if product_id in self.cart:
            if override_quantity:
                self.cart[product_id]['quantity'] = quantity
            else:
                self.cart[product_id]['quantity'] += quantity
        else:
            self.cart[product_id] = {
                'price': str(product.price),
                'quantity': quantity
            }

        self.session.modified = True

    def update(self, product, quantity):
        """
        Update the quantity of a product in the cart.
        If quantity is 0, remove the product.
        
        Args:
            product: Product instance
            quantity: New quantity (0 to remove)
        """
        product_id = str(product.id)
        
        if product_id in self.cart:
            if quantity > 0:
                self.cart[product_id]['quantity'] = quantity
            else:
                # Remove if quantity is 0
                self.cart.pop(product_id, None)
            self.session.modified = True
            return True
        return False

    def remove(self, product):
        """
        Remove a product from the cart completely.
        
        Args:
            product: Product instance or product_id
        """
        # Handle both Product object and product_id string/int
        if isinstance(product, Product):
            product_id = str(product.id)
        else:
            product_id = str(product)
            
        if product_id in self.cart:
            del self.cart[product_id]
            self.session.modified = True
            return True
        return False

    def clear(self):
        """Clear all items from the cart."""
        self.cart = self.session['session_key'] = {}
        self.session.modified = True

    def __len__(self):
        """Return the number of unique items in the cart."""
        return len(self.cart)

    def get_total_quantity(self):
        """Return the total quantity of all items in the cart."""
        return sum(int(item['quantity']) for item in self.cart.values())

    def get_products(self):
        """
        Get all products in the cart with their details.
        
        Returns:
            List of dicts with product, quantity, price, and total_price
        """
        # Get product IDs from cart
        product_ids = self.cart.keys()
        
        # Fetch products from database
        products = Product.objects.filter(id__in=product_ids)
        
        items = []
        products_map = {str(p.id): p for p in products}
        
        for pid, data in self.cart.items():
            product = products_map.get(pid)
            if product is None:
                # Product deleted from DB, skip it
                continue
                
            quantity = int(data.get('quantity', 1))
            price = Decimal(str(product.price))
            total_price = price * quantity
            
            items.append({
                'product': product,
                'quantity': quantity,
                'price': price,
                'total_price': total_price
            })
            
        return items

    def get_subtotal(self):
        """Calculate and return the cart subtotal."""
        return sum(Decimal(str(item['total_price'])) for item in self.get_products())

    def get_total(self, shipping_cost=0):
        """
        Calculate and return the cart total including shipping.
        
        Args:
            shipping_cost: Additional shipping cost (default: 0)
        """
        subtotal = self.get_subtotal()
        return subtotal + Decimal(str(shipping_cost))

    def get_item(self, product_id):
        """
        Get a specific item from the cart.
        
        Args:
            product_id: ID of the product
            
        Returns:
            Dict with product details or None
        """
        items = self.get_products()
        for item in items:
            if item['product'].id == int(product_id):
                return item
        return None

    def is_empty(self):
        """Check if the cart is empty."""
        return len(self.cart) == 0