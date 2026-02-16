# Django Admin Custom - Guide de mise en place

Ce guide explique comment intégrer le panel admin personnalisé dans un autre projet Django **pour que toute l’administration** (tableau de bord, grilles, graphiques, listes et formulaires de modèles) utilise le thème personnalisé, et non uniquement la page d’accueil.

---

## Problème courant : « Le tableau de bord est custom mais les autres pages reviennent à l’admin Django »

**Symptôme :** Après intégration de `admin_custom`, la page d’accueil ou le tableau de bord est bien personnalisé, mais en cliquant sur « Grilles de données », « Graphiques » ou sur un modèle (liste / formulaire), l’interface redevient l’admin Django par défaut (thème vert, formulaire standard).

**Cause :** L’admin personnalisé n’est pas utilisé pour **toutes** les URLs sous `/admin/`. Souvent :

1. Le projet garde `path('admin/', admin.site.urls)` (admin Django par défaut) au lieu de `path('admin/', custom_admin_site.urls)`.
2. Ou `autodiscover_models(custom_admin_site)` n’est pas appelé, donc les modèles ne sont pas enregistrés sur le site personnalisé.

**Règle à retenir :** Il ne doit y avoir **qu’un seul** point d’entrée pour l’admin : `path('admin/', custom_admin_site.urls)`. Il ne faut **pas** utiliser `admin.site.urls` pour le préfixe `admin/`. Suivre exactement l’étape 3 (urls.py) et la checklist ci‑dessous garantit que tout le panel (dashboard, grilles, formulaires) reste personnalisé.

---

## Objectif et résumé

**Objectif :** Une fois la mise en place terminée, **tout le backend** du projet (tous les modèles, listes, formulaires, grilles, graphiques) est accessible dans le panel personnalisé. Le panel fonctionne avec **n'importe quel type de projet** (e-commerce, blog, CRM, etc.) ; l'auto-découverte adapte le menu et les indicateurs aux modèles présents.

**Résumé en 6 étapes :** (1) Copier `admin_custom/` à la racine du projet. (2) Dans `settings.py` : ajouter `'admin_custom'` dans `INSTALLED_APPS` et le middleware `AdminInterfaceRedirectMiddleware`. (3) Dans `urls.py` : mettre `path('admin/', admin.site.urls)` et `path('admin_custom/', include('admin_custom.urls'))` (admin.site est automatiquement remplacé par le panel personnalisé au démarrage). (4) `python manage.py migrate`. (5) En production : `python manage.py collectstatic`. (6) Vérifier en ouvrant `/admin/` que tout le menu, les listes et formulaires sont dans le panel personnalisé.

---

## Le dossier a copier

Le dossier a fournir aux autres developpeurs est :

```
admin_custom/
```

Ce dossier unique contient **tout** ce qu'il faut : le code Python, les templates HTML, les fichiers CSS/JS, et les migrations.

### Contenu du dossier

