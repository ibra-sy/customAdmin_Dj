"""
URL configuration for sandbox project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from admin_custom.admin_site import custom_admin_site
from admin_custom.autodiscover import autodiscover_models

# Auto-découvrir et enregistrer tous les modèles avec le CustomAdminSite
# Cela permet de détecter automatiquement tous les modèles du projet
# Exclure admin_custom de l'auto-découverte pour éviter les conflits
# Note: django.contrib.auth est exclu par défaut, on l'ajoute manuellement
autodiscover_models(custom_admin_site, exclude_apps=['admin_custom'])

# Enregistrer explicitement User et Group avec leurs classes d'admin personnalisées
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import GroupAdmin
from admin_custom.user_admin import CustomUserAdmin

# Vérifier et désenregistrer si déjà enregistré
if User in custom_admin_site._registry:
    custom_admin_site.unregister(User)
if Group in custom_admin_site._registry:
    custom_admin_site.unregister(Group)

# Enregistrer avec les classes d'admin personnalisées
custom_admin_site.register(User, CustomUserAdmin)
custom_admin_site.register(Group, GroupAdmin)

# Enregistrer explicitement les modèles admin_custom avec leurs classes d'admin personnalisées
from admin_custom.models import DashboardGrid, DashboardChart
from admin_custom.admin import DashboardGridAdmin, DashboardChartAdmin

# Vérifier et désenregistrer si déjà enregistré (au cas où)
if DashboardGrid in custom_admin_site._registry:
    custom_admin_site.unregister(DashboardGrid)
if DashboardChart in custom_admin_site._registry:
    custom_admin_site.unregister(DashboardChart)

# Enregistrer avec les classes d'admin personnalisées
custom_admin_site.register(DashboardGrid, DashboardGridAdmin)
custom_admin_site.register(DashboardChart, DashboardChartAdmin)

# Personnaliser l'en-tête du site
custom_admin_site.site_header = "Administration Django Personnalisée"
custom_admin_site.site_title = "Admin Personnalisé"
custom_admin_site.index_title = "Tableau de bord"

urlpatterns = [
    path('admin/', custom_admin_site.urls),  # Utiliser le CustomAdminSite
    path('admin_custom/', include('admin_custom.urls')),  # APIs REST
]
