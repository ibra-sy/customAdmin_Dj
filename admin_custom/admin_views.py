from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Sum
from django.apps import apps
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from .auth_views import SESSION_INTERFACE_KEY, INTERFACE_CLASSIC, INTERFACE_MODERN
from .autodiscover import get_all_models_for_charts, get_all_models_for_grids
from .models import UserPreference


def get_custom_admin_site():
    """
    Fonction helper pour obtenir custom_admin_site sans import circulaire.
    """
    from .admin_site import custom_admin_site
    return custom_admin_site


@require_http_methods(["POST"])
@staff_member_required
def save_user_preference(request):
    """API pour sauvegarder les préférences utilisateur"""
    try:
        import json
        data = json.loads(request.body)
        
        preference, _ = UserPreference.objects.get_or_create(user=request.user)
        
        # Mise à jour du thème moderne
        if 'theme_modern' in data:
            theme = data['theme_modern']
            if theme in [choice[0] for choice in UserPreference.THEME_CHOICES_MODERN]:
                preference.theme_modern = theme
        
        # Mise à jour du thème classique
        if 'theme_classic' in data:
            theme = data['theme_classic']
            if theme in [choice[0] for choice in UserPreference.THEME_CHOICES_CLASSIC]:
                preference.theme_classic = theme
        
        # Mise à jour du collapse de la sidebar
        if 'sidebar_collapsed' in data:
            preference.sidebar_collapsed = data['sidebar_collapsed']
        
        # Mise à jour des items per page
        if 'items_per_page' in data:
            try:
                items = int(data['items_per_page'])
                if 1 <= items <= 500:
                    preference.items_per_page = items
            except (ValueError, TypeError):
                pass
        
        preference.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Préférences sauvegardées avec succès'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    # finish API response for save_user_preference


@staff_member_required
def charts_view(request):
    """Vue pour les graphiques dynamiques - utilise l'auto-découverte"""
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


@staff_member_required
def classic_settings(request):
    """Page Paramètres - interface classique, avec option pour passer à l'interface moderne."""
    custom_admin_site = get_custom_admin_site()
    context = custom_admin_site.each_context(request)
    context.update({
        'title': 'Paramètres',
        'current_interface': request.session.get(SESSION_INTERFACE_KEY, INTERFACE_CLASSIC),
        'switch_to_classic_url': '/admin/switch-interface/?to=classic',
        'switch_to_modern_url': '/admin/switch-interface/?to=modern',
    })
    return render(request, 'admin_custom/settings.html', context)
