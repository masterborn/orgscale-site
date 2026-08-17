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

  /* 2. The alignment diagram animates only while it is on screen, so the
     beam sweep and the red→green score flip stay in step with each other
     and don't burn frames off-screen. */
  var diagram = document.querySelector(".diagram__stage");
  if (diagram) {
    new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        diagram.classList.toggle("is-running", entry.isIntersecting);
      });
    }, { threshold: 0.25 }).observe(diagram);
  }
})();
