from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from catalog.models import Product


class Order(models.Model):
    """Commande client"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En traitement'),
        ('shipped', 'Expédiée'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    # Généré automatiquement à la création : ORD00001, ORD00002, ...
    order_number = models.CharField(max_length=50, unique=True, blank=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=10)
    shipping_country = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Commande {self.order_number} - {self.user.username}"

    def save(self, *args, **kwargs):
        """
        Assigne automatiquement un numéro de commande si absent.
        Format : ORD00001, ORD00002, ...
        """
        creating = self._state.adding and not self.pk
        super().save(*args, **kwargs)
        if creating and not self.order_number:
            self.order_number = f"ORD{self.pk:05d}"
            # Mise à jour uniquement du numéro pour éviter la récursion infinie
            super(Order, self).save(update_fields=['order_number'])

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-created_at']


class OrderItem(models.Model):
    """Article d'une commande"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} - Commande {self.order.order_number}"

    class Meta:
        verbose_name = "Article de commande"
        verbose_name_plural = "Articles de commande"


class Invoice(models.Model):
    """Facture"""
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('sent', 'Envoyée'),
        ('paid', 'Payée'),
        ('cancelled', 'Annulée'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice')
    # Généré automatiquement à la création : INVYYYYMMDD (à partir de issued_date ou de la date du jour)
    invoice_number = models.CharField(max_length=50, unique=True, blank=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    issued_date = models.DateField()
    due_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Facture {self.invoice_number} - Commande {self.order.order_number}"

    def save(self, *args, **kwargs):
        """
        Assigne automatiquement un numéro de facture si absent.
        Format de base : INVYYYYMMDD (date d'émission ou date du jour).
        On ajoute un suffixe si nécessaire pour garantir l'unicité.
        """
        creating = self._state.adding and not self.pk
        if not self.issued_date:
            # Si la date d'émission n'est pas encore renseignée, utiliser la date du jour par défaut
            self.issued_date = timezone.now().date()

        super().save(*args, **kwargs)

        if creating and not self.invoice_number:
            base = self.issued_date.strftime("INV%Y%m%d")
            candidate = base
            index = 1
            # Garantir l'unicité même si plusieurs factures partagent la même date (par sécurité)
            while Invoice.objects.filter(invoice_number=candidate).exclude(pk=self.pk).exists():
                index += 1
                candidate = f"{base}-{index:02d}"

            self.invoice_number = candidate
            super(Invoice, self).save(update_fields=['invoice_number'])

    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        ordering = ['-issued_date']


class Payment(models.Model):
    """Paiement"""
    METHOD_CHOICES = [
        ('credit_card', 'Carte de crédit'),
        ('bank_transfer', 'Virement bancaire'),
        ('paypal', 'PayPal'),
        ('cash', 'Espèces'),
        ('check', 'Chèque'),
    ]

    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En traitement'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
        ('refunded', 'Remboursé'),
    ]

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=200, blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Paiement {self.transaction_id or 'N/A'} - {self.amount} FCFA"

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-created_at']
