/**
 * Analyze page — upload with validation, redirect to dashboard
 */
(function () {
  "use strict";

  const API = "/api/v1";
  const MAX_MB = 16;

  document.addEventListener("DOMContentLoaded", init);

  function init() {
    const form = document.getElementById("upload-form");
    const input = document.getElementById("resume-input");
    if (!form || !input) return;

    const zone = form;
    const loading = document.getElementById("analysis-loading");

    input.addEventListener("change", () => {
      if (input.files?.[0]) submit(input.files[0], loading);
    });

    ["dragenter", "dragover"].forEach((evt) => {
      zone.addEventListener(evt, (e) => {
        e.preventDefault();
        zone.classList.add("dragover");
      });
    });
    ["dragleave", "drop"].forEach((evt) => {
      zone.addEventListener(evt, (e) => {
        e.preventDefault();
        zone.classList.remove("dragover");
      });
    });
    zone.addEventListener("drop", (e) => {
      const file = e.dataTransfer?.files?.[0];
      if (file) submit(file, loading);
    });
  }

  async function submit(file, loadingEl) {
    const err = validateClient(file);
    if (err) {
      alert(err);
      return;
    }

    show(loadingEl);
    const body = new FormData();
    body.append("resume", file);

    try {
      const res = await fetch(`${API}/analyze`, { method: "POST", body });
      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || "Analysis failed");
      }
      window.location.href = `/dashboard/${data.data.id}`;
    } catch (err) {
      alert(err.message || "Unable to analyze resume.");
      hide(loadingEl);
    }
  }

  function validateClient(file) {
    const ext = file.name.split(".").pop()?.toLowerCase();
    if (!["pdf", "doc", "docx", "txt"].includes(ext)) {
      return "Only PDF and DOCX/DOC/TXT files are supported.";
    }
    if (file.size > MAX_MB * 1024 * 1024) return `Max file size is ${MAX_MB} MB.`;
    if (!file.size) return "File is empty.";
    return null;
  }

  function show(el) {
    if (el) el.classList.remove("hidden");
  }
  function hide(el) {
    if (el) el.classList.add("hidden");
  }
})();
