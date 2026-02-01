from django.contrib import admin
from .models import DashboardGrid, DashboardChart


class DashboardGridAdmin(admin.ModelAdmin):
    """
    Admin pour DashboardGrid.
    Note: Le modèle doit être enregistré manuellement avec custom_admin_site
    dans le fichier urls.py du projet, pas via @admin.register.
    """
    list_display = ['name', 'model_name', 'created_at']
    search_fields = ['name', 'description', 'model_name']
    list_filter = ['created_at']


class DashboardChartAdmin(admin.ModelAdmin):
    """
    Admin pour DashboardChart.
    Note: Le modèle doit être enregistré manuellement avec custom_admin_site
    dans le fichier urls.py du projet, pas via @admin.register.
    """
    list_display = ['name', 'chart_type', 'model_name', 'field_name', 'frequency', 'created_at']
    search_fields = ['name', 'model_name', 'field_name']
    list_filter = ['chart_type', 'frequency', 'created_at']
