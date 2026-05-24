-- B-ResumeX v2 schema

CREATE TABLE IF NOT EXISTS resumes (
    id              VARCHAR(36) PRIMARY KEY,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_path       VARCHAR(512) NOT NULL,
    file_size       INTEGER DEFAULT 0,
    file_type       VARCHAR(16) NOT NULL,
    uploaded_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analysis_records (
    id          VARCHAR(36) PRIMARY KEY,
    resume_id   VARCHAR(36) NOT NULL REFERENCES resumes(id),
    ats_score   REAL DEFAULT 0,
    grade       VARCHAR(2) DEFAULT 'C',
    result_json TEXT NOT NULL,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_analysis_created ON analysis_records (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_resume_uploaded ON resumes (uploaded_at DESC);
