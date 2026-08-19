-- =========================================================
-- AI Resume Intelligence & ATS Optimization Platform
-- Database schema
--
-- PostgreSQL is the system of record; Milvus only stores vector
-- embeddings that reference rows here by ID.
--
-- This file is kept in sync with the SQLAlchemy models by hand
-- for reference / manual setup. The SQLAlchemy models
-- (backend/models/) are the actual source of truth used by the
-- application; Alembic migrations can replace this manual file
-- once the schema stabilizes.
-- =========================================================

-- users (implemented - Phase 2)
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);

-- resumes (implemented - Phase 3)
CREATE TABLE IF NOT EXISTS resumes (
    id                SERIAL PRIMARY KEY,
    user_id           INTEGER NOT NULL REFERENCES users(id),
    original_filename VARCHAR(255) NOT NULL,
    file_type         VARCHAR(10) NOT NULL,        -- 'pdf' | 'docx'
    storage_path      VARCHAR(500) NOT NULL,
    file_size_bytes   INTEGER NOT NULL,
    raw_text          TEXT,
    structured_data   JSONB,                        -- ContactInfo, summary, experience, education, skills, projects
    parsing_status    VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending | succeeded | failed
    parsing_error     TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_resumes_user_id ON resumes (user_id);

-- ats_scores (implemented - Phase 4)
CREATE TABLE IF NOT EXISTS ats_scores (
    id             SERIAL PRIMARY KEY,
    resume_id      INTEGER NOT NULL REFERENCES resumes(id),
    user_id        INTEGER NOT NULL REFERENCES users(id),
    overall_score  FLOAT NOT NULL,                  -- 0-100
    factors        JSONB NOT NULL,                  -- list of AtsFactorResult (key, label, points_earned, points_possible, passed, explanation)
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_ats_scores_resume_id ON ats_scores (resume_id);
CREATE INDEX IF NOT EXISTS ix_ats_scores_user_id ON ats_scores (user_id);

-- =========================================================
-- Planned entities (not yet implemented - added in later phases)
-- =========================================================
--
-- Note: for Phase 3, parsed resume structure (experience, education,
-- skills, projects) is stored as a single JSON column on `resumes`
-- rather than normalized into separate tables below. Normalizing
-- into dedicated tables (with querying/filtering needs) can happen
-- in a later phase if matching/analysis requires it.

-- resume_versions
--   Historical / AI-optimized variants of a resume, versioned over time. (Phase 7)

-- experiences
--   Normalized work history entries, if/when needed beyond the JSON
--   structure stored on resumes.structured_data. (Later, if needed)

-- education
--   Normalized education entries, if/when needed. (Later, if needed)

-- skills
--   Normalized skill entities, linked to resumes and/or job requirements. (Phase 5)

-- projects
--   Normalized project entries, if/when needed. (Later, if needed)

-- jobs
--   Job descriptions submitted by a user for matching/analysis. (Phase 5)

-- job_requirements
--   Structured requirements (skills, keywords, qualifications) extracted
--   from a job description. (Phase 5)

-- analyses
--   A single analysis run linking a resume (version) to a job, tracking
--   pipeline status (parsing -> ATS -> matching -> scoring -> optimization). (Phase 5)

-- match_results
--   Keyword / semantic / skill match results between a resume and a job,
--   including the resulting job-match score. (Phase 5)

-- optimization_requests
--   Requests to AI-optimize a resume for a specific job, including
--   fact-validation status against the original resume content. (Phase 7)

-- subscriptions
--   Billing/plan state for a user (free vs. paid tiers). (Later)