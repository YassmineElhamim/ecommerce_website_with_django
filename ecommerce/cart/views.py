from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .cart import Cart
from store.models import Product, Order, OrderItem
from store.forms import CheckoutForm, GuestCheckoutForm
from django.db import transaction
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


def cart_summary(request):
    try:
        cart = Cart(request)
        cart_products = cart.get_products()
        
        # Calculate cart totals
        cart_subtotal = cart.get_subtotal()
        shipping_cost = Decimal('0')  # Make this dynamic based on your shipping logic
        
        # Apply voucher discount if exists
        discount = Decimal(str(request.session.get('discount', 0)))
        cart_total = cart.get_total(shipping_cost) - discount
        
        # Get recommended products (exclude items already in cart)
        cart_product_ids = [item['product'].id for item in cart_products]
        recommended_products = Product.objects.exclude(id__in=cart_product_ids)[:12] if cart_product_ids else []
        
        # Get all products for empty cart state
        all_products = Product.objects.all()[:12]
        
        context = {
            'cart_products': cart_products,
            'cart_subtotal': cart_subtotal,
            'cart_total': cart_total,
            'cart_savings': discount if discount > 0 else None,
            'shipping_cost': shipping_cost if shipping_cost > 0 else None,
            'recommended_products': recommended_products,
            'products': all_products,
            'cart_count': cart.get_total_quantity(),
        }
        
        return render(request, 'cart_summary.html', context)
    
    except Exception as e:
        logger.error(f"Error in cart_summary: {str(e)}")
        messages.error(request, 'An error occurred while loading your cart.')
        return render(request, 'cart_summary.html', {'cart_products': [], 'products': Product.objects.all()[:12]})


@require_POST
def cart_add(request):
    """Add a product to the cart via AJAX."""
    try:
        cart = Cart(request)
        
        if request.POST.get('action') != 'post':
            return JsonResponse({
                'success': False,
                'message': 'Invalid action'
            }, status=400)
        
        # Get and validate input
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity', 1)
        
        if not product_id:
            return JsonResponse({
                'success': False,
                'message': 'Product ID is required'
            }, status=400)
        
        try:
            product_id = int(product_id)
            quantity = int(quantity)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'message': 'Invalid product ID or quantity'
            }, status=400)
        
        # Validate quantity
        if quantity < 1:
            return JsonResponse({
                'success': False,
                'message': 'Quantity must be at least 1'
            }, status=400)
        
        # Get product from database
        product = get_object_or_404(Product, id=product_id)
        
        # Check stock if you have inventory management
        # if product.stock < quantity:
        #     return JsonResponse({
        #         'success': False,
        #         'message': f'Only {product.stock} items available'
        #     }, status=400)
        
        # Add to cart
        cart.add(product=product, quantity=quantity)
        
        # Calculate updated cart info
        cart_quantity = cart.get_total_quantity()
        cart_subtotal = float(cart.get_subtotal())
        cart_total = float(cart.get_total())
        
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart',
            'product_name': product.name,
            'cart_qty': cart_quantity,
            'cart_subtotal': cart_subtotal,
            'cart_total': cart_total
        })
        
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Product not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error in cart_add: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while adding to cart'
        }, status=500)


