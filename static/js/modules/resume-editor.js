(function () {
  "use strict";

  var currentDoc = {};
  var analysisId = null;

  window.BResumeXEditor = {
    render: function (doc, id) {
      currentDoc = doc ? safeClone(doc) : {};
      analysisId = id;

      var root = document.getElementById("resume-editor");
      if (!root) return;

      root.innerHTML = buildEditorHtml(currentDoc);
      bindInputs();
      renderPreviewSafe(currentDoc);
    },
    getDocument: function () {
      return collectFromDom();
    }
  };

  function buildEditorHtml(doc) {
    var c = doc.contact || {};
    var skills = doc.skills || {};
    var exp = Array.isArray(doc.experience) ? doc.experience : [];
    var edu = Array.isArray(doc.education) ? doc.education : [];
    var projects = Array.isArray(doc.projects) ? doc.projects : [];
    var certs = Array.isArray(doc.certifications) ? doc.certifications : [];

    var html = "";

    html += '<div class="editor-block">';
    html += '  <label>Name</label>';
    html += '  <input data-field="contact.name" value="' + escAttr(c.name || "") + '"/>';
    html += '  <label>Email</label>';
    html += '  <input data-field="contact.email" value="' + escAttr(c.email || "") + '"/>';
    html += "</div>";

    html += '<div class="editor-block">';
    html += '  <label>Professional Summary</label>';
    html += '  <textarea data-field="summary" rows="4">' + escHtml(doc.summary || "") + "</textarea>";
    html += "</div>";

    html += '<div class="editor-block">';
    html += '  <label>Skills (comma separated)</label>';
    html += '  <textarea data-field="skills_text" rows="3">' + escHtml(skillsToText(skills)) + "</textarea>";
    html += "</div>";

    html += '<div class="editor-block"><label>Experience</label>';
    for (var i = 0; i < exp.length; i++) {
      var e = exp[i] || {};
      html += '<div class="editor-exp" data-exp="' + i + '">';
      html += '  <input data-exp-field="title" value="' + escAttr(e.title || "") + '" placeholder="Title"/>';
      html += '  <input data-exp-field="company" value="' + escAttr(e.company || "") + '" placeholder="Company"/>';
      html += '  <input data-exp-field="dates" value="' + escAttr(e.dates || "") + '" placeholder="Dates"/>';
      html += '  <textarea data-exp-field="bullets" rows="3">' + escHtml((e.bullets || []).join("\n")) + "</textarea>";
      html += "</div>";
    }
    html += "</div>";

    html += '<div class="editor-block"><label>Education</label>';
    for (var j = 0; j < edu.length; j++) {
      var ed = edu[j] || {};
      html += '<div class="editor-ed" data-ed="' + j + '">';
      html += '  <input data-ed-field="degree" value="' + escAttr(ed.degree || "") + '" placeholder="Degree"/>';
      html += '  <input data-ed-field="institution" value="' + escAttr(ed.institution || "") + '" placeholder="Institution"/>';
      html += '  <input data-ed-field="years" value="' + escAttr(ed.years || "") + '" placeholder="YYYY"/>';
      html += "</div>";
    }
    html += "</div>";

    html += '<div class="editor-block"><label>Projects</label>';
    for (var k = 0; k < projects.length; k++) {
      var p = projects[k] || {};
      html += '<div class="editor-proj" data-proj="' + k + '">';
      html += '  <input data-proj-field="title" value="' + escAttr(p.title || "") + '" placeholder="Project"/>';
      html += '  <textarea data-proj-field="bullets" rows="3">' + escHtml((p.bullets || []).join("\n")) + "</textarea>";
      html += "</div>";
    }
    html += "</div>";

    html += '<div class="editor-block">';
    html += '  <label>Certifications</label>';
    html += '  <textarea data-field="certs_text" rows="3">' + escHtml((certs || []).join("\n")) + "</textarea>";
    html += "</div>";

    return html;
  }

  function bindInputs() {
    var btn = document.getElementById("btn-save-resume");
    if (btn && !btn.__bresumeBind) {
      btn.__bresumeBind = true;
      btn.addEventListener("click", saveResume);
    }

    document.addEventListener("input", function () {
      if (!currentDoc) return;
      try {
        renderPreviewSafe(collectFromDom());
      } catch (err) {}
    });
  }

  async function saveResume() {
    if (!analysisId) return;
    var doc = collectFromDom();

    try {
      var res = await fetch("/api/v1/analyses/" + analysisId + "/resume", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rebuilt_resume: doc })
      });

      var json = await res.json();
      if (!json.success) throw new Error(json.error);

      currentDoc = doc;
      renderPreviewSafe(currentDoc);
      alert("Resume saved successfully.");
    } catch (e) {
      alert(e && e.message ? e.message : "Save failed");
    }
  }

  function collectFromDom() {
    var doc = currentDoc ? safeClone(currentDoc) : {};
    doc.contact = doc.contact || {};

    var fields = document.querySelectorAll("[data-field]");
    for (var i = 0; i < fields.length; i++) {
      var inp = fields[i];
      var key = inp.dataset.field || "";
      if (key.indexOf("contact.") === 0) {
        doc.contact[key.split(".")[1]] = inp.value;
      } else if (key === "summary") {
        doc.summary = inp.value;
      }
    }

    var skillsTextEl = document.querySelector("[data-field='skills_text']");
    doc.skills = textToSkills(skillsTextEl ? skillsTextEl.value : "");

    var certsTextEl = document.querySelector("[data-field='certs_text']");
    doc.certifications = (certsTextEl ? certsTextEl.value : "")
      .split("\n")
      .map(function (s) { return s.trim(); })
      .filter(Boolean);

    doc.experience = [];
    var expBlocks = document.querySelectorAll(".editor-exp");
    for (var e = 0; e < expBlocks.length; e++) {
      var block = expBlocks[e];
      var item = {};
      var inputs = block.querySelectorAll("[data-exp-field]");
      for (var ii = 0; ii < inputs.length; ii++) {
        var el = inputs[ii];
        var f = el.dataset.expField;
        if (f === "bullets") {
          item.bullets = el.value
            .split("\n")
            .map(function (s) { return s.trim(); })
            .filter(Boolean);
        } else {
          item[f] = el.value;
        }
      }
      doc.experience.push(item);
    }

    doc.education = [];
    var eduBlocks = document.querySelectorAll(".editor-ed");
    for (var d = 0; d < eduBlocks.length; d++) {
      var edBlock = eduBlocks[d];
      var edItem = {};
      var edInputs = edBlock.querySelectorAll("[data-ed-field]");
      for (var jj = 0; jj < edInputs.length; jj++) {
        var el2 = edInputs[jj];
        edItem[el2.dataset.edField] = el2.value;
      }
      doc.education.push(edItem);
    }

    doc.projects = [];
    var projBlocks = document.querySelectorAll(".editor-proj");
    for (var pidx = 0; pidx < projBlocks.length; pidx++) {
      var projBlock = projBlocks[pidx];
      var pItem = {};
      var pInputs = projBlock.querySelectorAll("[data-proj-field]");
      for (var kk = 0; kk < pInputs.length; kk++) {
        var pl = pInputs[kk];
        var pf = pl.dataset.projField;
        if (pf === "bullets") {
          pItem.bullets = pl.value
            .split("\n")
            .map(function (s) { return s.trim(); })
            .filter(Boolean);
        } else {
          pItem[pf] = pl.value;
        }
      }
      doc.projects.push(pItem);
    }

    return doc;
  }

  function skillsToText(skills) {
    if (!skills) return "";
    if (Array.isArray(skills)) return skills.join(", ");
    if (typeof skills === "string") return skills;
    if (skills.core && Array.isArray(skills.core)) return skills.core.join(", ");
    if (skills.all_skills && Array.isArray(skills.all_skills)) return skills.all_skills.join(", ");
    if (typeof skills === "object") {
      var vals = [];
      Object.keys(skills).forEach(function (k) {
        var v = skills[k];
        if (Array.isArray(v)) vals = vals.concat(v);
      });
      return vals.join(", ");
    }
    return "";
  }

  function textToSkills(skillsText) {
    var parts = (skillsText || "")
      .split(",")
      .map(function (s) { return s.trim(); })
      .filter(Boolean);

    return { core: unique(parts).slice(0, 60) };
  }

  function unique(arr) {
    return Array.from(new Set(arr));
  }

  function renderPreviewSafe(doc) {
    var previewEl = document.getElementById("resume-preview");
    if (!previewEl) return;
    previewEl.innerHTML = renderPreviewHtml(doc);
  }

  function renderPreviewHtml(doc) {
    var c = doc.contact || {};
    var skills = doc.skills || {};
    var skillsList = Array.isArray(skills) ? skills : (skills.core || skills.all_skills || []);

    var html = '<div class="preview-doc">';
    html += '<h1 class="preview-name">' + escHtml(c.name || "Your Name") + "</h1>";

    var contactLine = [c.email, c.phone, c.linkedin, c.location].filter(Boolean).join(" | ");
    if (contactLine) html += '<div class="preview-contact">' + escHtml(contactLine) + "</div>";

    if (doc.summary) html += "<h2>Professional Summary</h2><p>" + escHtml(doc.summary) + "</p>";
    if (skillsList.length) html += "<h2>Skills</h2><p>" + escHtml(skillsList.join(", ")) + "</p>";

    if (Array.isArray(doc.experience) && doc.experience.length) {
      html += "<h2>Experience</h2>";
      for (var i = 0; i < doc.experience.length; i++) {
        var e = doc.experience[i] || {};
        html += '<div class="preview-item">';
        html += '<div class="preview-item-title">' + escHtml(e.title || "") + (e.company ? " — " + escHtml(e.company) : "") + "</div>";
        if (e.dates) html += '<div class="preview-item-sub">' + escHtml(e.dates) + "</div>";
        var bullets = Array.isArray(e.bullets) ? e.bullets : [];
        if (bullets.length) {
          html += "<ul>";
          for (var j = 0; j < bullets.length; j++) html += "<li>" + escHtml(bullets[j]) + "</li>";
          html += "</ul>";
        }
        html += "</div>";
      }
    }

    if (Array.isArray(doc.education) && doc.education.length) {
      html += "<h2>Education</h2>";
      for (var k = 0; k < doc.education.length; k++) {
        var ed = doc.education[k] || {};
        var title = escHtml(ed.degree || "");
        var sub = escHtml(ed.institution || "") + (ed.years ? " (" + escHtml(ed.years) + ")" : "");
        html += '<div class="preview-item"><div class="preview-item-title">' + title + '</div><div class="preview-item-sub">' + sub + "</div>";
      }
    }

    if (Array.isArray(doc.projects) && doc.projects.length) {
      html += "<h2>Projects</h2>";
      for (var p = 0; p < doc.projects.length; p++) {
        var pr = doc.projects[p] || {};
        html += '<div class="preview-item"><div class="preview-item-title">' + escHtml(pr.title || "") + "</div>";
        var b2 = Array.isArray(pr.bullets) ? pr.bullets : [];
        if (b2.length) {
          html += "<ul>";
          for (var q = 0; q < b2.length; q++) html += "<li>" + escHtml(b2[q]) + "</li>";
          html += "</ul>";
        }
        html += "</div>";
      }
    }

    if (Array.isArray(doc.certifications) && doc.certifications.length) {
      html += "<h2>Certifications</h2><ul>";
      for (var cidx = 0; cidx < doc.certifications.length; cidx++) {
        html += "<li>" + escHtml(doc.certifications[cidx]) + "</li>";
      }
      html += "</ul>";
    }

    html += "</div>";
    return html;
  }

  function escHtml(str) {
    var s = (str === undefined || str === null) ? "" : String(str);
    return s
      .replace(/&/g, "&amp;")
      .replace(/</g, "<")
      .replace(/>/g, ">")
      .replace(/"/g, "&quot;")

      .replace(/'/g, "&#039;");
  }


  function escAttr(str) {
    return escHtml(str);
  }

  function safeClone(obj) {
    try {
      return JSON.parse(JSON.stringify(obj));
    } catch (e) {
      return {};
    }
  }
})();
