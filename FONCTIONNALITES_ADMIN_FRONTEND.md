# Fonctionnalités ajoutées (Admin Frontend – maquette)

Après le merge de `feature/admin-frontend`, une **maquette statique** d’interface admin a été ajoutée. Voici ce qu’elle contient et comment la lancer.

---

## Ce qui a été ajouté (résumé)

| Élément | Description |
|--------|-------------|
| **Type** | Maquette statique (HTML + CSS + JS), **pas encore branchée** sur le backend Django. |
| **Emplacement** | Dossier `admin_frontend/` à la racine du projet. |
| **Données** | Données fictives en dur ; pas de lecture en base pour l’instant. |

---

## Fonctionnalités de la maquette

### 1. **Navigation (menu latéral)**

- **Dashboard** – Aperçu et indicateurs
- **Commandes** – Liste des commandes (données de démo)
- **Produits** – Liste des produits
- **Clients** – Liste des clients
- **Utilisateurs** – Gestion des utilisateurs
- **Paramètres** – Personnalisation (thème, couleurs, graphiques)

### 2. **Dashboard**

- **KPIs** : Chiffre d’affaires, Commandes, Panier moyen, Taux d’erreur (avec mini graphiques)
- **Activité récente** : Timeline d’événements fictifs
- **Raccourcis** : Ajouter produit, Générer facture, Remboursement, Export
- **Graphiques personnalisables** :
  - Ventes (CA / commandes / panier moyen)
  - Conversion (taux de conversion / abandon panier / remboursements)
  - Trafic (visiteurs / sessions / taux de rebond)
  - Ordre des graphiques modifiable (↑ / ↓), activation/désactivation, choix de la métrique

### 3. **Personnalisation (thème)**

- **Mode clair / sombre** : interrupteur en haut à droite
- **Couleur principale** : color picker (couleur d’accent de l’interface)
- **Persistance** : préférences enregistrées dans le navigateur (`localStorage`)

### 4. **Terminologie**

- **Sélecteur** en haut : Standard / Commerce / English  
- Change les libellés (ex. « Commandes » → « Ventes », « Produits » → « Articles »)

### 5. **Autres**

- **Sidebar** : bouton pour replier / déplier le menu
- **Notifications** et **Aide** : boutons en barre supérieure (toasts / messages de démo)
- **Recherche** dans le menu (champ de recherche dans la nav)
- **Accessibilité** : lien « Aller au contenu », labels pour lecteurs d’écran

---

## Comment lancer le projet et voir la maquette

### Option A – Ouvrir la maquette directement dans le navigateur

1. Ouvre le fichier suivant dans ton navigateur (double-clic ou « Ouvrir avec ») :
   ```
   c:\Users\HP\Desktop\Admin_custom_django\customAdmin_Dj\admin_frontend\index.html
   ```
2. Tu verras l’interface Admin Console avec toutes les fonctionnalités ci-dessus (données fictives).

### Option B – Via le serveur Django (recommandé)

1. À la racine du projet (`customAdmin_Dj`), active l’environnement virtuel si tu en as un, puis lance :
   ```bash
   python manage.py runserver
   ```
2. Ouvre dans le navigateur :
   - **Maquette admin** : [http://127.0.0.1:8000/admin-console/](http://127.0.0.1:8000/admin-console/)
   - **Admin Django réel** (données en base) : [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

Pour que l’admin Django ait des données, exécute une fois :
```bash
python manage.py populate_data
```
Puis connecte-toi à `/admin/` avec un superutilisateur (à créer avec `python manage.py createsuperuser` si besoin).

---

## Différence maquette vs admin Django

| | Maquette (`/admin-console/`) | Admin Django (`/admin/`) |
|---|------------------------------|---------------------------|
| **Données** | Fictives (HTML/JS) | Vraie base (SQLite) |
| **Connexion** | Aucune | Login requis |
| **Actions** | Clics visuels uniquement | CRUD réel (accounts, catalog, sales) |
| **Usage** | Démo / design | Backoffice opérationnel |

L’intégration future (templates Django, static, modèle pour les préférences) est décrite dans `admin_frontend/README.md`.
