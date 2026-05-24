/**
 * Homepage upload zone — redirects to analyzer with file or quick upload
 */
(function () {
  "use strict";

  const API_BASE = "/api/v1";

  function init() {
    const zone = document.getElementById("home-upload-zone");
    const input = document.getElementById("home-resume-input");
    if (!zone || !input) return;

    zone.addEventListener("click", () => input.click());
    zone.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        input.click();
      }
    });

    input.addEventListener("change", () => {
      const file = input.files?.[0];
      if (file) handleFile(file, zone);
    });

    ["dragenter", "dragover"].forEach((evt) => {
      zone.addEventListener(evt, (e) => {
        e.preventDefault();
        zone.classList.add("is-dragover");
      });
    });

    ["dragleave", "drop"].forEach((evt) => {
      zone.addEventListener(evt, (e) => {
        e.preventDefault();
        zone.classList.remove("is-dragover");
      });
    });

    zone.addEventListener("drop", (e) => {
      const file = e.dataTransfer?.files?.[0];
      if (file) handleFile(file, zone);
    });
  }

  function handleFile(file, zone) {
    zone.querySelector("h3").textContent = "Scanning…";
    zone.style.pointerEvents = "none";

    const body = new FormData();
    body.append("resume", file);

    fetch(`${API_BASE}/analyze`, { method: "POST", body })
      .then((res) => res.json().then((data) => ({ ok: res.ok, data })))
      .then(({ ok, data }) => {
        if (!ok) throw new Error(data.error || "Analysis failed");
        window.location.href = `/dashboard/${data.data.id}`;
      })
      .catch((err) => {
        alert(err.message || "Upload failed. Try the full analyzer.");
        zone.querySelector("h3").textContent = "Drop Resume Here";
        zone.style.pointerEvents = "";
      });
  }

  document.addEventListener("DOMContentLoaded", init);
})();
