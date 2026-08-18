/* Orgscale — the only two behaviours on the page that need script.
   Everything else (hover swaps, gradients, layout) is CSS. */

(function () {
  "use strict";

  /* 1. Scroll reveal.
     Elements start hidden via .reveal and settle once they enter the
     viewport. If IntersectionObserver is missing we reveal everything
     immediately rather than leaving the page blank. */
  var targets = document.querySelectorAll(".reveal");

  if (!("IntersectionObserver" in window)) {
    document.documentElement.classList.add("no-js");
    return;
  }

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      // Stagger siblings so a row of cards cascades instead of popping.
      var siblings = Array.prototype.slice.call(entry.target.parentNode.children);
      var index = siblings.indexOf(entry.target);
      entry.target.style.transitionDelay = Math.min(index, 6) * 70 + "ms";
      entry.target.classList.add("is-in");
      observer.unobserve(entry.target);
    });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });

  targets.forEach(function (el) { observer.observe(el); });

  /* 2. The pinned bar contracts around its contents once the page scrolls. */
  var header = document.querySelector(".site-header");
  if (header) {
    var compact = null;
    var sync = function () {
      var next = window.scrollY > 250;
      if (next === compact) return;
      compact = next;
      header.classList.toggle("is-compact", next);
    };
    addEventListener("scroll", sync, { passive: true });
    sync();
  }

  /* 3. Both decorative stages grow as they travel into view, and the growth
     tracks scroll position rather than firing once on intersection —
     measured against the original, which sits at 0.787 of its resting size
     with ~133px showing and reaches full size at ~450px. Expressed here
     against our own base, which is authored at that 0.7 starting size. */
  var stages = [].slice.call(document.querySelectorAll(".diagram__stage, .report__stage"));
  if (stages.length) {
    var TRAVEL = 450;
    var GROWTH = 0.4286;                  // 1 / 0.7 - 1
    var ticking = false;
    var paint = function () {
      ticking = false;
      var vh = window.innerHeight;
      stages.forEach(function (stage) {
        var layer = stage.firstElementChild;
        if (!layer) return;
        var seen = vh - stage.getBoundingClientRect().top;
        var p = seen / TRAVEL;
        p = p < 0 ? 0 : p > 1 ? 1 : p;
        layer.style.transform = "scale(" + (1 + GROWTH * p).toFixed(4) + ")";
      });
    };
    var onScroll = function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(paint);
    };
    addEventListener("scroll", onScroll, { passive: true });
    addEventListener("resize", onScroll, { passive: true });
    paint();
  }
})();