```
admin_custom/
├── __init__.py                  # Point d'entree du package
├── apps.py                      # Configuration Django AppConfig
├── admin.py                     # ModelAdmin pour DashboardGrid/DashboardChart
├── admin_site.py                # CustomAdminSite (coeur de la customisation)
├── admin_views.py               # Vues interface classique (dashboard, charts, grids)
├── auth_views.py                # Login avec choix d'interface + switch
├── autodiscover.py              # Auto-decouverte de tous les modeles du projet
├── hooks.py                     # Systeme de hooks extensible
├── middleware.py                 # Redirection automatique vers l'interface choisie
├── models.py                    # Modeles DashboardGrid, DashboardChart, UserDashboardConfig
├── modern_model_admin.py        # Mixin pour templates modernes
├── modern_views.py              # Vues interface moderne
├── urls.py                      # Endpoints API (charts, grids, stats)
├── user_admin.py                # Admin User ameliore
├── views.py                     # API REST (chart-data, grid-data, stats)
├── tests.py                     # Tests
│
├── migrations/
│   ├── 0001_initial.py          # Migration initiale (DashboardGrid, DashboardChart)
│   └── 0002_user_dashboard_config.py  # UserDashboardConfig (config indicateurs par utilisateur)
│
├── templates/
│   └── admin_custom/
│       ├── base.html                # Base classique (AdminLTE)
│       ├── base_site.html           # Branding + navigation
│       ├── index.html               # Page d'accueil admin
│       ├── dashboard.html           # Tableau de bord
│       ├── dashboard_customize.html  # Page personnalisation indicateurs du dashboard
│       ├── charts.html              # Page graphiques
│       ├── grids.html               # Page grilles de donnees
│       ├── settings.html            # Page parametres
│       ├── change_list.html         # Liste des objets
│       ├── change_form.html         # Formulaire d'edition (onglets parent/enfants)
│       ├── object_history.html      # Historique d'un objet
│       ├── delete_confirmation.html
│       ├── delete_selected_confirmation.html
│       │
│       ├── auth/
│       │   ├── login_with_interface.html   # Login avec choix classique/moderne
│       │   └── user/
│       │       ├── add_form.html
│       │       └── change_form.html
│       │
│       └── modern/                   # Interface moderne (Bootstrap 5)
│           ├── admin_base.html       # Base moderne pour pages Django
│           ├── base.html             # Base moderne pour pages custom
│           ├── dashboard.html
│           ├── charts.html
│           ├── grids.html
│           ├── settings.html
│           ├── change_list.html
│           ├── change_form.html
│           ├── object_history.html
│           ├── delete_confirmation.html
│           ├── delete_selected_confirmation.html
│           └── auth/user/
│               └── add_form.html
│
└── static/
    └── admin_custom/
        ├── image.png                # Logo (optionnel, fallback automatique)
        │
        ├── css/
        │   ├── design_system.css
        │   ├── professional_admin.css
        │   ├── ux_enhancements.css
        │   ├── themes.css               # Themes interface classique
        │   ├── themes_modern.css        # Themes interface moderne
        │   ├── theme_override.css
        │   ├── theme_icons.css
        │   ├── admin_forms.css
        │   ├── admin_custom.css
        │   ├── modern_admin.css
        │   ├── modern_admin_unified.css
        │   ├── modern_layout.css
        │   ├── modern_components.css
        │   ├── modern_list_form.css
        │   ├── admin_tools_cards.css
        │   ├── business_apps_hover.css
        │   ├── dashboard_cards_colorful.css
        │   ├── dashboard_stats_animation.css
        │   ├── nav_fluid.css
        │   ├── settings_page.css
        │   ├── sidebar_icons_fix.css
        │   ├── tabular_inline_fix.css
        │   ├── button_text_white.css
        │   └── responsive_admin.css     # Responsive mobile/tablette
        │
        └── js/
            ├── admin_custom.js
            └── button_text_white.js
```

---

## Mise en place dans un autre projet Django

### Prerequis

- Python 3.10+
- Django 5.0+ (teste avec Django 5.2)
- Aucun package Python supplementaire requis

Les dependances frontend (Bootstrap, AdminLTE, Font Awesome, Chart.js, DataTables) sont chargees via CDN directement dans les templates.

---

### Etape 1 : Copier le dossier

Copiez le dossier `admin_custom/` a la racine de votre projet Django (au meme niveau que `manage.py`) :

```
mon_projet/
├── manage.py
├── mon_projet/          # <-- dossier de configuration (settings.py, urls.py)
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── mon_app/             # <-- vos apps metier
├── admin_custom/        # <-- COLLER ICI
└── ...
```

---

### Etape 2 : Configurer settings.py

Ouvrez `mon_projet/settings.py` et ajoutez :

#### 2.1 - Ajouter l'app aux INSTALLED_APPS

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Vos apps metier
    'mon_app',

    # Admin personnalise (AJOUTER EN DERNIER)
    'admin_custom',
]
```

#### 2.2 - Ajouter le middleware

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Middleware admin custom (AJOUTER A LA FIN)
    'admin_custom.middleware.AdminInterfaceRedirectMiddleware',
]
```

#### 2.3 - Verifier la configuration des templates

Assurez-vous que `APP_DIRS` est a `True` :

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,                        # <-- IMPORTANT
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',   # <-- REQUIS
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

---

### Etape 3 : Configurer urls.py

**Important :** Pour que **tout** l’admin (tableau de bord, grilles, graphiques, listes et formulaires) soit personnalisé, il faut que **toutes** les URLs sous `/admin/` passent par le site personnalisé. Il ne doit **pas** y avoir de `path('admin/', admin.site.urls)`.

- **À faire :** utiliser uniquement `path('admin/', custom_admin_site.urls)`.
- **À ne pas faire :** garder `path('admin/', admin.site.urls)` ou avoir deux entrées pour le même préfixe `admin/`.

Remplacez le contenu de `mon_projet/urls.py` par :

```python
from django.urls import path, include
from admin_custom.admin_site import custom_admin_site

urlpatterns = [
    path('admin/', custom_admin_site.urls),
    path('admin_custom/', include('admin_custom.urls')),
]
```

**Pourquoi :** Utiliser **explicitement** `custom_admin_site.urls` garantit que les listes affichent toutes les colonnes (`list_display`) et que les formulaires affichent les inlines (ex. articles commandés et factures sous Commande). N'ajoutez pas une deuxieme ligne `path('admin/', ...)`. Si vous l’aviez avant, supprimez‑le.

