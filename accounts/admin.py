from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


# ÉTAPE 1 : On crée la table pour le profil
class UserProfileInline(admin.TabularInline): # <--- Toujours le mode Table (Consigne M. Sédrick)
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Informations de Profil'
    # Pour un profil unique (OneToOne), extra=0 suffit
    extra = 1


# ÉTAPE 2 : On redéfinit l'interface de l'Utilisateur
class UserAdmin(BaseUserAdmin):
    # On injecte le tableau de profil en bas de la page User
    inlines = [UserProfileInline]

# ÉTAPE 3 : On désenregistre l'admin par défaut et on met le nôtre
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'country', 'is_premium', 'newsletter_subscribed', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone', 'city', 'country']
    list_filter = ['is_premium', 'newsletter_subscribed', 'country', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
