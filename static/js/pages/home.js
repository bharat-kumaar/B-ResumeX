/**
 * Homepage-specific enhancements
 */
(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", () => {
    // Stagger hero terminal typing effect (optional polish)
    const lines = document.querySelectorAll(".terminal-body div");
    lines.forEach((line, i) => {
      line.style.opacity = "0";
      line.style.transform = "translateX(-8px)";
      setTimeout(() => {
        line.style.transition = "opacity 0.4s ease, transform 0.4s ease";
        line.style.opacity = "1";
        line.style.transform = "translateX(0)";
      }, 800 + i * 200);
    });
  });
})();
