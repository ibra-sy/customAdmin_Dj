/**
 * Theme Manager - Gestion centralisée des thèmes
 * Supporte les thèmes modernes et classiques
 * Avec persistance locale et backend
 */

(function() {
    'use strict';

    // Configuration des thèmes disponibles
    const THEME_CONFIG = {
        modern: ['bleu-moderne', 'emeraude', 'coucher-soleil', 'sombre'],
        classic: ['default', 'nostalgie', 'ocean', 'sunset', 'forest', 'dark', 'liquid-glass']
    };

    const STORAGE_KEYS = {
        modern: 'admin_modern_theme',
        classic: 'admin-theme'
    };

    const DEFAULT_THEMES = {
        modern: 'bleu-moderne',
        classic: 'default'
    };

    /**
     * Détermine quel type d'interface est en cours d'utilisation
     */
    function getInterfaceType() {
        const htmlClass = document.documentElement.className;
        const bodyClass = document.body.className;
        
        // Vérifier si c'est l'interface moderne
        if (document.querySelector('.admin-layout') || 
            htmlClass.includes('modern') || 
            bodyClass.includes('modern') ||
            document.querySelector('[data-interface="modern"]')) {
            return 'modern';
        }
        
        return 'classic';
    }

    /**
     * Obtient le thème actuellement appliqué
     */
    function getCurrentTheme() {
        const interfaceType = getInterfaceType();
        const storageKey = STORAGE_KEYS[interfaceType];
        const validThemes = THEME_CONFIG[interfaceType];
        const defaultTheme = DEFAULT_THEMES[interfaceType];
        
        const saved = localStorage.getItem(storageKey);
        const htmlTheme = document.documentElement.getAttribute('data-theme');
        
        const theme = htmlTheme || saved || defaultTheme;
        
        // Valider que le thème existe
        if (validThemes.includes(theme)) {
            return theme;
        }
        
        return defaultTheme;
    }

    /**
     * Sauvegarde les préférences utilisateur sur le backend
     */
    function savePreferenceToBackend(theme, interfaceType) {
        // Récupérer le token CSRF
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                         document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1] ||
                         null;
        
        const data = {};
        
        if (interfaceType === 'modern') {
            data.theme_modern = theme;
        } else {
            data.theme_classic = theme;
        }
        
        // Envoyer une requête POST au serveur
        fetch('/admin/api/save-preference/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken || ''
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (!result.success) {
                console.warn('Erreur lors de la sauvegarde des préférences:', result.error);
            }
        })
        .catch(error => {
            // Ignorer les erreurs réseau - localStorage est suffisant
            console.debug('Sauvegarde backend impossible, utilisation du localStorage', error);
        });
    }

    /**
     * Applique un thème donné
     */
    function applyTheme(theme) {
        const interfaceType = getInterfaceType();
        const validThemes = THEME_CONFIG[interfaceType];
        const storageKey = STORAGE_KEYS[interfaceType];
        
        // Valider le thème
        if (!validThemes.includes(theme)) {
            console.warn(`Theme "${theme}" is not valid for ${interfaceType} interface`);
            return false;
        }
        
        // Appliquer le thème
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem(storageKey, theme);
        
        // Sauvegarder sur le backend (asynchrone, ne bloque pas)
        savePreferenceToBackend(theme, interfaceType);
        
        // Déclencher un événement personnalisé
        window.dispatchEvent(new CustomEvent('themeChanged', {
            detail: { theme, interfaceType }
        }));
        
        return true;
    }

    /**
     * Initialise le thème au chargement de la page
     */
    function initializeTheme() {
        const interfaceType = getInterfaceType();
        const currentTheme = getCurrentTheme();
        
        // Appliquer le thème
        applyTheme(currentTheme);
        
        // Initialiser les boutons de sélection de thème
        initializeThemeButtons();
    }

    /**
     * Configure les événements des boutons de sélection de thème
     */
    function initializeThemeButtons() {
        // Pour les boutons avec la classe 'theme-option-modern'
        const modernButtons = document.querySelectorAll('.theme-option-modern');
        modernButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const theme = button.getAttribute('data-theme');
                const interfaceType = getInterfaceType();
                
                // Appliquer le thème
                if (applyTheme(theme)) {
                    // Mettre à jour l'UI
                    updateThemeButtonsUI(modernButtons, theme);
                }
            });
        });
        
        // Pour les boutons dans l'interface classique
        const classicButtons = document.querySelectorAll('.theme-option');
        classicButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const theme = button.getAttribute('data-theme');
                
                if (applyTheme(theme)) {
                    updateThemeButtonsUI(classicButtons, theme);
                }
            });
        });
        
        // Mettre à jour l'UI pour refléter le thème actuel
        const currentTheme = getCurrentTheme();
        updateThemeButtonsUI(modernButtons, currentTheme);
        updateThemeButtonsUI(classicButtons, currentTheme);
    }

    /**
     * Met à jour l'interface des boutons de sélection
     */
    function updateThemeButtonsUI(buttons, activeTheme) {
        buttons.forEach(button => {
            const theme = button.getAttribute('data-theme');
            const isActive = theme === activeTheme;
            
            // Mettre à jour les classes
            button.classList.toggle('active', isActive);
            
            // Mettre à jour les styles inline si nécessaire
            if (button.style) {
                if (isActive) {
                    button.style.borderColor = 'var(--color-primary)';
                    button.style.backgroundColor = 'var(--color-primary-light)';
                } else {
                    button.style.borderColor = 'var(--color-border)';
                    button.style.backgroundColor = '';
                }
            }
        });
    }

    /**
     * Exporte l'API globale
     */
    window.ThemeManager = {
        getCurrentTheme: getCurrentTheme,
        applyTheme: applyTheme,
        getInterfaceType: getInterfaceType,
        initialize: initializeTheme
    };

    // Initialiser quand le DOM est prêt
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeTheme);
    } else {
        initializeTheme();
    }

    // Rendre disponible une fonction globale pour le theme switching
    window.setModernTheme = function(theme) {
        return applyTheme(theme);
    };

})();
