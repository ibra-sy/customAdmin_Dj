from django.apps import AppConfig


class AdminCustomConfig(AppConfig):
    """
    Configuration de l'application admin_custom.
    
    Cette app peut être utilisée comme package réutilisable.
    Elle auto-découvre les modèles si AUTO_DISCOVER est activé dans settings.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_custom'
    verbose_name = 'Django Admin Custom'
    
    def ready(self):
        """
        Appelé quand l'app Django est prête.
        Ici, on peut activer l'auto-découverte si configuré.
        
        Pour activer l'auto-découverte dans un projet :
        
        # settings.py
        ADMIN_CUSTOM = {
            'AUTO_DISCOVER': True,
        }
        """
        from django.conf import settings
        
        # Vérifier si l'auto-découverte est activée
        admin_custom_config = getattr(settings, 'ADMIN_CUSTOM', {})
        auto_discover = admin_custom_config.get('AUTO_DISCOVER', False)
        
        if auto_discover:
            # Importer ici pour éviter les imports circulaires
            from .autodiscover import autodiscover_models
            from .admin_site import custom_admin_site
            
            # Auto-découvrir et enregistrer les modèles
            try:
                autodiscover_models(custom_admin_site)
            except Exception as e:
                # Logger l'erreur mais ne pas bloquer le démarrage
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Erreur lors de l'auto-découverte des modèles: {e}")
