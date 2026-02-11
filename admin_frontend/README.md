# Admin Frontend (maquette statique)

Cette maquette est une interface admin moderne (Light + Dark) avec couleur primaire globale personnalisable.

## Lancer

Ouvre `admin_frontend/index.html` dans ton navigateur.

## Thème

- Mode Light/Dark: toggle en haut à droite
- Couleur principale: color picker
- Persistance: `localStorage`

## Intégration Django (plus tard)

Quand tu voudras intégrer au backend Django:

- Templates: copier la structure dans `templates/admin/` (override `base_site.html`, `base.html`, `index.html`)
- Static: copier `assets/styles.css` et `assets/app.js` dans `static/admin_custom/`
- Persistance DB: remplacer `localStorage` par un modèle singleton (ex: `AdminBrandingSettings`) + context processor/admin view
