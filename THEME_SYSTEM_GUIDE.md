# Guide de Configuration des Thèmes - Admin Django Personnalisé

## Vue d'ensemble

Le système de gestion des thèmes a été considérablement amélioré pour permettre aux utilisateurs de basculer facilement entre les différents thèmes disponibles dans l'interface d'administration.

## Améliorations Apportées

### 1. **Gestionnaire de Thèmes Centralisé**

**Fichier:** `admin_custom/static/admin_custom/js/theme-manager.js`

Un nouveau script JavaScript complet a été créé pour gérer les thèmes de manière centralisée:

- **Détection automatique du type d'interface** (moderne ou classique)
- **Gestion des thèmes modernes:** bleu-moderne, émeraude, coucher-soleil, sombre
- **Gestion des thèmes classiques:** default, nostalgie, ocean, sunset, forest, dark, liquid-glass
- **Persistance locale** via localStorage
- **Persistance backend** dans la base de données
- **API d'événements personnalisés** via `CustomEvent`

### 2. **Modèle de Préférences Utilisateur**

**Fichier:** `admin_custom/models.py`

Nouveau modèle `UserPreference`:
```python
class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    theme_modern = models.CharField(default='bleu-moderne')
    theme_classic = models.CharField(default='default')
    sidebar_collapsed = models.BooleanField(default=False)
    items_per_page = models.IntegerField(default=25)
```

**Avantages:**
- Les préférences utilisateur sont sauvegardées en base de données
- Les paramètres sont restaurés automatiquement lors de la connexion
- Gestion centralisée des préférences

### 3. **API de Sauvegarde des Préférences**

**Fichier:** `admin_custom/admin_views.py`

Nouvelle fonction `save_user_preference`:
```python
@require_http_methods(["POST"])
@staff_member_required
def save_user_preference(request):
    """API pour sauvegarder les préférences utilisateur"""
    # Valide et sauvegarde les préférences en base de données
```

**Utilisation:**
- URL: `/admin/api/save-preference/`
- Méthode: POST
- Authentification: Utilisateur staff requis

### 4. **Admin Personnalisé pour les Préférences**

**Fichier:** `admin_custom/admin.py`

Classe `UserPreferenceAdmin` pour gérer les préférences depuis l'interface d'administration:
- Affichage et modification des préférences utilisateur
- Groupage logique des paramètres
- Protection contre l'ajout manuel (création automatique lors de la première utilisation)

### 5. **Page de Paramètres Améliorée**

**Fichier:** `admin_custom/templates/admin_custom/modern/settings.html`

Améliorations:
- **Interface de sélection des thèmes** avec aperçu visuel
- **Boutons de thème interactifs** avec styles CSS modernes
- **Transitions fluides** lors du changement de thème
- **Navigation du menu latéral** améliore
- **Prévisualisation des couleurs** pour chaque thème

### 6. **Styles pour la Page de Paramètres**

**Fichier:** `admin_custom/static/admin_custom/css/settings.css`

Nouveaux styles:
- `.theme-option-modern`: Boutons de sélection de thème
- `.settings-nav-item`: Navigation du menu de paramètres
- Animations et transitions fluides
- Support du mode sombre
- Amélioration de l'accessibilité (focus visible)

### 7. **Base HTML Moderne Mise à Jour**

**Fichier:** `admin_custom/templates/admin_custom/modern/base.html`

Modifications:
- Inclusion du script `theme-manager.js`
- Initialisation rapide du thème avant le rendu du DOM
- Gestion améliorée de la détection du thème enregistré

### 8. **Vues Modernes Améliorées**

**Fichier:** `admin_custom/modern_views.py`

Ajouts:
- `get_user_preference()`: Fonction helper pour obtenir les préférences utilisateur
- Contexte des vues enrichi avec `user_theme` et `sidebar_collapsed`
- Intégration de la base de données pour la persistance

## Architecture du Système de Thèmes

```
┌─────────────────────────────────────────────────────┐
│         Utilisateur Change de Thème                 │
│     (Clique sur un bouton de sélection)             │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│   theme-manager.js (applyTheme)                     │
├─────────────────────────────────────────────────────┤
│ 1. Valide le thème                                  │
│ 2. Applique au document (data-theme)                │
│ 3. Sauvegarde dans localStorage                     │
│ 4. Envoie au serveur (async)                        │
│ 5. Déclenche un événement personnalisé              │
└────────────────┬──────────────────────┬─────────────┘
                 │                      │
        ┌────────▼────────┐    ┌────────▼──────────┐
        │  LocalStorage   │    │  save_user_prefe │
        │  ('admin_*')    │    │  rene API         │
        │                 │    │  (/admin/api/s...)│
        └─────────────────┘    └────────┬──────────┘
                                        │
                        ┌───────────────▼────────┐
                        │  UserPreference Model  │
                        │  (Base de données)     │
                        └────────────────────────┘
```

## Fonctionnement Détaillé

### Initialisation au Chargement

