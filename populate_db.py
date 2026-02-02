"""
Script pour peupler la base de données avec des données réalistes
À exécuter après les migrations : python manage.py shell < populate_db.py
Ou directement : python manage.py shell puis copier-coller le contenu
"""
import os
import django
from datetime import date, timedelta
from decimal import Decimal
from django.utils import timezone

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sandbox.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from catalog.models import Category, Product
from sales.models import Order, OrderItem, Invoice, Payment

# Nettoyer les données existantes (optionnel, commenté pour éviter de supprimer les données)
# UserProfile.objects.all().delete()
# Payment.objects.all().delete()
# Invoice.objects.all().delete()
# OrderItem.objects.all().delete()
# Order.objects.all().delete()
# Product.objects.all().delete()
# Category.objects.all().delete()
# User.objects.filter(is_superuser=False).delete()

print("Création des utilisateurs...")
users_data = [
    {'username': 'alice', 'email': 'alice@example.com', 'first_name': 'Alice', 'last_name': 'Martin'},
    {'username': 'bob', 'email': 'bob@example.com', 'first_name': 'Bob', 'last_name': 'Dupont'},
    {'username': 'charlie', 'email': 'charlie@example.com', 'first_name': 'Charlie', 'last_name': 'Bernard'},
    {'username': 'diana', 'email': 'diana@example.com', 'first_name': 'Diana', 'last_name': 'Moreau'},
    {'username': 'eve', 'email': 'eve@example.com', 'first_name': 'Eve', 'last_name': 'Petit'},
    {'username': 'bleou', 'email': 'christbleou@example.com', 'first_name': 'Christ', 'last_name': 'Bléou'},
]

users = []
for user_data in users_data:
    user, created = User.objects.get_or_create(
        username=user_data['username'],
        defaults={
            'email': user_data['email'],
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
        }
    )
    if created:
        user.set_password('password123')
        user.save()
    users.append(user)

print(f"✓ {len(users)} utilisateurs créés")

print("\nCréation des profils utilisateurs...")
profiles_data = [
    {'phone': '+33123456789', 'city': 'Paris', 'postal_code': '75001', 'country': 'France', 'is_premium': True},
    {'phone': '+33987654321', 'city': 'Lyon', 'postal_code': '69001', 'country': 'France', 'is_premium': False},
    {'phone': '+33555123456', 'city': 'Marseille', 'postal_code': '13001', 'country': 'France', 'newsletter_subscribed': True},
    {'phone': '+33444111222', 'city': 'Toulouse', 'postal_code': '31000', 'country': 'France', 'is_premium': True},
    {'phone': '+33333222333', 'city': 'Nice', 'postal_code': '06000', 'country': 'France', 'newsletter_subscribed': True},
]

for i, user in enumerate(users):
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults=profiles_data[i]
    )
    if not created:
        for key, value in profiles_data[i].items():
            setattr(profile, key, value)
        profile.save()

print(f"✓ {len(users)} profils créés")

print("\nCréation des catégories...")
categories_data = [
    {'name': 'Électronique', 'slug': 'electronique', 'description': 'Appareils électroniques et gadgets'},
    {'name': 'Vêtements', 'slug': 'vetements', 'description': 'Mode et habillement'},
    {'name': 'Maison & Jardin', 'slug': 'maison-jardin', 'description': 'Décoration et aménagement'},
    {'name': 'Sports & Loisirs', 'slug': 'sports-loisirs', 'description': 'Équipements sportifs et activités'},
    {'name': 'Livres', 'slug': 'livres', 'description': 'Livres et publications'},
    {'name': 'Informatique', 'slug': 'informatique', 'description': 'Ordinateurs et accessoires'},
    {'name': 'Cuisine', 'slug': 'cuisine', 'description': 'Ustensiles et électroménager'},
    {'name': 'Beauté & Santé', 'slug': 'beaute-sante', 'description': 'Produits de beauté et bien-être'},
]

categories = []
for cat_data in categories_data:
    category, created = Category.objects.get_or_create(
        slug=cat_data['slug'],
        defaults=cat_data
    )
    categories.append(category)

