/**
 * Admin Custom - JavaScript principal
 * Thèmes, graphiques, interactions, toasts, modales
 */

(function () {
  'use strict';

  const STORAGE_THEME = 'admin_custom_theme';
  const THEMES = ['bleu-moderne', 'emeraude', 'coucher-soleil', 'sombre'];

  // ========== THÈME ==========
  function initTheme() {
    const saved = localStorage.getItem(STORAGE_THEME);
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = saved || (prefersDark ? 'sombre' : 'bleu-moderne');
    document.documentElement.setAttribute('data-theme', theme);
    return theme;
  }

  function setTheme(theme) {
    if (!THEMES.includes(theme)) return;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_THEME, theme);
    showToast('Thème appliqué : ' + theme, 'success');
  }

  window.setAdminTheme = setTheme;
  window.getAdminTheme = () => document.documentElement.getAttribute('data-theme') || initTheme();

  // ========== SIDEBAR ==========
  function initSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.querySelector('.header-toggle-sidebar');
    const mainWrapper = document.querySelector('.main-wrapper');
    if (!sidebar || !toggleBtn) return;

    const collapsed = localStorage.getItem('admin_sidebar_collapsed') === 'true';
    if (collapsed) {
      sidebar.classList.add('collapsed');
      mainWrapper && mainWrapper.classList.add('sidebar-collapsed');
    }

    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
      mainWrapper && mainWrapper.classList.toggle('sidebar-collapsed');
      localStorage.setItem('admin_sidebar_collapsed', sidebar.classList.contains('collapsed'));
    });

    // Mobile: ouvrir sidebar au clic
    const overlay = document.querySelector('.sidebar-overlay');
    if (overlay) {
      overlay.addEventListener('click', () => sidebar.classList.remove('open'));
    }
  }

  // ========== RECHERCHE GLOBALE (Ctrl+K) ==========
  function initSearch() {
    const searchInput = document.querySelector('.header-search input');
    if (!searchInput) return;

    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        searchInput.focus();
        searchInput.select();
      }
    });
  }

  // ========== DROPDOWNS ==========
  // Les dropdowns du header (notifications, profil) sont gérés par le script inline dans base_site.html
  function initDropdowns() {
    document.querySelectorAll('.dropdown').forEach((dropdown) => {
      if (dropdown.closest && dropdown.closest('.header-right')) return;
      const trigger = dropdown.querySelector('[data-dropdown-trigger]') || dropdown.querySelector('.user-menu-trigger') || dropdown.querySelector('button') || dropdown.firstElementChild;
      if (!trigger) return;
      trigger.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        dropdown.classList.toggle('open');
      });
      const menu = dropdown.querySelector('.dropdown-menu');
      if (menu) menu.addEventListener('click', function (e) { e.stopPropagation(); });
    });
    document.addEventListener('click', function () {
      document.querySelectorAll('.dropdown.open').forEach(function (d) {
        d.classList.remove('open');
      });
    });
  }

  // ========== TOAST ==========
  function getToastContainer() {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }
    return container;
  }

  function showToast(message, type = 'info', duration = 4000) {
    const container = getToastContainer();
    const toast = document.createElement('div');
    toast.className = 'toast ' + type;
    const icons = { success: 'fa-check-circle', error: 'fa-times-circle', warning: 'fa-exclamation-triangle', info: 'fa-info-circle' };
    toast.innerHTML = `
      <i class="fa-solid ${icons[type] || icons.info}"></i>
      <span>${message}</span>
      <button class="toast-close" aria-label="Fermer">&times;</button>
    `;
    toast.querySelector('.toast-close').addEventListener('click', () => removeToast(toast));
    container.appendChild(toast);
    if (duration > 0) setTimeout(() => removeToast(toast), duration);
    return toast;
  }

  function removeToast(toast) {
    toast.style.animation = 'toast-in 0.2s ease reverse';
    setTimeout(() => toast.remove(), 200);
  }

  window.showToast = showToast;

  // ========== MODALES ==========
  function initModals() {
    document.querySelectorAll('[data-modal-open]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const id = btn.getAttribute('data-modal-open');
        const modal = document.getElementById(id);
        if (modal) openModal(modal);
      });
    });
    document.querySelectorAll('[data-modal-close]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const modal = btn.closest('.modal');
        if (modal) closeModal(modal);
      });
    });
    document.querySelectorAll('.modal-backdrop').forEach((backdrop) => {
      backdrop.addEventListener('click', () => {
        const modal = document.querySelector('.modal.show');
        if (modal) closeModal(modal);
      });
    });
  }

  function openModal(modal) {
    const backdrop = document.querySelector('.modal-backdrop') || (() => {
      const b = document.createElement('div');
      b.className = 'modal-backdrop';
      document.body.appendChild(b);
      b.addEventListener('click', () => closeModal(modal));
      return b;
    })();
    if (!document.querySelector('.modal-backdrop')) {
      const b = document.createElement('div');
      b.className = 'modal-backdrop';
      document.body.appendChild(b);
      b.addEventListener('click', () => closeModal(modal));
    }
    document.querySelector('.modal-backdrop').classList.add('show');
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
  }

  function closeModal(modal) {
    if (!modal) return;
    modal.classList.remove('show');
    const backdrop = document.querySelector('.modal-backdrop');
    if (backdrop) backdrop.classList.remove('show');
    document.body.style.overflow = '';
  }

  window.openModal = openModal;
  window.closeModal = closeModal;

  // ========== INLINES (ajout/suppression lignes) ==========
  function initInlines() {
    document.querySelectorAll('.add-inline-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        const container = btn.closest('.inline-group')?.querySelector('.inline-rows') || btn.previousElementSibling;
        if (!container) return;
        const template = container.getAttribute('data-inline-template');
        if (template) {
          const div = document.createElement('div');
          div.className = 'inline-row';
          div.innerHTML = template;
          container.appendChild(div);
          initInlineRow(div);
        } else {
          const firstRow = container.querySelector('.inline-row');
          if (firstRow) {
            const clone = firstRow.cloneNode(true);
            clone.querySelectorAll('input, select, textarea').forEach((el) => { el.value = ''; el.name = el.name ? el.name.replace(/-\d+-/, '-' + (container.children.length) + '-') : ''; });
            container.appendChild(clone);
            initInlineRow(clone);
          }
        }
      });
    });
    document.querySelectorAll('.inline-group').forEach((group) => {
      group.addEventListener('click', (e) => {
        const removeBtn = e.target.closest('.btn-remove-inline');
        if (removeBtn) {
          const row = removeBtn.closest('.inline-row');
          if (row && group.querySelectorAll('.inline-row').length > 1) {
            row.style.animation = 'toast-in 0.2s ease reverse';
            setTimeout(() => row.remove(), 200);
          }
        }
      });
    });
  }

  function initInlineRow(row) {
    row.querySelectorAll('.form-control').forEach((el) => el.addEventListener('input', () => {}));
  }

  // ========== UPLOAD FICHIER + APERÇU ==========
  function initFileUpload() {
    document.querySelectorAll('.file-upload-zone').forEach((zone) => {
      const input = zone.querySelector('input[type="file"]');
      const preview = zone.querySelector('.file-preview') || (() => {
        const p = document.createElement('div');
        p.className = 'file-preview';
        p.style.display = 'none';
        zone.appendChild(p);
        return p;
      })();
      if (!input) return;

      ['change', 'drop', 'dragover', 'dragleave'].forEach((ev) => {
        zone.addEventListener(ev, (e) => {
          if (ev === 'dragover') { e.preventDefault(); zone.classList.add('dragover'); }
          if (ev === 'dragleave') zone.classList.remove('dragover');
          if (ev === 'drop') {
            e.preventDefault();
            zone.classList.remove('dragover');
            if (e.dataTransfer?.files?.length) input.files = e.dataTransfer.files;
          }
        });
      });
      zone.addEventListener('drop', (e) => e.preventDefault());
      zone.addEventListener('dragover', (e) => e.preventDefault());

      input.addEventListener('change', () => {
        const file = input.files?.[0];
        if (!file) { preview.style.display = 'none'; preview.innerHTML = ''; return; }
        preview.style.display = 'flex';
        const isImage = file.type.startsWith('image/');
        preview.innerHTML = `
          ${isImage ? `<img src="${URL.createObjectURL(file)}" alt="Aperçu">` : ''}
          <span class="file-name">${file.name}</span>
          <button type="button" class="btn btn-sm btn-danger btn-remove-file"><i class="fa-solid fa-trash"></i></button>
        `;
        preview.querySelector('.btn-remove-file')?.addEventListener('click', () => {
          input.value = '';
          preview.style.display = 'none';
          preview.innerHTML = '';
        });
      });
    });
  }

  // ========== GRAPHIQUES (Chart.js) ==========
  function initCharts() {
    if (typeof Chart === 'undefined') return;

    document.querySelectorAll('[data-chart]').forEach((canvas) => {
      const type = canvas.getAttribute('data-chart');
      const primary = getComputedStyle(document.documentElement).getPropertyValue('--color-primary').trim() || '#3B82F6';
      const secondary = getComputedStyle(document.documentElement).getPropertyValue('--color-secondary').trim() || '#8B5CF6';
      const accent = getComputedStyle(document.documentElement).getPropertyValue('--color-accent').trim() || '#06B6D4';

      if (type === 'line') {
        new Chart(canvas, {
          type: 'line',
          data: {
            labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc'],
            datasets: [
              { label: 'Utilisateurs', data: [12, 19, 15, 25, 22, 30, 28, 35, 42, 38, 45, 52], borderColor: primary, backgroundColor: primary + '20', fill: true, tension: 0.4 },
              { label: 'Commandes', data: [8, 14, 12, 18, 20, 24, 22, 28, 32, 30, 36, 40], borderColor: secondary, backgroundColor: secondary + '20', fill: true, tension: 0.4 }
            ]
          },
          options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true } } }
        });
      }
      if (type === 'bar') {
        new Chart(canvas, {
          type: 'bar',
          data: {
            labels: ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'],
            datasets: [{ label: 'Vues', data: [65, 78, 90, 81, 96, 105, 92], backgroundColor: primary }, { label: 'Conversions', data: [12, 19, 15, 22, 18, 24, 20], backgroundColor: accent }]
          },
          options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true } } }
        });
      }
      if (type === 'doughnut') {
        new Chart(canvas, {
          type: 'doughnut',
          data: {
            labels: ['Actifs', 'En attente', 'Archivés', 'Brouillons'],
            datasets: [{ data: [45, 25, 20, 10], backgroundColor: [primary, secondary, accent, '#94A3B8'] }]
          },
          options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }
        });
      }
    });
  }

  // ========== PAGINATION / FILTRES (événements) ==========
  function initFilters() {
    document.querySelectorAll('.data-table th.sortable').forEach((th) => {
      th.addEventListener('click', () => {
        const table = th.closest('.data-table');
        const idx = Array.from(th.parentNode.children).indexOf(th);
        const dir = th.getAttribute('data-sort-dir') !== 'asc' ? 'asc' : 'desc';
        th.setAttribute('data-sort-dir', dir);
        const rows = Array.from(table.querySelectorAll('tbody tr'));
        rows.sort((a, b) => {
          const va = a.children[idx]?.textContent?.trim() || '';
          const vb = b.children[idx]?.textContent?.trim() || '';
          return dir === 'asc' ? (va.localeCompare(vb)) : (vb.localeCompare(va));
        });
        rows.forEach((r) => table.querySelector('tbody').appendChild(r));
      });
    });
  }

  // ========== INIT ==========
  function init() {
    initTheme();
    initSidebar();
    initSearch();
    initDropdowns();
    initModals();
    initInlines();
    initFileUpload();
    initCharts();
    initFilters();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
