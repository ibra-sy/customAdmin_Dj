(function () {
  const STORAGE_KEY = 'admin_console_theme_v1';
  const KNOWN_VIEWS = new Set(['dashboard', 'orders', 'products', 'customers', 'users', 'settings']);
  const KNOWN_CHARTS = new Set(['sales', 'funnel', 'traffic']);

  // Store Chart.js instances
  const chartInstances = {};

  function safeParse(json) {
    try { return JSON.parse(json); } catch { return null; }
  }

  function clampHex(hex) {
    if (!hex) return '#4f46e5';
    const s = String(hex).trim();
    if (/^#[0-9a-fA-F]{6}$/.test(s)) return s;
    return '#4f46e5';
  }

  function loadPrefs() {
    const fromStorage = safeParse(localStorage.getItem(STORAGE_KEY) || '');
    const lastView = (typeof fromStorage?.lastView === 'string' && KNOWN_VIEWS.has(fromStorage.lastView))
      ? fromStorage.lastView
      : 'dashboard';

    const rawOrder = Array.isArray(fromStorage?.charts?.order) ? fromStorage.charts.order : ['sales', 'funnel', 'traffic'];
    const order = rawOrder.filter((x) => typeof x === 'string' && KNOWN_CHARTS.has(x));
    const normalizedOrder = order.length ? order : ['sales', 'funnel', 'traffic'];

    return {
      theme: fromStorage?.theme === 'dark' ? 'dark' : 'light',
      primary: clampHex(fromStorage?.primary || '#4f46e5'),
      sidebarCollapsed: !!fromStorage?.sidebarCollapsed,
      lastView,
      terminology: typeof fromStorage?.terminology === 'string' ? fromStorage.terminology : 'standard',
      charts: {
        order: normalizedOrder,
        enabled: {
          sales: fromStorage?.charts?.enabled?.sales !== false,
          funnel: fromStorage?.charts?.enabled?.funnel !== false,
          traffic: fromStorage?.charts?.enabled?.traffic !== false,
        },
        metric: {
          sales: typeof fromStorage?.charts?.metric?.sales === 'string' ? fromStorage.charts.metric.sales : 'revenue',
          funnel: typeof fromStorage?.charts?.metric?.funnel === 'string' ? fromStorage.charts.metric.funnel : 'conversion',
          traffic: typeof fromStorage?.charts?.metric?.traffic === 'string' ? fromStorage.charts.metric.traffic : 'visitors',
        },
      },
    };
  }

  function savePrefs(prefs) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs));
  }

  function setThemeMode(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    const modeToggle = document.getElementById('themeMode');
    if (modeToggle) modeToggle.checked = theme === 'dark';
    
    // Update charts to match theme (grid lines color, etc.)
    Object.values(chartInstances).forEach(chart => chart.update());
  }

  function setPrimaryColor(hex) {
    const c = clampHex(hex);
    document.documentElement.style.setProperty('--primary', c);
    const pickers = document.querySelectorAll('input[type="color"][data-action="primary-color"]');
    pickers.forEach((p) => { p.value = c; });
    
    // Update charts to match primary color
    Object.values(chartInstances).forEach(chart => {
      if (chart.data.datasets[0]) {
        chart.data.datasets[0].borderColor = c;
        chart.data.datasets[0].backgroundColor = hexToRgba(c, 0.1);
      }
      chart.update();
    });
  }

  function setLayoutCollapsed(collapsed) {
    const app = document.querySelector('.app');
    if (!app) return;
    app.setAttribute('data-layout', collapsed ? 'collapsed' : 'default');
  }

  function showView(view) {
    const title = document.getElementById('pageTitle');
    const navItems = document.querySelectorAll('.nav__item[data-view]');
    const views = document.querySelectorAll('.view[data-view]');

    navItems.forEach((a) => a.classList.toggle('is-active', a.getAttribute('data-view') === view));
    views.forEach((v) => v.classList.toggle('is-active', v.getAttribute('data-view') === view));

    const activeNav = Array.from(navItems).find((a) => a.getAttribute('data-view') === view);
    const label = activeNav?.querySelector('.nav__label')?.textContent?.trim() || 'Dashboard';
    if (title) title.textContent = label;
  }

  function getViewFromHash() {
    const raw = (location.hash || '').replace('#', '').trim();
    if (KNOWN_VIEWS.has(raw)) return raw;
    return null;
  }

  function setHash(view) {
    if (!KNOWN_VIEWS.has(view)) return;
    if (location.hash === `#${view}`) return;
    history.replaceState(null, '', `#${view}`);
  }

  function toast(message) {
    const el = document.querySelector('[data-toast]');
    if (!(el instanceof HTMLElement)) return;
    el.textContent = message;
    el.classList.add('is-visible');
    clearTimeout(toast._t);
    toast._t = setTimeout(() => el.classList.remove('is-visible'), 2200);
  }

  function getTerminologyDict(mode) {
    if (mode === 'commerce') {
      return {
        'nav.dashboard': 'Dashboard',
        'nav.orders': 'Ventes',
        'nav.products': 'Articles',
        'nav.customers': 'Acheteurs',
        'nav.users': 'Équipe',
        'nav.settings': 'Réglages',
        'actions.create_product': 'Ajouter un article',
        'actions.new_order': 'Nouvelle vente',
      };
    }
    if (mode === 'en') {
      return {
        'nav.dashboard': 'Dashboard',
        'nav.orders': 'Orders',
        'nav.products': 'Products',
        'nav.customers': 'Customers',
        'nav.users': 'Users',
        'nav.settings': 'Settings',
        'actions.create_product': 'Create product',
        'actions.new_order': 'New order',
      };
    }
    return {
      'nav.dashboard': 'Dashboard',
      'nav.orders': 'Commandes',
      'nav.products': 'Produits',
      'nav.customers': 'Clients',
      'nav.users': 'Utilisateurs',
      'nav.settings': 'Paramètres',
      'actions.create_product': 'Créer un produit',
      'actions.new_order': 'Nouvelle commande',
    };
  }

  function applyTerminology(mode) {
    const dict = getTerminologyDict(mode);
    const nodes = document.querySelectorAll('[data-term]');
    nodes.forEach((n) => {
      const key = n.getAttribute('data-term');
      if (!key) return;
      const value = dict[key];
      if (typeof value === 'string') n.textContent = value;
    });

    const selects = document.querySelectorAll('select[data-action="terminology"]');
    selects.forEach((s) => {
      if (s instanceof HTMLSelectElement) s.value = mode;
    });

    showView(prefs.lastView);
  }

  function chartLabel(metric) {
    const map = {
      revenue: 'Chiffre d’affaires',
      orders: 'Commandes',
      aov: 'Panier moyen',
      conversion: 'Taux de conversion',
      abandon: 'Abandon panier',
      refunds: 'Remboursements',
      visitors: 'Visiteurs',
      sessions: 'Sessions',
      bounce: 'Taux de rebond',
    };
    return map[metric] || 'Métrique';
  }

  // Helper to generate dummy chart data
  function getChartData(metric, period) {
    const p = parseInt(period, 10) || 30;
    let count = 7;
    let labels = [];
    
    if (p === 7) {
      count = 7;
      labels = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];
    } else if (p === 90) {
      count = 12;
      for (let i = 1; i <= 12; i++) labels.push(`S${i}`);
    } else {
      count = 15; // Simplify 30 days to 15 points for cleaner chart
      for (let i = 1; i <= 15; i++) labels.push(`${i * 2}j`);
    }

    const data = [];
    let min = 10, max = 100;

    if (['revenue', 'aov'].includes(metric)) { min = 10000; max = 50000; }
    if (['orders', 'visitors', 'sessions'].includes(metric)) { min = 50; max = 500; }
    if (['conversion', 'abandon', 'bounce', 'refunds'].includes(metric)) { min = 1; max = 15; }

    for (let i = 0; i < count; i++) {
      data.push(Math.floor(Math.random() * (max - min + 1) + min));
    }

    return { labels, data, label: chartLabel(metric) };
  }

  function hexToRgba(hex, alpha) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  function createOrUpdateChart(id, metric, period) {
    const container = document.querySelector(`[data-chart-canvas="${id}"]`);
    if (!container) return;

    // Ensure canvas exists
    let canvas = container.querySelector('canvas');
    if (!canvas) {
      canvas = document.createElement('canvas');
      container.innerHTML = '';
      container.appendChild(canvas);
    }

    const ctx = canvas.getContext('2d');
    const { labels, data, label } = getChartData(metric, period);
    const color = prefs.primary;
    const isDark = prefs.theme === 'dark';
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)';
    const textColor = isDark ? '#a8b3c7' : '#55627a';

    if (chartInstances[id]) {
      // Update existing
      chartInstances[id].data.labels = labels;
      chartInstances[id].data.datasets[0].data = data;
      chartInstances[id].data.datasets[0].label = label;
      chartInstances[id].data.datasets[0].borderColor = color;
      chartInstances[id].data.datasets[0].backgroundColor = hexToRgba(color, 0.1);
      chartInstances[id].options.scales.x.grid.color = gridColor;
      chartInstances[id].options.scales.y.grid.color = gridColor;
      chartInstances[id].options.scales.x.ticks.color = textColor;
      chartInstances[id].options.scales.y.ticks.color = textColor;
      chartInstances[id].update();
    } else {
      // Create new
      if (typeof Chart === 'undefined') return; // Safety check
      
      chartInstances[id] = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: label,
            data: data,
            borderColor: color,
            backgroundColor: hexToRgba(color, 0.1),
            borderWidth: 2,
            tension: 0.4,
            fill: true,
            pointRadius: 0,
            pointHoverRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              mode: 'index',
              intersect: false,
            }
          },
          scales: {
            x: {
              grid: { color: gridColor, drawBorder: false },
              ticks: { color: textColor, font: { size: 10 } }
            },
            y: {
              grid: { color: gridColor, drawBorder: false, borderDash: [4, 4] },
              ticks: { color: textColor, font: { size: 10 } },
              beginAtZero: true
            }
          },
          interaction: {
            mode: 'nearest',
            axis: 'x',
            intersect: false
          }
        }
      });
    }
  }

  function renderCharts() {
    const grid = document.querySelector('[data-charts-grid]');
    if (!(grid instanceof HTMLElement)) return;

    const items = {};
    grid.querySelectorAll('[data-chart]').forEach((el) => {
      const id = el.getAttribute('data-chart');
      if (id) items[id] = el;
    });

    prefs.charts.order.forEach((id) => {
      const el = items[id];
      if (!el) return;
      const enabled = !!prefs.charts.enabled[id];
      el.style.display = enabled ? '' : 'none';
      grid.appendChild(el);

      const meta = document.querySelector(`[data-chart-meta="${id}"]`);
      const m = prefs.charts.metric[id];
      
      // Get current period from the select
      const periodSelect = document.querySelector(`select[data-chart-quick="${id}"]`);
      const period = periodSelect ? periodSelect.value : '30';

      if (meta) meta.textContent = `${chartLabel(m)} · ${period} jours`;
      
      const metricSelect = document.querySelector(`select[data-chart-metric="${id}"]`);
      if (metricSelect instanceof HTMLSelectElement) metricSelect.value = m;
      
      const enabledCheck = document.querySelector(`input[type="checkbox"][data-chart-enabled="${id}"]`);
      if (enabledCheck instanceof HTMLInputElement) enabledCheck.checked = enabled;

      if (enabled) {
        createOrUpdateChart(id, m, period);
      }
    });
  }

  function setChartsPanelOpen(open) {
    const panel = document.querySelector('[data-charts-panel]');
    if (!(panel instanceof HTMLElement)) return;
    panel.hidden = !open;
  }

  function randomColor() {
    const palette = ['#4f46e5', '#2563eb', '#0ea5e9', '#14b8a6', '#16a34a', '#f59e0b', '#f97316', '#ef4444', '#db2777', '#9333ea'];
    return palette[Math.floor(Math.random() * palette.length)];
  }

  let prefs;
  try {
    prefs = loadPrefs();
  } catch {
    prefs = {
      theme: 'light',
      primary: '#4f46e5',
      sidebarCollapsed: false,
      lastView: 'dashboard',
      terminology: 'standard',
      charts: {
        order: ['sales', 'funnel', 'traffic'],
        enabled: { sales: true, funnel: true, traffic: true },
        metric: { sales: 'revenue', funnel: 'conversion', traffic: 'visitors' },
      },
    };
  }

  const initialView = getViewFromHash() || prefs.lastView;
  prefs.lastView = initialView;
  setThemeMode(prefs.theme);
  setPrimaryColor(prefs.primary);
  setLayoutCollapsed(prefs.sidebarCollapsed);
  applyTerminology(prefs.terminology);
  showView(prefs.lastView);
  setHash(prefs.lastView);
  
  // Initial render (delayed slightly to ensure Chart.js is loaded if script order varies, though we put it before)
  setTimeout(renderCharts, 50);

  window.addEventListener('hashchange', () => {
    const v = getViewFromHash();
    if (!v) return;
    prefs.lastView = v;
    savePrefs(prefs);
    showView(v);
  });
  
  // Listen for quick period changes on the charts themselves
  document.addEventListener('change', (e) => {
    const t = e.target;
    if (t instanceof HTMLSelectElement && t.matches('select[data-chart-quick]')) {
      const id = t.getAttribute('data-chart-quick');
      if (id) {
        renderCharts(); // Re-render to update the specific chart
      }
    }
  });

  document.addEventListener('click', (e) => {
    const t = e.target;
    if (!(t instanceof HTMLElement)) return;

    const nav = t.closest('.nav__item[data-view]');
    if (nav) {
      e.preventDefault();
      const view = nav.getAttribute('data-view') || 'dashboard';
      prefs.lastView = view;
      savePrefs(prefs);
      showView(view);
      setHash(view);
      return;
    }

    const actionEl = t.closest('[data-action]');
    if (!actionEl) return;

    const action = actionEl.getAttribute('data-action');
    if (action === 'toggle-sidebar') {
      prefs.sidebarCollapsed = !prefs.sidebarCollapsed;
      savePrefs(prefs);
      setLayoutCollapsed(prefs.sidebarCollapsed);
      return;
    }

    if (action === 'charts-open') {
      setChartsPanelOpen(true);
      return;
    }

    if (action === 'charts-close') {
      setChartsPanelOpen(false);
      return;
    }

    if (action === 'charts-save') {
      savePrefs(prefs);
      setChartsPanelOpen(false);
      renderCharts();
      return;
    }

    if (action === 'charts-reset') {
      prefs.charts = {
        order: ['sales', 'funnel', 'traffic'],
        enabled: { sales: true, funnel: true, traffic: true },
        metric: { sales: 'revenue', funnel: 'conversion', traffic: 'visitors' },
      };
      savePrefs(prefs);
      renderCharts();
      return;
    }

    if (action === 'chart-up' || action === 'chart-down') {
      const chart = actionEl.getAttribute('data-chart');
      if (!chart) return;
      const i = prefs.charts.order.indexOf(chart);
      if (i < 0) return;
      const delta = action === 'chart-up' ? -1 : 1;
      const j = i + delta;
      if (j < 0 || j >= prefs.charts.order.length) return;
      const next = prefs.charts.order.slice();
      const tmp = next[i];
      next[i] = next[j];
      next[j] = tmp;
      prefs.charts.order = next;
      savePrefs(prefs);
      renderCharts();
      return;
    }

    if (action === 'set-light') {
      prefs.theme = 'light';
      savePrefs(prefs);
      setThemeMode('light');
      return;
    }

    if (action === 'set-dark') {
      prefs.theme = 'dark';
      savePrefs(prefs);
      setThemeMode('dark');
      return;
    }

    if (action === 'random-color') {
      const c = randomColor();
      prefs.primary = c;
      savePrefs(prefs);
      setPrimaryColor(c);
      return;
    }

    if (action === 'save-theme') {
      savePrefs(prefs);
      return;
    }

    if (action === 'reset-theme') {
      prefs.theme = 'light';
      prefs.primary = '#4f46e5';
      savePrefs(prefs);
      setThemeMode(prefs.theme);
      setPrimaryColor(prefs.primary);
      return;
    }

    if (action === 'logout') {
      toast('Démo: déconnexion');
      return;
    }

    // New actions
    if (action === 'go-to-products') {
      prefs.lastView = 'products';
      savePrefs(prefs);
      showView('products');
      setHash('products');
      return;
    }

    if (action === 'go-to-orders') {
      prefs.lastView = 'orders';
      savePrefs(prefs);
      showView('orders');
      setHash('orders');
      return;
    }
    
    if (action === 'go-to-settings') {
      prefs.lastView = 'settings';
      savePrefs(prefs);
      showView('settings');
      setHash('settings');
      return;
    }

    if (action === 'notifications') {
      toast('Aucune nouvelle notification');
      return;
    }

    if (action === 'help') {
      toast('Aide: Consulter la documentation (non disponible)');
      return;
    }

    if (action === 'export-data') {
      toast('Exportation des données en cours...');
      setTimeout(() => toast('Export terminé (simulé)'), 1500);
      return;
    }

    if (action === 'create-order') {
      // For now, just show a toast or maybe redirect to a create view if we had one
      toast('Création de commande (simulée)');
      return;
    }

    if (action === 'apply-filters') {
      toast('Filtres appliqués');
      return;
    }

    if (action === 'reset-filters') {
      const q = document.getElementById('qOrders');
      if (q) q.value = '';
      const s = document.getElementById('statusOrders');
      if (s) s.selectedIndex = 0;
      const d = document.getElementById('dateOrders');
      if (d) d.selectedIndex = 1;
      toast('Filtres réinitialisés');
      return;
    }

    if (action === 'view-details') {
      const id = actionEl.getAttribute('data-id') || '???';
      toast(`Détails de la commande ${id}`);
      return;
    }

    if (action === 'edit-order') {
      const id = actionEl.getAttribute('data-id') || '???';
      toast(`Modification de la commande ${id}`);
      return;
    }
    
    if (action === 'prev-page' || action === 'next-page') {
      toast('Pagination non disponible en démo');
      return;
    }

    if (action === 'reset-product-form') {
      const form = document.getElementById('productForm');
      if (form) form.reset();
      // Scroll to form if needed
      const card = form ? form.closest('.card') : null;
      if (card) card.scrollIntoView({ behavior: 'smooth' });
      return;
    }

    if (action === 'save-product') {
      const name = document.getElementById('pName')?.value;
      if (!name) {
        toast('Erreur: Le nom est requis');
        return;
      }
      toast(`Produit "${name}" enregistré !`);
      // Go back to list or stay?
      return;
    }

    if (action === 'save-product-continue') {
       const name = document.getElementById('pName')?.value;
      if (!name) {
        toast('Erreur: Le nom est requis');
        return;
      }
      toast(`Produit "${name}" enregistré. Continuez...`);
      const form = document.getElementById('productForm');
      if (form) form.reset();
      return;
    }

    if (action === 'cancel-product') {
      const form = document.getElementById('productForm');
      if (form) form.reset();
      toast('Annulé');
      return;
    }

    if (action === 'switch-interface') {
      // Dans le futur, ceci redirigera vers l'URL Django : /admin/switch-interface/?next=/admin/
      // Pour l'instant, on simule l'action
      toast('Redirection vers l\'interface Classique...');
      setTimeout(() => {
        alert('Simulation : Vous seriez redirigé vers l\'interface classique Django Admin.');
      }, 1000);
      return;
    }

    if (action === 'switch-interface-classic') {
      toast('Redirection vers l\'interface Classique...');
      setTimeout(() => {
        alert('Simulation : Vous seriez redirigé vers l\'interface classique Django Admin.');
      }, 1000);
      return;
    }

    if (action === 'switch-interface-modern') {
      toast('Vous êtes déjà sur l\'interface Moderne.');
      return;
    }

    if (action === 'create-customer') {
      const form = document.getElementById('customerFormSection');
      if (form) {
        form.hidden = false;
        form.scrollIntoView({ behavior: 'smooth' });
      }
      return;
    }

    if (action === 'create-user') {
      const form = document.getElementById('userFormSection');
      if (form) {
        form.hidden = false;
        form.scrollIntoView({ behavior: 'smooth' });
      }
      return;
    }

    const btn = t.closest('button, a');
    if (btn instanceof HTMLElement) {
      const label = (btn.textContent || '').trim();
      if (label) toast(`Démo: ${label}`);
    }
  });

  const termSelects = document.querySelectorAll('select[data-action="terminology"]');
  termSelects.forEach((termSelect) => {
    if (termSelect instanceof HTMLSelectElement) {
      termSelect.value = prefs.terminology;
      termSelect.addEventListener('change', () => {
        prefs.terminology = termSelect.value;
        savePrefs(prefs);
        applyTerminology(prefs.terminology);
        toast('Terminologie mise à jour');
      });
    }
  });

  const chartsControls = document.querySelector('[data-charts-controls]');
  if (chartsControls instanceof HTMLElement) {
    chartsControls.addEventListener('change', (e) => {
      const t = e.target;
      if (!(t instanceof HTMLElement)) return;

      if (t instanceof HTMLInputElement && t.matches('input[type="checkbox"][data-chart-enabled]')) {
        const id = t.getAttribute('data-chart-enabled');
        if (!id) return;
        prefs.charts.enabled[id] = t.checked;
        return;
      }

      if (t instanceof HTMLSelectElement && t.matches('select[data-chart-metric]')) {
        const id = t.getAttribute('data-chart-metric');
        if (!id) return;
        prefs.charts.metric[id] = t.value;
        renderCharts();
        return;
      }
    });
  }

  const modeToggle = document.getElementById('themeMode');
  if (modeToggle) {
    modeToggle.addEventListener('change', () => {
      prefs.theme = modeToggle.checked ? 'dark' : 'light';
      savePrefs(prefs);
      setThemeMode(prefs.theme);
      toast(prefs.theme === 'dark' ? 'Mode Dark' : 'Mode Light');
    });
  }

  const primaryPickers = document.querySelectorAll('input[type="color"][data-action="primary-color"]');
  primaryPickers.forEach((p) => {
    p.addEventListener('input', () => {
      const v = (p instanceof HTMLInputElement) ? p.value : '#4f46e5';
      prefs.primary = clampHex(v);
      setPrimaryColor(prefs.primary);
    });
    p.addEventListener('change', () => {
      const v = (p instanceof HTMLInputElement) ? p.value : '#4f46e5';
      prefs.primary = clampHex(v);
      savePrefs(prefs);
      setPrimaryColor(prefs.primary);
    });
  });

  const navSearch = document.getElementById('navSearch');
  if (navSearch) {
    navSearch.addEventListener('input', () => {
      const q = navSearch.value.toLowerCase().trim();
      const navItems = document.querySelectorAll('.nav__item[data-view]');
      navItems.forEach((a) => {
        const label = a.querySelector('.nav__label')?.textContent?.toLowerCase() || '';
        a.style.display = (!q || label.includes(q)) ? '' : 'none';
      });
    });
  }
})();
