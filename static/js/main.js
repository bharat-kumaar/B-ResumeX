/**
 * B-ResumeX — Main application bootstrap
 * Modules load independently; this file handles global init.
 */
(function () {
  "use strict";

  const App = {
    version: "1.0.0",
    apiBase: "/api/v1",
  };

  window.BResumeX = App;

  document.addEventListener("DOMContentLoaded", () => {
    initNavCta();
    initParallaxGlow();
  });

  function initNavCta() {
    const cta = document.getElementById("nav-cta");
    if (!cta || cta.tagName === "A") return;
    cta.addEventListener("click", () => {
      window.location.href = "/analyze";
    });
  }

  /** Subtle parallax on scroll for mesh layers */
  function initParallaxGlow() {
    const mesh = document.querySelector(".bg-mesh");
    if (!mesh) return;

    window.addEventListener(
      "scroll",
      () => {
        const y = window.scrollY * 0.15;
        mesh.style.transform = `translateY(${y}px)`;
      },
      { passive: true }
    );
  }
})();
