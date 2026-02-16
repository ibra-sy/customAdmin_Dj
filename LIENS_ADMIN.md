# Les deux interfaces admin — Ce qui existait et ce qu’on a ajouté

**Connexion pour tout le backoffice :** identifiant **admin**, mot de passe **admin**.

**Base URL :** http://127.0.0.1:8000/

---

## Les deux liens principaux (après le merge)

Tu as maintenant **deux entrées** pour l’administration :

| Lien | URL | Rôle |
|------|-----|------|
| **Admin** | **http://127.0.0.1:8000/admin/** | Backoffice Django (gestion des modèles : utilisateurs, catalogues, ventes, etc.). |
| **Admin Console** | **http://127.0.0.1:8000/admin-console/** | Nouvelle interface type tableau de bord (KPIs, graphiques, Commandes, Produits, thème clair/sombre). |

Les deux demandent d’être connecté. Avec **admin** / **admin**, tu peux accéder à toutes les pages correctement.

---

## Ce qui existait AVANT le merge

- **Un seul “admin”** :  
  - **http://127.0.0.1:8000/admin/**  
  - C’est l’admin Django personnalisé (CustomAdminSite) : connexion, puis gestion des modèles (accounts, catalog, sales, etc.).  
- La maquette (fichiers dans `admin_frontend/`) existait en **fichiers statiques** seulement : pas d’URL Django pour y accéder depuis le navigateur.

En résumé : avant le merge, il n’y avait qu’**un** lien d’admin principal, **/admin/**.

---

## Ce qu’on a AJOUTÉ APRÈS le merge

- **Admin Console** :  
  - **http://127.0.0.1:8000/admin-console/**  
  - Interface en une page (SPA) : Dashboard, Commandes, Produits, Clients, Utilisateurs, Paramètres, graphiques, thème light/dark, couleur principale.  
  - Données de démo (pas encore branchées sur la base).  
- **Page de connexion maquette** (optionnelle) :  
  - **http://127.0.0.1:8000/admin-login/**  
  - Maquette de l’écran de connexion ; le bouton « Se connecter » envoie vers l’Admin Console.

En résumé : après le merge, on a ajouté **un deuxième** lien d’admin, **/admin-console/**, plus la page maquette **/admin-login/**.

---

## Utilisation rapide

1. Ouvre **http://127.0.0.1:8000/admin/**.
2. Connecte-toi avec **admin** / **admin**.
3. Ensuite tu peux :
   - Rester sur **/admin/** pour gérer les données (utilisateurs, produits, commandes, etc.).
   - Aller sur **http://127.0.0.1:8000/admin-console/** pour la nouvelle interface tableau de bord (Admin Console).

Avec le compte **admin** / **admin**, tu passes correctement sur toutes les pages (admin et admin console).
