/**
 * ATS score ring + breakdown bar animation
 */
(function () {
  "use strict";

  const CIRCUMFERENCE = 2 * Math.PI * 45; // r=45
  const TARGET_SCORE = 91;

  function grade(score) {
    if (score >= 85) return "A";
    if (score >= 70) return "B";
    if (score >= 55) return "C";
    return "D";
  }

  function animateRing(ringEl, scoreEl, gradeEl, score) {
    const offset = CIRCUMFERENCE - (score / 100) * CIRCUMFERENCE;
    ringEl.style.strokeDashoffset = String(offset);

    const duration = 2000;
    const start = performance.now();

    function tick(now) {
      const t = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - t, 3);
      const current = Math.floor(eased * score);
      scoreEl.textContent = current;
      if (t < 1) requestAnimationFrame(tick);
      else gradeEl.textContent = `GRADE ${grade(score)}`;
    }

    requestAnimationFrame(tick);
  }

  function animateBars(rows) {
    rows.forEach((row, i) => {
      const score = parseInt(row.dataset.score, 10) || 0;
      const fill = row.querySelector(".score-fill");
      const pct = row.querySelector(".score-pct");

      setTimeout(() => {
        if (fill) fill.style.width = `${score}%`;
        if (pct) {
          let n = 0;
          const step = () => {
            n += 2;
            if (n <= score) {
              pct.textContent = `${n}%`;
              requestAnimationFrame(step);
            } else {
              pct.textContent = `${score}%`;
            }
          };
          requestAnimationFrame(step);
        }
      }, 300 + i * 150);
    });
  }

  function init() {
    const section = document.getElementById("ats");
    const ring = document.getElementById("ats-ring");
    const scoreDisplay = document.getElementById("ats-score-display");
    const gradeDisplay = document.getElementById("ats-grade-display");
    const rows = document.querySelectorAll(".score-row");

    if (!section || !ring) return;

    ring.style.strokeDasharray = String(CIRCUMFERENCE);
    ring.style.strokeDashoffset = String(CIRCUMFERENCE);

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            animateRing(ring, scoreDisplay, gradeDisplay, TARGET_SCORE);
            animateBars(rows);
            observer.disconnect();
          }
        });
      },
      { threshold: 0.25 }
    );

    observer.observe(section);
  }

  document.addEventListener("DOMContentLoaded", init);
})();
