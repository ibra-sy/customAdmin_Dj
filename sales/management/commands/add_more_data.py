"""
Commande Django pour ajouter plus de données avec des dates variées dans le passé
Usage: python manage.py add_more_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import date, datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
import random

from accounts.models import UserProfile
from catalog.models import Category, Product
from sales.models import Order, OrderItem, Invoice, Payment


class Command(BaseCommand):
    help = 'Ajoute des données avec des dates passées (mois précédent et autres mois)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Ajout de données avec dates passées...'))
        
        # Récupérer les utilisateurs et produits existants
        users = list(User.objects.all())
        products = list(Product.objects.all())
        
        if not users or not products:
            self.stdout.write(self.style.ERROR('Veuillez d\'abord exécuter populate_data'))
            return
        
        # Date actuelle : 01/02/2026
        now = timezone.now()
        current_year = 2026
        current_month = 2  # Février
        
        orders_created = 0
        invoices_created = 0
        payments_created = 0
        
        # Générer des données pour les 6 derniers mois (août 2025 à janvier 2026)
        # Avec focus sur janvier 2026 (mois précédent)
        months_to_generate = [
            (2025, 8), (2025, 9), (2025, 10), (2025, 11), (2025, 12),
            (2026, 1)  # Mois précédent - focus ici
        ]
        
        for year, month in months_to_generate:
            # Plus de données pour janvier 2026 (mois précédent)
            if year == 2026 and month == 1:
                num_orders = random.randint(15, 25)  # Plus de commandes
            else:
                num_orders = random.randint(8, 15)
            
            self.stdout.write(f'Génération pour {month:02d}/{year} : {num_orders} commandes...')
            
            for order_idx in range(num_orders):
                # Date aléatoire dans le mois - gérer correctement les jours par mois
                if month in [1, 3, 5, 7, 8, 10, 12]:
                    days_in_month = 31
                elif month in [4, 6, 9, 11]:
                    days_in_month = 30
                else:  # Février
                    # Février : 28 jours (2026 n'est pas bissextile)
                    days_in_month = 28
                
                random_day = random.randint(1, days_in_month)
                
                try:
                    order_date = timezone.make_aware(
                        datetime(year, month, random_day, 
                                random.randint(9, 18), 
                                random.randint(0, 59),
                                random.randint(0, 59))
                    )
                except ValueError:
                    # Si la date est invalide (ex: 31 février), utiliser le dernier jour du mois
                    order_date = timezone.make_aware(
                        datetime(year, month, days_in_month, 
                                random.randint(9, 18), 
                                random.randint(0, 59))
                    )
                
                # Statuts variés selon la date
                days_ago = (now - order_date).days
                if days_ago <= 7:
                    status = random.choice(['pending', 'processing'])
                elif days_ago <= 30:
                    status = random.choice(['processing', 'shipped'])
                else:
                    status = random.choice(['shipped', 'delivered'])
                
                # Utilisateur aléatoire
                user = random.choice(users)
                
                # Générer un numéro de commande unique
                base_number = year * 10000 + month * 100 + order_idx
                order_number = f'ORD{base_number:06d}'
                
                # Vérifier si la commande existe déjà
                if Order.objects.filter(order_number=order_number).exists():
                    continue
                
                # Calculer le montant total
                num_items = random.randint(1, 4)
                selected_products = random.sample(products, min(num_items, len(products)))
                total_amount = Decimal('0')
                
                with transaction.atomic():
                    # Créer la commande
                    order = Order.objects.create(
                        user=user,
                        order_number=order_number,
                        status=status,
                        total_amount=Decimal('0'),  # Sera mis à jour
                        shipping_address=f'{random.randint(1, 999)} Rue de la {random.choice(["Paix", "Commerce", "République", "Champs", "Liberté", "Victoire"])}',
                        shipping_city=random.choice(['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice', 'Bordeaux', 'Nantes', 'Strasbourg']),
                        shipping_postal_code=f'{random.randint(10000, 99999)}',
                        shipping_country='France',
                        notes=random.choice(['', 'Livraison express', 'Fragile', 'Cadeau']) if random.random() > 0.7 else ''
                    )
                    
                    # Mettre à jour les dates manuellement (contourner auto_now_add)
                    Order.objects.filter(pk=order.pk).update(
                        created_at=order_date,
                        updated_at=order_date
                    )
                    order.refresh_from_db()
                    
                    # Ajouter les articles
                    for product in selected_products:
                        quantity = random.randint(1, 5)
                        unit_price = product.price
                        subtotal = unit_price * quantity
                        total_amount += subtotal
                        
                        item = OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            unit_price=unit_price,
                            subtotal=subtotal
                        )
                        # Mettre à jour la date
                        OrderItem.objects.filter(pk=item.pk).update(created_at=order_date)
                    
                    # Mettre à jour le montant total de la commande
                    Order.objects.filter(pk=order.pk).update(total_amount=total_amount)
                    
                    # Créer une facture si la commande est livrée ou expédiée
                    if status in ['delivered', 'shipped']:
                        invoice_number = f'INV{base_number:06d}'
                        
                        invoice, created = Invoice.objects.get_or_create(
                            order=order,
                            defaults={
                                'invoice_number': invoice_number,
                                'status': 'paid' if status == 'delivered' else 'sent',
                                'subtotal': total_amount * Decimal('0.833'),
                                'tax_amount': total_amount * Decimal('0.167'),
                                'total_amount': total_amount,
                                'issued_date': order_date.date(),
                                'due_date': (order_date + timedelta(days=30)).date()
                            }
                        )
                        
                        if created:
                            invoices_created += 1
                            # Mettre à jour les dates
                            Invoice.objects.filter(pk=invoice.pk).update(
                                created_at=order_date,
                                updated_at=order_date
                            )
                            
                            # Créer un paiement si la facture est payée
                            if invoice.status == 'paid':
                                payment_date = order_date + timedelta(days=random.randint(1, 10))
                                
                                payment, p_created = Payment.objects.get_or_create(
                                    invoice=invoice,
                                    defaults={
                                        'amount': invoice.total_amount,
                                        'method': random.choice(['credit_card', 'bank_transfer', 'paypal', 'cash']),
                                        'status': 'completed',
                                        'transaction_id': f'TXN{invoice.invoice_number}',
                                        'payment_date': payment_date
                                    }
                                )
                                
                                if p_created:
                                    payments_created += 1
                                    # Mettre à jour les dates
                                    Payment.objects.filter(pk=payment.pk).update(
                                        created_at=payment_date,
                                        updated_at=payment_date
                                    )
                    
                    orders_created += 1
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS(f'✓ {orders_created} commandes créées'))
        self.stdout.write(self.style.SUCCESS(f'✓ {invoices_created} factures créées'))
        self.stdout.write(self.style.SUCCESS(f'✓ {payments_created} paiements créés'))
        self.stdout.write(self.style.SUCCESS(f'✓ Données réparties sur les 6 derniers mois'))
        self.stdout.write(self.style.SUCCESS(f'✓ Focus sur janvier 2026 (mois précédent)'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('✓ Données avec dates passées ajoutées avec succès !'))
