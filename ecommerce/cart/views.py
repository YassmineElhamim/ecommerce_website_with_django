from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .cart import Cart
from store.models import Product
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