# Ajouter quelques sous-catégories
smartphones = Category.objects.create(
    name='Smartphones',
    slug='smartphones',
    description='Téléphones intelligents',
    parent=categories[0]  # Électronique
)
laptops = Category.objects.create(
    name='Ordinateurs portables',
    slug='ordinateurs-portables',
    description='Laptops et notebooks',
    parent=categories[5]  # Informatique
)
categories.extend([smartphones, laptops])

print(f"✓ {len(categories)} catégories créées")

print("\nCréation des produits...")
products_data = [
    # Électronique / Smartphones
    {'name': 'iPhone 15 Pro', 'slug': 'iphone-15-pro', 'category': smartphones, 'price': Decimal('1199.99'),
     'compare_price': Decimal('1299.99'), 'sku': 'IPH15PRO001', 'stock_quantity': 25, 'is_featured': True,
     'description': 'Dernier iPhone avec puce A17 Pro', 'weight': Decimal('0.187')},
    {'name': 'Samsung Galaxy S24', 'slug': 'samsung-galaxy-s24', 'category': smartphones, 'price': Decimal('999.99'),
     'sku': 'SGS24001', 'stock_quantity': 30, 'is_featured': True,
     'description': 'Smartphone Android haut de gamme', 'weight': Decimal('0.168')},
    {'name': 'Google Pixel 8', 'slug': 'google-pixel-8', 'category': smartphones, 'price': Decimal('699.99'),
     'sku': 'GPX8001', 'stock_quantity': 15, 'description': 'Smartphone Google avec Android pur'},

    # Informatique / Laptops
    {'name': 'MacBook Pro 16"', 'slug': 'macbook-pro-16', 'category': laptops, 'price': Decimal('2499.99'),
     'sku': 'MBP16001', 'stock_quantity': 10, 'is_featured': True,
     'description': 'Ordinateur portable professionnel Apple', 'weight': Decimal('2.14')},
    {'name': 'Dell XPS 15', 'slug': 'dell-xps-15', 'category': laptops, 'price': Decimal('1899.99'),
     'sku': 'DXP15001', 'stock_quantity': 12, 'description': 'Laptop Dell haut de gamme', 'weight': Decimal('1.92')},
    {'name': 'Lenovo ThinkPad X1', 'slug': 'lenovo-thinkpad-x1', 'category': laptops, 'price': Decimal('1599.99'),
     'sku': 'LTX1001', 'stock_quantity': 8, 'description': 'Laptop professionnel Lenovo'},

    # Vêtements
    {'name': 'T-shirt Premium', 'slug': 'tshirt-premium', 'category': categories[1], 'price': Decimal('29.99'),
     'sku': 'TSH001', 'stock_quantity': 100, 'description': 'T-shirt en coton bio'},
    {'name': 'Jean Slim', 'slug': 'jean-slim', 'category': categories[1], 'price': Decimal('79.99'),
     'sku': 'JEA001', 'stock_quantity': 50, 'description': 'Jean coupe slim'},
    {'name': 'Veste en Cuir', 'slug': 'veste-cuir', 'category': categories[1], 'price': Decimal('299.99'),
     'sku': 'VES001', 'stock_quantity': 20, 'is_featured': True, 'description': 'Veste en cuir véritable'},

    # Maison & Jardin
    {'name': 'Lampadaire Design', 'slug': 'lampadaire-design', 'category': categories[2], 'price': Decimal('149.99'),
     'sku': 'LAM001', 'stock_quantity': 30, 'description': 'Lampadaire moderne et élégant'},
    {'name': 'Table Basse Bois', 'slug': 'table-basse-bois', 'category': categories[2], 'price': Decimal('199.99'),
     'sku': 'TAB001', 'stock_quantity': 15, 'description': 'Table basse en bois massif'},

    # Sports & Loisirs
    {'name': 'Vélo de Route', 'slug': 'velo-route', 'category': categories[3], 'price': Decimal('899.99'),
     'sku': 'VEL001', 'stock_quantity': 5, 'is_featured': True, 'description': 'Vélo de route professionnel'},
    {'name': 'Raquette de Tennis', 'slug': 'raquette-tennis', 'category': categories[3], 'price': Decimal('129.99'),
     'sku': 'RAQ001', 'stock_quantity': 25, 'description': 'Raquette de tennis professionnelle'},

    # Livres
    {'name': 'Le Guide Django', 'slug': 'guide-django', 'category': categories[4], 'price': Decimal('39.99'),
     'sku': 'LIV001', 'stock_quantity': 50, 'description': 'Guide complet sur Django'},
    {'name': 'Python Avancé', 'slug': 'python-avance', 'category': categories[4], 'price': Decimal('45.99'),
     'sku': 'LIV002', 'stock_quantity': 40, 'description': 'Programmation Python avancée'},

    # Cuisine
    {'name': 'Robot Cuiseur', 'slug': 'robot-cuiseur', 'category': categories[6], 'price': Decimal('299.99'),
     'sku': 'ROB001', 'stock_quantity': 20, 'description': 'Robot cuiseur multifonction'},
    {'name': 'Casserole Inox', 'slug': 'casserole-inox', 'category': categories[6], 'price': Decimal('49.99'),
     'sku': 'CAS001', 'stock_quantity': 60, 'description': 'Casserole en inox 18/10'},

    # Beauté & Santé
    {'name': 'Crème Visage', 'slug': 'creme-visage', 'category': categories[7], 'price': Decimal('24.99'),
     'sku': 'CRE001', 'stock_quantity': 80, 'description': 'Crème hydratante visage'},
    {'name': 'Shampoing Bio', 'slug': 'shampoing-bio', 'category': categories[7], 'price': Decimal('12.99'),
     'sku': 'SHA001', 'stock_quantity': 100, 'description': 'Shampoing bio naturel'},
]

