# Admin Frontend — Templates et interface

Dossier contenant **uniquement le front-end** (templates HTML, CSS, JavaScript) de l’interface d’administration, sans backend.

## Structure

```
admin_frontend/
├── index.html          # Page de connexion
├── dashboard.html      # Tableau de bord
├── charts.html         # Graphiques
├── chart_create.html   # Créer un graphique
├── change_list.html    # Liste (ex: Utilisateurs)
├── change_form.html    # Formulaire d’édition
├── add_form.html       # Ajouter un utilisateur
├── grids.html          # Exemples de grilles
├── notifications.html  # Centre de notifications
├── profile.html        # Profil utilisateur
├── settings.html       # Paramètres (thèmes, profil, etc.)
├── object_history.html # Historique des modifications
├── css/                # Feuilles de style
│   ├── design_system.css
│   ├── themes.css
│   ├── modern_admin.css
│   ├── professional_admin.css
│   ├── ux_enhancements.css
│   └── admin_custom.css
├── js/
│   ├── admin_custom.js # Scripts principaux
│   └── layout.js       # Données de navigation
└── images/
    └── image.png
```

## Utilisation

1. Ouvrir `index.html` dans un navigateur pour la page de connexion.
2. Cliquer sur « Se connecter » pour accéder au tableau de bord.
3. Ou ouvrir directement `dashboard.html` pour l’interface principale.

**Remarque :** Utiliser un serveur HTTP local (Live Server, `python -m http.server`, etc.) si les ressources ne se chargent pas correctement en ouvrant le fichier directement.

## Dépendances (CDN)

- Bootstrap 5.3.2
- Font Awesome 6.5.1
- Chart.js 4.4.1
- Google Fonts (Inter)

## Fonctionnalités

- **Thèmes** : Bleu moderne, Émeraude, Coucher de soleil, Mode sombre (Paramètres)
- **Graphiques** : Création et enregistrement en `localStorage`
- **Formulaires** : Validation côté client, upload de fichiers
- **Responsive** : Adapté mobile et desktop
- **Navigation** : Sidebar rétractable, fil d’Ariane, notifications

## Pas de backend

- Les formulaires ne sont pas soumis à un serveur.
- Les données sont stockées uniquement en `localStorage` (graphiques, thème).
- Aucune authentification réelle.
