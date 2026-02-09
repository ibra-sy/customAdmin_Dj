from django.contrib import admin
from admin_custom.modern_model_admin import ModernTemplateMixin
from .models import Order, OrderItem, Invoice, Payment


class OrderItemInline(admin.TabularInline):
    """
    TabularInline : peu de champs (produit, quantité, prix), beaucoup de lignes.
    Le parent (order) n'est jamais affiché ni saisi — il est lié automatiquement à la commande éditée.
    """
    model = OrderItem
    extra = 1
    fields = ['product', 'quantity', 'unit_price', 'subtotal', 'created_at']
    readonly_fields = ['created_at']
    # Le champ 'order' (FK parent) est toujours exclu en inline : Django le gère automatiquement.


class InvoiceInline(admin.StackedInline):
    """
    StackedInline : beaucoup de champs (numéro, statut, montants, dates, notes).
    Le parent (order) n'est jamais affiché — lié automatiquement à la commande éditée.
    """
    model = Invoice
    extra = 0
    # Le numéro de facture est généré automatiquement et affiché en lecture seule.
    fields = [
        'invoice_number', 'status',
        'subtotal', 'tax_amount', 'total_amount',
        'issued_date', 'due_date', 'notes',
        'created_at', 'updated_at',
    ]
    readonly_fields = ['invoice_number', 'created_at', 'updated_at']
    # Le champ 'order' (OneToOne parent) est géré automatiquement par Django.


@admin.register(Order)
class OrderAdmin(ModernTemplateMixin, admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total_amount', 'shipping_city', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__email', 'shipping_address', 'shipping_city']
    list_filter = ['status', 'shipping_country', 'created_at']
    # Le numéro de commande est généré automatiquement : lecture seule dans l'admin.
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline, InvoiceInline]


@admin.register(OrderItem)
class OrderItemAdmin(ModernTemplateMixin, admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'unit_price', 'subtotal', 'created_at']
    search_fields = ['order__order_number', 'product__name', 'product__sku']
    list_filter = ['created_at']
    readonly_fields = ['created_at']


class PaymentInline(admin.TabularInline):
    """
    TabularInline : champs facture (montant, moyen, statut, etc.) en lignes.
    Le parent (invoice) n'est jamais affiché — lié automatiquement à la facture éditée.
    """
    model = Payment
    extra = 0
    fields = ['amount', 'method', 'status', 'transaction_id', 'payment_date', 'notes', 'created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    # Le champ 'invoice' (FK parent) est géré automatiquement par Django.


@admin.register(Invoice)
class InvoiceAdmin(ModernTemplateMixin, admin.ModelAdmin):
    list_display = ['invoice_number', 'order', 'status', 'total_amount', 'issued_date', 'due_date', 'created_at']
    search_fields = ['invoice_number', 'order__order_number', 'order__user__username']
    list_filter = ['status', 'issued_date', 'due_date', 'created_at']
    # Le numéro de facture est généré automatiquement : lecture seule dans l'admin.
    readonly_fields = ['invoice_number', 'created_at', 'updated_at']
    inlines = [PaymentInline]


@admin.register(Payment)
class PaymentAdmin(ModernTemplateMixin, admin.ModelAdmin):
    list_display = ['invoice', 'amount', 'method', 'status', 'payment_date', 'transaction_id', 'created_at']
    search_fields = ['transaction_id', 'invoice__invoice_number', 'invoice__order__order_number']
    list_filter = ['method', 'status', 'payment_date', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
