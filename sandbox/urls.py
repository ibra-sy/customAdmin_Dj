"""
URL configuration for sandbox project.

On utilise explicitement custom_admin_site pour que les listes (list_display)
et les inlines (articles commandés, factures) s'affichent correctement.
"""
from django.urls import path, include

# Import explicite du site admin personnalisé (enregistrements + inlines)
from admin_custom.admin_site import custom_admin_site

urlpatterns = [
    # Tout l'admin : listes avec toutes les colonnes, formulaires avec inlines
    path('admin/', custom_admin_site.urls),
    # API REST (graphiques, grilles, config dashboard)
    path('admin_custom/', include('admin_custom.urls')),
]
