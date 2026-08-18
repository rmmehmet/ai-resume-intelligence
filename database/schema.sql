-- =========================================================
-- AI Resume Intelligence & ATS Optimization Platform
-- Database schema (Phase 1 placeholder)
--
-- This file documents the planned major entities. Actual
-- SQLAlchemy models and Alembic migrations will be introduced
-- in Phase 2. PostgreSQL is the system of record; Milvus only
-- stores vector embeddings that reference rows here by ID.
-- =========================================================

-- users
--   Account identity, credentials (hashed), plan/subscription tier.

-- resumes
--   Uploaded resume files and their parsed, structured content.
--   Belongs to a user.

-- resume_versions
--   Historical / AI-optimized variants of a resume, versioned over time.

-- experiences
--   Work history entries parsed from a resume (title, company, dates, bullets).

-- education
--   Education history entries parsed from a resume.

-- skills
--   Normalized skill entities, linked to resumes and/or job requirements.

-- projects
--   Project entries parsed from a resume.

-- jobs
--   Job descriptions submitted by a user for matching/analysis.

-- job_requirements
--   Structured requirements (skills, keywords, qualifications) extracted
--   from a job description.

-- analyses
--   A single analysis run linking a resume (version) to a job, tracking
--   pipeline status (parsing -> ATS -> matching -> scoring -> optimization).

-- ats_scores
--   Explainable ATS compatibility score and its contributing factors
--   for a given resume version.

-- match_results
--   Keyword / semantic / skill match results between a resume and a job,
--   including the resulting job-match score.

-- optimization_requests
--   Requests to AI-optimize a resume for a specific job, including
--   fact-validation status against the original resume content.

-- subscriptions
--   Billing/plan state for a user (free vs. paid tiers).

-- Actual table definitions (columns, types, constraints, indexes,
-- foreign keys) will be added in Phase 2 alongside the corresponding
-- SQLAlchemy models.