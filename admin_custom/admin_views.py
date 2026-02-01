from django.contrib import admin
from django.shortcuts import render
from django.db.models import Sum
from django.apps import apps

from .autodiscover import get_all_models_for_charts, get_all_models_for_grids


def get_custom_admin_site():
    """
    Fonction helper pour obtenir custom_admin_site sans import circulaire.
    """
    from .admin_site import custom_admin_site
    return custom_admin_site


def charts_view(request):
    """Vue pour les graphiques - utilise l'auto-découverte"""
    custom_admin_site = get_custom_admin_site()
    context = custom_admin_site.each_context(request)
    
    # Utiliser l'auto-découverte pour obtenir les modèles disponibles
    models = get_all_models_for_charts()
    
    context.update({
        'title': 'Graphiques Dynamiques',
        'models': models,
    })
    return render(request, 'admin_custom/charts.html', context)


def grids_view(request):
    """Vue pour les grilles - utilise l'auto-découverte"""
    custom_admin_site = get_custom_admin_site()
    context = custom_admin_site.each_context(request)
    
    # Utiliser l'auto-découverte pour obtenir les modèles disponibles
    models = get_all_models_for_grids()
    
    context.update({
        'title': 'Grilles de Données',
        'models': models,
    })
    return render(request, 'admin_custom/grids.html', context)


def dashboard_view(request):
    """Vue dashboard principal - utilise l'auto-découverte"""
    from django.db.models import Sum, Count
    
    # Détecter automatiquement les modèles avec des montants
    stats = {}
    total_revenue = 0
    
    # Parcourir tous les modèles pour trouver ceux avec total_amount ou amount
    for app_config in apps.get_app_configs():
        # Ignorer les apps Django internes
        if app_config.name.startswith('django.contrib'):
            continue
        
        for model in app_config.get_models():
            if model._meta.abstract or model._meta.proxy:
                continue
            
            model_name = model.__name__.lower()
            
            # Chercher des champs de montant
            if hasattr(model, 'total_amount'):
                count = model.objects.count()
                revenue = float(model.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0)
                stats[f'total_{model_name}'] = count
                total_revenue += revenue
            elif hasattr(model, 'amount'):
                count = model.objects.count()
                revenue = float(model.objects.aggregate(Sum('amount'))['amount__sum'] or 0)
                stats[f'total_{model_name}'] = count
                total_revenue += revenue
            else:
                # Compter simplement le nombre d'objets
                count = model.objects.count()
                if count > 0:  # Ne garder que les modèles avec des données
                    stats[f'total_{model_name}'] = count
    
    stats['total_revenue'] = total_revenue
    
    custom_admin_site = get_custom_admin_site()
    context = custom_admin_site.each_context(request)
    context.update({
        'title': 'Tableau de bord',
        'stats': stats,
    })
    return render(request, 'admin_custom/dashboard.html', context)
