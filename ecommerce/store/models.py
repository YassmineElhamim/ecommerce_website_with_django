from django.db import models
import datetime
from django.contrib.auth.models import User
import uuid


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, default='', null=True, blank=True)
    # cover_image = models.ImageField(upload_to='uploads/categories/')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural= 'Categories'



class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    description = models.CharField(max_length=1500)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    stock = models.IntegerField()
    is_disponible = models.BooleanField(default=True)
    image = models.ImageField(upload_to='uploads/products/')
    is_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0, max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name
    
    def get_price(self):
        if self.is_sale and self.sale_price > 0:
            return self.sale_price
        return self.price



class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'



# class Order(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
#     quantity = models.IntegerField()
#     address = models.CharField(max_length=200, default='', blank=True)
#     phone = models.CharField(max_length=20, default='', blank=True)
#     date = models.DateField(default=datetime.datetime.today)
#     status = models.BooleanField(default=False)

#     def __str__(self):
#         return self.product



# NEW: Main Order model (one order can have multiple items)
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('cod', 'Cash on Delivery'),
        ('card', 'Credit/Debit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
    )
    
    # Order identification
    order_number = models.CharField(max_length=20, unique=True, editable=False, default='PENDING')  
    
    # Customer info
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Contact details - ADD null=True, blank=True OR default
    email = models.EmailField(max_length=100, default='')  
    phone = models.CharField(max_length=20, default='')  
    
    # Shipping address - ADD default='' to all
    full_name = models.CharField(max_length=100, default='')  
    address_line1 = models.CharField(max_length=200, default='')  
    address_line2 = models.CharField(max_length=200, blank=True, null=True)  
    city = models.CharField(max_length=100, default='')  
    postal_code = models.CharField(max_length=20, default='')  
    country = models.CharField(max_length=100, default='Morocco')  
    
    # Order details - ADD defaults
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)  
    shipping_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0)  
    discount = models.DecimalField(max_digits=6, decimal_places=2, default=0) 
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)  
    
    # Payment
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod')  
    is_paid = models.BooleanField(default=False)  
    paid_at = models.DateTimeField(null=True, blank=True)  
    
    # Order status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending') 
    
    # Notes
    notes = models.TextField(blank=True, null=True)  
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Order {self.order_number}'
    
    def save(self, *args, **kwargs):
        if not self.order_number or self.order_number == 'PENDING':
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        import datetime
        import uuid
        date_str = datetime.datetime.now().strftime('%Y%m%d')
        random_str = str(uuid.uuid4().hex)[:6].upper()
        return f'ORD-{date_str}-{random_str}'



# NEW: Order items (products in the order)
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    
    # Store product details at time of order (in case product changes later)
    product_name = models.CharField(max_length=200)
    product_price = models.DecimalField(max_digits=6, decimal_places=2)
    
    quantity = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.quantity}x {self.product_name} in Order {self.order.order_number}'
    
    def save(self, *args, **kwargs):
        # Calculate total price
        self.total_price = self.product_price * self.quantity
        super().save(*args, **kwargs)


# Optional: Shipping address model if you want to save multiple addresses per customer
class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Morocco')
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Shipping Addresses'
    
    def __str__(self):
        return f'{self.full_name} - {self.city}'