products = []
for prod_data in products_data:
    product, created = Product.objects.get_or_create(
        sku=prod_data['sku'],
        defaults=prod_data
    )
    products.append(product)

print(f"✓ {len(products)} produits créés")

print("\nCréation des commandes...")
orders = []
order_counter = 1

# Commande 1 - Alice
order1 = Order.objects.create(
    user=users[0],
    order_number=f'ORD{order_counter:05d}',
    status='delivered',
    total_amount=Decimal('1199.99'),
    shipping_address='123 Rue de la Paix',
    shipping_city='Paris',
    shipping_postal_code='75001',
    shipping_country='France',
    notes='Livraison express demandée',
    created_at=timezone.now() - timedelta(days=30)
)
orders.append(order1)
order_counter += 1

# Commande 2 - Bob
order2 = Order.objects.create(
    user=users[1],
    order_number=f'ORD{order_counter:05d}',
    status='shipped',
    total_amount=Decimal('1899.99'),
    shipping_address='456 Avenue des Champs',
    shipping_city='Lyon',
    shipping_postal_code='69001',
    shipping_country='France',
    created_at=timezone.now() - timedelta(days=15)
)
orders.append(order2)
order_counter += 1

# Commande 3 - Charlie
order3 = Order.objects.create(
    user=users[2],
    order_number=f'ORD{order_counter:05d}',
    status='processing',
    total_amount=Decimal('129.99'),
    shipping_address='789 Boulevard du Port',
    shipping_city='Marseille',
    shipping_postal_code='13001',
    shipping_country='France',
    created_at=timezone.now() - timedelta(days=5)
)
orders.append(order3)
order_counter += 1

# Commande 4 - Diana
order4 = Order.objects.create(
    user=users[3],
    order_number=f'ORD{order_counter:05d}',
    status='pending',
    total_amount=Decimal('299.99'),
    shipping_address='321 Rue du Commerce',
    shipping_city='Toulouse',
    shipping_postal_code='31000',
    shipping_country='France',
    created_at=timezone.now() - timedelta(days=2)
)
orders.append(order4)
order_counter += 1

# Commande 5 - Eve
order5 = Order.objects.create(
    user=users[4],
    order_number=f'ORD{order_counter:05d}',
    status='delivered',
    total_amount=Decimal('79.99'),
    shipping_address='654 Place de la République',
    shipping_city='Nice',
    shipping_postal_code='06000',
    shipping_country='France',
    created_at=timezone.now() - timedelta(days=45)
)
orders.append(order5)
order_counter += 1

# Commande 6 - Alice (seconde commande)
order6 = Order.objects.create(
    user=users[0],
    order_number=f'ORD{order_counter:05d}',
    status='shipped',
    total_amount=Decimal('149.99'),
    shipping_address='123 Rue de la Paix',
    shipping_city='Paris',
    shipping_postal_code='75001',
    shipping_country='France',
    created_at=timezone.now() - timedelta(days=10)
)
orders.append(order6)

print(f"✓ {len(orders)} commandes créées")

