from django.contrib import admin
from .models import Order, OrderItem, Invoice, Payment


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total_amount', 'shipping_city', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__email', 'shipping_address', 'shipping_city']
    list_filter = ['status', 'shipping_country', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'unit_price', 'subtotal', 'created_at']
    search_fields = ['order__order_number', 'product__name', 'product__sku']
    list_filter = ['created_at']
    readonly_fields = ['created_at']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'order', 'status', 'total_amount', 'issued_date', 'due_date', 'created_at']
    search_fields = ['invoice_number', 'order__order_number', 'order__user__username']
    list_filter = ['status', 'issued_date', 'due_date', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'amount', 'method', 'status', 'payment_date', 'transaction_id', 'created_at']
    search_fields = ['transaction_id', 'invoice__invoice_number', 'invoice__order__order_number']
    list_filter = ['method', 'status', 'payment_date', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
