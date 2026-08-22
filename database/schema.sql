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

-- resumes (implemented - Phase 3, embedding + layout_analysis added later)
CREATE TABLE IF NOT EXISTS resumes (
    id                SERIAL PRIMARY KEY,
    user_id           INTEGER NOT NULL REFERENCES users(id),
    original_filename VARCHAR(255) NOT NULL,
    file_type         VARCHAR(10) NOT NULL,        -- 'pdf' | 'docx'
    storage_path      VARCHAR(500) NOT NULL,
    file_size_bytes   INTEGER NOT NULL,
    raw_text          TEXT,
    embedding         JSONB,                        -- fixed-dim vector (384 for sentence-BERT MiniLM), null if not yet computed
    structured_data   JSONB,                        -- ContactInfo, summary, experience, education, skills, projects
    layout_analysis   JSONB,                        -- multi_column, has_tables, contact_only_in_header_footer, garbled_text_ratio, notes
    parsing_status    VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending | succeeded | failed
    parsing_error     TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_resumes_user_id ON resumes (user_id);

-- ats_scores (implemented - Phase 4, job-specific scan added later)
CREATE TABLE IF NOT EXISTS ats_scores (
    id             SERIAL PRIMARY KEY,
    resume_id      INTEGER NOT NULL REFERENCES resumes(id),
    user_id        INTEGER NOT NULL REFERENCES users(id),
    overall_score  FLOAT NOT NULL,                  -- 0-100, job-independent parsability/quality score
    factors        JSONB NOT NULL,                  -- list of AtsFactorResult (key, label, points_earned, points_possible, passed, explanation)
    job_id         INTEGER REFERENCES jobs(id),      -- nullable: set when analysis included a job-specific scan
    job_match      JSONB,                            -- nullable AtsJobMatch: match_score, matched/missing skills+keywords for job_id
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_ats_scores_resume_id ON ats_scores (resume_id);
CREATE INDEX IF NOT EXISTS ix_ats_scores_user_id ON ats_scores (user_id);

-- jobs (implemented - Phase 5, embedding added later)
CREATE TABLE IF NOT EXISTS jobs (
    id               SERIAL PRIMARY KEY,
    user_id          INTEGER NOT NULL REFERENCES users(id),
    title            VARCHAR(255) NOT NULL,
    description      TEXT NOT NULL,
    required_skills  JSONB NOT NULL DEFAULT '[]',   -- skills detected via vocabulary matching
    keywords         JSONB NOT NULL DEFAULT '[]',   -- frequent significant unigrams/bigrams, excluding detected skills
    embedding        JSONB,                          -- fixed-dim vector (384 for sentence-BERT MiniLM), null if not yet computed
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_jobs_user_id ON jobs (user_id);

-- match_results (implemented - Phase 5)
CREATE TABLE IF NOT EXISTS match_results (
    id                 SERIAL PRIMARY KEY,
    user_id            INTEGER NOT NULL REFERENCES users(id),
    resume_id          INTEGER NOT NULL REFERENCES resumes(id),
    job_id             INTEGER NOT NULL REFERENCES jobs(id),
    keyword_score      FLOAT NOT NULL,              -- 0-100
    semantic_score     FLOAT NOT NULL,               -- 0-100, sentence-BERT cosine similarity
    skill_score        FLOAT NOT NULL,               -- 0-100
    overall_score      FLOAT NOT NULL,               -- weighted: 35% skill, 30% keyword, 35% semantic
    matched_keywords   JSONB NOT NULL DEFAULT '[]',
    missing_keywords   JSONB NOT NULL DEFAULT '[]',
    matched_skills     JSONB NOT NULL DEFAULT '[]',
    missing_skills     JSONB NOT NULL DEFAULT '[]',
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_match_results_resume_id ON match_results (resume_id);
CREATE INDEX IF NOT EXISTS ix_match_results_job_id ON match_results (job_id);
CREATE INDEX IF NOT EXISTS ix_match_results_user_id ON match_results (user_id);

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
--   Normalized skill entities, if querying/filtering by skill across
--   resumes/jobs is needed beyond the JSON columns already in place. (Later, if needed)

-- projects
--   Normalized project entries, if/when needed. (Later, if needed)

-- job_requirements
--   Normalized requirement rows, if needed beyond jobs.required_skills /
--   jobs.keywords JSON columns. (Later, if needed)

-- analyses
--   A single analysis run linking a resume (version) to a job, tracking
--   pipeline status end-to-end (parsing -> ATS -> matching -> scoring ->
--   optimization), if a unified pipeline-tracking view becomes useful
--   beyond querying ats_scores/match_results directly. (Later, if needed)

-- optimization_requests
--   Requests to AI-optimize a resume for a specific job, including
--   fact-validation status against the original resume content. (Phase 7)

-- subscriptions
--   Billing/plan state for a user (free vs. paid tiers). (Later)