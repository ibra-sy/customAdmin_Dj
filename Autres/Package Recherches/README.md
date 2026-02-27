🚀 personnalisation-admin-django-IIT
Admin Custom est un package Django réutilisable conçu par le Groupe 4 (IIT - L3 Computer Science). Il transforme l'interface d'administration standard en un tableau de bord moderne, fluide et entièrement personnalisable.

✨ Fonctionnalités
Auto-découverte intelligente : Vos modèles sont détectés et enregistrés automatiquement. Plus besoin de admin.site.register().

7 Thèmes Professionnels :

Default (Gris-bleu), Dark (Sombre), Liquid Glass (Effets de transparence), Nostalgie, Océan, Sunset, et Forêt.

Dashboard Analytique : Visualisation de données intégrée avec des graphiques dynamiques (Chart.js).

Navigation Moderne : Sidebar rétractable et responsive avec icônes FontAwesome 6.

Expérience UX/UI : Design épuré basé sur Bootstrap 5 avec animations fluides.

📦 Installation
Installez le package via pip :

Bash
pip install personnalisation-admin-django-IIT
🛠 Configuration
1. Paramètres (settings.py)
Ajoutez admin_custom à vos INSTALLED_APPS. Attention : Il doit impérativement être placé avant l'administration par défaut de Django.

Python
INSTALLED_APPS = [
    'admin_custom',  # Indispensable pour surcharger l'admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Vos autres applications...
]
Ajoutez le Context Processor pour activer les graphiques du Dashboard :

Python
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                # ...
                'admin_custom.context_processors.admin_dashboard_charts',
            ],
        },
    },
]
2. URLs (urls.py)
Remplacez l'admin par défaut par le custom_admin_site et activez l'auto-découverte :

Python
from django.urls import path, include
from admin_custom.admin_site import custom_admin_site
from admin_custom.autodiscover import autodiscover_models

# Auto-découverte des modèles (exclure les apps internes)
autodiscover_models(custom_admin_site, exclude_apps=['admin_custom', 'auth', 'contenttypes'])

urlpatterns = [
    path('admin/', custom_admin_site.urls),
    path('admin_custom/', include('admin_custom.urls')), # Pour les APIs de stats
]
📊 Utilisation du Dashboard
Une fois installé, rendez-vous dans la section "Admin Charts" de votre interface :

Créez un nouveau graphique.

Indiquez le modèle cible (ex: Order).

Choisissez le type de graphique (Line, Bar, Pie).

Le graphique apparaîtra automatiquement sur votre page d'accueil admin.

🎨 Changer de Thème
Le thème peut être modifié via le dictionnaire CUSTOM_ADMIN_SETTINGS dans votre settings.py :

Python
CUSTOM_ADMIN_SETTINGS = {
    'THEME': 'liquid_glass',  # Options: default, dark, ocean, sunset, forest, nostalgia
    'SITE_TITLE': 'IIT Admin Custom',
    'SITE_HEADER': 'Dashboard Groupe 4',
}
👥 Contributeurs (Groupe 4 - IIT)
Bléou Christ, Sylla Scheickna, Kossonou Marie Joseph, Kouassi Nissi, Yoboué Romuald.

📄 Licence
Ce projet est distribué sous licence MIT. Développé dans le cadre du cours de Méthodologies Agiles à l'Institut Ivoirien de Technologie.