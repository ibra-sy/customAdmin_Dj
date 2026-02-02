from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'is_active', 'created_at']
    search_fields = ['name', 'slug', 'description']
    list_filter = ['is_active', 'parent', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'price', 'stock_quantity', 'is_active', 'is_featured', 'created_at']
    search_fields = ['name', 'sku', 'description', 'short_description']
    list_filter = ['category', 'is_active', 'is_featured', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
