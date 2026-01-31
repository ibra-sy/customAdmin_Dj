"""
Commande Django pour peupler la base de données avec des données réalistes
Usage: python manage.py populate_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import date, timedelta
from decimal import Decimal
from django.utils import timezone

from accounts.models import UserProfile
from catalog.models import Category, Product
from sales.models import Order, OrderItem, Invoice, Payment


class Command(BaseCommand):
    help = 'Peuple la base de données avec des données réalistes'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Création des utilisateurs...'))
        users_data = [
            {'username': 'alice', 'email': 'alice@example.com', 'first_name': 'Alice', 'last_name': 'Martin'},
            {'username': 'bob', 'email': 'bob@example.com', 'first_name': 'Bob', 'last_name': 'Dupont'},
            {'username': 'charlie', 'email': 'charlie@example.com', 'first_name': 'Charlie', 'last_name': 'Bernard'},
            {'username': 'diana', 'email': 'diana@example.com', 'first_name': 'Diana', 'last_name': 'Moreau'},
            {'username': 'eve', 'email': 'eve@example.com', 'first_name': 'Eve', 'last_name': 'Petit'},
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

        self.stdout.write(self.style.SUCCESS(f'✓ {len(users)} utilisateurs créés'))

        self.stdout.write(self.style.SUCCESS('\nCréation des profils utilisateurs...'))
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

        self.stdout.write(self.style.SUCCESS(f'✓ {len(users)} profils créés'))

        self.stdout.write(self.style.SUCCESS('\nCréation des catégories...'))
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
        smartphones = Category.objects.get_or_create(
            name='Smartphones',
            slug='smartphones',
            defaults={
                'description': 'Téléphones intelligents',
                'parent': categories[0]  # Électronique
            }
        )[0]
        laptops = Category.objects.get_or_create(
            name='Ordinateurs portables',
            slug='ordinateurs-portables',
            defaults={
                'description': 'Laptops et notebooks',
                'parent': categories[5]  # Informatique
            }
        )[0]
        categories.extend([smartphones, laptops])

        self.stdout.write(self.style.SUCCESS(f'✓ {len(categories)} catégories créées'))

        self.stdout.write(self.style.SUCCESS('\nCréation des produits...'))
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

        self.stdout.write(self.style.SUCCESS(f'✓ {len(products)} produits créés'))

        self.stdout.write(self.style.SUCCESS('\nCréation des commandes...'))
        orders = []
        order_counter = 1

        # Commande 1 - Alice
        order1, _ = Order.objects.get_or_create(
            order_number=f'ORD{order_counter:05d}',
            defaults={
                'user': users[0],
                'status': 'delivered',
                'total_amount': Decimal('1199.99'),
                'shipping_address': '123 Rue de la Paix',
                'shipping_city': 'Paris',
                'shipping_postal_code': '75001',
                'shipping_country': 'France',
                'notes': 'Livraison express demandée',
                'created_at': timezone.now() - timedelta(days=30)
            }
        )
        orders.append(order1)
        order_counter += 1

        # Commande 2 - Bob
        order2, _ = Order.objects.get_or_create(
            order_number=f'ORD{order_counter:05d}',
            defaults={
                'user': users[1],
                'status': 'shipped',
                'total_amount': Decimal('1899.99'),
                'shipping_address': '456 Avenue des Champs',
                'shipping_city': 'Lyon',
                'shipping_postal_code': '69001',
                'shipping_country': 'France',
                'created_at': timezone.now() - timedelta(days=15)
            }
        )
        orders.append(order2)
        order_counter += 1

        # Commande 3 - Charlie
        order3, _ = Order.objects.get_or_create(
            order_number=f'ORD{order_counter:05d}',
            defaults={
                'user': users[2],
                'status': 'processing',
                'total_amount': Decimal('129.99'),
                'shipping_address': '789 Boulevard du Port',
                'shipping_city': 'Marseille',
                'shipping_postal_code': '13001',
                'shipping_country': 'France',
                'created_at': timezone.now() - timedelta(days=5)
            }
        )
        orders.append(order3)
        order_counter += 1

        # Commande 4 - Diana
        order4, _ = Order.objects.get_or_create(
            order_number=f'ORD{order_counter:05d}',
            defaults={
                'user': users[3],
                'status': 'pending',
                'total_amount': Decimal('299.99'),
                'shipping_address': '321 Rue du Commerce',
                'shipping_city': 'Toulouse',
                'shipping_postal_code': '31000',
                'shipping_country': 'France',
                'created_at': timezone.now() - timedelta(days=2)
            }
        )
        orders.append(order4)
        order_counter += 1

        # Commande 5 - Eve
        order5, _ = Order.objects.get_or_create(
            order_number=f'ORD{order_counter:05d}',
            defaults={
                'user': users[4],
                'status': 'delivered',
                'total_amount': Decimal('79.99'),
                'shipping_address': '654 Place de la République',
                'shipping_city': 'Nice',
                'shipping_postal_code': '06000',
                'shipping_country': 'France',
                'created_at': timezone.now() - timedelta(days=45)
            }
        )
        orders.append(order5)
        order_counter += 1

        # Commande 6 - Alice (seconde commande)
        order6, _ = Order.objects.get_or_create(
            order_number=f'ORD{order_counter:05d}',
            defaults={
                'user': users[0],
                'status': 'shipped',
                'total_amount': Decimal('149.99'),
                'shipping_address': '123 Rue de la Paix',
                'shipping_city': 'Paris',
                'shipping_postal_code': '75001',
                'shipping_country': 'France',
                'created_at': timezone.now() - timedelta(days=10)
            }
        )
        orders.append(order6)

        self.stdout.write(self.style.SUCCESS(f'✓ {len(orders)} commandes créées'))

        self.stdout.write(self.style.SUCCESS('\nCréation des articles de commande...'))
        # Articles pour commande 1
        OrderItem.objects.get_or_create(
            order=order1,
            product=products[0],  # iPhone 15 Pro
            defaults={
                'quantity': 1,
                'unit_price': Decimal('1199.99'),
                'subtotal': Decimal('1199.99')
            }
        )

        # Articles pour commande 2
        OrderItem.objects.get_or_create(
            order=order2,
            product=products[3],  # MacBook Pro
            defaults={
                'quantity': 1,
                'unit_price': Decimal('1899.99'),
                'subtotal': Decimal('1899.99')
            }
        )

        # Articles pour commande 3
        OrderItem.objects.get_or_create(
            order=order3,
            product=products[12],  # Raquette de Tennis
            defaults={
                'quantity': 1,
                'unit_price': Decimal('129.99'),
                'subtotal': Decimal('129.99')
            }
        )

        # Articles pour commande 4
        OrderItem.objects.get_or_create(
            order=order4,
            product=products[8],  # Veste en Cuir
            defaults={
                'quantity': 1,
                'unit_price': Decimal('299.99'),
                'subtotal': Decimal('299.99')
            }
        )

        # Articles pour commande 5
        OrderItem.objects.get_or_create(
            order=order5,
            product=products[7],  # Jean Slim
            defaults={
                'quantity': 1,
                'unit_price': Decimal('79.99'),
                'subtotal': Decimal('79.99')
            }
        )

        # Articles pour commande 6 (plusieurs produits)
        OrderItem.objects.get_or_create(
            order=order6,
            product=products[9],  # Lampadaire Design
            defaults={
                'quantity': 1,
                'unit_price': Decimal('149.99'),
                'subtotal': Decimal('149.99')
            }
        )

        # Commande supplémentaire avec plusieurs articles
        order7, _ = Order.objects.get_or_create(
            order_number=f'ORD{order_counter+1:05d}',
            defaults={
                'user': users[1],
                'status': 'processing',
                'total_amount': Decimal('159.94'),
                'shipping_address': '456 Avenue des Champs',
                'shipping_city': 'Lyon',
                'shipping_postal_code': '69001',
                'shipping_country': 'France',
                'created_at': timezone.now() - timedelta(days=3)
            }
        )

        OrderItem.objects.get_or_create(
            order=order7,
            product=products[6],  # T-shirt Premium
            defaults={
                'quantity': 2,
                'unit_price': Decimal('29.99'),
                'subtotal': Decimal('59.98')
            }
        )

        OrderItem.objects.get_or_create(
            order=order7,
            product=products[17],  # Crème Visage
            defaults={
                'quantity': 4,
                'unit_price': Decimal('24.99'),
                'subtotal': Decimal('99.96')
            }
        )

        self.stdout.write(self.style.SUCCESS('✓ Articles de commande créés'))

        self.stdout.write(self.style.SUCCESS('\nCréation des factures...'))
        invoices = []
        invoice_counter = 1

        for order in orders[:5]:  # Factures pour les 5 premières commandes
            invoice = Invoice.objects.get_or_create(
                order=order,
                defaults={
                    'invoice_number': f'INV{invoice_counter:05d}',
                    'status': 'paid' if order.status == 'delivered' else 'sent',
                    'subtotal': order.total_amount * Decimal('0.833'),  # HT (TVA 20%)
                    'tax_amount': order.total_amount * Decimal('0.167'),
                    'total_amount': order.total_amount,
                    'issued_date': order.created_at.date(),
                    'due_date': order.created_at.date() + timedelta(days=30)
                }
            )[0]
            invoices.append(invoice)
            invoice_counter += 1

        self.stdout.write(self.style.SUCCESS(f'✓ {len(invoices)} factures créées'))

        self.stdout.write(self.style.SUCCESS('\nCréation des paiements...'))
        payment_methods = ['credit_card', 'bank_transfer', 'paypal', 'credit_card', 'bank_transfer']
        payment_statuses = ['completed', 'completed', 'processing', 'pending', 'completed']

        for i, invoice in enumerate(invoices):
            Payment.objects.get_or_create(
                invoice=invoice,
                defaults={
                    'amount': invoice.total_amount,
                    'method': payment_methods[i],
                    'status': payment_statuses[i],
                    'transaction_id': f'TXN{invoice.invoice_number}',
                    'payment_date': invoice.issued_date if payment_statuses[i] == 'completed' else None
                }
            )

        self.stdout.write(self.style.SUCCESS(f'✓ {len(invoices)} paiements créés'))

        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('✓ Base de données peuplée avec succès !'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.SUCCESS(f'\nRésumé :'))
        self.stdout.write(self.style.SUCCESS(f'- {User.objects.count()} utilisateurs'))
        self.stdout.write(self.style.SUCCESS(f'- {UserProfile.objects.count()} profils'))
        self.stdout.write(self.style.SUCCESS(f'- {Category.objects.count()} catégories'))
        self.stdout.write(self.style.SUCCESS(f'- {Product.objects.count()} produits'))
        self.stdout.write(self.style.SUCCESS(f'- {Order.objects.count()} commandes'))
        self.stdout.write(self.style.SUCCESS(f'- {OrderItem.objects.count()} articles de commande'))
        self.stdout.write(self.style.SUCCESS(f'- {Invoice.objects.count()} factures'))
        self.stdout.write(self.style.SUCCESS(f'- {Payment.objects.count()} paiements'))
