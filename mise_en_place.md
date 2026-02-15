# Django Admin Custom - Guide de mise en place

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
├── models.py                    # Modeles DashboardGrid et DashboardChart
├── modern_model_admin.py        # Mixin pour templates modernes
├── modern_views.py              # Vues interface moderne
├── urls.py                      # Endpoints API (charts, grids, stats)
├── user_admin.py                # Admin User ameliore
├── views.py                     # API REST (chart-data, grid-data, stats)
├── tests.py                     # Tests
│
├── migrations/
│   └── 0001_initial.py          # Migration initiale
│
├── templates/
│   └── admin_custom/
│       ├── base.html                # Base classique (AdminLTE)
│       ├── base_site.html           # Branding + navigation
│       ├── index.html               # Page d'accueil admin
│       ├── dashboard.html           # Tableau de bord
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

Remplacez le contenu de `mon_projet/urls.py` :

```python
from django.urls import path, include
from django.contrib import admin
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.admin import GroupAdmin

from admin_custom.admin_site import custom_admin_site
from admin_custom.autodiscover import autodiscover_models
from admin_custom.user_admin import CustomUserAdmin
from admin_custom.modern_model_admin import ModernTemplateMixin
from admin_custom.models import DashboardGrid, DashboardChart
from admin_custom.admin import DashboardGridAdmin, DashboardChartAdmin

# ─── 1. Auto-decouvrir tous les modeles du projet ───
autodiscover_models(custom_admin_site, exclude_apps=['admin_custom'])

# ─── 2. Enregistrer les modeles auth manuellement ───
for model in [User, Group, Permission]:
    if model in custom_admin_site._registry:
        custom_admin_site.unregister(model)

custom_admin_site.register(User, CustomUserAdmin)
custom_admin_site.register(Group, GroupAdmin)
custom_admin_site.register(Permission, type('PermissionAdmin', (
    ModernTemplateMixin, admin.ModelAdmin
), {
    'list_display': ['name', 'content_type', 'codename'],
    'list_filter': ['content_type'],
    'search_fields': ['name', 'codename'],
}))

# ─── 3. Enregistrer les modeles admin_custom ───
for model, admin_class in [(DashboardGrid, DashboardGridAdmin),
                            (DashboardChart, DashboardChartAdmin)]:
    if model in custom_admin_site._registry:
        custom_admin_site.unregister(model)
    custom_admin_site.register(model, admin_class)

# ─── 4. Personnaliser les titres ───
custom_admin_site.site_header = "Mon Administration"      # Titre dans le header
custom_admin_site.site_title  = "Admin"                    # Titre de l'onglet
custom_admin_site.index_title = "Tableau de bord"          # Titre de la page d'accueil

# ─── 5. URLs ───
urlpatterns = [
    path('admin/', custom_admin_site.urls),                # Interface admin
    path('admin_custom/', include('admin_custom.urls')),   # API REST (graphiques, grilles)

    # Ajoutez vos autres URLs ici :
    # path('', include('mon_app.urls')),
]
```

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

## Fonctionnalites incluses

| Fonctionnalite | Description |
|---|---|
| **Double interface** | Choix entre interface classique (AdminLTE) et moderne (Bootstrap 5) |
| **Themes** | 7 themes pour le classique, 4 pour le moderne (changement en temps reel) |
| **Dashboard** | Tableau de bord avec statistiques et graphiques dynamiques |
| **Graphiques** | Generateur de graphiques (ligne, barre, camembert, etc.) via Chart.js |
| **Grilles** | Grilles de donnees interactives avec tri, recherche et pagination |
| **Auto-decouverte** | Tous les modeles du projet sont automatiquement detectes et enregistres |
| **Onglets inline** | Les modeles parent/enfants s'affichent en onglets |
| **Responsive** | Interface adaptee mobile, tablette et desktop |
| **API REST** | Endpoints pour les donnees de graphiques et statistiques |

---

## Personnalisation du logo

Le logo affiche dans le header classique est charge depuis :

```
admin_custom/static/admin_custom/image.png
```

Remplacez ce fichier par votre propre logo. Si le fichier n'existe pas, une icone de remplacement s'affiche automatiquement.

---

## Enregistrement manuel d'un modele (optionnel)

Si vous voulez personnaliser l'admin d'un modele specifique au lieu de l'auto-decouverte :

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

# Enregistrer sur le custom_admin_site (PAS admin.site)
custom_admin_site.register(MonModele, MonModeleAdmin)
```

> **Important** : Utilisez `custom_admin_site.register()` et non `admin.site.register()`.
> Le mixin `ModernTemplateMixin` permet au modele de s'afficher correctement dans les deux interfaces.

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

| Probleme | Solution |
|---|---|
| Les styles ne s'affichent pas | Lancez `python manage.py collectstatic` puis faites Ctrl+Shift+R |
| Erreur "No module named admin_custom" | Verifiez que le dossier `admin_custom/` est a la racine du projet (meme niveau que `manage.py`) |
| Les modeles n'apparaissent pas | Verifiez que `autodiscover_models()` est appele dans `urls.py` |
| Page blanche apres login | Verifiez que le middleware `AdminInterfaceRedirectMiddleware` est dans `MIDDLEWARE` |
| Erreur de migration | Lancez `python manage.py makemigrations admin_custom` puis `python manage.py migrate` |
