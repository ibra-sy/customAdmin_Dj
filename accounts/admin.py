from django.contrib import admin
from admin_custom.modern_model_admin import ModernTemplateMixin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(ModernTemplateMixin, admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'country', 'is_premium', 'newsletter_subscribed', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone', 'city', 'country']
    list_filter = ['is_premium', 'newsletter_subscribed', 'country', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
