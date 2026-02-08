from django.urls import path
from . import views

app_name = 'admin_custom'

urlpatterns = [
    path('api/chart-data/', views.chart_data, name='chart_data'),
    path('api/grid-data/', views.grid_data, name='grid_data'),
    path('api/stats/', views.stats_data, name='stats_data'),
    path('api/model-fields/', views.model_fields, name='model_fields'),  # Nouvelle API pour les champs
]
