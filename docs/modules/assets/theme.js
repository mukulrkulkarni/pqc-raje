/**
 * Theme toggle for ELECTRE III module tutorials.
 * Stores preference in localStorage, applies to <html data-theme>.
 * Supports: light, dark, system (auto-detect).
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

  function setStoredTheme(theme) {
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch (e) {}
  }

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    updateToggleButtons(theme);
  }

  function updateToggleButtons(active) {
    var buttons = document.querySelectorAll('[data-theme-toggle]');
    buttons.forEach(function(btn) {
      var value = btn.getAttribute('data-theme-toggle');
      btn.classList.toggle('active', value === active);
      btn.setAttribute('aria-pressed', value === active);
    });
  }

  function handleToggleClick(e) {
    var btn = e.target.closest('[data-theme-toggle]');
    if (!btn) return;
    var theme = btn.getAttribute('data-theme-toggle');
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