1. **Script inline dans `<head>`**: Récupère le thème enregistré très rapidement
2. **Theme Manager**: Initialise les boutons et applique les styles CSS
3. **CSS variables**: Les couleurs sont gérées via variables CSS (`--color-primary`, etc.)

### Changement de Thème

1. **Clic utilisateur** sur un bouton de sélection
2. **Validation** du thème choisi
3. **Application immédiate** sur le DOM
4. **Sauvegarde localStorage** (pour une restauration rapide)
5. **Requête asynchrone** vers le serveur (ne bloque pas l'UI)
6. **Mise à jour** de la base de données
7. **Événement personnalisé** déclenché pour les scripts externes

### Restauration du Thème

- À chaque chargement de page, le thème est:
  1. Récupéré du localStorage (au démarrage)
  2. Restauré immédiatement avant le rendu visuel
  3. Confirmé par la préférence en base de données si disponible

## Utilisation

### Pour les Utilisateurs

1. Accédez à **Paramètres** > **Thème**
2. Cliquez sur le thème de votre choix
3. Les changements sont appliqués instantanément
4. Les paramètres sont sauvegardés automatiquement

### Pour les Développeurs

#### Accéder au gestionnaire de thèmes

```javascript
// Récupérer le thème actuel
const currentTheme = window.ThemeManager.getCurrentTheme();

// Changer le thème par programmation
window.ThemeManager.applyTheme('emeraude');

// Écouter les changements de thème
window.addEventListener('themeChanged', (event) => {
  console.log('Nouveau thème:', event.detail.theme);
});
```

#### Ajouter un nouveau thème

1. **CSS**: Ajouter les variables CSS dans `themes_modern.css`:
```css
[data-theme="mon-theme"] {
  --color-primary: #...;
  --color-background: #...;
  /* ... autres variables */
}
```

2. **Configuration JS**: Ajouter à `THEME_CONFIG` dans `theme-manager.js`:
```javascript
modern: ['bleu-moderne', 'emeraude', 'mon-theme', ...]
```

3. **Base de données**: Ajouter le choix au modèle `UserPreference`:
```python
THEME_CHOICES_MODERN = [
    ('mon-theme', 'Mon Thème'),
    ...
]
```

4. **Bouton HTML**: Ajouter un bouton dans `settings.html`:
```html
<button class="theme-option-modern" data-theme="mon-theme">
  <!-- ... -->
</button>
```

## Fichiers Modifiés

```
admin_custom/
├── migrations/
│   └── 0002_userpreference.py          [NOUVEAU]
├── static/
│   └── admin_custom/
│       ├── css/
│       │   └── settings.css             [NOUVEAU]
│       └── js/
│           └── theme-manager.js         [NOUVEAU]
├── templates/
│   └── admin_custom/
│       └── modern/
│           ├── base.html                [MODIFIÉ]
│           └── settings.html            [MODIFIÉ]
├── admin.py                             [MODIFIÉ]
├── admin_views.py                       [MODIFIÉ]
├── models.py                            [MODIFIÉ]
└── modern_views.py                      [MODIFIÉ]

sandbox/
└── urls.py                              [MODIFIÉ]
```

## Migration de la Base de Données

Pour appliquer les changements:

```bash
# Appliquer les migrations
python manage.py migrate admin_custom

# Ou créer les migrations manuellement
python manage.py makemigrations admin_custom
python manage.py migrate
```

## Tests Recommandés

1. **Changement de thème**: Vérifier que tous les thèmes s'appliquent correctement
2. **Persistance localStorage**: Vérifier que le thème persiste après un refresh
3. **Persistance backend**: Vérifier que les préférences sont sauvegardées en base de données
4. **Responsivité**: Tester sur différentes résolutions d'écran
5. **Compatibilité navigateur**: Tester sur les navigateurs modernes

## Troubleshooting

### Le thème ne change pas
- Vérifier que `theme-manager.js` est chargé correctement
- Vérifier les erreurs dans la console du navigateur
- Supprimer le cache localStorage: `localStorage.clear()`

### Les préférences ne sont pas sauvegardées en base
- Vérifier que les migrations ont été appliquées
- Vérifier que l'API est accessible: `/admin/api/save-preference/`
- Vérifier les droits de l'utilisateur (doit être staff_member)

### Les couleurs du thème ne sont pas correctes
- Vérifier que `data-theme` est correctement défini sur l'élément HTML root
- Vérifier les variables CSS dans `themes_modern.css`
- Nettoyer le cache du navigateur

## Licences et Attributions

- Inspiré des meilleures pratiques de gestion de thèmes
- Intégration avec Django ORM pour la persistance
- CSS variables (IE11+, tous les navigateurs modernes)

## Notes de Version

### Version 1.0

- ✅ Gestionnaire de thèmes centralisé
- ✅ 4 thèmes modernes
- ✅ 7 thèmes classiques
- ✅ Persistance locale et backend
- ✅ Interface utilisateur améliorée
- ✅ API de sauvegarde des préférences
- ✅ Admin Django pour la gestion