---

### Checklist : vérifier que tout le panel est personnalisé

Après la mise en place, vérifiez :

| Vérification                                                                                   | Où regarder    |
| ----------------------------------------------------------------------------------------------- | --------------- |
| `admin_custom` est dans `INSTALLED_APPS`                                                    | `settings.py` |
| Le middleware `AdminInterfaceRedirectMiddleware` est dans `MIDDLEWARE`                      | `settings.py` |
| Il y a bien `path('admin/', custom_admin_site.urls)` (import + une seule entrée admin) | `urls.py`     |
| Il y a bien `path('admin_custom/', include('admin_custom.urls'))`      | `urls.py`     |

Si le tableau de bord est personnalisé mais pas les grilles / formulaires : en général c’est que l’admin par défaut est encore utilisé (ligne avec `admin.site.urls`) ou que `autodiscover_models(custom_admin_site)` n’est pas exécuté.

---

### Etape 4 : Appliquer les migrations

```bash
python manage.py makemigrations admin_custom
python manage.py migrate
```

---

### Etape 5 : Collecter les fichiers statiques (production)

```bash
python manage.py collectstatic
```

---

### Etape 6 : Lancer le serveur

```bash
python manage.py runserver
```

Rendez-vous sur `http://127.0.0.1:8000/admin/` pour voir l'interface personnalisee.

---

## Vérification finale : tout le backend est dans le panel

Après la mise en place, vérifiez que **toutes** les données et pages d’admin passent par le panel personnalisé :

| Vérification                     | Comment vérifier                                                                                                                                                                                            |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Page d’accueil admin             | `/admin/` affiche le thème personnalisé (pas le vert Django par défaut).                                                                                                                                |
| Tableau de bord                   | Le lien « Dashboard » ou « Tableau de bord » ouvre la page personnalisée. Si aucun indicateur n’est configuré, un message invite à « Personnaliser l’affichage » (normal pour un nouveau projet). |
| Grilles de données               | Le lien « Grilles » ouvre la page grilles personnalisée.                                                                                                                                                  |
| Graphiques                        | Le lien « Graphiques » ouvre la page graphiques personnalisée.                                                                                                                                            |
| **Listes de modèles**      | Dans le menu (sidebar ou cartes), chaque application et chaque modèle ouvre une**liste** avec le thème personnalisé (pas l’admin Django par défaut).                                              |
| **Formulaires d’édition** | En cliquant sur un objet (ex. « Modifier »), le**formulaire** d’édition utilise le thème personnalisé.                                                                                           |

Si une de ces pages affiche encore l’admin Django par défaut (thème vert, formulaire standard), revenez à l’**Étape 3 (urls.py)** : il ne doit pas y avoir de `path('admin/', admin.site.urls)` et `autodiscover_models(custom_admin_site, ...)` doit bien être appelé.

---

## Fonctionnalites incluses

| Fonctionnalite                       | Description                                                                                                                                                                                                                                                                                                                         |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Double interface**           | Choix entre interface classique (AdminLTE) et moderne (Bootstrap 5)                                                                                                                                                                                                                                                                 |
| **Themes**                     | 7 themes pour le classique, 4 pour le moderne (changement en temps reel)                                                                                                                                                                                                                                                            |
| **Dashboard**                  | Tableau de bord avec statistiques et graphiques dynamiques                                                                                                                                                                                                                                                                          |
| **Personnalisation dashboard** | Par défaut le tableau de bord n’affiche aucun indicateur (projet générique). Chaque utilisateur choisit ses indicateurs via « Personnaliser l’affichage » (modèles de son projet : nombre, somme, moyenne) et les enregistre en base ; suppression de colonnes possible depuis le dashboard ou la page de personnalisation. |
| **Graphiques**                 | Generateur de graphiques (ligne, barre, camembert, etc.) via Chart.js                                                                                                                                                                                                                                                               |
| **Grilles**                    | Grilles de donnees interactives avec tri, recherche et pagination                                                                                                                                                                                                                                                                   |
| **Auto-decouverte**            | Tous les modeles du projet sont automatiquement detectes et enregistres sur le site admin personnalise                                                                                                                                                                                                                              |
| **Onglets inline**             | Les modeles parent/enfants s'affichent en onglets                                                                                                                                                                                                                                                                                   |
| **Responsive**                 | Interface adaptee mobile, tablette et desktop                                                                                                                                                                                                                                                                                       |
| **API REST**                   | Endpoints pour les donnees de graphiques et statistiques                                                                                                                                                                                                                                                                            |

---

## Personnalisation du logo

Le logo affiche dans le header classique est charge depuis :

```
admin_custom/static/admin_custom/image.png
```

