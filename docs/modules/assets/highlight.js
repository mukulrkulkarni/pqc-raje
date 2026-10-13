/**
 * @file highlight.js
 * @source In-house (ELECTRE III project)
 * @license Project license (see repository root)
 *
 * Range highlight and scroll sync for ELECTRE III module tutorials.
 * Features:
 * - Click code range marker (R1-R5) → scrolls doc pane to callout
 * - Click callout badge in doc → scrolls code pane to range
 * - Highlight toggle on click (click same range to deselect)
 * - Continuous scroll sync (percentage-based, off by default)
 * - Debug mode: ?debug=1 for console logging
 */
(function() {
  'use strict';

  // Constants
  var SELECTED_CLASS = 'range-selected';
  var SYNC_ENABLED_CLASS = 'sync-enabled';
  var CODE_SCROLL_ID = 'codeScroll';
  var DOC_SCROLL_ID = 'docScroll';

  // State
  var DEBUG = window.location.search.indexOf('debug=1') !== -1;
  var currentRange = null;
  var syncEnabled = false;
  var isSyncing = false;  // Loop guard to prevent scroll oscillation
  var prefersReducedMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Cached DOM refs
  var codeScroll = null;
  var docScroll = null;

  function log() {
    if (DEBUG && console && console.log) {
      console.log.apply(console, ['[highlight]'].concat(Array.prototype.slice.call(arguments)));
    }
  }

  // ========================================================================
  // DOM Setup
  // ========================================================================

  function initScrollContainers() {
    codeScroll = document.getElementById(CODE_SCROLL_ID);
    docScroll = document.getElementById(DOC_SCROLL_ID);

    log('Scroll containers:', {
      code: codeScroll ? CODE_SCROLL_ID : 'NOT FOUND',
      doc: docScroll ? DOC_SCROLL_ID : 'NOT FOUND'
    });

    if (!codeScroll || !docScroll) {
      console.warn('[highlight] Missing scroll container IDs:', CODE_SCROLL_ID, DOC_SCROLL_ID);
    }

    return codeScroll && docScroll;
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

  function highlightRange(rangeId) {
    // Highlight code lines
    var codeLines = document.querySelectorAll('[data-range="' + rangeId + '"]');
    log('Highlighting', codeLines.length, 'code lines for', rangeId);
    codeLines.forEach(function(line) {
      line.classList.add(SELECTED_CLASS);
    });

    // Highlight doc section
    var docSection = document.getElementById('doc-' + rangeId);
    if (docSection) {
      docSection.classList.add(SELECTED_CLASS);
      log('Highlighted doc section: doc-' + rangeId);
    }
  }

  // ========================================================================
  // Click-to-Scroll & Alignment
  // ========================================================================

  function scrollToElement(container, element) {
    if (!container || !element) {
      log('scrollToElement: missing', { container: !!container, element: !!element });
      return;
    }

    var containerRect = container.getBoundingClientRect();
    var elementRect = element.getBoundingClientRect();

    // Element's position relative to container's scroll origin
    var elementTop = elementRect.top - containerRect.top + container.scrollTop;

    // Place element at 25% from top of visible area
    var targetScroll = elementTop - (containerRect.height * 0.25);
    targetScroll = Math.max(0, Math.min(targetScroll, container.scrollHeight - container.clientHeight));

    log('scrollToElement:', {
      elementId: element.id,
      from: container.scrollTop,
      to: targetScroll,
      reducedMotion: prefersReducedMotion
    });

    var scrollBehavior = prefersReducedMotion ? 'auto' : 'smooth';
    container.scrollTo({ top: targetScroll, behavior: scrollBehavior });
  }

  function scrollDocToRange(rangeId) {
    if (!docScroll) return;
    var docTarget = document.getElementById('doc-' + rangeId);
    if (docTarget) {
      scrollToElement(docScroll, docTarget);
    }
  }

  function scrollCodeToRange(rangeId) {
    if (!codeScroll) return;
    var codeTarget = document.getElementById(rangeId);
    if (codeTarget) {
      scrollToElement(codeScroll, codeTarget);
    }
  }

  /**
   * Align both panes so top edges of code range and doc callout match.
   * Places both elements at 10% from top of their respective containers.
   * No-ops gracefully if containers or target elements are missing.
   */
  function alignPanes(rangeId) {
    // Guard: missing containers - no-op without throwing
    if (!codeScroll || !docScroll) {
      log('alignPanes: containers missing', { code: !!codeScroll, doc: !!docScroll });
      return;
    }

    var codeTarget = document.getElementById(rangeId);
    var docTarget = document.getElementById('doc-' + rangeId);

    // Guard: missing targets - no-op without throwing
    if (!codeTarget || !docTarget) {
      log('alignPanes: targets missing', {
        rangeId: rangeId,
        codeTarget: !!codeTarget,
        docTarget: !!docTarget
      });
      return;
    }

    // Calculate scroll positions to place elements at 10% from top
    var alignOffset = 0.10;  // 10% from top edge

    var codeRect = codeScroll.getBoundingClientRect();
    var codeTargetRect = codeTarget.getBoundingClientRect();
    var codeTargetTop = codeTargetRect.top - codeRect.top + codeScroll.scrollTop;
    var codeScrollPos = codeTargetTop - (codeRect.height * alignOffset);
    codeScrollPos = Math.max(0, Math.min(codeScrollPos, codeScroll.scrollHeight - codeScroll.clientHeight));

    var docRect = docScroll.getBoundingClientRect();
    var docTargetRect = docTarget.getBoundingClientRect();
    var docTargetTop = docTargetRect.top - docRect.top + docScroll.scrollTop;
    var docScrollPos = docTargetTop - (docRect.height * alignOffset);
    docScrollPos = Math.max(0, Math.min(docScrollPos, docScroll.scrollHeight - docScroll.clientHeight));

    log('alignPanes:', {
      rangeId: rangeId,
      codeFrom: codeScroll.scrollTop,
      codeTo: codeScrollPos,
      docFrom: docScroll.scrollTop,
      docTo: docScrollPos,
      reducedMotion: prefersReducedMotion
    });

    var scrollBehavior = prefersReducedMotion ? 'auto' : 'smooth';
    codeScroll.scrollTo({ top: codeScrollPos, behavior: scrollBehavior });
    docScroll.scrollTo({ top: docScrollPos, behavior: scrollBehavior });
  }

  function selectRange(rangeId) {
    if (!rangeId) return;

    log('selectRange:', rangeId, 'current:', currentRange);

    // Toggle off if same range
    if (currentRange === rangeId) {
      clearSelection();
      if (history.replaceState) {
        history.replaceState(null, '', location.pathname + location.search);
      }
      return;
    }

    clearSelection();
    currentRange = rangeId;
    highlightRange(rangeId);

    // Update URL hash
    if (history.pushState) {
      history.pushState(null, '', '#' + rangeId);
    }
  }

  // ========================================================================
  // Click Handler
  // ========================================================================

  function handleClick(e) {
    // Check for range-related click targets
    var marker = e.target.closest('a.range-marker');
    var ref = e.target.closest('a.range-ref');

    if (!marker && !ref) return;

    var rangeId = null;
    var scrollTarget = null;  // 'code' or 'doc'

    if (marker) {
      // Clicked range marker in code pane → scroll doc
      var href = marker.getAttribute('href') || '';
      var match = href.match(/#doc-(R\d+)/);
      if (match) {
        rangeId = match[1];
        scrollTarget = 'doc';
      }
    } else if (ref) {
      // Clicked range ref in doc pane → scroll code
      var href = ref.getAttribute('href') || '';
      var match = href.match(/#(R\d+)/);
      if (match) {
        rangeId = match[1];
        scrollTarget = 'code';
      }
    }

    if (rangeId) {
      e.preventDefault();
      e.stopPropagation();

      // Check if this is a toggle-off (re-click same selection)
      var wasSelected = currentRange === rangeId;

      selectRange(rangeId);

      // Only align panes if this is a new selection, not a toggle-off
      if (!wasSelected) {
        alignPanes(rangeId);
      }
    }
  }

  // ========================================================================
  // Continuous Scroll Sync
  // ========================================================================

  function getScrollPercent(el) {
    if (!el) return 0;
    var maxScroll = el.scrollHeight - el.clientHeight;
    return maxScroll > 0 ? el.scrollTop / maxScroll : 0;
  }

  function setScrollPercent(el, percent) {
    if (!el) return;
    var maxScroll = el.scrollHeight - el.clientHeight;
    el.scrollTop = percent * maxScroll;
  }

  function syncScroll(source, target, sourceName) {
    // Guard: sync disabled or already syncing (prevents oscillation)
    if (!syncEnabled || isSyncing) {
      return;
    }

    // Guard: missing containers - no-op without throwing
    if (!source || !target) {
      log('syncScroll: missing container', { source: !!source, target: !!target });
      return;
    }

    isSyncing = true;
    var percent = getScrollPercent(source);

    log('syncScroll:', {
      from: sourceName,
      percent: (percent * 100).toFixed(1) + '%',
      reducedMotion: prefersReducedMotion
    });

    setScrollPercent(target, percent);

    // Release loop guard after animation frames to prevent oscillation
    // Double rAF ensures the scroll event from setScrollPercent has fired
    requestAnimationFrame(function() {
      requestAnimationFrame(function() {
        isSyncing = false;
      });
    });
  }

  function handleCodeScroll() {
    syncScroll(codeScroll, docScroll, 'code');
  }

  function handleDocScroll() {
    syncScroll(docScroll, codeScroll, 'doc');
  }

  function setupSyncListeners() {
    // Guard: missing containers - no-op without throwing
    if (!codeScroll || !docScroll) {
      log('setupSyncListeners: containers missing, skipping');
      return;
    }

    codeScroll.addEventListener('scroll', handleCodeScroll, { passive: true });
    docScroll.addEventListener('scroll', handleDocScroll, { passive: true });

    log('Sync scroll listeners attached to #' + CODE_SCROLL_ID + ' and #' + DOC_SCROLL_ID);
  }

  // ========================================================================
  // Sync Toggle
  // ========================================================================

  function handleSyncToggle(e) {
    var toggle = e.target.closest('[data-sync-toggle]');
    if (!toggle) return;

    e.preventDefault();
    syncEnabled = !syncEnabled;
    toggle.classList.toggle(SYNC_ENABLED_CLASS, syncEnabled);
    toggle.setAttribute('aria-pressed', String(syncEnabled));

    log('Sync toggle:', syncEnabled ? 'ON' : 'OFF');

    // Persist preference
    try {
      localStorage.setItem('electre3-sync', syncEnabled ? '1' : '0');
    } catch (err) {
      // localStorage unavailable - silently ignore
    }
  }

  function loadSyncPreference() {
    try {
      var pref = localStorage.getItem('electre3-sync');
      if (pref === '1') {
        syncEnabled = true;
        var toggle = document.querySelector('[data-sync-toggle]');
        if (toggle) {
          toggle.classList.add(SYNC_ENABLED_CLASS);
          toggle.setAttribute('aria-pressed', 'true');
        }
        log('Sync preference loaded: enabled');
      }
    } catch (err) {
      // localStorage unavailable - silently ignore
    }
  }

  // ========================================================================
  // Hash Navigation
  // ========================================================================

  function handleHashChange() {
    var hash = location.hash.slice(1);
    log('hashchange:', hash);

    var match = hash.match(/^(doc-)?(R\d+)$/);
    if (match) {
      var rangeId = match[2];
      selectRange(rangeId);

      // Align both panes to show the selected range
      alignPanes(rangeId);
    }
  }

  // ========================================================================
  // Initialization
  // ========================================================================

  function init() {
    log('Initializing, DEBUG:', DEBUG, 'reducedMotion:', prefersReducedMotion);

    if (!initScrollContainers()) {
      log('Initialization failed: scroll containers not found');
      return;
    }

    // Event listeners
    document.addEventListener('click', handleClick, true);
    document.addEventListener('click', handleSyncToggle, true);
    window.addEventListener('hashchange', handleHashChange);

    // Setup continuous scroll sync
    setupSyncListeners();
    loadSyncPreference();

    // Handle initial hash
    if (location.hash) {
      setTimeout(handleHashChange, 50);
    }

    log('Initialization complete');
  }

  // Test API
  if (typeof window !== 'undefined') {
    window.highlightModule = {
      selectRange: selectRange,
      clearSelection: clearSelection,
      scrollCodeToRange: scrollCodeToRange,
      scrollDocToRange: scrollDocToRange,
      alignPanes: alignPanes,
      getCurrentRange: function() { return currentRange; },
      getCodeScroll: function() { return codeScroll; },
      getDocScroll: function() { return docScroll; },
      isSyncEnabled: function() { return syncEnabled; },
      isSyncing: function() { return isSyncing; },
      CODE_SCROLL_ID: CODE_SCROLL_ID,
      DOC_SCROLL_ID: DOC_SCROLL_ID,
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
