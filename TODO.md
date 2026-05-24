# TODO — B-ResumeX: advance + accuracy improvements

## Plan (approved)
### Phase 1 — Parsing accuracy core
- Inspect current section detection + entity parsers.
- Implement spaCy-backed semantic section detection.
- Add fuzzy heading matching + heading normalization.
- Add per-section and per-entity confidence scoring.
- Improve education/experience/skills/projects/certifications extraction with regex fallback.
- Add/adjust unit tests for parsing stability and confidence fields.
- Run pytest.

### Phase 2 — Job-specific ATS gap analysis
- Add job-description keyword extraction + canonical mapping.
- Update ATS scoring to compute job-specific missing keywords.
- Update suggestions engine accordingly.

### Phase 3 — AI resume rebuilder
- Make rebuild job-aware.
- Rewrite bullets using action verbs and consistent ATS formatting.

### Phase 4 — Export
- DOCX + PDF correctness.

### Phase 5 — Frontend dashboard
- Premium UX + real charts driven by backend JSON.

### Phase 6 — Backend + DB production readiness
- Modular refactor + persistence improvements.

### Phase 7 — Deployment configs
- Procfile/runtime/runtime.txt + env support.

---

## Progress
- [x] Repo exploration (core AI engine files read)
- [x] Plan approval received
- [x] Phase 1: spaCy-backed semantic section detection + fuzzy heading matching
- [x] Phase 1: confidence scoring + regex fallback improvements
- [x] Phase 1: tests + run pytest
- [ ] Phase 2: job-specific ATS gap analysis