Remplacez ce fichier par votre propre logo. Si le fichier n'existe pas, une icone de remplacement s'affiche automatiquement.

---

## Enregistrement des modeles : auto-decouverte vs manuel

L’appel à `autodiscover_models(custom_admin_site, ...)` dans `urls.py` charge tous les `admin.py` du projet et **recopie** les modeles enregistrés sur `admin.site` vers `custom_admin_site`. Vous n’êtes donc **pas obligé** de modifier vos apps existantes qui font déjà `admin.site.register(MonModele, MonModeleAdmin)` : ils apparaîtront quand même dans le panel personnalisé.

Si vous voulez personnaliser l’admin d’un modele et utiliser le mixin moderne, vous pouvez enregistrer explicitement sur `custom_admin_site` :

```python
# mon_app/admin.py
from django.contrib import admin
from admin_custom.admin_site import custom_admin_site
from admin_custom.modern_model_admin import ModernTemplateMixin
from .models import MonModele

class MonModeleAdmin(ModernTemplateMixin, admin.ModelAdmin):
    list_display = ['nom', 'date_creation', 'statut']
    list_filter = ['statut']
    search_fields = ['nom']

# Enregistrer sur le custom_admin_site pour le panel personnalise
custom_admin_site.register(MonModele, MonModeleAdmin)
```

> **Important** : Pour que les listes et formulaires de ce modele utilisent le thème personnalisé, il doit être enregistré sur `custom_admin_site` (via autodiscover ou via `custom_admin_site.register()`). Le mixin `ModernTemplateMixin` permet au modele de s'afficher correctement dans les deux interfaces (classique et moderne).

---

## Systeme de hooks (optionnel)

Pour etendre le comportement sans modifier le code source :

```python
# mon_app/apps.py
from django.apps import AppConfig

class MonAppConfig(AppConfig):
    name = 'mon_app'

    def ready(self):
        from admin_custom.hooks import register_hook

        def mon_hook_dashboard(context):
            context['extra_stats'] = {'clients_actifs': 42}
            return context

        register_hook('dashboard_context', mon_hook_dashboard)
```

---

## Depannage

| Probleme                                                                                                                                  | Solution                                                                                                                                                                                                                                                                                                                                         |
| ----------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Le tableau de bord est personnalisé mais les autres pages (grilles, formulaires, listes) affichent l’admin Django par défaut** | Vous utilisez encore l’admin Django par défaut pour ces URLs. Dans `urls.py` : supprimez toute ligne `path('admin/', admin.site.urls)` et gardez uniquement `path('admin/', custom_admin_site.urls)`. Vérifiez aussi que `autodiscover_models(custom_admin_site, exclude_apps=['admin_custom'])` est bien appelé en haut du fichier. |
| Les styles ne s'affichent pas                                                                                                             | Lancez `python manage.py collectstatic` puis faites Ctrl+Shift+R                                                                                                                                                                                                                                                                               |
| Erreur "No module named admin_custom"                                                                                                     | Verifiez que le dossier `admin_custom/` est a la racine du projet (meme niveau que `manage.py`) et que `admin_custom` est dans `INSTALLED_APPS`                                                                                                                                                                                          |
| Les modeles n'apparaissent pas dans le menu / les listes                                                                                  | Verifiez que `autodiscover_models(custom_admin_site, ...)` est appele dans `urls.py` **avant** la definition de `urlpatterns`                                                                                                                                                                                                        |
| Page blanche apres login                                                                                                                  | Verifiez que le middleware `AdminInterfaceRedirectMiddleware` est dans `MIDDLEWARE`                                                                                                                                                                                                                                                          |
| Erreur de migration                                                                                                                       | Lancez `python manage.py makemigrations admin_custom` puis `python manage.py migrate`                                                                                                                                                                                                                                                        |
| Le tableau de bord affiche « Aucun indicateur configuré »                                                                              | Comportement normal. Cliquez sur « Personnaliser l'affichage » et ajoutez des indicateurs (vos modeles).                                                                                                                                                                                                                                       |
| Aucun modele dans le menu admin                                                                                                           | Apps dans `INSTALLED_APPS`, fichiers `admin.py` avec enregistrement des modeles ; `autodiscover_models(custom_admin_site, ...)` les recopie vers le panel.                                                                                                                                                                                 |
| Erreur `UserDashboardConfigAdmin` ou `UserDashboardConfig`                                                                            | Le guide inclut l’enregistrement de `UserDashboardConfig` ; assurez-vous que votre copie de `admin_custom` contient le modele `UserDashboardConfig` et la migration correspondante, et que `urls.py` enregistre `UserDashboardConfig` comme dans l’exemple Etape 3.                                                                  |
