/**
 * Page loader — simulates boot sequence then reveals UI
 */
(function () {
  "use strict";

  const LOADER_ID = "page-loader";
  const FILL_ID = "loader-fill";
  const MIN_DISPLAY_MS = 1200;

  function init() {
    const loader = document.getElementById(LOADER_ID);
    const fill = document.getElementById(FILL_ID);
    if (!loader) return;

    document.body.classList.add("is-loading");

    let progress = 0;
    const tick = setInterval(() => {
      progress += Math.random() * 18 + 8;
      if (progress > 100) progress = 100;
      if (fill) fill.style.width = `${progress}%`;
      if (progress >= 100) clearInterval(tick);
    }, 80);

    const start = performance.now();

    function finish() {
      const elapsed = performance.now() - start;
      const delay = Math.max(0, MIN_DISPLAY_MS - elapsed);

      setTimeout(() => {
        if (fill) fill.style.width = "100%";
        loader.classList.add("is-done");
        document.body.classList.remove("is-loading");
        loader.setAttribute("aria-hidden", "true");
      }, delay);
    }

    if (document.readyState === "complete") {
      finish();
    } else {
      window.addEventListener("load", finish);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
