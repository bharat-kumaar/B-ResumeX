# B-ResumeX

**AI Resume Intelligence Platform** — parse, score, and optimize resumes with a production-ready Flask stack, modular AI engine, and SQL-backed reporting.

---

## Architecture

```
B-ResumeX/
├── app.py                 # Application factory & entry point
├── config.py              # Environment-aware configuration
├── requirements.txt
├── routes/                # Web UI + REST API blueprints
├── services/              # Business logic orchestration
├── ai_engine/             # Parser, analyzer, scorer, ML models
├── database/              # SQLAlchemy models + schema.sql
├── utils/                 # File handling, validation, helpers
├── templates/             # Jinja2 HTML templates
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── images/
├── uploads/               # Incoming resume files
├── reports/               # Generated JSON intelligence reports
└── logs/                  # Runtime logs
```

### Design principles

| Layer | Responsibility |
|-------|----------------|
| **Routes** | HTTP only — no business logic |
| **Services** | Orchestrate AI + DB + file I/O |
| **AI Engine** | Swappable ML/NLP modules |
| **Database** | Persistence via SQLAlchemy |
| **Utils** | Cross-cutting helpers |

---

## Tech stack

- **Backend:** Python 3.10+, Flask 3
- **Frontend:** HTML, CSS, JavaScript
- **AI/ML:** scikit-learn, numpy (extensible `ai_engine/models/`)
- **Database:** SQLite (dev) → PostgreSQL/MySQL (prod via `DATABASE_URL`)

---

## Quick start

### 1. Create virtual environment

```bash
cd B-ResumeX
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # macOS / Linux
```

Edit `.env` and set a strong `SECRET_KEY` for production.

### 4. Run the application

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## Platform features (v2)

- **Resume upload** — PDF/DOCX with validation (16 MB max)
- **Parsing** — Experience, education, projects, skills sections
- **ATS engine** — Real 0–100 score (formatting, keywords, completeness, structure, contact)
- **Skill detection** — Categorized skills + missing recommendations
- **AI suggestions** — Actionable improvements by priority
- **Dashboard** — `/dashboard` with sidebar, charts, insights
- **Database** — Resumes + analysis history (SQLite)

## API reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Service health check |
| `POST` | `/api/v1/analyze` | Upload + full analysis pipeline |
| `GET` | `/api/v1/analyses` | List analysis history |
| `GET` | `/api/v1/analyses/<id>` | Full analysis JSON |
| `GET` | `/api/v1/dashboard/stats` | Platform stats |
| `GET` | `/api/v1/reports/<id>` | Alias for analyses |

### Example — analyze resume

```bash
curl -X POST http://127.0.0.1:5000/api/v1/analyze \
  -F "resume=@/path/to/resume.pdf"
```

---

## Production deployment

```bash
gunicorn -w 4 -b 0.0.0.0:8000 "app:app"
```

Recommended:

- Set `FLASK_DEBUG=false`
- Use PostgreSQL: `DATABASE_URL=postgresql://user:pass@host/db`
- Serve static files via CDN or reverse proxy (Nginx)
- Store uploads/reports on object storage (S3, Azure Blob) at scale

---

## Roadmap

- [ ] Job-description matching & keyword gap analysis
- [ ] User accounts & saved resume history
- [ ] PDF/HTML export for reports
- [ ] Transformer-based NLP models in `ai_engine/models/`
- [ ] Docker & CI/CD pipeline

---

## License

MIT — Built for advanced resume intelligence workflows.