print("\nCréation des articles de commande...")
# Articles pour commande 1
OrderItem.objects.create(
    order=order1,
    product=products[0],  # iPhone 15 Pro
    quantity=1,
    unit_price=Decimal('1199.99'),
    subtotal=Decimal('1199.99')
)

# Articles pour commande 2
OrderItem.objects.create(
    order=order2,
    product=products[3],  # MacBook Pro
    quantity=1,
    unit_price=Decimal('1899.99'),
    subtotal=Decimal('1899.99')
)

# Articles pour commande 3
OrderItem.objects.create(
    order=order3,
    product=products[13],  # Raquette de Tennis
    quantity=1,
    unit_price=Decimal('129.99'),
    subtotal=Decimal('129.99')
)

# Articles pour commande 4
OrderItem.objects.create(
    order=order4,
    product=products[8],  # Veste en Cuir
    quantity=1,
    unit_price=Decimal('299.99'),
    subtotal=Decimal('299.99')
)

# Articles pour commande 5
OrderItem.objects.create(
    order=order5,
    product=products[7],  # Jean Slim
    quantity=1,
    unit_price=Decimal('79.99'),
    subtotal=Decimal('79.99')
)

# Articles pour commande 6 (plusieurs produits)
OrderItem.objects.create(
    order=order6,
    product=products[9],  # Lampadaire Design
    quantity=1,
    unit_price=Decimal('149.99'),
    subtotal=Decimal('149.99')
)

# Commande supplémentaire avec plusieurs articles
order7 = Order.objects.create(
    user=users[1],
    order_number=f'ORD{order_counter+1:05d}',
    status='processing',
    total_amount=Decimal('179.97'),
    shipping_address='456 Avenue des Champs',
    shipping_city='Lyon',
    shipping_postal_code='69001',
    shipping_country='France',
    created_at=timezone.now() - timedelta(days=3)
)

OrderItem.objects.create(
    order=order7,
    product=products[6],  # T-shirt Premium
    quantity=2,
    unit_price=Decimal('29.99'),
    subtotal=Decimal('59.98')
)

OrderItem.objects.create(
    order=order7,
    product=products[19],  # Crème Visage
    quantity=4,
    unit_price=Decimal('24.99'),
    subtotal=Decimal('99.96')
)
order7.total_amount = Decimal('159.94')
order7.save()

print("✓ Articles de commande créés")

print("\nCréation des factures...")
invoices = []
invoice_counter = 1

for order in orders[:5]:  # Factures pour les 5 premières commandes
    invoice = Invoice.objects.create(
        order=order,
        invoice_number=f'INV{invoice_counter:05d}',
        status='paid' if order.status == 'delivered' else 'sent',
        subtotal=order.total_amount * Decimal('0.833'),  # HT (TVA 20%)
        tax_amount=order.total_amount * Decimal('0.167'),
        total_amount=order.total_amount,
        issued_date=order.created_at.date(),
        due_date=order.created_at.date() + timedelta(days=30)
    )
    invoices.append(invoice)
    invoice_counter += 1

print(f"✓ {len(invoices)} factures créées")

print("\nCréation des paiements...")
payment_methods = ['credit_card', 'bank_transfer', 'paypal', 'credit_card', 'bank_transfer']
payment_statuses = ['completed', 'completed', 'processing', 'pending', 'completed']

for i, invoice in enumerate(invoices):
    Payment.objects.create(
        invoice=invoice,
        amount=invoice.total_amount,
        method=payment_methods[i],
        status=payment_statuses[i],
        transaction_id=f'TXN{invoice.invoice_number}',
        payment_date=invoice.issued_date if payment_statuses[i] == 'completed' else None
    )

print(f"✓ {len(invoices)} paiements créés")

print("\n" + "="*50)
print("✓ Base de données peuplée avec succès !")
print("="*50)
print(f"\nRésumé :")
print(f"- {User.objects.count()} utilisateurs")
print(f"- {UserProfile.objects.count()} profils")
print(f"- {Category.objects.count()} catégories")
print(f"- {Product.objects.count()} produits")
print(f"- {Order.objects.count()} commandes")
print(f"- {OrderItem.objects.count()} articles de commande")
print(f"- {Invoice.objects.count()} factures")
print(f"- {Payment.objects.count()} paiements")
