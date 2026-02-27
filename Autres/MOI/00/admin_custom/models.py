from django.db import models
from django.contrib.auth.models import User


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