@require_POST
def cart_update(request):
    """Update product quantity in the cart via AJAX."""
    try:
        cart = Cart(request)
        
        # Handle both update and remove actions
        action = request.POST.get('action')
        
        if action not in ['post', 'remove']:
            return JsonResponse({
                'success': False,
                'message': 'Invalid action'
            }, status=400)
        
        # Get and validate input
        product_id = request.POST.get('product_id')
        
        if not product_id:
            return JsonResponse({
                'success': False,
                'message': 'Product ID is required'
            }, status=400)
        
        try:
            product_id = int(product_id)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'message': 'Invalid product ID'
            }, status=400)
        
        # Get product from database
        product = get_object_or_404(Product, id=product_id)
        
        # Handle remove action
        if action == 'remove':
            removed = cart.remove(product)
            
            if removed:
                cart_quantity = cart.get_total_quantity()
                cart_subtotal = float(cart.get_subtotal()) if not cart.is_empty() else 0
                cart_total = float(cart.get_total()) if not cart.is_empty() else 0
                
                return JsonResponse({
                    'success': True,
                    'message': f'{product.name} removed from cart',
                    'cart_qty': cart_quantity,
                    'cart_subtotal': cart_subtotal,
                    'cart_total': cart_total,
                    'cart_empty': cart.is_empty()
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Product not in cart'
                }, status=400)
        
        # Handle update action
        quantity = request.POST.get('quantity', 0)
        
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'message': 'Invalid quantity'
            }, status=400)
        
        if quantity < 0:
            return JsonResponse({
                'success': False,
                'message': 'Quantity cannot be negative'
            }, status=400)
        
        # Update cart
        cart.update(product=product, quantity=quantity)
        
        # Get updated item subtotal
        item_subtotal = 0
        if quantity > 0:
            item = cart.get_item(product_id)
            if item:
                item_subtotal = float(item['total_price'])
        
        # Calculate updated cart info
        cart_quantity = cart.get_total_quantity()
        cart_subtotal = float(cart.get_subtotal()) if not cart.is_empty() else 0
        cart_total = float(cart.get_total()) if not cart.is_empty() else 0
        
        return JsonResponse({
            'success': True,
            'item_subtotal': item_subtotal,
            'cart_qty': cart_quantity,
            'cart_subtotal': cart_subtotal,
            'cart_total': cart_total,
            'cart_empty': cart.is_empty()
        })
        
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Product not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error in cart_update: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while updating cart'
        }, status=500)


@require_POST
def cart_delete(request):
    """
    Remove a product from the cart via AJAX.
    This is an alias for cart_update with action='remove'
    """
    # Set action to 'remove' and call cart_update
    request.POST = request.POST.copy()
    request.POST['action'] = 'remove'
    return cart_update(request)


@require_POST
def cart_clear(request):
    """Clear all items from the cart."""
    try:
        cart = Cart(request)
        cart.clear()
        
        # Clear any voucher/discount
        if 'voucher_code' in request.session:
            del request.session['voucher_code']
        if 'discount' in request.session:
            del request.session['discount']
        
        return JsonResponse({
            'success': True,
            'message': 'Cart cleared successfully'
        })
    except Exception as e:
        logger.error(f"Error in cart_clear: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while clearing cart'
        }, status=500)


@require_POST
def apply_voucher(request):
    """Apply a voucher/coupon code to the cart."""
    try:
        cart = Cart(request)
        
        if cart.is_empty():
            return JsonResponse({
                'success': False,
                'message': 'Your cart is empty'
            }, status=400)
        
        voucher_code = request.POST.get('voucher_code', '').strip().upper()
        
        if not voucher_code:
            return JsonResponse({
                'success': False,
                'message': 'Please enter a voucher code'
            }, status=400)
        
        # todo: Implement your voucher validation logic here
        # Example implementation:
        
        # Dummy voucher for testing - Remove this in production
        if voucher_code == 'SAVE10':
            cart_subtotal = cart.get_subtotal()
            discount = cart_subtotal * Decimal('0.10')  # 10% discount
            
            request.session['voucher_code'] = voucher_code
            request.session['discount'] = float(discount)
            request.session.modified = True
            
            cart_total = float(cart.get_total()) - float(discount)
            
            return JsonResponse({
                'success': True,
                'message': f'Voucher applied! You saved {discount:.2f} DH',
                'discount': float(discount),
                'cart_total': cart_total,
                'cart_subtotal': float(cart_subtotal)
            })
        
        # Real implementation would be:
        # from store.models import Voucher
        # try:
        #     voucher = Voucher.objects.get(
        #         code=voucher_code,
        #         is_active=True,
        #         valid_from__lte=timezone.now(),
        #         valid_to__gte=timezone.now()
        #     )
        #     
        #     # Check if voucher is valid for this user/cart
        #     if voucher.minimum_amount and cart.get_subtotal() < voucher.minimum_amount:
        #         return JsonResponse({
        #             'success': False,
        #             'message': f'Minimum cart value of {voucher.minimum_amount} DH required'
        #         }, status=400)
        #     
        #     # Calculate discount
        #     discount = voucher.calculate_discount(cart.get_subtotal())
        #     
        #     request.session['voucher_code'] = voucher_code
        #     request.session['discount'] = float(discount)
        #     request.session.modified = True
        #     
        #     cart_total = float(cart.get_total()) - float(discount)
        #     
        #     return JsonResponse({
        #         'success': True,
        #         'message': f'Voucher applied! You saved {discount:.2f} DH',
        #         'discount': float(discount),
        #         'cart_total': cart_total
        #     })
        # except Voucher.DoesNotExist:
        #     pass
        
        return JsonResponse({
            'success': False,
            'message': 'Invalid or expired voucher code'
        }, status=400)
        
    except Exception as e:
        logger.error(f"Error in apply_voucher: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while applying voucher'
        }, status=500)


