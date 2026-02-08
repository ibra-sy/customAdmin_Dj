/**
 * Données de layout partagées - URLs et navigation
 * Pour utilisation dans des pages statiques
 */
const LAYOUT = {
  nav: [
    { href: 'dashboard.html', icon: 'fa-gauge-high', label: 'Tableau de bord', section: 'Principal', active: false },
    { href: 'charts.html', icon: 'fa-chart-line', label: 'Graphiques', section: 'Principal', active: false },
    { href: 'chart_create.html', icon: 'fa-plus', label: 'Créer un graphique', section: 'Principal', active: false },
    { href: 'change_list.html', icon: 'fa-users', label: 'Utilisateurs', section: 'Contenu', badge: 12, active: false },
    { href: 'change_list.html?model=article', icon: 'fa-file-lines', label: 'Articles', section: 'Contenu', active: false },
    { href: 'change_list.html?model=product', icon: 'fa-box', label: 'Produits', section: 'Contenu', active: false },
    { href: 'settings.html', icon: 'fa-gear', label: 'Paramètres', section: 'Système', active: false }
  ]
};
