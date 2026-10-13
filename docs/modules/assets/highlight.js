/**
 * @file highlight.js
 * @source In-house (ELECTRE III project)
 * @license Project license (see repository root)
 *
 * Range row selection for ELECTRE III module tutorials.
 * Features:
 * - Click range badge to toggle row selection (highlight)
 * - Hash navigation: #row-R1 scrolls to row and selects it
 * - Click again to clear selection
 * - Respects prefers-reduced-motion
 * - Debug mode: ?debug=1 for console logging
 */
(function() {
  'use strict';

  // Constants
  var SELECTED_CLASS = 'range-selected';
  var ROW_PREFIX = 'row-';

  // State
  var DEBUG = window.location.search.indexOf('debug=1') !== -1;
  var currentRange = null;
  var prefersReducedMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function log() {
    if (DEBUG && console && console.log) {
      console.log.apply(console, ['[highlight]'].concat(Array.prototype.slice.call(arguments)));
    }
  }

  // ========================================================================
  // Selection & Highlight
  // ========================================================================

  function clearSelection() {
    var selected = document.querySelectorAll('.' + SELECTED_CLASS);
    selected.forEach(function(el) {
      el.classList.remove(SELECTED_CLASS);
    });
    currentRange = null;
    log('Selection cleared');
  }

  function selectRow(rangeId) {
    if (!rangeId) return false;

    var rowId = ROW_PREFIX + rangeId;
    var row = document.getElementById(rowId);

    // Guard: missing row - no-op without throwing
    if (!row) {
      log('selectRow: row not found', rowId);
      return false;
    }

    log('selectRow:', rangeId, 'current:', currentRange);

    // Toggle off if same range
    if (currentRange === rangeId) {
      clearSelection();
      if (history.replaceState) {
        history.replaceState(null, '', location.pathname + location.search);
      }
      return false;
    }

    clearSelection();
    currentRange = rangeId;
    row.classList.add(SELECTED_CLASS);

    // Update URL hash
    if (history.pushState) {
      history.pushState(null, '', '#' + rowId);
    }

    return true;
  }

  function scrollToRow(rangeId) {
    var rowId = ROW_PREFIX + rangeId;
    var row = document.getElementById(rowId);

    // Guard: missing row - no-op without throwing
    if (!row) {
      log('scrollToRow: row not found', rowId);
      return;
    }

    var scrollBehavior = prefersReducedMotion ? 'auto' : 'smooth';
    row.scrollIntoView({ behavior: scrollBehavior, block: 'start' });
    log('scrollToRow:', rowId, 'reducedMotion:', prefersReducedMotion);
  }

  // ========================================================================
  // Click Handler
  // ========================================================================

  function handleClick(e) {
    var badge = e.target.closest('[data-range]');
    if (!badge) return;

    var rangeId = badge.getAttribute('data-range');
    if (!rangeId) return;

    e.preventDefault();
    e.stopPropagation();

    var wasSelected = currentRange === rangeId;
    var selected = selectRow(rangeId);

    // Scroll to row if newly selected (not toggle-off)
    if (selected && !wasSelected) {
      scrollToRow(rangeId);
    }
  }

  // ========================================================================
  // Hash Navigation
  // ========================================================================

  function handleHashChange() {
    var hash = location.hash.slice(1);
    log('hashchange:', hash);

    // Match row-R1, row-R2, etc.
    var match = hash.match(/^row-(R\d+)$/);
    if (match) {
      var rangeId = match[1];
      selectRow(rangeId);
      scrollToRow(rangeId);
    }
  }

  // ========================================================================
  // Initialization
  // ========================================================================

  function init() {
    log('Initializing, DEBUG:', DEBUG, 'reducedMotion:', prefersReducedMotion);

    // Event listeners
    document.addEventListener('click', handleClick, true);
    window.addEventListener('hashchange', handleHashChange);

    // Handle initial hash
    if (location.hash) {
      setTimeout(handleHashChange, 50);
    }

    log('Initialization complete');
  }

  // Test API
  if (typeof window !== 'undefined') {
    window.highlightModule = {
      selectRow: selectRow,
      clearSelection: clearSelection,
      scrollToRow: scrollToRow,
      getCurrentRange: function() { return currentRange; },
      ROW_PREFIX: ROW_PREFIX,
      debug: DEBUG
    };
  }

  // Start
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
