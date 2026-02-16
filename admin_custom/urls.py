from django.urls import path
from . import views

app_name = 'admin_custom'

urlpatterns = [
    path('api/chart-data/', views.chart_data, name='chart_data'),
    path('api/grid-data/', views.grid_data, name='grid_data'),
    path('api/stats/', views.stats_data, name='stats_data'),
    path('api/orders/', views.order_create, name='order_create'),
    path('api/clients/', views.client_create, name='client_create'),
    path('api/model-fields/', views.model_fields, name='model_fields'),
]
