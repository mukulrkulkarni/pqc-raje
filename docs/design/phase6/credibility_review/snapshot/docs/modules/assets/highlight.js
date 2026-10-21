/**
 * @file highlight.js
 * @source In-house (ELECTRE III project)
 * @license Project license (see repository root)
 *
 * Range row selection for ELECTRE III module tutorials (Layout 2 parity).
 * Features:
 * - Click row-head or sidebar jump to toggle row selection
 * - Selection aligns row top edge with sidebar jump item offset
 * - Progress indicator updates to show selected range
 * - Hash navigation: #row-R1 scrolls to row and selects it
 * - Click again to clear selection
 * - Respects prefers-reduced-motion
 * - Debug mode: ?debug=1 for console logging
 */
(function() {
  'use strict';

  // Constants - Layout 2 uses .row.sel not .range-row.range-selected
  var SELECTED_CLASS = 'sel';
  var ROW_PREFIX = 'row-';
  var JUMP_PREFIX = 'jump-';
  var PROG_TEXT_ID = 'prog-txt';
  var PROG_FILL_ID = 'prog-fill';
  var TOTAL_RANGES = 5;
  var BASELINE_RANGE = 'R1'; // Fixed baseline for alignment

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
  // Progress Indicator
  // ========================================================================

  /**
   * Get range number from range ID (e.g., 'R1' -> 1, 'R2' -> 2).
   * @param {string} rangeId - Range ID (e.g., 'R1')
   * @returns {number|null}
   */
  function getRangeNumber(rangeId) {
    if (!rangeId) return null;
    var match = rangeId.match(/^R(\d+)$/);
    return match ? parseInt(match[1], 10) : null;
  }

  /**
   * Update the progress indicator to show current selection.
   * @param {string|null} rangeId - Range ID or null if cleared
   */
  function updateProgressIndicator(rangeId) {
    var progText = document.getElementById(PROG_TEXT_ID);
    var progFill = document.getElementById(PROG_FILL_ID);

    // Guard: missing indicator elements - no-op without throwing
    if (!progText) {
      log('updateProgressIndicator: prog-txt element not found');
      return;
    }

    var rangeNum = getRangeNumber(rangeId);

    if (rangeNum) {
      // Update text to show selected range
      progText.textContent = 'Range ' + rangeNum + ' of ' + TOTAL_RANGES;
      progText.setAttribute('data-range', rangeId);

      // Update fill bar width (percentage of total)
      if (progFill) {
        var percent = (rangeNum / TOTAL_RANGES) * 100;
        progFill.style.width = percent + '%';
      }

      log('updateProgressIndicator: set to', rangeId, rangeNum + '/' + TOTAL_RANGES);
    } else {
      // Clear selection - show no selection state
      progText.textContent = 'No selection';
      progText.removeAttribute('data-range');

      // Reset fill bar
      if (progFill) {
        progFill.style.width = '0%';
      }

      log('updateProgressIndicator: cleared');
    }
  }

  // ========================================================================
  // Sidebar Alignment
  // ========================================================================

  /**
   * Get sidebar jump item element for a range ID.
   * @param {string} rangeId - Range ID (e.g., 'R1')
   * @returns {HTMLElement|null}
   */
  function getSidebarItem(rangeId) {
    return document.getElementById(JUMP_PREFIX + rangeId);
  }

  /**
   * Get the fixed baseline offset from sidebar R1 item.
   * All row selections align to this baseline.
   * @returns {number|null}
   */
  function getSidebarBaseline() {
    var baselineItem = getSidebarItem(BASELINE_RANGE);
    if (!baselineItem) {
      log('getSidebarBaseline: baseline element not found', JUMP_PREFIX + BASELINE_RANGE);
      return null;
    }
    return baselineItem.offsetTop;
  }

  /**
   * Align row selection with sidebar baseline (R1's top edge).
   * Scrolls main content so selected row's top aligns with sidebar R1 position.
   * @param {string} rangeId - Range ID (e.g., 'R1', 'R2', etc.)
   */
  function alignWithSidebar(rangeId) {
    var row = document.getElementById(ROW_PREFIX + rangeId);
    var mainScroll = document.getElementById('main-scroll');

    // Guard: missing row - no-op without throwing
    if (!row) {
      log('alignWithSidebar: row not found', ROW_PREFIX + rangeId);
      return;
    }

    // Guard: missing main container
    if (!mainScroll) {
      log('alignWithSidebar: main-scroll not found');
      return;
    }

    // Get fixed baseline from sidebar R1 item
    var baselineOffset = getSidebarBaseline();
    if (baselineOffset === null) {
      // Fallback to simple scrollIntoView if baseline missing
      var scrollBehavior = prefersReducedMotion ? 'auto' : 'smooth';
      row.scrollIntoView({ behavior: scrollBehavior, block: 'start' });
      return;
    }

    // Get row's position relative to viewport
    var rowRect = row.getBoundingClientRect();

    // Account for topbar sticky header (64px scroll-margin-top in CSS)
    var topbarOffset = 64;

    // Target position: align row top with baseline offset minus topbar
    var targetRowTop = baselineOffset - topbarOffset;

    // Current scroll position
    var currentScroll = window.scrollY || document.documentElement.scrollTop;

    // Row's current position relative to viewport
    var rowViewportTop = rowRect.top;

    // Target scroll = current scroll + (row's current viewport position - target position)
    var targetScroll = currentScroll + rowViewportTop - targetRowTop;

    // Clamp to valid range
    var maxScroll = document.documentElement.scrollHeight - window.innerHeight;
    targetScroll = Math.max(0, Math.min(targetScroll, maxScroll));

    log('alignWithSidebar:', rangeId,
        'baseline:', baselineOffset,
        'targetScroll:', targetScroll);

    // Scroll with appropriate behavior
    var scrollBehavior = prefersReducedMotion ? 'auto' : 'smooth';
    window.scrollTo({
      top: targetScroll,
      behavior: scrollBehavior
    });
  }

  // ========================================================================
  // Sidebar Active State
  // ========================================================================

  function clearSidebarActive() {
    var activeItems = document.querySelectorAll('.jump a.active');
    activeItems.forEach(function(el) {
      el.classList.remove('active');
    });
  }

  function setSidebarActive(rangeId) {
    clearSidebarActive();
    var sidebarItem = getSidebarItem(rangeId);
    if (sidebarItem) {
      sidebarItem.classList.add('active');
    }
  }

  // ========================================================================
  // Selection & Highlight
  // ========================================================================

  function clearSelection() {
    var selected = document.querySelectorAll('.row.' + SELECTED_CLASS);
    selected.forEach(function(el) {
      el.classList.remove(SELECTED_CLASS);
      // Clear aria-pressed on row-head
      var rowHead = el.querySelector('.row-head[role="button"]');
      if (rowHead) {
        rowHead.setAttribute('aria-pressed', 'false');
      }
    });
    clearSidebarActive();
    updateProgressIndicator(null);
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
    // Set aria-pressed on row-head
    var rowHead = row.querySelector('.row-head[role="button"]');
    if (rowHead) {
      rowHead.setAttribute('aria-pressed', 'true');
    }
    setSidebarActive(rangeId);
    updateProgressIndicator(rangeId);

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

    // Use baseline alignment (handles fallback internally)
    alignWithSidebar(rangeId);

    log('scrollToRow:', rowId, 'reducedMotion:', prefersReducedMotion);
  }

  // ========================================================================
  // Click Handler
  // ========================================================================

  function handleClick(e) {
    // Check for row-head click (data-range on row-head)
    var rowHead = e.target.closest('.row-head[data-range]');
    if (rowHead) {
      var rangeId = rowHead.getAttribute('data-range');
      if (rangeId) {
        e.preventDefault();
        e.stopPropagation();
        var wasSelected = currentRange === rangeId;
        var selected = selectRow(rangeId);
        if (selected && !wasSelected) {
          scrollToRow(rangeId);
        }
        return;
      }
    }

    // Check for sidebar jump click (data-range on jump link)
    var jumpLink = e.target.closest('.jump a[data-range]');
    if (jumpLink) {
      var rangeId = jumpLink.getAttribute('data-range');
      if (rangeId) {
        e.preventDefault();
        e.stopPropagation();
        var wasSelected = currentRange === rangeId;
        var selected = selectRow(rangeId);
        if (selected && !wasSelected) {
          scrollToRow(rangeId);
        }
        return;
      }
    }
  }

  // ========================================================================
  // Keyboard Handler (WCAG 2.1.1)
  // ========================================================================

  function handleKeydown(e) {
    // Only handle Enter and Space on role="button" elements
    if (e.key !== 'Enter' && e.key !== ' ') return;

    // Check for row-head with role="button"
    var rowHead = e.target.closest('.row-head[role="button"][data-range]');
    if (rowHead) {
      var rangeId = rowHead.getAttribute('data-range');
      if (rangeId) {
        // Prevent default (Space scrolls page)
        e.preventDefault();
        e.stopPropagation();
        var wasSelected = currentRange === rangeId;
        var selected = selectRow(rangeId);
        if (selected && !wasSelected) {
          scrollToRow(rangeId);
        }
        return;
      }
    }

    // Check for sidebar jump link with role="button"
    var jumpLink = e.target.closest('.jump a[data-range]');
    if (jumpLink) {
      var rangeId = jumpLink.getAttribute('data-range');
      if (rangeId) {
        e.preventDefault();
        e.stopPropagation();
        var wasSelected = currentRange === rangeId;
        var selected = selectRow(rangeId);
        if (selected && !wasSelected) {
          scrollToRow(rangeId);
        }
        return;
      }
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
    document.addEventListener('keydown', handleKeydown, true);
    window.addEventListener('hashchange', handleHashChange);

    // Handle initial hash
    if (location.hash) {
      setTimeout(handleHashChange, 50);
    } else {
      // No initial hash - show "No selection" state
      updateProgressIndicator(null);
    }

    log('Initialization complete');
  }

  // Test API
  if (typeof window !== 'undefined') {
    window.highlightModule = {
      selectRow: selectRow,
      clearSelection: clearSelection,
      scrollToRow: scrollToRow,
      alignWithSidebar: alignWithSidebar,
      getSidebarItem: getSidebarItem,
      getSidebarBaseline: getSidebarBaseline,
      updateProgressIndicator: updateProgressIndicator,
      getRangeNumber: getRangeNumber,
      getCurrentRange: function() { return currentRange; },
      ROW_PREFIX: ROW_PREFIX,
      JUMP_PREFIX: JUMP_PREFIX,
      PROG_TEXT_ID: PROG_TEXT_ID,
      PROG_FILL_ID: PROG_FILL_ID,
      BASELINE_RANGE: BASELINE_RANGE,
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
