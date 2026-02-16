"""
Auto-découverte des modèles Django pour enregistrement automatique

Ce module permet de détecter automatiquement tous les modèles Django
d'un projet et de les enregistrer avec le CustomAdminSite, en détectant
automatiquement les classes ModelAdmin définies dans les fichiers admin.py.
"""
from django.apps import apps
from django.contrib import admin
from django.conf import settings
from django.utils.module_loading import autodiscover_modules


def autodiscover_models(custom_admin_site=None, exclude_apps=None, exclude_models=None):
    """
    Découvre automatiquement tous les modèles Django du projet
    et les enregistre avec le CustomAdminSite.
    
    Cette fonction fonctionne en deux étapes :
    1. Elle charge tous les fichiers admin.py des apps installées
    2. Elle détecte les modèles enregistrés avec @admin.register() dans admin.site
    3. Elle les ré-enregistre automatiquement dans custom_admin_site
    
    Args:
        custom_admin_site: Instance de CustomAdminSite (optionnel)
        exclude_apps: Liste d'apps à exclure (optionnel)
        exclude_models: Liste de modèles à exclure (optionnel)
    
    Returns:
        Tuple (custom_admin_site, registered_count)
    """
    if custom_admin_site is None:
        # Import lazy pour éviter les imports circulaires
        from .admin_site import CustomAdminSite
        custom_admin_site = CustomAdminSite()
    
    # Configuration depuis settings (pour package futur)
    admin_custom_config = getattr(settings, 'ADMIN_CUSTOM', {})
    exclude_apps = exclude_apps or admin_custom_config.get('EXCLUDE_APPS', [])
    exclude_models = exclude_models or admin_custom_config.get('EXCLUDE_MODELS', [])
    
    # Apps Django internes à exclure par défaut
    default_exclude_apps = [
        'django.contrib.admin',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
    ]
    exclude_apps = list(exclude_apps) if exclude_apps else []
    exclude_apps.extend(default_exclude_apps)
    
    # ÉTAPE 1 : Charger tous les fichiers admin.py pour déclencher les @admin.register()
    # Cela permet de détecter toutes les classes ModelAdmin définies
    autodiscover_modules('admin', register_to=admin.site)
    
    # ÉTAPE 2 : Parcourir tous les modèles enregistrés dans admin.site
    # et les ré-enregistrer dans custom_admin_site
    registered_count = 0
    
    for model, admin_class in admin.site._registry.items():
        app_label = model._meta.app_label
        
        # Ignorer les apps exclues
        if app_label in exclude_apps:
            continue
        
        # Ignorer admin_custom lui-même
        if app_label == 'admin_custom':
            continue
        
        # Ignorer les modèles exclus
        model_name = f"{app_label}.{model._meta.model_name}"
        if model_name in exclude_models or model.__name__ in exclude_models:
            continue
        
        # Ignorer les modèles abstraits
        if model._meta.abstract:
            continue
        
        # Ignorer les modèles proxy (sauf si explicitement demandé)
        if model._meta.proxy and not admin_custom_config.get('INCLUDE_PROXY', False):
            continue
        
        # Ré-enregistrer dans custom_admin_site avec la même classe d'admin
        try:
            # Désenregistrer si déjà enregistré (au cas où)
            if model in custom_admin_site._registry:
                custom_admin_site.unregister(model)
            
            # Créer une nouvelle instance de la classe d'admin pour custom_admin_site
            # On utilise la classe (admin_class.__class__) et on crée une nouvelle instance
            admin_class_type = admin_class.__class__
            
            # Enregistrer avec la classe d'admin détectée
            custom_admin_site.register(model, admin_class_type)
            registered_count += 1
        except admin.sites.AlreadyRegistered:
            # Déjà enregistré, ignorer
            pass
        except Exception as e:
            # En cas d'erreur, essayer avec un ModelAdmin par défaut
            try:
                if model in custom_admin_site._registry:
                    custom_admin_site.unregister(model)
                custom_admin_site.register(model)
                registered_count += 1
            except Exception:
                # Ignorer les erreurs silencieusement
                pass
    
    # ÉTAPE 3 : Enregistrer les modèles non encore enregistrés
    # (ceux qui n'ont pas de fichier admin.py)
    for app_config in apps.get_app_configs():
        app_name = app_config.name
        
        # Ignorer les apps exclues
        if app_name in exclude_apps:
            continue
        
        # Ignorer admin_custom lui-même
        if app_name == 'admin_custom':
            continue
        
        # Récupérer tous les modèles de l'app
        for model in app_config.get_models():
            # Ignorer si déjà enregistré
            if model in custom_admin_site._registry:
                continue
            
            # Ignorer les modèles exclus
            model_name = f"{model._meta.app_label}.{model._meta.model_name}"
            if model_name in exclude_models or model.__name__ in exclude_models:
                continue
            
            # Ignorer les modèles abstraits
            if model._meta.abstract:
                continue
            
            # Ignorer les modèles proxy (sauf si explicitement demandé)
            if model._meta.proxy and not admin_custom_config.get('INCLUDE_PROXY', False):
                continue
            
            # Enregistrer avec un ModelAdmin par défaut
            try:
                custom_admin_site.register(model)
                registered_count += 1
            except admin.sites.AlreadyRegistered:
                # Déjà enregistré, ignorer
                pass
            except Exception:
                # Ignorer les erreurs silencieusement
                pass
    
    return custom_admin_site, registered_count


def get_all_models_for_charts():
    """
    Retourne tous les modèles disponibles pour les graphiques.
    Utile pour l'auto-complétion dans l'interface.
    """
    models_list = []
    
    for app_config in apps.get_app_configs():
        if app_config.name.startswith('django.contrib'):
            continue
        
        for model in app_config.get_models():
            if model._meta.abstract or model._meta.proxy:
                continue
            
            # Détecter les champs numériques
            numeric_fields = []
            for field in model._meta.get_fields():
                if hasattr(field, 'name'):
                    try:
                        field_obj = model._meta.get_field(field.name)
                        if hasattr(field_obj, 'get_internal_type'):
                            field_type = field_obj.get_internal_type()
                            if field_type in ['DecimalField', 'FloatField', 'IntegerField', 
                                             'PositiveIntegerField', 'BigIntegerField', 'SmallIntegerField']:
                                numeric_fields.append(field.name)
                    except Exception:
                        # Ignorer les champs qui ne peuvent pas être inspectés
                        continue
            
            if numeric_fields:
                models_list.append({
                    'name': model.__name__,
                    'label': model._meta.verbose_name.title(),
                    'app': model._meta.app_label,
                    'fields': numeric_fields,
                })
    
    return models_list


def get_all_models_for_grids():
    """
    Retourne tous les modèles disponibles pour les grilles.
    """
    models_list = []
    
    for app_config in apps.get_app_configs():
        if app_config.name.startswith('django.contrib'):
            continue
        
        for model in app_config.get_models():
            if model._meta.abstract or model._meta.proxy:
                continue
            
            models_list.append({
                'name': model.__name__,
                'label': model._meta.verbose_name.title(),
                'app': model._meta.app_label,
            })
    
    return models_list
