/**
 * @file highlight.js
 * @source In-house (ELECTRE III project)
 * @license Project license (see repository root)
 *
 * Range highlight and click-to-scroll for ELECTRE III module tutorials.
 * Features:
 * - Click code range marker (R1-R5) → scrolls doc pane to callout
 * - Click callout badge in doc → scrolls code pane to range
 * - Highlight toggle on click (click same range to deselect)
 * - Debug mode: ?debug=1 for console logging
 */
(function() {
  'use strict';

  // Constants
  var SELECTED_CLASS = 'range-selected';
  var CODE_SCROLL_ID = 'codeScroll';
  var DOC_SCROLL_ID = 'docScroll';

  // State
  var DEBUG = window.location.search.indexOf('debug=1') !== -1;
  var currentRange = null;
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
  // Click-to-Scroll
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

      selectRange(rangeId);

      // Scroll opposite pane to show corresponding element
      if (scrollTarget === 'doc') {
        scrollDocToRange(rangeId);
      } else if (scrollTarget === 'code') {
        scrollCodeToRange(rangeId);
      }
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

      // Scroll both panes
      scrollCodeToRange(rangeId);
      scrollDocToRange(rangeId);
    }
  }

  // ========================================================================
  // Initialization
  // ========================================================================

  function init() {
    log('Initializing, DEBUG:', DEBUG);

    if (!initScrollContainers()) {
      log('Initialization failed: scroll containers not found');
      return;
    }

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
      selectRange: selectRange,
      clearSelection: clearSelection,
      scrollCodeToRange: scrollCodeToRange,
      scrollDocToRange: scrollDocToRange,
      getCurrentRange: function() { return currentRange; },
      getCodeScroll: function() { return codeScroll; },
      getDocScroll: function() { return docScroll; },
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
