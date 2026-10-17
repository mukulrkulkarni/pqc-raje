/**
 * @file theme.js
 * @source In-house (ELECTRE III project)
 * @license Project license (see repository root)
 *
 * Theme toggle for ELECTRE III module tutorials (Layout 2 parity).
 * Stores preference in localStorage, applies to <html data-theme>.
 * Supports: light, dark, system (auto-detect).
 *
 * Works in both served mode (/docs/modules/config/assets/theme.js) and
 * file:// mode (relative assets/theme.js path). localStorage may be
 * unavailable in file:// mode on some browsers - falls back to system theme.
 */
(function() {
  'use strict';

  var STORAGE_KEY = 'electre3-theme';
  var root = document.documentElement;

  function getStoredTheme() {
    try {
      return localStorage.getItem(STORAGE_KEY) || 'system';
    } catch (e) {
      return 'system';
    }
  }

  function resolveSystemTheme() {
    if (!window.matchMedia) return 'light';
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function setStoredTheme(theme) {
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch (e) {
      // localStorage unavailable (file:// mode in some browsers)
    }
  }

  function applyTheme(theme) {
    var effective = theme === 'system' ? resolveSystemTheme() : theme;
    root.setAttribute('data-theme', effective);
    updateToggleButtons(theme);
  }

  function updateToggleButtons(active) {
    // Support both data-theme-toggle (legacy) and data-theme-value (Layout 2)
    var buttons = document.querySelectorAll('[data-theme-toggle], [data-theme-value]');
    buttons.forEach(function(btn) {
      var value = btn.getAttribute('data-theme-toggle') || btn.getAttribute('data-theme-value');
      var isActive = value === active;
      btn.classList.toggle('active', isActive);
      btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');
    });
  }

  function handleToggleClick(e) {
    // Support both data-theme-toggle (legacy) and data-theme-value (Layout 2)
    var btn = e.target.closest('[data-theme-toggle], [data-theme-value]');
    if (!btn) return;
    var theme = btn.getAttribute('data-theme-toggle') || btn.getAttribute('data-theme-value');
    if (!theme) return;
    setStoredTheme(theme);
    applyTheme(theme);
  }

  // Apply stored theme immediately (before DOMContentLoaded to prevent flash)
  applyTheme(getStoredTheme());

  // Setup toggle listeners after DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    document.addEventListener('click', handleToggleClick);
    updateToggleButtons(getStoredTheme());
  }
})();
