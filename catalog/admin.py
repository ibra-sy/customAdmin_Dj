from django.contrib import admin
from .models import Category, Product

# ÉTAPE 1 : La table des enfants (Produits)
class ProductInline(admin.TabularInline): # <--- "Ça doit fonctionner en tables"
    model = Product
    extra = 2  # Affiche 2 lignes vides pour aller vite
    fields = ['name', 'slug', 'sku', 'price', 'stock_quantity', 'is_active'] # Colonnes de la table
    prepopulated_fields = {'slug': ('name',)} # Automatise le slug pour chaque ligne !


# ÉTAPE 2 : La page du Parent (Catégorie)
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # 1er qu'on voit : les champs principaux de la catégorie
    list_display = ['name', 'slug', 'parent', 'is_active', 'created_at']
    search_fields = ['name', 'slug', 'description']
    list_filter = ['is_active', 'parent', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    # Juste en dessous : La liste des produits liés
    inlines = [ProductInline]
    


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'price', 'stock_quantity', 'is_active', 'is_featured', 'created_at']
    search_fields = ['name', 'sku', 'description', 'short_description']
    list_filter = ['category', 'is_active', 'is_featured', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
