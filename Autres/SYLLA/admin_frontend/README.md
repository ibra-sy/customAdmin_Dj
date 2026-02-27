# Admin Frontend — Templates et interface (Option A)

Ce dossier contient **deux entrées** : la **page de connexion** (base design) et l’**Admin Console** (maquette SPA). Les deux sont intégrées au backend Django.

---

## 1. Page de connexion et tableau de bord (base design)

### Fichiers

- **index.html** — Page de connexion (formulaire login, lien vers Admin Console ou dashboard).
- **dashboard.html**, **charts.html**, **change_list.html**, etc. — Autres pages de la maquette multi-pages (si présentes).
- **css/** — design_system.css, themes.css, modern_admin.css, professional_admin.css, ux_enhancements.css, admin_custom.css.
- **js/** — admin_custom.js, layout.js.

### Utilisation (fichiers statiques)

1. Ouvrir `index.html` dans un navigateur pour la page de connexion.
2. Cliquer sur « Se connecter » pour accéder à **admin_console.html** (Admin Console SPA).
3. Ou ouvrir directement `dashboard.html` pour l’interface principale (si vous utilisez la structure multi-pages).

**Remarque :** Utiliser un serveur HTTP local (Live Server, `python -m http.server`, etc.) si les ressources ne se chargent pas en ouvrant le fichier directement.

### Dépendances (CDN)

- Bootstrap 5.3.2  
- Font Awesome 6.5.1  
- Chart.js 4.4.1  
- Google Fonts (Inter)

### Fonctionnalités (base design)

- **Thèmes** : Bleu moderne, Émeraude, Coucher de soleil, Mode sombre (Paramètres).
- **Graphiques** : Création et enregistrement en `localStorage`.
- **Formulaires** : Validation côté client, upload de fichiers.
- **Responsive** : Adapté mobile et desktop.
- **Navigation** : Sidebar rétractable, fil d’Ariane, notifications.

---

## 2. Admin Console (maquette SPA)

### Fichiers

- **admin_console.html** — Interface single-page (Dashboard, Commandes, Produits, Clients, Utilisateurs, Paramètres).
- **assets/styles.css** — Styles de l’Admin Console.
- **assets/app.js** — Logique (vues, thème, graphiques, terminologie).

### Lancer (fichiers statiques)

Ouvrir `admin_console.html` dans le navigateur (ou passer par `index.html` → Se connecter → admin_console.html).

### Thème (Admin Console)

- Mode Light/Dark : toggle en haut à droite.
- Couleur principale : color picker.
- Persistance : `localStorage`.

### Intégration Django

Les deux entrées sont servies par le backend :

- **Page de connexion** : `/admin-login/` (maquette statique) ou utiliser l’authentification Django (`/admin/`, interface avec choix).
- **Admin Console** : `/admin-console/` (réservé aux utilisateurs connectés). Les assets sont servis sous `/admin-console/assets/`.

Pour une intégration avancée plus tard :

- Templates : copier la structure dans `templates/admin/` (override `base_site.html`, `base.html`, `index.html`).
- Static : `assets/styles.css` et `assets/app.js` sont servis par Django via les vues dédiées (ou copier dans `static/admin_custom/`).
- Persistance DB : remplacer `localStorage` par un modèle singleton (ex. `AdminBrandingSettings`) + context processor / admin view.

---

## 3. Pas de backend (mode maquette seule)

En ouvrant uniquement les fichiers HTML (sans passer par Django) :

- Les formulaires ne sont pas soumis à un serveur.
- Les données sont stockées uniquement en `localStorage` (graphiques, thème).
- Aucune authentification réelle.