@require_POST
def remove_voucher(request):
    """Remove applied voucher from the cart."""
    try:
        if 'voucher_code' in request.session:
            del request.session['voucher_code']
        if 'discount' in request.session:
            del request.session['discount']
        
        request.session.modified = True
        
        cart = Cart(request)
        cart_total = float(cart.get_total())
        
        return JsonResponse({
            'success': True,
            'message': 'Voucher removed',
            'cart_total': cart_total,
            'cart_subtotal': float(cart.get_subtotal())
        })
    except Exception as e:
        logger.error(f"Error in remove_voucher: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred'
        }, status=500)


def checkout(request):
    cart = Cart(request)
    
    if cart.is_empty():
        messages.warning(request, 'Your cart is empty!')
        return redirect('cart_summary')
    
    # Get cart details
    cart_products = cart.get_products()
    cart_subtotal = cart.get_subtotal()
    discount = Decimal(str(request.session.get('discount', 0)))
    shipping_cost = Decimal('0')  # Calculate based on your logic
    cart_total = cart.get_total(shipping_cost) - discount
    
    context = {
        'cart_products': cart_products,
        'cart_subtotal': cart_subtotal,
        'cart_total': cart_total,
        'discount': discount if discount > 0 else None,
        'shipping_cost': shipping_cost,
        'voucher_code': request.session.get('voucher_code'),
    }
    
    # TODO: Create checkout.html template
    return render(request, 'checkout.html', context)


def get_cart_count(request):
    """API endpoint to get current cart count."""
    try:
        cart = Cart(request)
        return JsonResponse({
            'success': True,
            'cart_count': cart.get_total_quantity()
        })
    except Exception as e:
        logger.error(f"Error in get_cart_count: {str(e)}")
        return JsonResponse({
            'success': False,
            'cart_count': 0
        }, status=500)

