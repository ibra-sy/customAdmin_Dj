# Personnalisation des Inlines dans l'Admin Django

Ce document décrit comment les formulaires inline sont gérés et personnalisés dans le projet admin_custom.

---

## 1. Vue d'ensemble

Les **inlines** permettent d'éditer des modèles liés (relation ForeignKey ou OneToOne) directement depuis la page d'édition du modèle parent. Par exemple : éditer les articles d'une commande (OrderItem) depuis la page de la commande (Order).

### Types d'inlines Django

| Type | Description | Rendu |
|------|-------------|-------|
| **TabularInline** | Affichage en tableau (une ligne par enregistrement) | Table HTML |
| **StackedInline** | Affichage empilé (un bloc par enregistrement) | Blocs verticaux |

---

## 2. Configuration Python

### 2.1 Déclaration dans l'admin

```python
from django.contrib import admin

# Inline Tabulaire (tableau)
class OrderItemInline(admin.TabularInline):
    model = OrderItem           # Modèle lié
    extra = 1                   # Lignes vides affichées par défaut
    readonly_fields = ['created_at']
    # Autres options : fields, exclude, max_num, min_num, can_delete...

# Inline Empilé (blocs)
class InvoiceInline(admin.StackedInline):
    model = Invoice
    extra = 0
    readonly_fields = ['created_at', 'updated_at']

# Liaison au ModelAdmin parent
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline, InvoiceInline]
```

### 2.2 Options principales des InlineModelAdmin

| Option | Type | Description |
|--------|------|-------------|
| `model` | Model | Modèle lié (obligatoire) |
| `extra` | int | Nombre de formulaires vides à afficher (défaut: 3) |
| `max_num` | int | Nombre maximum de formulaires (None = illimité) |
| `min_num` | int | Nombre minimum de formulaires |
| `fields` | list | Champs à afficher (si non précisé = tous) |
| `exclude` | list | Champs à exclure |
| `readonly_fields` | list | Champs en lecture seule |
| `can_delete` | bool | Autoriser la suppression (défaut: True) |
| `show_change_link` | bool | Afficher un lien vers la page d'édition de l'objet |
| `verbose_name` | str | Nom singulier affiché |
| `verbose_name_plural` | str | Nom pluriel affiché |

### 2.3 Exemple complet avec personnalisation

```python
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    max_num = 20
    can_delete = True
    show_change_link = True
    verbose_name = "Article"
    verbose_name_plural = "Articles de la commande"
    readonly_fields = ['created_at', 'subtotal']  # subtotal calculé
    
    fields = ['product', 'quantity', 'unit_price', 'subtotal', 'created_at']
    # ou exclude = ['order']  # exclure la clé étrangère
    
    def subtotal(self, obj):
        if obj.pk:
            return obj.quantity * obj.unit_price
        return '-'
    subtotal.short_description = 'Sous-total'
```

---

## 3. Rendu dans les templates

### 3.1 Chaîne de templates

Le formulaire d'édition moderne utilise :

```
admin_custom/modern/change_form.html
  → extends admin/change_form.html (Django)
  → block inline_field_sets
```

### 3.2 Bloc inline_field_sets

```django
{% block inline_field_sets %}
{% for inline_admin_formset in inline_admin_formsets %}
<div class="inline-group mb-4">
  {{ inline_admin_formset }}
</div>
{% endfor %}
{% endblock %}
```

La variable `inline_admin_formsets` est fournie par Django dans le contexte de `ModelAdmin.changeform_view()`.

### 3.3 Structure HTML générée par Django

**TabularInline** génère :
- Une `<table>` avec classe `tabular`
- En-têtes (`<th>`) pour chaque champ
- Une ligne (`<tr>`) par formulaire
- Une ligne "Ajouter" (`.add-row`) pour ajouter des enregistrements

**StackedInline** génère :
- Des divs `.inline-related` pour chaque formulaire
- Chaque champ dans une `.form-row`
- Un lien `.add-row` pour ajouter

---

## 4. Personnalisation des templates

### 4.1 Surcharger le template d'un inline

Créez un template dans votre projet :

```
templates/admin/<app>/<model>/edit_inline/tabular.html
templates/admin/<app>/<model>/edit_inline/stacked.html
```

Puis dans votre Inline :

```python
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    template = 'admin/sales/orderitem/edit_inline/tabular.html'
```

### 4.2 Variables disponibles dans le template

| Variable | Description |
|----------|-------------|
| `inline_admin_formset` | Le formset complet |
| `inline_admin_formset.formset` | Objet formset Django |
| `inline_admin_formset.opts` | Options de l'Inline |
| `inline_admin_form` | Un formulaire individuel (dans la boucle) |
| `inline_admin_form.original` | Instance existante (ou None si nouveau) |
| `inline_admin_form.deletion_field` | Champ checkbox "Supprimer" |

