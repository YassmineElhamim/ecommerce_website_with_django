from django.contrib import admin
from .models import Category, Product, Customer, Order, OrderItem, ShippingAddress


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Customer)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'email', 'status', 'total', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'email', 'full_name', 'phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'status', 'created_at', 'updated_at')
        }),
        ('Customer Information', {
            'fields': ('customer', 'user', 'full_name', 'email', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'postal_code', 'country')
        }),
        ('Payment', {
            'fields': ('payment_method', 'is_paid', 'paid_at')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'shipping_cost', 'discount', 'total')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'quantity', 'product_price', 'total_price']
    list_filter = ['order__status', 'created_at']
    search_fields = ['product_name', 'order__order_number']

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'full_name', 'city', 'is_default']
    list_filter = ['city', 'country', 'is_default']
    search_fields = ['full_name', 'city', 'phone']
