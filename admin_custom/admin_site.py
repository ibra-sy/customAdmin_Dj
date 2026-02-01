"""
CustomAdminSite - Site d'administration Django personnalisé et réutilisable

Ce module définit un AdminSite personnalisé qui peut être utilisé
comme package réutilisable dans d'autres projets Django.
"""
from django.contrib import admin
from django.urls import path
from django.shortcuts import render

from . import admin_views as custom_views


class CustomAdminSite(admin.AdminSite):
    """
    Site d'administration personnalisé avec fonctionnalités avancées :
    - Graphiques dynamiques
    - Grilles de données configurables
    - Dashboard personnalisé
    - Design moderne avec thèmes
    """
    site_header = "Administration Django Personnalisée"
    site_title = "Admin Personnalisé"
    index_title = "Tableau de bord"
    
    def get_urls(self):
        """
        Ajoute les URLs personnalisées (charts, grids, dashboard)
        aux URLs standard de l'admin Django
        """
        urls = super().get_urls()
        
        # URLs personnalisées
        custom_urls = [
            path('charts/', self.admin_view(custom_views.charts_view), name='admin_charts'),
            path('grids/', self.admin_view(custom_views.grids_view), name='admin_grids'),
            path('dashboard/', self.admin_view(custom_views.dashboard_view), name='admin_dashboard'),
        ]
        
        # Les URLs personnalisées sont ajoutées AVANT les URLs standard
        # pour éviter les conflits
        return custom_urls + urls
    
    def get_app_list(self, request, app_label=None):
        """
        Retourne la liste des applications, en excluant admin_custom
        pour qu'elle n'apparaisse pas comme une application normale.
        """
        app_list = super().get_app_list(request, app_label)
        
        # Filtrer admin_custom de la liste des applications
        filtered_app_list = [
            app for app in app_list 
            if app.get('app_label') != 'admin_custom'
        ]
        
        return filtered_app_list


# Instance globale par défaut
# Dans un package, cette instance sera remplacée par autodiscover
custom_admin_site = CustomAdminSite()
