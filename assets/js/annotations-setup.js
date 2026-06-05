/**
 * Inline annotations: click/tap to pin the popover open, dismiss on outside
 * click or Escape, and keep the popover inside the viewport (clamp + flip).
 * Hover/focus reveal is handled in CSS; this only manages the pinned state and
 * positioning. See _includes/annotation.liquid and _sass/_annotations.scss.
 */
(function () {
  function init() {
    var annotations = Array.prototype.slice.call(
      document.querySelectorAll(".annotation"),
    );
    if (!annotations.length) return;

    /**
     * Position the popover so it stays within the viewport: flip above the
     * marker when there is no room below, and shift horizontally when it would
     * overflow either edge.
     */
    function position(annotation) {
      var content = annotation.querySelector(".annotation-content");
      var marker = annotation.querySelector(".annotation-marker");
      if (!content || !marker) return;

      // Reset prior adjustments before measuring.
      content.classList.remove("annotation-content--above");
      content.style.left = "";
      content.style.right = "";

      var markerRect = marker.getBoundingClientRect();
      var contentRect = content.getBoundingClientRect();
      var margin = 8;
      var vw = document.documentElement.clientWidth;
      var vh = document.documentElement.clientHeight;

      // Flip above if it would overflow the bottom and there is room above.
      if (
        markerRect.bottom + contentRect.height + margin > vh &&
        markerRect.top - contentRect.height - margin > 0
      ) {
        content.classList.add("annotation-content--above");
      }

      // Default left edge is aligned with the marker; shift if it overflows.
      var overflowRight = contentRect.right - (vw - margin);
      var overflowLeft = margin - contentRect.left;
      if (overflowRight > 0) {
        content.style.left = -overflowRight + "px";
      } else if (overflowLeft > 0) {
        content.style.left = overflowLeft + "px";
      }
    }

    function close(annotation) {
      annotation.classList.remove("is-open");
      var marker = annotation.querySelector(".annotation-marker");
      if (marker) marker.setAttribute("aria-expanded", "false");
    }

    function closeAll(except) {
      annotations.forEach(function (annotation) {
        if (annotation !== except) close(annotation);
      });
    }

    annotations.forEach(function (annotation) {
      var marker = annotation.querySelector(".annotation-marker");
      if (!marker) return;

      // Position on hover/focus reveal as well as on click.
      annotation.addEventListener("mouseenter", function () {
        position(annotation);
      });
      marker.addEventListener("focus", function () {
        position(annotation);
      });

      marker.addEventListener("click", function (event) {
        event.stopPropagation();
        var willOpen = !annotation.classList.contains("is-open");
        closeAll(annotation);
        annotation.classList.toggle("is-open", willOpen);
        marker.setAttribute("aria-expanded", willOpen ? "true" : "false");
        if (willOpen) position(annotation);
      });
    });

    // Dismiss pinned popovers on outside click/tap.
    document.addEventListener("click", function (event) {
      if (!event.target.closest(".annotation")) closeAll(null);
    });

    // Dismiss on Escape.
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") closeAll(null);
    });

    // Re-clamp any open popover on resize.
    window.addEventListener("resize", function () {
      annotations.forEach(function (annotation) {
        if (annotation.classList.contains("is-open")) position(annotation);
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
