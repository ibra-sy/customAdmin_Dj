"""
Script de peuplement de la base de données avec des données de test variées.

Ce script génère des données sur plusieurs périodes pour que les graphiques
et courbes montrent des variations intéressantes.

Usage:
    python populate_db.py
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sandbox.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from catalog.models import Category, Product
from sales.models import Order, OrderItem, Invoice, Payment
from accounts.models import UserProfile


def create_users(count=10):
    """Crée des utilisateurs de test"""
    print(f"Création de {count} utilisateurs...")
    users = []
    
    first_names = ['Jean', 'Marie', 'Pierre', 'Sophie', 'Luc', 'Julie', 'Marc', 'Anne', 
                   'Thomas', 'Claire']
    
    last_names = ['Dupont', 'Martin', 'Bernard', 'Thomas', 'Petit', 'Robert', 'Richard',
                   'Durand', 'Dubois', 'Moreau']
    
    cities = ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice', 'Nantes', 'Strasbourg',
              'Montpellier', 'Bordeaux', 'Lille', 'Rennes', 'Reims', 'Le Havre', 'Saint-Étienne']
    
    countries = ['France', 'Belgique', 'Suisse', 'Canada', 'Espagne']
    
    for i in range(count):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        username = f"{first_name.lower()}.{last_name.lower()}{i}"
        email = f"{username}@example.com"
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=username,
            email=email,
            password='test123',
            first_name=first_name,
            last_name=last_name
        )
        
        # Créer le profil
        UserProfile.objects.create(
            user=user,
            phone=f"0{random.randint(100000000, 999999999)}",
            city=random.choice(cities),
            country=random.choice(countries),
            postal_code=f"{random.randint(10000, 99999)}",
            is_premium=random.choice([True, False, False, False]),  # 25% premium
            newsletter_subscribed=random.choice([True, False]),
            birth_date=timezone.now().date() - timedelta(days=random.randint(18*365, 65*365))
        )
        
        users.append(user)
    
    print(f"✓ {len(users)} utilisateurs créés")
    return users


def create_categories():
    """Crée des catégories de produits"""
    print("Création des catégories...")
    
    categories_data = [
        {'name': 'Électronique', 'description': 'Appareils électroniques et gadgets'},
        {'name': 'Vêtements', 'description': 'Mode et habillement'},
        {'name': 'Maison & Jardin', 'description': 'Décoration et aménagement'},
        {'name': 'Sport & Loisirs', 'description': 'Équipements sportifs'},
        {'name': 'Livres', 'description': 'Livres et magazines'},
        {'name': 'Alimentation', 'description': 'Produits alimentaires'},
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'slug': cat_data['name'].lower().replace(' ', '-').replace('&', 'et'),
                'description': cat_data['description'],
                'is_active': True
            }
        )
        categories.append(category)
    
    print(f"✓ {len(categories)} catégories créées")
    return categories


def create_products(categories, count=10):
    """Crée des produits variés"""
    print(f"Création de {count} produits variés...")
    
    # Sélectionner 10 produits variés de différentes catégories
    products_data = [
        # Électronique - prix élevés
        ('Smartphone Pro', 'Électronique', 599.99, 'SMART-PRO-001'),
        ('Tablette 10 pouces', 'Électronique', 299.99, 'TAB-10-001'),
        ('Écouteurs sans fil', 'Électronique', 89.99, 'ECOUT-WF-001'),
        # Vêtements - prix moyens
        ('T-shirt coton bio', 'Vêtements', 24.99, 'TSHIRT-BIO-001'),
        ('Jean slim', 'Vêtements', 59.99, 'JEAN-SLIM-001'),
        ('Veste en cuir', 'Vêtements', 149.99, 'VESTE-CUIR-001'),
        # Maison - prix variés
        ('Lampadaire design', 'Maison & Jardin', 129.99, 'LAMP-DESIGN-001'),
        ('Coussin décoratif', 'Maison & Jardin', 19.99, 'COUSSIN-DEC-001'),
        # Sport - prix moyens
        ('Raquette de tennis', 'Sport & Loisirs', 89.99, 'RAQ-TENNIS-001'),
        # Alimentation - prix bas
        ('Café bio 500g', 'Alimentation', 12.99, 'FOOD-CAFE-001'),
    ]
    
    products = []
    sku_counter = 1
    
    for name, cat_name, price, sku_base in products_data:
        # Trouver la catégorie correspondante
        category = next((c for c in categories if c.name == cat_name), categories[0])
        
        # Varier les prix légèrement pour plus de réalisme
        varied_price = Decimal(str(price)) * Decimal(str(random.uniform(0.95, 1.05)))
        
        product = Product.objects.create(
            name=name,
            slug=f"{name.lower().replace(' ', '-').replace('\'', '')}-{sku_counter}",
            category=category,
            price=varied_price,
            compare_price=varied_price * Decimal('1.2'),
            sku=f"{sku_base}-{sku_counter:03d}",
            stock_quantity=random.randint(10, 100),
            is_active=True,
            is_featured=random.choice([True, False, False]),  # 33% featured
            weight=Decimal(str(random.uniform(0.1, 5.0))),
            description=f"Description détaillée du produit {name}",
            short_description=f"Produit de qualité {name}"
        )
        products.append(product)
        sku_counter += 1
    
    print(f"✓ {len(products)} produits créés")
    return products


def create_orders(users, products, total_orders=40):
    """Crée des commandes avec des dates variées pour faire varier les courbes"""
    print(f"Création de {total_orders} commandes sur plusieurs périodes...")
    
    statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
    cities = ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice', 'Nantes', 'Bordeaux']
    countries = ['France', 'Belgique', 'Suisse']
    
    # Définir les périodes pour varier les dates (répartition équilibrée)
    now = timezone.now()
    periods = [
        # Dernier mois (30 derniers jours) - 35% des commandes
        (now - timedelta(days=30), now, 0.35),
        # Mois précédent (30-60 jours) - 25% des commandes
        (now - timedelta(days=60), now - timedelta(days=30), 0.25),
        # Il y a 2-3 mois (60-90 jours) - 20% des commandes
        (now - timedelta(days=90), now - timedelta(days=60), 0.20),
        # Il y a 3-4 mois (90-120 jours) - 10% des commandes
        (now - timedelta(days=120), now - timedelta(days=90), 0.10),
        # Il y a 4-6 mois (120-180 jours) - 10% des commandes
        (now - timedelta(days=180), now - timedelta(days=120), 0.10),
    ]
    
    orders = []
    order_counter = 1
    
    for period_start, period_end, percentage in periods:
        period_count = int(total_orders * percentage)
        
        for i in range(period_count):
            # Générer une date aléatoire dans la période
            days_diff = (period_end - period_start).days
            random_days = random.randint(0, days_diff)
            order_date = period_start + timedelta(days=random_days)
            
            user = random.choice(users)
            order_number = f"CMD-{order_date.strftime('%Y%m%d')}-{order_counter:04d}"
            status = random.choice(statuses)
            
            # Créer la commande avec une date personnalisée
            order = Order(
                user=user,
                order_number=order_number,
                status=status,
                shipping_address=f"{random.randint(1, 200)} Rue de la République",
                shipping_city=random.choice(cities),
                shipping_postal_code=f"{random.randint(10000, 99999)}",
                shipping_country=random.choice(countries),
                total_amount=Decimal('0'),
                created_at=order_date,
                updated_at=order_date
            )
            order.save()
            
            # Créer 1-5 articles par commande
            num_items = random.randint(1, 5)
            order_total = Decimal('0')
            
            for j in range(num_items):
                product = random.choice(products)
                quantity = random.randint(1, 3)
                unit_price = product.price
                subtotal = unit_price * quantity
                order_total += subtotal
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    subtotal=subtotal,
                    created_at=order_date
                )
            
            # Mettre à jour le total de la commande
            order.total_amount = order_total
            order.save()
            
            # Créer une facture pour les commandes livrées ou expédiées
            if status in ['shipped', 'delivered']:
                invoice_number = f"FAC-{order_date.strftime('%Y%m%d')}-{order_counter:04d}"
                issued_date = order_date.date()
                due_date = issued_date + timedelta(days=30)
                
                subtotal = order_total
                tax_amount = subtotal * Decimal('0.20')  # TVA 20%
                total_amount = subtotal + tax_amount
                
                invoice = Invoice.objects.create(
                    order=order,
                    invoice_number=invoice_number,
                    status=random.choice(['sent', 'paid', 'paid']),  # Plus de chances d'être payée
                    subtotal=subtotal,
                    tax_amount=tax_amount,
                    total_amount=total_amount,
                    issued_date=issued_date,
                    due_date=due_date,
                    created_at=order_date,
                    updated_at=order_date
                )
                
                # Créer un paiement si la facture est payée
                if invoice.status == 'paid':
                    payment_method = random.choice(['credit_card', 'bank_transfer', 'paypal'])
                    payment = Payment.objects.create(
                        invoice=invoice,
                        amount=total_amount,
                        method=payment_method,
                        status='completed',
                        transaction_id=f"TXN-{random.randint(100000, 999999)}",
                        payment_date=order_date + timedelta(days=random.randint(1, 5)),
                        created_at=order_date,
                        updated_at=order_date
                    )
            
            orders.append(order)
            order_counter += 1
    
    print(f"✓ {len(orders)} commandes créées avec dates variées")
    return orders


def main():
    """Fonction principale"""
    print("=" * 60)
    print("PEUPLEMENT DE LA BASE DE DONNÉES")
    print("=" * 60)
    print()
    
    # Vérifier si des données existent déjà
    if Order.objects.exists():
        response = input("Des données existent déjà. Voulez-vous continuer ? (o/n): ")
        if response.lower() not in ['o', 'oui', 'y', 'yes']:
            print("Opération annulée.")
            return
    
    try:
        # 1. Créer les utilisateurs
        users = create_users(count=10)
        print()
        
        # 2. Créer les catégories
        categories = create_categories()
        print()
        
        # 3. Créer les produits variés
        products = create_products(categories, count=10)
        print()
        
        # 4. Créer les commandes avec dates variées
        orders = create_orders(users, products, total_orders=40)
        print()
        
        # Statistiques finales
        print("=" * 60)
        print("STATISTIQUES FINALES")
        print("=" * 60)
        print(f"Utilisateurs: {User.objects.count()}")
        print(f"Profils: {UserProfile.objects.count()}")
        print(f"Catégories: {Category.objects.count()}")
        print(f"Produits: {Product.objects.count()}")
        print(f"Commandes: {Order.objects.count()}")
        print(f"Articles de commande: {OrderItem.objects.count()}")
        print(f"Factures: {Invoice.objects.count()}")
        print(f"Paiements: {Payment.objects.count()}")
        print()
        print("✓ Base de données peuplée avec succès !")
        print()
        print("Les données sont réparties sur les 6 derniers mois")
        print("pour que les graphiques montrent des variations intéressantes.")
        print()
        print("Résumé:")
        print(f"  - {len(users)} utilisateurs créés")
        print(f"  - {len(products)} produits variés créés")
        print(f"  - {len(orders)} commandes réparties sur 6 mois")
        
    except Exception as e:
        print(f"\n❌ Erreur lors du peuplement: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
