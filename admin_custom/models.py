from django.db import models
from django.contrib.auth.models import User


class UserPreference(models.Model):
    """Préférences utilisateur pour l'interface d'administration"""
    THEME_CHOICES_MODERN = [
        ('bleu-moderne', 'Bleu Moderne'),
        ('emeraude', 'Émeraude'),
        ('coucher-soleil', 'Coucher de soleil'),
        ('sombre', 'Mode sombre'),
    ]
    
    THEME_CHOICES_CLASSIC = [
        ('default', 'Par défaut'),
        ('nostalgie', 'Nostalgie'),
        ('ocean', 'Océan'),
        ('sunset', 'Coucher de soleil'),
        ('forest', 'Forêt'),
        ('dark', 'Sombre'),
        ('liquid-glass', 'Crystal Glass'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_preference')
    theme_modern = models.CharField(
        max_length=50,
        choices=THEME_CHOICES_MODERN,
        default='bleu-moderne',
        help_text='Thème pour l\'interface moderne'
    )
    theme_classic = models.CharField(
        max_length=50,
        choices=THEME_CHOICES_CLASSIC,
        default='default',
        help_text='Thème pour l\'interface classique'
    )
    sidebar_collapsed = models.BooleanField(default=False, help_text='Barre latérale réduite par défaut')
    items_per_page = models.IntegerField(default=25, help_text='Nombre d\'éléments par page')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Préférences de {self.user.username}'

    class Meta:
        verbose_name = "Préférence utilisateur"
        verbose_name_plural = "Préférences utilisateur"

    def get_theme(self, interface_type='modern'):
        """Obtient le thème pour le type d'interface spécifié"""
        if interface_type == 'modern':
            return self.theme_modern
        elif interface_type == 'classic':
            return self.theme_classic
        return self.theme_modern

    def set_theme(self, theme, interface_type='modern'):
        """Définit le thème pour le type d'interface spécifié"""
        if interface_type == 'modern':
            self.theme_modern = theme
        elif interface_type == 'classic':
            self.theme_classic = theme
        self.save()


class DashboardGrid(models.Model):
    """Grille de données configurable pour le dashboard"""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    model_name = models.CharField(max_length=200)  # Nom du modèle Django
    columns = models.JSONField(default=list)  # Liste des colonnes à afficher
    filters = models.JSONField(default=dict, blank=True)  # Filtres à appliquer
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Grille de données"
        verbose_name_plural = "Grilles de données"


class DashboardChart(models.Model):
    """Configuration de graphique pour le dashboard"""
    CHART_TYPES = [
        ('line', 'Courbe'),
        ('bar', 'Histogramme'),
        ('pie', 'Camembert'),
        ('doughnut', 'Donut'),
        ('area', 'Aire'),
    ]
    
    FREQUENCY_CHOICES = [
        ('day', 'Jour'),
        ('week', 'Semaine'),
        ('month', 'Mois'),
        ('quarter', 'Trimestre'),
        ('year', 'Année'),
    ]

    name = models.CharField(max_length=200, unique=True)
    chart_type = models.CharField(max_length=20, choices=CHART_TYPES, default='line')
    model_name = models.CharField(max_length=200)  # Nom du modèle principal
    field_name = models.CharField(max_length=200)  # Champ à analyser
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='month')
    operation = models.CharField(max_length=20, default='sum', blank=True)  # sum, avg, count, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_chart_type_display()})"

    class Meta:
        verbose_name = "Graphique"
        verbose_name_plural = "Graphiques"
