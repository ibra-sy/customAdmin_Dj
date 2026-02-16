from django.apps import AppConfig
from django.contrib import admin


def _reregister_inline_admins(custom_admin_site):
    """
    Ré-enregistre chaque modèle dont le ModelAdmin définit des inlines,
    pour garantir que les inlines (ex. OrderItem, Invoice sous Order) s'affichent.
    """
    for model, admin_instance in list(custom_admin_site._registry.items()):
        if not getattr(admin_instance, 'inlines', None):
            continue
        admin_cls = admin_instance.__class__
        try:
            custom_admin_site.unregister(model)
            custom_admin_site.register(model, admin_cls)
        except Exception:
            pass


class AdminCustomConfig(AppConfig):
    """
    Configuration de l'application admin_custom.
    
    Au chargement, remplace le site admin Django par défaut (admin.site)
    par notre CustomAdminSite. Ainsi, tout projet qui utilise
    path('admin/', admin.site.urls) affiche automatiquement le panel personnalisé
    sur toutes les pages (dashboard, listes, formulaires, grilles).
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_custom'
    verbose_name = 'Django Admin Custom'
    
    def ready(self):
        self._install_custom_admin_site()
    
    def _install_custom_admin_site(self):
        """
        Remplace admin.site par notre CustomAdminSite et enregistre tous les
        modèles du projet dessus. À appeler une seule fois au démarrage.
        """
        import django.contrib.admin
        from django.conf import settings
        
        from .admin_site import custom_admin_site
        
        # 1) Remplacer le site admin par défaut : tout code qui utilise
        #    admin.site (y compris path('admin/', admin.site.urls)) utilisera
        #    notre panel personnalisé.
        django.contrib.admin.site = custom_admin_site
        
        # 2) Charger tous les admin.py et enregistrer les modèles sur notre site
        try:
            from .autodiscover import autodiscover_models
            autodiscover_models(custom_admin_site, exclude_apps=['admin_custom'])
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(
                "admin_custom: erreur autodiscover_models: %s", e
            )
        
        # 2b) Ré-enregistrer les ModelAdmin qui ont des inlines pour garantir l'affichage
        _reregister_inline_admins(custom_admin_site)
        
        # 2c) Si l'app sales existe, forcer Order et Invoice avec leurs ModelAdmin (inlines enfants)
        try:
            from django.apps import apps as django_apps
            if django_apps.is_installed('sales'):
                from sales.models import Order, Invoice
                from sales.admin import OrderAdmin, InvoiceAdmin
                for model, admin_cls in [(Order, OrderAdmin), (Invoice, InvoiceAdmin)]:
                    if model in custom_admin_site._registry:
                        custom_admin_site.unregister(model)
                    custom_admin_site.register(model, admin_cls)
        except ImportError:
            pass
        
        # 3) Remplacer User, Group, Permission par nos classes d'admin
        from django.contrib.auth.models import User, Group, Permission
        from django.contrib.auth.admin import GroupAdmin
        from .user_admin import CustomUserAdmin
        from .modern_model_admin import ModernTemplateMixin
        
        for model in (User, Group, Permission):
            if model in custom_admin_site._registry:
                custom_admin_site.unregister(model)
        
        custom_admin_site.register(User, CustomUserAdmin)
        custom_admin_site.register(Group, GroupAdmin)
        custom_admin_site.register(Permission, type(
            'PermissionAdmin', (ModernTemplateMixin, admin.ModelAdmin), {
                'list_display': ['name', 'content_type', 'codename'],
                'list_filter': ['content_type'],
                'search_fields': ['name', 'codename'],
            }
        ))
        
        # 4) Enregistrer les modèles admin_custom (grilles, graphiques, config dashboard)
        from .models import DashboardGrid, DashboardChart, UserDashboardConfig
        from .admin import DashboardGridAdmin, DashboardChartAdmin, UserDashboardConfigAdmin
        
        for model, admin_class in (
            (DashboardGrid, DashboardGridAdmin),
            (DashboardChart, DashboardChartAdmin),
            (UserDashboardConfig, UserDashboardConfigAdmin),
        ):
            if model in custom_admin_site._registry:
                custom_admin_site.unregister(model)
            custom_admin_site.register(model, admin_class)
