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
    autodiscover_modules('admin', register_to=admin.site)
    
    # ÉTAPE 2 : Ré-enregistrer tous les modèles sur custom_admin_site avec leur classe ModelAdmin.
    # Obligatoire pour que les inlines (ex. OrderItem, Invoice sous Order) soient bien pris en compte
    # quand on partage le dossier admin_custom : on obtient des instances fraîches avec inlines.
    registered_count = 0
    registry_items = list(admin.site._registry.items())
    for model, admin_instance in registry_items:
        app_label = model._meta.app_label
        if app_label in exclude_apps or app_label == 'admin_custom':
            continue
        model_name = f"{app_label}.{model._meta.model_name}"
        if model_name in exclude_models or model.__name__ in exclude_models:
            continue
        if model._meta.abstract:
            continue
        if model._meta.proxy and not admin_custom_config.get('INCLUDE_PROXY', False):
            continue
        try:
            if model in custom_admin_site._registry:
                custom_admin_site.unregister(model)
            admin_class = admin_instance.__class__
            custom_admin_site.register(model, admin_class)
            registered_count += 1
        except admin.sites.AlreadyRegistered:
            pass
        except Exception:
            try:
                if model in custom_admin_site._registry:
                    custom_admin_site.unregister(model)
                custom_admin_site.register(model)
                registered_count += 1
            except Exception:
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
    Retourne tous les modèles disponibles pour les grilles, avec la liste
    de tous les champs (concrets, non relation inversée) pour afficher toute la grille.
    """
    models_list = []
    
    for app_config in apps.get_app_configs():
        if app_config.name.startswith('django.contrib'):
            continue
        
        for model in app_config.get_models():
            if model._meta.abstract or model._meta.proxy:
                continue
            
            # Tous les champs du modèle (id, nom, slug, description, catégorie, prix, stock, etc.)
            fields = [f.name for f in model._meta.fields]
            
            models_list.append({
                'name': model.__name__,
                'label': model._meta.verbose_name.title(),
                'app': model._meta.app_label,
                'fields': fields,
            })
    
    return models_list
