from django.contrib import admin
from .models import DashboardGrid, DashboardChart, UserPreference
from .modern_model_admin import ModernTemplateMixin


class UserPreferenceAdmin(ModernTemplateMixin, admin.ModelAdmin):
    """Admin pour UserPreference"""
    list_display = ['user', 'theme_modern', 'theme_classic', 'sidebar_collapsed', 'updated_at']
    search_fields = ['user__username', 'user__email']
    list_filter = ['theme_modern', 'theme_classic', 'sidebar_collapsed', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Thèmes', {
            'fields': ('theme_modern', 'theme_classic'),
            'description': 'Choisissez les thèmes pour chaque interface.'
        }),
        ('Paramètres d\'affichage', {
            'fields': ('sidebar_collapsed', 'items_per_page'),
            'description': 'Paramètres d\'affichage personnalisés.'
        }),
        ('Informations', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Les préférences sont créées automatiquement
        return False

class DashboardGridAdmin(ModernTemplateMixin, admin.ModelAdmin):
    """
    Admin pour DashboardGrid.
    Note: Le modèle doit être enregistré manuellement avec custom_admin_site
    dans le fichier urls.py du projet, pas via @admin.register.
    """
    list_display = ['name', 'model_name', 'created_at']
    search_fields = ['name', 'description', 'model_name']
    list_filter = ['created_at']


class DashboardChartAdmin(ModernTemplateMixin, admin.ModelAdmin):
    """
    Admin pour DashboardChart.
    Note: Le modèle doit être enregistré manuellement avec custom_admin_site
    dans le fichier urls.py du projet, pas via @admin.register.
    """
    list_display = ['name', 'chart_type', 'model_name', 'field_name', 'frequency', 'created_at']
    search_fields = ['name', 'model_name', 'field_name']
    list_filter = ['chart_type', 'frequency', 'created_at']
