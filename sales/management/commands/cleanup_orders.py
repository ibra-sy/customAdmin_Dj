"""
Commande pour nettoyer la base de données en supprimant des commandes
tout en gardant une variété de dates pour les graphiques
"""
from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from sales.models import Order, OrderItem, Invoice, Payment
import random


class Command(BaseCommand):
    help = 'Nettoie la base de données en supprimant des commandes tout en gardant des dates variées'

    def add_arguments(self, parser):
        parser.add_argument(
            '--keep',
            type=int,
            default=50,
            help='Nombre de commandes à garder (défaut: 50)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer la suppression sans confirmation',
        )

    def handle(self, *args, **options):
        keep_count = options['keep']
        force = options['force']
        
        total_orders = Order.objects.count()
        
        if total_orders <= keep_count:
            self.stdout.write(self.style.SUCCESS(f'Il n\'y a que {total_orders} commandes, aucune suppression nécessaire.'))
            return
        
        if not force:
            self.stdout.write(self.style.WARNING(f'Il y a actuellement {total_orders} commandes.'))
            self.stdout.write(self.style.WARNING(f'Cette commande va supprimer {total_orders - keep_count} commandes.'))
            self.stdout.write(self.style.WARNING(f'Seules {keep_count} commandes seront conservées.'))
            confirm = input('Continuer? (oui/non): ')
            if confirm.lower() not in ['oui', 'o', 'yes', 'y']:
                self.stdout.write(self.style.ERROR('Opération annulée.'))
                return
        
        self.stdout.write(self.style.SUCCESS('Nettoyage de la base de données...'))
        
        # Calculer les périodes à garder (pour varier les dates)
        now = timezone.now()
        periods = [
            (now - timedelta(days=30), now),  # Dernier mois
            (now - timedelta(days=60), now - timedelta(days=30)),  # Mois précédent
            (now - timedelta(days=90), now - timedelta(days=60)),  # Il y a 2 mois
            (now - timedelta(days=120), now - timedelta(days=90)),  # Il y a 3 mois
            (now - timedelta(days=180), now - timedelta(days=120)),  # Il y a 4-6 mois
        ]
        
        orders_to_keep = []
        orders_per_period = keep_count // len(periods)
        remaining = keep_count % len(periods)
        
        # Sélectionner des commandes de chaque période
        for i, (start_date, end_date) in enumerate(periods):
            count = orders_per_period + (1 if i < remaining else 0)
            
            period_orders = Order.objects.filter(
                created_at__gte=start_date,
                created_at__lt=end_date
            ).order_by('created_at')
            
            if period_orders.count() > count:
                # Sélectionner aléatoirement mais en gardant une distribution
                selected = random.sample(list(period_orders), count)
                orders_to_keep.extend([o.id for o in selected])
            else:
                orders_to_keep.extend([o.id for o in period_orders])
        
        # Si on n'a pas assez, compléter avec les plus récentes
        if len(orders_to_keep) < keep_count:
            additional = Order.objects.exclude(id__in=orders_to_keep).order_by('-created_at')[:keep_count - len(orders_to_keep)]
            orders_to_keep.extend([o.id for o in additional])
        
        # Supprimer les commandes non sélectionnées
        orders_to_delete = Order.objects.exclude(id__in=orders_to_keep)
        deleted_count = orders_to_delete.count()
        
        # Supprimer les Invoices associées (OrderItems et Payments en cascade)
        invoice_ids = [inv.id for inv in Invoice.objects.filter(order__in=orders_to_delete)]
        Payment.objects.filter(invoice_id__in=invoice_ids).delete()
        Invoice.objects.filter(order__in=orders_to_delete).delete()
        
        # Supprimer les commandes (OrderItems en cascade)
        orders_to_delete.delete()
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ {deleted_count} commandes supprimées'))
        self.stdout.write(self.style.SUCCESS(f'✓ {len(orders_to_keep)} commandes conservées'))
        self.stdout.write(self.style.SUCCESS(f'✓ Dates variées conservées pour les graphiques'))
        
        # Statistiques finales
        final_count = Order.objects.count()
        self.stdout.write(self.style.SUCCESS(f'\nTotal final: {final_count} commandes'))