def checkout(request):
    """
    Checkout page - collect shipping info and process order
    
    Flow:
    1. Display cart summary
    2. Show checkout form
    3. Validate form
    4. Create order and order items
    5. Clear cart
    6. Redirect to order confirmation
    """
    cart = Cart(request)
    
    # Check if cart is empty
    if cart.is_empty():
        messages.warning(request, 'Your cart is empty!')
        return redirect('cart_summary')
    
    # Get cart details
    cart_products = cart.get_products()
    cart_subtotal = cart.get_subtotal()
    discount = Decimal(str(request.session.get('discount', 0)))
    
    # Calculate shipping (you can make this dynamic based on location/weight)
    shipping_cost = calculate_shipping(cart_products, request)
    
    cart_total = cart_subtotal + shipping_cost - discount
    
    # Handle form submission
    if request.method == 'POST':
        form = GuestCheckoutForm(request.POST)
        
        if form.is_valid():
            try:
                # Create order in a transaction (all-or-nothing)
                with transaction.atomic():
                    # Create the order
                    order = Order.objects.create(
                        email=form.cleaned_data['email'],
                        phone=form.cleaned_data['phone'],
                        full_name=form.cleaned_data['full_name'],
                        address_line1=form.cleaned_data['address_line1'],
                        address_line2=form.cleaned_data.get('address_line2', ''),
                        city=form.cleaned_data['city'],
                        postal_code=form.cleaned_data['postal_code'],
                        country=form.cleaned_data['country'],
                        subtotal=cart_subtotal,
                        shipping_cost=shipping_cost,
                        discount=discount,
                        total=cart_total,
                        payment_method=form.cleaned_data['payment_method'],
                        notes=form.cleaned_data.get('notes', ''),
                        status='pending'
                    )
                    
                    # Create order items
                    for item in cart_products:
                        product = item['product']
                        quantity = item['quantity']
                        
                        # Check stock availability
                        if product.stock < quantity:
                            raise Exception(f'Insufficient stock for {product.name}')
                        
                        # Create order item
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            product_name=product.name,
                            product_price=product.get_price(),
                            quantity=quantity
                        )
                        
                        # Reduce stock
                        product.stock -= quantity
                        if product.stock == 0:
                            product.is_disponible = False
                        product.save()
                    
                    # Clear the cart
                    cart.clear()
                    
                    # Clear discount/voucher
                    if 'voucher_code' in request.session:
                        del request.session['voucher_code']
                    if 'discount' in request.session:
                        del request.session['discount']
                    
                    # Success message
                    messages.success(
                        request, 
                        f'Order {order.order_number} placed successfully! You will receive a confirmation email shortly.'
                    )
                    
                    # Redirect to order confirmation page
                    return redirect('order_confirmation', order_number=order.order_number)
                    
            except Exception as e:
                logger.error(f"Error processing order: {str(e)}")
                messages.error(request, f'Error processing order: {str(e)}')
                
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill form if user is logged in
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'email': request.user.email,
                'full_name': request.user.get_full_name(),
            }
        
        form = GuestCheckoutForm(initial=initial_data)
    
    context = {
        'form': form,
        'cart_products': cart_products,
        'cart_subtotal': cart_subtotal,
        'shipping_cost': shipping_cost,
        'discount': discount if discount > 0 else None,
        'cart_total': cart_total,
        'voucher_code': request.session.get('voucher_code'),
    }
    
    return render(request, 'checkout.html', context)


def calculate_shipping(cart_products, request):
    """
    Calculate shipping cost based on various factors
    
    You can customize this based on:
    - Location/city
    - Total weight
    - Total price (free shipping over certain amount)
    - Number of items
    """
    cart_subtotal = sum(item['total_price'] for item in cart_products)
    
    # Example: Free shipping for orders over 500 DH
    FREE_SHIPPING_THRESHOLD = Decimal('500')
    if cart_subtotal >= FREE_SHIPPING_THRESHOLD:
        return Decimal('0')
    
    # Example: Flat rate shipping
    FLAT_RATE = Decimal('30')  # 30 DH shipping
    
    # Or calculate based on location
    # city = request.POST.get('city', '').lower()
    # if city in ['casablanca', 'rabat']:
    #     return Decimal('30')
    # elif city in ['marrakech', 'tanger']:
    #     return Decimal('50')
    # else:
    #     return Decimal('70')
    
    return FLAT_RATE


def order_confirmation(request, order_number):
    """
    Order confirmation page after successful checkout
    """
    try:
        order = Order.objects.get(order_number=order_number)
        
        # Get order items
        order_items = OrderItem.objects.filter(order=order).select_related('product')
        
        context = {
            'order': order,
            'order_items': order_items,
        }
        
        return render(request, 'order_confirmation.html', context)
        
    except Order.DoesNotExist:
        messages.error(request, 'Order not found')
        return redirect('home')


def order_tracking(request, order_number):
    """
    Track order status
    """
    try:
        order = Order.objects.get(order_number=order_number)
        order_items = OrderItem.objects.filter(order=order).select_related('product')
        
        context = {
            'order': order,
            'order_items': order_items,
        }
        
        return render(request, 'order_tracking.html', context)
        
    except Order.DoesNotExist:
        messages.error(request, 'Order not found')
        return redirect('home')


def my_orders(request):
    """
    Display all orders for logged in user
    """
    if not request.user.is_authenticated:
        messages.warning(request, 'Please login to view your orders')
        return redirect('login')
    
    # Get orders for this user
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    
    return render(request, 'my_orders.html', context)