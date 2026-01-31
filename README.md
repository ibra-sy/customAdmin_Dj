# Django Sandbox - Projet de test pour l'admin Django

Projet Django sandbox complet et réaliste, destiné à servir de base de test pour de futurs développements autour de l'admin Django.

## 🏗️ Structure du projet

- **accounts** : Gestion des profils utilisateurs
- **catalog** : Produits et catégories
- **sales** : Commandes, factures, paiements

## 📦 Modèles créés

### accounts
- `UserProfile` : Profil utilisateur étendu (OneToOne avec User)

### catalog
- `Category` : Catégories de produits (avec hiérarchie)
- `Product` : Produits du catalogue

### sales
- `Order` : Commandes clients
- `OrderItem` : Articles de commande
- `Invoice` : Factures
- `Payment` : Paiements

**Total : 7 modèles** avec relations cohérentes et réalistes.

## 🚀 Installation et démarrage

### 1. Activer l'environnement virtuel
```bash
venv\Scripts\Activate.ps1
```

### 2. Générer les migrations
```bash
python manage.py makemigrations
```

### 3. Appliquer les migrations
```bash
python manage.py migrate
```

### 4. Peupler la base de données
```bash
python manage.py populate_data
```

Cette commande créera :
- 5 utilisateurs avec leurs profils
- 10 catégories (dont 2 sous-catégories)
- 20+ produits
- 7 commandes avec articles
- 5 factures
- 5 paiements

### 5. Créer un superutilisateur
```bash
python manage.py createsuperuser
```

### 6. Lancer le serveur de développement
```bash
python manage.py runserver
```

### 7. Accéder à l'admin Django
Ouvrir dans le navigateur : http://127.0.0.1:8000/admin/

## 📋 Configuration admin

Tous les modèles sont enregistrés dans l'admin Django avec :
- `list_display` : Colonnes affichées dans la liste
- `search_fields` : Champs recherchables
- `list_filter` : Filtres disponibles

**Aucune personnalisation visuelle ou fonctionnelle** - utilisation de l'admin Django par défaut uniquement.

## 🔑 Identifiants de test

Les utilisateurs créés par `populate_data` ont tous le mot de passe : `password123`

- alice@example.com
- bob@example.com
- charlie@example.com
- diana@example.com
- eve@example.com

## 📁 Fichiers importants

- `requirements.txt` : Dépendances Python
- `populate_db.py` : Script alternatif pour peupler la base (peut être utilisé via shell Django)
- `sales/management/commands/populate_data.py` : Commande Django pour peupler la base

## 🎯 Objectif

Ce projet sert de **sandbox de référence** pour tester et développer des fonctionnalités autour de l'admin Django, avec une base de données riche et réaliste.
