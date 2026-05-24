/**
 * Mini sparkline bars in analytics cards
 */
(function () {
  "use strict";

  function init() {
    document.querySelectorAll("[data-spark]").forEach((container) => {
      const values = container.dataset.spark.split(",").map(Number);
      const max = Math.max(...values, 1);

      values.forEach((v) => {
        const bar = document.createElement("div");
        bar.className = "spark-bar";
        bar.style.height = `${(v / max) * 100}%`;
        container.appendChild(bar);
      });
    });
  }

  document.addEventListener("DOMContentLoaded", init);
})();
