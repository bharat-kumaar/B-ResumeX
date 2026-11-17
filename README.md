# RESUMATE AI - Fast Architecture

## Overview
RESUMATE AI is a modern, premium AI-powered resume analysis platform. It securely parses your resume (PDF/DOCX) locally, compares it against target Job Descriptions, and provides a deterministic, explainable ATS compatibility score with precise keyword highlighting.

## Tech Stack
* **Backend:** FastAPI (Python 3)
* **Database:** SQLite (managed via SQLModel / SQLAlchemy)
* **Authentication:** JWT & bcrypt
* **Frontend:** Jinja2 Templates + Tailwind CSS (Standalone) + Vanilla JS (No Node.js required)
* **NLP & Parsing:** `spacy`, `pdfplumber`, `docx2txt`

## Installation

### 1. Set up Environment
```bash
python -m venv venv
# On Windows
.\venv\Scripts\Activate.ps1
# On Mac/Linux
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install fastapi uvicorn[standard] sqlmodel jinja2 python-multipart pydantic[email] bcrypt pyjwt pdfplumber docx2txt spacy
python -m spacy download en_core_web_sm
```

### 3. Run the Application
```bash
python -m uvicorn app.main:app --reload --port 8000
```
Open `http://127.0.0.1:8000` in your browser.

## Features Built
- Beautiful, accessible, premium Vercel-inspired UI.
- Light and Dark mode theming.
- Secure user authentication.
- Drag-and-drop resume uploading with optional Job Description context.
- Explanatory scoring (Keywords, Readability, Structure).
- Live Dashboard with history and metrics.

## Limitations
- AI suggestions (rewriting) are currently simulated because no API key (e.g. OpenAI/Anthropic) is configured in the environment.
- The `Editor Workspace` is stubbed and opens an alert for now, as we focus on the core analysis pipeline.