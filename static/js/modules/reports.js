/**
 * Reports history page — loads analysis list from API
 */
(function () {
  "use strict";

  const API = "/api/v1";

  document.addEventListener("DOMContentLoaded", async () => {
    const empty = document.getElementById("reports-empty");
    const list = document.getElementById("reports-container");
    if (!list) return;

    try {
      const res = await fetch(`${API}/analyses?limit=30`);
      const json = await res.json();
      if (!json.success || !json.data?.length) return;

      empty?.classList.add("hidden");
      list.classList.remove("hidden");
      list.className = "reports-grid";
      list.innerHTML = json.data
        .map(
          (r) => `
        <li class="report-card glass">
          <div class="report-card-head">
            <span class="report-grade grade-${r.grade}">${r.grade}</span>
            <span class="report-score">${Math.round(r.ats_score)}%</span>
          </div>
          <h3>${escapeHtml(r.filename || "Resume")}</h3>
          <p class="report-date">${formatDate(r.created_at)}</p>
          <a href="/dashboard/${r.id}" class="btn btn-glow btn-sm">View Report</a>
        </li>`
        )
        .join("");
    } catch (_) {}
  });

  function formatDate(iso) {
    try {
      return new Date(iso).toLocaleString();
    } catch {
      return iso;
    }
  }

  function escapeHtml(s) {
    const d = document.createElement("div");
    d.textContent = s || "";
    return d.innerHTML;
  }
})();
