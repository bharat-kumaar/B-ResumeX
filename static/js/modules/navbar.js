/**
 * Animated navbar — scroll hide, active links, mobile menu
 */
(function () {
  "use strict";

  const header = document.getElementById("site-header");
  const toggle = document.getElementById("nav-toggle");
  const navLinks = document.getElementById("nav-links");
  let lastScroll = 0;

  function initScroll() {
    if (!header) return;

    window.addEventListener(
      "scroll",
      () => {
        const y = window.scrollY;

        header.classList.toggle("is-scrolled", y > 40);

        if (y > lastScroll && y > 120) {
          header.classList.add("is-hidden");
        } else {
          header.classList.remove("is-hidden");
        }
        lastScroll = y;
      },
      { passive: true }
    );
  }

  function initMobile() {
    if (!toggle || !navLinks) return;

    toggle.addEventListener("click", () => {
      const open = navLinks.classList.toggle("is-open");
      toggle.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", String(open));
    });

    navLinks.querySelectorAll(".nav-link").forEach((link) => {
      link.addEventListener("click", () => {
        navLinks.classList.remove("is-open");
        toggle.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  function initActiveLinks() {
    const path = window.location.pathname;
    document.querySelectorAll(".nav-link[data-nav]").forEach((link) => {
      const nav = link.dataset.nav;
      if (
        (nav === "home" && (path === "/" || path.endsWith("/"))) ||
        (nav !== "home" && path.includes(nav))
      ) {
        link.classList.add("is-active");
      }
    });
  }

  function initSmoothAnchors() {
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener("click", (e) => {
        const id = anchor.getAttribute("href");
        if (!id || id === "#") return;
        const target = document.querySelector(id);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      });
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    initScroll();
    initMobile();
    initActiveLinks();
    initSmoothAnchors();
  });
})();
