/**
 * Dashboard upload zone — analyze and redirect
 */
(function () {
  "use strict";

  const API = "/api/v1";
  const MAX_MB = 16;

  document.addEventListener("DOMContentLoaded", init);

  function init() {
    const zone = document.getElementById("dash-upload-zone");
    const input = document.getElementById("dash-file-input");
    if (!zone || !input) return;

    zone.addEventListener("click", () => input.click());
    input.addEventListener("change", () => {
      if (input.files?.[0]) handleFile(input.files[0]);
    });

    ["dragenter", "dragover"].forEach((e) => {
      zone.addEventListener(e, (ev) => {
        ev.preventDefault();
        zone.classList.add("is-dragover");
      });
    });
    ["dragleave", "drop"].forEach((e) => {
      zone.addEventListener(e, (ev) => {
        ev.preventDefault();
        zone.classList.remove("is-dragover");
      });
    });
    zone.addEventListener("drop", (ev) => {
      const f = ev.dataTransfer?.files?.[0];
      if (f) handleFile(f);
    });
  }

  async function handleFile(file) {
    const err = validateClient(file);
    if (err) {
      alert(err);
      return;
    }

    const progress = document.getElementById("dash-upload-progress");
    progress?.classList.remove("hidden");

    const body = new FormData();
    body.append("resume", file);

    try {
      const res = await fetch(`${API}/analyze`, { method: "POST", body });
      const json = await res.json();
      if (!json.success) throw new Error(json.error || "Analysis failed");

      const id = json.data.id;
      window.location.href = `/dashboard/${id}`;
    } catch (e) {
      alert(e.message);
      progress?.classList.add("hidden");
    }
  }

  function validateClient(file) {
    const ext = file.name.split(".").pop()?.toLowerCase();
    if (!["pdf", "doc", "docx", "txt"].includes(ext)) {
      return "Use PDF or DOCX format.";
    }
    if (file.size > MAX_MB * 1024 * 1024) {
      return `File must be under ${MAX_MB} MB.`;
    }
    if (file.size === 0) return "File is empty.";
    return null;
  }
})();
