/**
 * B-ResumeX Dashboard v3 — full SaaS results UI
 */
(function () {
  "use strict";

  const API = "/api/v1";
  const CIRCUMFERENCE = 2 * Math.PI * 42;
  let currentData = null;
  let currentId = null;

  document.addEventListener("DOMContentLoaded", () => {
    loadPlatformStats();
    initTabs();
    initExportButtons();
    const id = window.BResumeX_ANALYSIS_ID;
    if (id) loadAnalysis(id);
  });

  function initTabs() {
    document.querySelectorAll(".dash-tab").forEach((tab) => {
      tab.addEventListener("click", () => {
        document.querySelectorAll(".dash-tab").forEach((t) => t.classList.remove("active"));
        document.querySelectorAll(".dash-panel").forEach((p) => p.classList.add("hidden"));
        tab.classList.add("active");
        document.getElementById(`panel-${tab.dataset.panel}`)?.classList.remove("hidden");
      });
    });
  }

  function initExportButtons() {
    document.getElementById("btn-export-pdf")?.addEventListener("click", (e) => {
      e.preventDefault();
      if (currentId) window.location.href = `${API}/analyses/${currentId}/export/pdf`;
    });
    document.getElementById("btn-export-docx")?.addEventListener("click", (e) => {
      e.preventDefault();
      if (currentId) window.location.href = `${API}/analyses/${currentId}/export/docx`;
    });
  }

  async function loadPlatformStats() {
    try {
      const res = await fetch(`${API}/dashboard/stats`);
      const json = await res.json();
      if (!json.success) return;
      const d = json.data;
      setText("stat-total", d.total_analyses);
      setText("stat-avg", d.avg_ats_score ? `${d.avg_ats_score}%` : "—");
    } catch (_) {}
  }

  async function loadAnalysis(id) {
    currentId = id;
    showResults();
    try {
      const res = await fetch(`${API}/analyses/${id}`);
      const json = await res.json();
      if (!json.success) throw new Error(json.error || "Not found");
      currentData = json.data;
      renderDashboard(json.data);
      if (window.BResumeXEditor && json.data.rebuilt_resume) {
        window.BResumeXEditor.render(json.data.rebuilt_resume, id);
      }
    } catch (err) {
      alert(err.message);
      window.location.href = "/dashboard";
    }
  }

  window.BResumeXLoadDashboard = loadAnalysis;

  function showResults() {
    document.getElementById("dash-empty")?.classList.add("hidden");
    document.getElementById("dash-results")?.classList.remove("hidden");
  }

  function renderDashboard(data) {
    const ats = data.ats || {};
    const parsed = data.parsed || {};
    const skills = data.skills || {};
    const analytics = data.analytics || {};
    const insights = data.insights || {};
    const contact = parsed.contact || {};

    renderContactOverview(contact, analytics, data.engine);
    setText("dash-filename", data.filename || "Resume");
    setText(
      "dash-meta",
      `Analyzed ${formatDate(data.analyzed_at)} · NLP: ${data.engine?.nlp_mode || "—"} · ${analytics.word_count || 0} words`
    );

    animateRing(ats.overall || 0);
    setText("dash-ats-score", Math.round(ats.overall || 0));
    setText("dash-ats-grade", `GRADE ${ats.grade || "—"}`);
    const strengthEl = document.getElementById("dash-strength");
    if (strengthEl) {
      strengthEl.textContent = (ats.strength || "").replace("_", " ");
      strengthEl.className = `strength-badge ${ats.strength || ""}`;
    }

    renderBreakdown(ats.breakdown || {});
    renderMetrics(analytics);
    renderSkills(skills);
    renderSkillChart(skills.categorized || {});
    renderSkillMatch(skills.skill_match_percent || analytics.skill_match_percent);
    renderSwot(
      [...new Set([...(insights.strengths || []), ...(ats.strengths || [])])],
      [...new Set([...(insights.weaknesses || []), ...(insights.content_gaps || [])])]
    );
    renderSectionStatus(parsed.section_status || {}, parsed.missing_sections || []);
    initParsedTabs(parsed);
    renderSuggestions(data.suggestions || []);
    renderCompare(ats, analytics);
    renderDetailedReport(ats.detailed_report || []);
  }

  function renderSkillMatch(pct) {
    const el = document.getElementById("skill-match-display");
    if (!el) return;
    let n = 0;
    const target = pct || 0;
    const tick = () => {
      n = Math.min(target, n + 2);
      el.textContent = `${n}%`;
      if (n < target) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  function renderSwot(strengths, weaknesses) {
    const sEl = document.getElementById("dash-strengths");
    const wEl = document.getElementById("dash-weaknesses");
    if (sEl) sEl.innerHTML = (strengths || []).map((x) => `<li>${escapeHtml(x)}</li>`).join("") || "<li>—</li>";
    if (wEl) wEl.innerHTML = (weaknesses || []).map((x) => `<li>${escapeHtml(x)}</li>`).join("") || "<li>—</li>";
  }

  function renderSectionStatus(status, missing) {
    const grid = document.getElementById("section-status-grid");
    if (!grid) return;
    const all = ["summary", "skills", "experience", "education", "projects", "certifications", "contact"];
    grid.innerHTML = all
      .map((sec) => {
        const st = status[sec] || (missing.includes(sec) ? "missing" : "found");
        return `<div class="section-pill section-pill--${st}">${sec}<span>${st}</span></div>`;
      })
      .join("");
  }

  function renderCompare(ats, analytics) {
    setText("compare-original", `${Math.round(ats.overall || 0)}%`);
    setText("compare-projected", `${analytics.projected_ats_after_rebuild || "—"}%`);
  }

  function renderDetailedReport(report) {
    const el = document.getElementById("ats-detailed-report");
    if (!el) return;
    el.innerHTML = report.length
      ? report
          .map(
            (r) => `
        <div class="report-row report-row--${r.status}">
          <span>${escapeHtml(r.dimension)}</span>
          <span class="report-score">${r.score}%</span>
          <span class="report-badge">${r.status}</span>
        </div>`
          )
          .join("")
      : "<p style='color:var(--text-dim)'>No report data</p>";
  }

  function animateRing(score) {
    const ring = document.getElementById("dash-ring-fg");
    if (!ring) return;
    ring.style.strokeDasharray = String(CIRCUMFERENCE);
    requestAnimationFrame(() => {
      ring.style.strokeDashoffset = String(CIRCUMFERENCE - (score / 100) * CIRCUMFERENCE);
    });
  }

  function renderBreakdown(breakdown) {
    const el = document.getElementById("dash-breakdown");
    if (!el) return;
    const labels = {
      formatting: "Formatting",
      keywords: "Keywords",
      completeness: "Completeness",
      structure: "Structure",
      readability: "Readability",
      contact: "Contact",
    };
    el.innerHTML = Object.entries(breakdown)
      .map(
        ([k, v]) => `
      <div class="breakdown-item">
        <label><span>${labels[k] || k}</span><span>${v}%</span></label>
        <div class="breakdown-track"><div class="breakdown-fill" data-w="${v}"></div></div>
      </div>`
      )
      .join("");
    requestAnimationFrame(() => {
      el.querySelectorAll(".breakdown-fill").forEach((b) => (b.style.width = `${b.dataset.w}%`));
    });
  }

  function renderContactOverview(contact, analytics, engine) {
    const el = document.getElementById("contact-overview");
    if (!el) return;
    el.innerHTML = `
      <div class="contact-grid">
        <div><span class="lbl">Name</span><strong>${escapeHtml(contact.name || "—")}</strong></div>
        <div><span class="lbl">Email</span><strong>${escapeHtml(contact.email || "—")}</strong></div>
        <div><span class="lbl">Phone</span><strong>${escapeHtml(contact.phone || "—")}</strong></div>
        <div><span class="lbl">LinkedIn</span><strong>${escapeHtml(contact.linkedin || "—")}</strong></div>
        <div><span class="lbl">Quality</span><strong class="quality-tag">${escapeHtml(analytics.quality_label || "—")} (${analytics.quality_score || 0})</strong></div>
        <div><span class="lbl">Parse Confidence</span><strong>${analytics.parse_confidence || engine?.parse_confidence || 0}%</strong></div>
        <div><span class="lbl">NLP Engine</span><strong>${escapeHtml(engine?.nlp_mode || "—")}</strong></div>
        <div><span class="lbl">Exp. Depth</span><strong>${analytics.experience_depth_score || 0}%</strong></div>
      </div>`;
  }

  function renderMetrics(a) {
    const el = document.getElementById("dash-metrics");
    if (!el) return;
    const items = [
      ["Words", a.word_count],
      ["Readability", `${a.readability || "—"}%`],
      ["Skill Match", `${a.skill_match_percent || 0}%`],
      ["Quality", `${a.quality_score || 0}%`],
      ["Skills Found", a.skills_count],
      ["Education Q", `${a.education_quality_score || 0}%`],
    ];
    el.innerHTML = items
      .map(([l, v]) => `<div class="metric-box"><div class="val">${v ?? 0}</div><div class="lbl">${l}</div></div>`)
      .join("");
  }

  function renderSkills(skills) {
    const cloud = document.getElementById("dash-skills");
    const missing = document.getElementById("dash-missing-skills");
    const all = skills.all_skills || [];
    if (cloud) {
      cloud.innerHTML = all.length
        ? all.map((s) => `<span class="skill-chip">${escapeHtml(s)}</span>`).join("")
        : "<span style='color:var(--text-dim)'>No skills detected</span>";
    }
    if (missing) {
      const m = skills.missing_recommended || [];
      missing.innerHTML = m.length
        ? m.map((s) => `<span class="skill-chip missing">${escapeHtml(s)}</span>`).join("")
        : "<span style='color:var(--text-dim)'>Strong coverage</span>";
    }
  }

  function renderSkillChart(categorized) {
    const el = document.getElementById("dash-skill-chart");
    if (!el) return;
    const entries = Object.entries(categorized);
    if (!entries.length) {
      el.innerHTML = "<p style='color:var(--text-dim)'>—</p>";
      return;
    }
    const max = Math.max(...entries.map(([, v]) => v.length), 1);
    el.innerHTML = entries
      .map(([cat, list]) => {
        const pct = Math.round((list.length / max) * 100);
        return `<div class="chart-row"><span>${formatCat(cat)}</span><div class="bar"><div class="bar-fill" style="width:${pct}%"></div></div><span>${list.length}</span></div>`;
      })
      .join("");
  }

  let parsedCache = {};

  function initParsedTabs(parsed) {
    parsedCache = {
      experience: parsed.experience || [],
      education: parsed.education || [],
      projects: parsed.projects || [],
      achievements: parsed.achievements || [],
    };
    document.querySelectorAll(".parsed-tab").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".parsed-tab").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        showParsedTab(btn.dataset.tab);
      });
    });
    showParsedTab("experience");
  }

  function showParsedTab(tab) {
    const el = document.getElementById("dash-parsed-content");
    const items = parsedCache[tab] || [];
    if (!el) return;
    if (tab === "education") {
      el.innerHTML = items.length
        ? items
            .map(
              (it) => `
          <div class="parsed-item">
            <h4>${escapeHtml(it.degree || it.title || "Degree")}</h4>
            <p><strong>${escapeHtml(it.institution || "")}</strong> ${escapeHtml(it.years || "")}</p>
            <p>${escapeHtml(it.detail || "")}</p>
          </div>`
            )
            .join("")
        : "<p style='color:var(--text-dim)'>No education detected — add a clear Education section.</p>";
      return;
    }
    el.innerHTML = items.length
      ? items
          .map(
            (it) => `
        <div class="parsed-item">
          <h4>${escapeHtml(it.title || "Entry")}</h4>
          <p>${escapeHtml(it.detail || (it.bullets || []).join(" "))}</p>
        </div>`
          )
          .join("")
      : `<p style='color:var(--text-dim)'>No ${tab} detected.</p>`;
  }

  function renderSuggestions(list) {
    const el = document.getElementById("dash-suggestions");
    if (!el) return;
    el.innerHTML = list.length
      ? list
          .map(
            (s) => `
        <article class="suggestion-card">
          <span class="suggestion-priority ${s.priority}">${s.priority}</span>
          <div>
            <h4>${escapeHtml(s.title)}</h4>
            <p>${escapeHtml(s.detail)}</p>
            ${s.impact ? `<small style="color:var(--neon-cyan)">${escapeHtml(s.impact)}</small>` : ""}
          </div>
        </article>`
          )
          .join("")
      : "<p>No suggestions — excellent baseline.</p>";
  }

  function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
  }
  function formatDate(iso) {
    try {
      return new Date(iso).toLocaleString();
    } catch {
      return iso || "—";
    }
  }
  function formatCat(c) {
    return c.replace(/_/g, " ").replace(/\b\w/g, (x) => x.toUpperCase());
  }
  function escapeHtml(str) {
    const d = document.createElement("div");
    d.textContent = str || "";
    return d.innerHTML;
  }
})();
