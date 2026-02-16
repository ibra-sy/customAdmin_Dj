(function () {
  const STORAGE_KEY = 'admin_console_theme_v1';
  const KNOWN_VIEWS = new Set(['dashboard', 'orders', 'products', 'products-list', 'customers', 'users', 'settings']);
  const KNOWN_CHARTS = new Set(['sales', 'funnel', 'traffic']);

  // Store Chart.js instances
  const chartInstances = {};

  function safeParse(json) {
    try { return JSON.parse(json); } catch { return null; }
  }

  function getCookie(name) {
    var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : null;
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

  function formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1).replace('.', ',') + ' M';
    if (num >= 1000) return Math.round(num).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '\u202f');
    return String(Math.round(num));
  }

  function fetchDashboardStats() {
    fetch('/admin_custom/api/stats/', { credentials: 'same-origin' })
      .then((r) => r.ok ? r.json() : Promise.reject(new Error('Stats API error')))
      .then((data) => {
        const revenue = Number(data.revenue) || 0;
        const orders = Number(data.orders) || 0;
        const aov = orders > 0 ? revenue / orders : 0;
        const revenueEl = document.querySelector('[data-kpi="revenue"] .kpi__value');
        const ordersEl = document.querySelector('[data-kpi="orders"] .kpi__value');
        const aovEl = document.querySelector('[data-kpi="aov"] .kpi__value');
        if (revenueEl) revenueEl.textContent = formatNumber(revenue);
        if (ordersEl) ordersEl.textContent = formatNumber(orders);
        if (aovEl) aovEl.textContent = formatNumber(aov);
      })
      .catch(() => {
        const fallbacks = document.querySelectorAll('[data-kpi] .kpi__value');
        fallbacks.forEach((el) => { if (el && el.textContent === '—') el.textContent = '0'; });
      });
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

    if (view === 'dashboard') fetchDashboardStats();
    if (['orders', 'products-list', 'customers', 'users'].includes(view)) fetchGridData(view);
  }

  // Vue "products-list" utilise la grille "products"
  const VIEW_GRID_MAP = { 'products-list': 'products' };

  // Grilles : logique API pour toutes les vues liste
  const GRID_CONFIG = {
    orders: { model: 'Order', columns: ['id', 'order_number', 'user', 'status', 'total_amount', 'created_at'], displayCols: ['order_number', 'user', 'status', 'total_amount', 'created_at'] },
    products: { model: 'Product', columns: ['id', 'name', 'sku', 'price', 'stock_quantity', 'created_at'], displayCols: ['id', 'name', 'sku', 'price', 'stock_quantity', 'created_at'] },
    customers: { model: 'User', columns: ['username', 'email', 'first_name', 'last_name', 'date_joined'], displayCols: ['username', 'email', 'first_name', 'last_name', 'date_joined'], filter: { is_staff: 'false' } },
    users: { model: 'User', columns: ['username', 'email', 'is_staff', 'date_joined'], displayCols: ['username', 'email', 'is_staff', 'date_joined'] },
  };

  let ordersGridState = { page: 1, pageSize: 20, totalCount: 0 };

  function getOrdersParams() {
    const qEl = document.getElementById('qOrders');
    const statusEl = document.getElementById('statusOrders');
    const periodEl = document.getElementById('dateOrders');
    return {
      q: (qEl && qEl.value) ? qEl.value.trim() : '',
      status: (statusEl && statusEl.value) ? statusEl.value.trim() : '',
      period: (periodEl && periodEl.value) ? periodEl.value.trim() : '30 jours',
      page: ordersGridState.page,
      page_size: ordersGridState.pageSize,
    };
  }

  function updateOrdersPagination(totalCount) {
    ordersGridState.totalCount = totalCount;
    const meta = document.querySelector('[data-orders-pagination-meta]');
    const prevBtn = document.getElementById('btnOrdersPrev');
    const nextBtn = document.getElementById('btnOrdersNext');
    if (meta) meta.innerHTML = 'Page <span class="mono">' + ordersGridState.page + '</span> sur <span class="mono">' + Math.max(1, Math.ceil(totalCount / ordersGridState.pageSize)) + '</span>';
    if (prevBtn) prevBtn.disabled = ordersGridState.page <= 1;
    if (nextBtn) nextBtn.disabled = ordersGridState.page >= Math.ceil(totalCount / ordersGridState.pageSize);
  }

  let customersGridState = { page: 1, pageSize: 20, totalCount: 0 };

  function getCustomersParams() {
    const qMain = document.getElementById('qCustomersMain');
    const qSide = document.getElementById('qCustomers');
    const q = (qMain?.value || qSide?.value || '').trim();
    return {
      q: q,
      page: customersGridState.page,
      page_size: customersGridState.pageSize,
    };
  }

  function updateCustomersPagination(totalCount) {
    customersGridState.totalCount = totalCount;
    const meta = document.querySelector('[data-customers-pagination-meta]');
    const prevBtn = document.getElementById('btnCustomersPrev');
    const nextBtn = document.getElementById('btnCustomersNext');
    const countEl = document.querySelector('[data-customers-count]');
    const filterCountEl = document.querySelector('[data-customers-filter-count]');
    if (meta) meta.innerHTML = 'Page <span class="mono">' + customersGridState.page + '</span> sur <span class="mono">' + Math.max(1, Math.ceil(totalCount / customersGridState.pageSize)) + '</span>';
    if (prevBtn) prevBtn.disabled = customersGridState.page <= 1;
    if (nextBtn) nextBtn.disabled = customersGridState.page >= Math.ceil(totalCount / customersGridState.pageSize);
    const label = totalCount === 1 ? '1 client' : totalCount + ' clients';
    if (countEl) countEl.textContent = label;
    if (filterCountEl) filterCountEl.textContent = label;
  }

  function fetchGridData(view) {
    const gridId = VIEW_GRID_MAP[view] || view;
    const config = GRID_CONFIG[gridId];
    const tbody = config ? document.querySelector(`[data-view="${view}"] [data-grid-target="${gridId}"]`) : null;
    if (!config || !(tbody instanceof HTMLTableSectionElement)) return Promise.resolve();
    const params = new URLSearchParams({ model: config.model });
    config.columns.forEach((c) => params.append('columns', c));
    if (config.filter && typeof config.filter === 'object') {
      Object.keys(config.filter).forEach((k) => params.set(k, config.filter[k]));
    }
    if (gridId === 'orders') {
      const op = getOrdersParams();
      if (op.q) params.set('q', op.q);
      if (op.status) params.set('status', op.status);
      if (op.period) params.set('period', op.period);
      params.set('page', String(op.page));
      params.set('page_size', String(op.page_size));
    }
    if (gridId === 'customers') {
      const cp = getCustomersParams();
      if (cp.q) params.set('q', cp.q);
      params.set('page', String(cp.page));
      params.set('page_size', String(cp.page_size));
    }
    return fetch('/admin_custom/api/grid-data/?' + params.toString(), { credentials: 'same-origin' })
      .then((r) => r.ok ? r.json() : Promise.reject())
      .then((res) => {
        tbody.innerHTML = '';
        const cols = res.columns && res.columns.length ? res.columns : config.displayCols.filter(Boolean);
        const rows = res.data || [];
        if (rows.length === 0) {
          const colCount = (config.displayCols || cols).length + (gridId === 'orders' ? 1 : 0);
          const tr = document.createElement('tr');
          tr.innerHTML = '<td colspan="' + colCount + '" class="muted">' + (gridId === 'products' ? 'Aucun produit pour le moment.' : gridId === 'customers' ? 'Aucun client.' : 'Aucune donnée.') + '</td>';
          tbody.appendChild(tr);
        } else {
          rows.forEach((row) => {
            const tr = document.createElement('tr');
            (config.displayCols || cols).forEach((col) => {
              const td = document.createElement('td');
              if (col) {
                let val = row[col] != null ? String(row[col]) : '—';
                if (col === 'total_amount' || col === 'price') val = formatNumber(Number(val)) || val;
                if (col === 'created_at' || col === 'date_joined') val = val.slice(0, 10);
                if (col === 'is_staff') val = val === 'True' ? 'Oui' : 'Non';
                if (col === 'status') {
                  const s = { pending: 'En attente', processing: 'En traitement', shipped: 'Expédiée', delivered: 'Livrée', cancelled: 'Annulée' };
                  val = s[val] || val;
                }
                td.innerHTML = (col === 'order_number' || col === 'id' || col === 'username' || col === 'sku') ? `<span class="mono">${escapeHtml(val)}</span>` : escapeHtml(val);
              } else td.textContent = '—';
              tr.appendChild(td);
            });
            if (gridId === 'orders') {
              const actions = document.createElement('td');
              actions.className = 'ta-right';
              actions.innerHTML = '<div class="row-actions"><button class="button button--ghost" type="button" data-action="view-details" data-id="' + escapeHtml(String(row.id || '')) + '">Voir</button> <button class="button button--ghost" type="button" data-action="edit-order" data-id="' + escapeHtml(String(row.id || '')) + '">Modifier</button></div>';
              tr.appendChild(actions);
            }
            tbody.appendChild(tr);
          });
        }
        if (gridId === 'orders' && res.total_count != null) updateOrdersPagination(res.total_count);
        if (gridId === 'customers' && res.total_count != null) updateCustomersPagination(res.total_count);
      })
      .catch(() => {
        const colspan = (config.displayCols || []).length + (gridId === 'orders' ? 1 : 0);
        tbody.innerHTML = '<tr><td colspan="' + colspan + '" class="muted">Aucune donnée ou modèle indisponible.</td></tr>';
        if (gridId === 'orders') updateOrdersPagination(0);
        if (gridId === 'customers') updateCustomersPagination(0);
      });
  }

  function escapeHtml(s) {
    if (s == null) return '';
    const div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
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

  // Map metric + period to API params (logique Sylla)
  function getChartApiParams(metric, period) {
    const p = parseInt(period, 10) || 30;
    let frequency = 'month';
    if (p <= 7) frequency = 'day';
    else if (p <= 30) frequency = 'week';
    else if (p <= 90) frequency = 'month';
    const map = {
      revenue: { model: 'Order', field: 'total_amount', operation: 'sum' },
      orders: { model: 'Order', field: 'id', operation: 'count' },
      aov: { model: 'Order', field: 'total_amount', operation: 'avg' },
      conversion: { model: 'Order', field: 'id', operation: 'count' },
      visitors: { model: 'Order', field: 'id', operation: 'count' },
      sessions: { model: 'Order', field: 'id', operation: 'count' },
    };
    const cfg = map[metric] || map.revenue;
    return { ...cfg, frequency };
  }

  function fetchChartDataFromAPI(metric, period) {
    const params = getChartApiParams(metric, period);
    const qs = new URLSearchParams({
      model: params.model,
      field: params.field,
      frequency: params.frequency,
      operation: params.operation || 'sum',
    });
    return fetch('/admin_custom/api/chart-data/?' + qs.toString(), { credentials: 'same-origin' })
      .then((r) => r.ok ? r.json() : Promise.reject())
      .then((res) => ({ labels: res.labels, data: res.data, label: chartLabel(metric) }));
  }

  // Données vides pour les graphiques quand l'API échoue (aucune simulation)
  function getEmptyChartData(metric, period) {
    const p = parseInt(period, 10) || 30;
    let count = 7;
    let labels = [];
    if (p === 7) {
      labels = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];
      count = 7;
    } else if (p === 90) {
      count = 12;
      for (let i = 1; i <= 12; i++) labels.push(`S${i}`);
    } else {
      count = 15;
      for (let i = 1; i <= 15; i++) labels.push(`${i * 2}j`);
    }
    return { labels, data: new Array(count).fill(0), label: chartLabel(metric) };
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

    try {
      // Ensure canvas exists
      let canvas = container.querySelector('canvas');
      if (!canvas) {
        canvas = document.createElement('canvas');
        container.innerHTML = '';
        container.appendChild(canvas);
      }

      // Defensive checks
      if (!canvas) {
        console.error('Canvas element is null or invalid for chart:', id);
        return;
      }

      // Verify it's actually a canvas element
      if (!(canvas instanceof HTMLCanvasElement)) {
        console.error('Element is not a canvas for chart:', id);
        return;
      }

      // Check if Chart.js is loaded
      if (typeof Chart === 'undefined') {
        console.warn('Chart.js is not loaded');
        return;
      }

      // Try to get the drawing context
      let ctx;
      try {
        ctx = canvas.getContext('2d');
      } catch (e) {
        console.error('Error getting canvas context:', e);
        return;
      }

      if (!ctx) {
        console.error('Could not get 2D context for canvas');
        return;
      }

      const applyChartData = (labels, data, label) => {
        const color = prefs.primary;
        const isDark = prefs.theme === 'dark';
        const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)';
        const textColor = isDark ? '#a8b3c7' : '#55627a';

        if (chartInstances[id]) {
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
          if (typeof Chart === 'undefined') return;
          try {
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
                plugins: { legend: { display: false }, tooltip: { mode: 'index', intersect: false } },
                scales: {
                  x: { grid: { color: gridColor, drawBorder: false }, ticks: { color: textColor, font: { size: 10 } } },
                  y: { grid: { color: gridColor, drawBorder: false, borderDash: [4, 4] }, ticks: { color: textColor, font: { size: 10 } }, beginAtZero: true }
                },
                interaction: { mode: 'nearest', axis: 'x', intersect: false }
              }
            });
          } catch (e) {
            console.error('Error creating Chart.js instance:', e);
          }
        }
      };

      fetchChartDataFromAPI(metric, period)
        .then((res) => applyChartData(res.labels, res.data, res.label))
        .catch(() => {
          const { labels, data, label } = getEmptyChartData(metric, period);
          applyChartData(labels, data, label);
        });
    } catch (e) {
      console.error('Error in createOrUpdateChart:', e);
    }
  }

  function renderCharts() {
    const grid = document.querySelector('[data-charts-grid]');
    if (!(grid instanceof HTMLElement)) return;
    
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
      grid.innerHTML = '<div style="padding:20px; text-align:center; color: #666; grid-column: 1/-1;">Les graphiques ne peuvent pas être chargés. Veuillez vérifier votre connexion Internet.</div>';
      return;
    }

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
  
  // Wait for Chart.js to load before rendering charts
  function waitForChartAndRender(timeout = 5000, interval = 100) {
    const startTime = Date.now();
    const checkChart = () => {
      if (typeof Chart !== 'undefined') {
        try {
          renderCharts();
        } catch (e) {
          console.error('Error rendering charts:', e);
        }
      } else if (Date.now() - startTime < timeout) {
        setTimeout(checkChart, interval);
      } else {
        // Timeout: Chart.js failed to load, render with fallback
        console.warn('Chart.js failed to load within timeout');
        try {
          renderCharts();
        } catch (e) {
          console.error('Error in renderCharts fallback:', e);
        }
      }
    };
    checkChart();
  }
  
  waitForChartAndRender();

  window.addEventListener('hashchange', () => {
    const v = getViewFromHash();
    if (!v) return;
    prefs.lastView = v;
    savePrefs(prefs);
    showView(v);
  });

  document.getElementById('formCreateOrder')?.addEventListener('submit', (e) => {
    e.preventDefault();
    const userEl = document.getElementById('newOrderUser');
    const totalEl = document.getElementById('newOrderTotal');
    const addressEl = document.getElementById('newOrderAddress');
    const cityEl = document.getElementById('newOrderCity');
    const postalEl = document.getElementById('newOrderPostal');
    const countryEl = document.getElementById('newOrderCountry');
    const statusEl = document.getElementById('newOrderStatus');
    const notesEl = document.getElementById('newOrderNotes');
    const user_id = userEl?.value;
    if (!user_id) {
      toast('Choisissez un client.');
      return;
    }
    const payload = {
      user_id: user_id,
      total_amount: totalEl?.value || 0,
      shipping_address: addressEl?.value || 'À renseigner',
      shipping_city: cityEl?.value || 'Ville',
      shipping_postal_code: postalEl?.value || '',
      shipping_country: countryEl?.value || 'Pays',
      status: statusEl?.value || 'pending',
      notes: notesEl?.value || '',
    };
    fetch('/admin_custom/api/orders/', {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
      .then((r) => r.json().then((data) => ({ ok: r.ok, status: r.status, data })))
      .then(({ ok, data }) => {
        if (ok && data && data.order_number) {
          document.getElementById('modalCreateOrder')?.close();
          toast('Commande ' + data.order_number + ' créée.');
          ordersGridState.page = 1;
          fetchGridData('orders');
        } else {
          toast(data?.error || 'Erreur lors de la création.');
        }
      })
      .catch(() => toast('Erreur réseau.'));
  });

  document.addEventListener('submit', (e) => {
    const form = e.target;
    if (form?.id !== 'formCreateClient') return;
    e.preventDefault();
    const username = (document.getElementById('newClientUsername')?.value || '').trim();
    if (!username) {
      toast('Identifiant obligatoire.');
      return;
    }
    const submitBtn = document.getElementById('btnCreateClient');
    const btnLabel = submitBtn ? submitBtn.textContent : '';
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Cr\u00e9ation...';
    }
    const payload = {
      username: username,
      email: (document.getElementById('newClientEmail')?.value || '').trim(),
      first_name: (document.getElementById('newClientFirst')?.value || '').trim(),
      last_name: (document.getElementById('newClientLast')?.value || '').trim(),
      password: (document.getElementById('newClientPassword')?.value || '').trim() || undefined,
    };
    var headers = { 'Content-Type': 'application/json' };
    var csrfToken = getCookie('csrftoken');
    if (csrfToken) headers['X-CSRFToken'] = csrfToken;
    fetch('/admin_custom/api/clients/', {
      method: 'POST',
      credentials: 'same-origin',
      headers: headers,
      body: JSON.stringify(payload),
    })
      .then(function (r) {
        return r.text().then(function (text) {
          var data = null;
          try { data = text ? JSON.parse(text) : {}; } catch (_) {}
          return { ok: r.ok, data: data || {}, status: r.status };
        });
      })
      .then(function (result) {
        var ok = result.ok;
        var data = result.data || {};
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = btnLabel || 'Cr\u00e9er le client';
        }
        if (ok && data && data.username) {
          form.reset();
          customersGridState.page = 1;
          var createdUsername = data.username;
          fetchGridData('customers').then(function () {
            toast('Client \u00ab ' + createdUsername + ' \u00bb cr\u00e9\u00e9. Liste mise \u00e0 jour.');
            var listEl = document.getElementById('customersListBlock');
            if (listEl) listEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
            var firstInput = document.getElementById('newClientUsername');
            if (firstInput) firstInput.focus();
          }).catch(function () {
            toast('Client cr\u00e9\u00e9. Rechargez la liste si besoin.');
          });
        } else {
          var errMsg = data.error || 'Erreur lors de la cr\u00e9ation.';
          if (result.status === 400) console.error('[Clients API 400]', errMsg, data);
          toast(errMsg);
        }
      })
      .catch(function (err) {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = btnLabel || 'Cr\u00e9er le client';
        }
        toast('Erreur r\u00e9seau.');
      });
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
      window.location.href = '/admin-console/logout/';
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
      toast('Export non disponible.');
      return;
    }

    if (action === 'create-order') {
      const modal = document.getElementById('modalCreateOrder');
      if (modal && typeof modal.showModal === 'function') {
        const sel = document.getElementById('newOrderUser');
        if (sel) {
          sel.innerHTML = '<option value="">Chargement...</option>';
          fetch('/admin_custom/api/grid-data/?model=User&columns=id&columns=username', { credentials: 'same-origin' })
            .then((r) => r.ok ? r.json() : Promise.reject())
            .then((res) => {
              sel.innerHTML = '';
              (res.data || []).forEach((row) => {
                const opt = document.createElement('option');
                opt.value = row.id || '';
                opt.textContent = row.username || row.id || '—';
                sel.appendChild(opt);
              });
            })
            .catch(() => { sel.innerHTML = '<option value="">Aucun utilisateur</option>'; });
        }
        modal.showModal();
      }
      return;
    }

    if (action === 'close-modal-create-order') {
      const modal = document.getElementById('modalCreateOrder');
      if (modal && typeof modal.close === 'function') modal.close();
      return;
    }

    if (action === 'create-client') {
      const block = document.getElementById('customersCreateBlock');
      if (block) block.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setTimeout(function () {
        var firstInput = document.getElementById('newClientUsername');
        if (firstInput) firstInput.focus();
      }, 300);
      return;
    }

    if (action === 'apply-filters-customers') {
      customersGridState.page = 1;
      fetchGridData('customers');
      toast('Filtres appliqués.');
      return;
    }

    if (action === 'reset-filters-customers') {
      const q = document.getElementById('qCustomers');
      const qMain = document.getElementById('qCustomersMain');
      if (q) q.value = '';
      if (qMain) qMain.value = '';
      customersGridState.page = 1;
      fetchGridData('customers');
      toast('Filtres réinitialisés.');
      return;
    }

    if (action === 'apply-filters') {
      ordersGridState.page = 1;
      fetchGridData('orders');
      toast('Filtres appliqués.');
      return;
    }

    if (action === 'reset-filters') {
      const q = document.getElementById('qOrders');
      if (q) q.value = '';
      const s = document.getElementById('statusOrders');
      if (s) s.selectedIndex = 0;
      const d = document.getElementById('dateOrders');
      if (d) d.selectedIndex = 1;
      ordersGridState.page = 1;
      fetchGridData('orders');
      toast('Filtres réinitialisés.');
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
    
    if (action === 'prev-page') {
      if (prefs.lastView === 'orders' && ordersGridState.page > 1) {
        ordersGridState.page--;
        fetchGridData('orders');
      }
      return;
    }
    if (action === 'next-page') {
      if (prefs.lastView === 'orders') {
        const maxPage = Math.ceil(ordersGridState.totalCount / ordersGridState.pageSize);
        if (ordersGridState.page < maxPage) {
          ordersGridState.page++;
          fetchGridData('orders');
        }
      }
      return;
    }

    if (action === 'prev-page-customers') {
      if (prefs.lastView === 'customers' && customersGridState.page > 1) {
        customersGridState.page--;
        fetchGridData('customers');
      }
      return;
    }
    if (action === 'next-page-customers') {
      if (prefs.lastView === 'customers') {
        const maxPage = Math.ceil(customersGridState.totalCount / customersGridState.pageSize);
        if (customersGridState.page < maxPage) {
          customersGridState.page++;
          fetchGridData('customers');
        }
      }
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

    if (action === 'show-all-products') {
      prefs.lastView = 'products-list';
      savePrefs(prefs);
      showView('products-list');
      setHash('products-list');
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

  // ========== DYNAMISER LES PARAMETRES ==========
  function applySettingsFeedback(element) {
    if (!element || !(element instanceof HTMLElement)) return;
    const row = element.closest('.settings__row');
    if (row) {
      row.classList.add('saving');
      setTimeout(() => row.classList.remove('saving'), 600);
    }
    showSettingsFeedback(element);
  }

  function showSettingsFeedback(element) {
    let feedback = element.querySelector('.settings-feedback');
    if (!feedback) {
      feedback = document.createElement('span');
      feedback.className = 'settings-feedback';
      element.appendChild(feedback);
    }
    feedback.classList.add('show');
    setTimeout(() => feedback.classList.remove('show'), 2000);
  }

  // Boutons Light/Dark avec transition fluide
  document.addEventListener('click', (e) => {
    const lightBtn = e.target.closest('button[data-action="set-light"]');
    const darkBtn = e.target.closest('button[data-action="set-dark"]');

    if (lightBtn) {
      prefs.theme = 'light';
      savePrefs(prefs);
      document.documentElement.classList.add('theme-transitioning');
      setThemeMode('light');
      updateThemeButtons('light');
      applySettingsFeedback(lightBtn);
      setTimeout(() => document.documentElement.classList.remove('theme-transitioning'), 400);
    }

    if (darkBtn) {
      prefs.theme = 'dark';
      savePrefs(prefs);
      document.documentElement.classList.add('theme-transitioning');
      setThemeMode('dark');
      updateThemeButtons('dark');
      applySettingsFeedback(darkBtn);
      setTimeout(() => document.documentElement.classList.remove('theme-transitioning'), 400);
    }
  });

  function updateThemeButtons(theme) {
    const lightBtn = document.querySelector('button[data-action="set-light"]');
    const darkBtn = document.querySelector('button[data-action="set-dark"]');
    if (lightBtn) lightBtn.classList.toggle('is-active', theme === 'light');
    if (darkBtn) darkBtn.classList.toggle('is-active', theme === 'dark');
  }

  // Initialize theme buttons
  updateThemeButtons(prefs.theme);

  // Améliorer la sélection de couleur
  const colorInputs = document.querySelectorAll('input[type="color"][data-action="primary-color"]');
  colorInputs.forEach((input) => {
    input.addEventListener('input', (e) => {
      const color = clampHex(e.target.value);
      prefs.primary = color;
      setPrimaryColor(color);
      // Animation de transition
      document.documentElement.style.transition = 'all 0.3s ease';
    });

    input.addEventListener('change', (e) => {
      const color = clampHex(e.target.value);
      prefs.primary = color;
      savePrefs(prefs);
      setPrimaryColor(color);
      applySettingsFeedback(input);
      document.documentElement.style.transition = '';
    });
  });

  // Bouton couleur aléatoire avec animation
  document.addEventListener('click', (e) => {
    const randomBtn = e.target.closest('button[data-action="random-color"]');
    if (!randomBtn) return;

    const newColor = randomColor();
    prefs.primary = newColor;
    const colorInputs = document.querySelectorAll('input[type="color"][data-action="primary-color"]');
    colorInputs.forEach((input) => {
      input.value = newColor;
    });
    setPrimaryColor(newColor);
    savePrefs(prefs);
    
    // Ajouter une animation au bouton
    randomBtn.style.transform = 'scale(0.95) rotate(-5deg)';
    setTimeout(() => {
      randomBtn.style.transform = '';
      applySettingsFeedback(randomBtn);
    }, 100);
  });

  // Sauvegarde avec feedback
  document.addEventListener('click', (e) => {
    const saveBtn = e.target.closest('button[data-action="save-theme"]');
    if (!saveBtn) return;

    savePrefs(prefs);
    saveBtn.style.background = 'var(--success)';
    saveBtn.style.color = 'rgba(0,0,0,0.8)';
    setTimeout(() => {
      saveBtn.style.background = '';
      saveBtn.style.color = '';
    }, 1500);
    applySettingsFeedback(saveBtn);
  });

  // Réinitialiser avec confirmation
  document.addEventListener('click', (e) => {
    const resetBtn = e.target.closest('button[data-action="reset-theme"]');
    if (!resetBtn) return;

    if (!confirm('Voulez-vous réinitialiser tous les paramètres ?')) return;

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
    savePrefs(prefs);
    setThemeMode(prefs.theme);
    setPrimaryColor(prefs.primary);
    updateThemeButtons(prefs.theme);
    
    // Mettre à jour les inputs
    const colorInputs = document.querySelectorAll('input[type="color"][data-action="primary-color"]');
    colorInputs.forEach((input) => { input.value = prefs.primary; });
    
    showSettingsFeedback(resetBtn);
  });

  // Améliorer les cartes d'interface
  document.querySelectorAll('a[href="/admin/"], a[href="/admin/switch-interface/?to=modern"]').forEach((card) => {
    card.classList.add('settings-interface-card');
    const isCurrent = card.getAttribute('href') === '/admin-console/';
    if (isCurrent) card.classList.add('is-current');
    
    card.addEventListener('mouseenter', function() {
      this.style.animation = 'none';
      setTimeout(() => this.style.animation = '', 10);
    });
  });
})();