### 4.3 Exemple de template personnalisé

Copiez d'abord le template Django par défaut depuis :
- `django/contrib/admin/templates/admin/edit_inline/tabular.html`
- `django/contrib/admin/templates/admin/edit_inline/stacked.html`

Puis modifiez selon vos besoins (structure, classes CSS, logique conditionnelle).

---

## 5. Styles CSS (interface moderne)

Les inlines sont stylés dans `modern_admin_unified.css` :

### 5.1 Classes principales

| Classe | Élément | Rôle |
|--------|---------|------|
| `.inline-group` | Conteneur global | Bordure, coins arrondis |
| `.inline-related` | Chaque formulaire (stacked) | Padding, bordure |
| `.tabular` | Table (TabularInline) | Tableau |
| `.add-row` | Zone "Ajouter" | Lien d'ajout |
| `.form-row` | Ligne de champ | Espacement |

### 5.2 Variables CSS utilisées

```css
--color-background    /* Fond des en-têtes et add-row */
--color-surface       /* Fond des cellules et inputs */
--color-border        /* Bordures */
--color-text          /* Texte */
--color-primary       /* Liens et accents */
```

### 5.3 Personnaliser l'apparence

Ajoutez des règles dans `theme_override.css` ou `modern_admin_unified.css` :

```css
/* Exemple : modifier l'en-tête d'un inline spécifique */
.admin-layout .inline-group h2 {
  background: var(--color-primary) !important;
  color: white !important;
}
```

---

## 6. Exemples du projet

### 6.1 Order (Commandes)

**Fichier :** `sales/admin.py`

- **OrderItemInline** (TabularInline) : articles de la commande en tableau
- **InvoiceInline** (StackedInline) : facture associée en blocs

```python
@admin.register(Order)
class OrderAdmin(ModernTemplateMixin, admin.ModelAdmin):
    inlines = [OrderItemInline, InvoiceInline]
```

### 6.2 Invoice (Factures)

- **PaymentInline** (TabularInline) : paiements en tableau

```python
@admin.register(Invoice)
class InvoiceAdmin(ModernTemplateMixin, admin.ModelAdmin):
    inlines = [PaymentInline]
```

---

## 7. Créer un nouvel inline

### Étape 1 : Modèle avec ForeignKey

```python
# models.py
class Comment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

### Étape 2 : Déclarer l'Inline

```python
# admin.py
class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    fields = ['text', 'created_at']
    readonly_fields = ['created_at']

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline, InvoiceInline, CommentInline]
```

### Étape 3 : Migration

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 8. Bonnes pratiques

1. **extra** : Mettre 0 ou 1 pour les inlines avec beaucoup de champs (évite une page trop longue)
2. **readonly_fields** : Marquer les champs auto (created_at, computed) en lecture seule
3. **show_change_link** : Utile pour naviguer vers l'objet lié quand il est complexe
4. **max_num** : Limiter si une relation ne doit pas dépasser N enregistrements
5. **TabularInline** : Préféré pour peu de champs (2-5)
6. **StackedInline** : Préféré pour formulaires avec nombreux champs ou champs longs
7. **get_queryset()** : Surcharger pour filtrer les lignes affichées
8. **get_formset()** : Surcharger pour personnaliser le formulaire ou la validation

### Exemple : filtrer les lignes

```python
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('product')  # Optimisation
```

### Exemple : validation personnalisée

```python
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # Modifier le formulaire si besoin
        return formset
```

---

## 9. Fichiers de référence

| Fichier | Rôle |
|---------|------|
| `sales/admin.py` | Définition des inlines Order, Invoice |
| `admin_custom/templates/.../change_form.html` | Bloc inline_field_sets |
| `admin_custom/static/.../modern_admin_unified.css` | Styles .inline-group, .tabular, .stacked |
| `templates/admin/includes/fieldset.html` | Champs (hors inlines) |
| Django : `admin/edit_inline/tabular.html` | Template par défaut TabularInline |
| Django : `admin/edit_inline/stacked.html` | Template par défaut StackedInline |

---

## 10. Dépannage

**Les inlines ne s'affichent pas ?**
- Vérifier que le modèle a une ForeignKey vers le parent
- Vérifier que `inlines` est bien défini dans le ModelAdmin
- Vérifier que le user a les permissions (add, change) sur le modèle inline

**Erreur "formset" ?**
- S'assurer que le formulaire parent est valide
- Vérifier les contraintes (max_num, min_num)

**Style cassé ?**
- S'assurer que `modern_admin_unified.css` est chargé
- Vérifier que la page utilise `admin_base.html` (interface moderne)
- Inspecter les classes générées (.inline-group, .tabular, etc.)
