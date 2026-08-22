<div align="center">

# ResumeIQ

### AI-Powered Resume Intelligence & ATS Optimization Platform

Explainable ATS scoring, real semantic job matching, and resume parsing — built the way real Applicant Tracking Systems actually work, not a keyword-stuffing checklist.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-6-646CFF?style=flat&logo=vite&logoColor=white)](https://vitejs.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat&logo=python&logoColor=white)](https://www.sqlalchemy.org/)
[![Milvus](https://img.shields.io/badge/Milvus-Vector%20DB-00A1EA?style=flat&logo=milvus&logoColor=white)](https://milvus.io/)
[![Sentence Transformers](https://img.shields.io/badge/Sentence--BERT-Embeddings-FFD21E?style=flat&logo=huggingface&logoColor=black)](https://www.sbert.net/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-NLP-F7931E?style=flat&logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![JWT](https://img.shields.io/badge/Auth-JWT-000000?style=flat&logo=jsonwebtokens&logoColor=white)](https://jwt.io/)
[![Docker](https://img.shields.io/badge/Docker-Production-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

</div>

---

## Table of Contents

- [Overview](#overview)
- [What Makes This Different](#what-makes-this-different)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Development Phases](#development-phases)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Data Model](#data-model)
- [Roadmap](#roadmap)

---

## Overview

ResumeIQ takes a candidate's resume and, optionally, a target job description, and answers two questions that matter far more than most "ATS checkers" pretend to answer:

1. **Can an ATS actually parse this resume correctly?** — not "does it look nice," but will the parsing engine behind Workday, Greenhouse, iCIMS, or Taleo scramble the layout, drop a table's contents, or lose the candidate's contact info entirely.
2. **How well does this resume match a specific job?** — using the same literal keyword/skill screening real recruiters rely on, plus genuine semantic similarity via sentence embeddings, not superficial word overlap.

Every score the platform produces is fully explainable: no black-box percentage, every point earned or lost is tied to a specific, human-readable reason.

Resume ──▶ Document Parsing ──▶ Structured Resume ──▶ ATS Analysis
│
Job Description ──▶ Requirement Extraction │
│ ▼
└──────────────▶ Keyword / Skill / Semantic Matching ──▶ Explainable Score
│
(planned) AI Optimization ──▶ Fact Validation ──▶ Re-analysis

## What Makes This Different

| Capability | How it works |
|---|---|
| **Layout-aware parseability** | Detects multi-column layouts, tables, and header/footer-only contact info via `pdfplumber` word-position analysis (PDF) and raw XML inspection (DOCX) — the actual structural patterns that break real ATS parsers. |
| **Job-specific keyword screening** | Optionally scans a resume against a *specific* job posting's required skills and keywords, mirroring how systems like Workday/Taleo screen applicants for a requisition, not just a generic quality score. |
| **Synonym/acronym-aware matching** | "SEO" and "Search Engine Optimization" are treated as the same term. So are 30+ other common tech/business acronym pairs. Naive substring matching misses this constantly — a well-known complaint about low-quality ATS tools. |
| **Real semantic similarity** | Sentence-BERT (`all-MiniLM-L6-v2`) embeddings power genuine meaning-based matching, not keyword overlap. Embeddings are computed once at upload/creation time and cached, not recomputed per comparison. |
| **Fully explainable scoring** | Every ATS factor and match sub-score comes with the exact points earned, points possible, and a plain-language explanation. |

## Architecture

Strict layered architecture — routers never contain business logic:

┌─────────────┐ ┌──────────────┐ ┌────────────────────────┐
│ Router │ ──▶ │ Service │ ──▶ │ Database / AI / Files │
│ (HTTP only) │ │ (all logic) │ │ (PostgreSQL, Milvus, │
└─────────────┘ └──────────────┘ │ embedding models) │
└────────────────────────┘


- **Routers** — receive requests, validate input, authenticate, call a service, return a response. Nothing else.
- **Services** — own all business logic, grouped by domain (`auth`, `resume`, `ats`, `job`, `matching`, `embeddings`, `database`).
- **PostgreSQL** — system of record for every entity.
- **Milvus** — vector/semantic search only, never a source of truth. Optional: matching works via direct embedding comparison without it; Milvus becomes valuable once you need to search across thousands of resumes/jobs at once.
- **`EmbeddingProvider`** — an abstract interface so the embedding backend (currently sentence-BERT, with a TF-IDF fallback) can be swapped without touching any matching logic.

## Technology Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) + [Pydantic](https://docs.pydantic.dev/) — API framework and validation
- [SQLAlchemy 2.0](https://www.sqlalchemy.org/) — ORM, PostgreSQL only (no SQLite fallback)
- [python-jose](https://github.com/mpdavis/python-jose) + [passlib](https://passlib.readthedocs.io/)/bcrypt — JWT auth, password hashing
- [pypdf](https://pypdf.readthedocs.io/) / [pdfplumber](https://github.com/jsvine/pdfplumber) — PDF text + layout extraction
- [python-docx](https://python-docx.readthedocs.io/) — DOCX text + structure extraction
- [sentence-transformers](https://www.sbert.net/) — semantic embeddings (`all-MiniLM-L6-v2`, 384-dim)
- [scikit-learn](https://scikit-learn.org/) — TF-IDF fallback embeddings, keyword frequency analysis
- [pymilvus](https://milvus.io/docs/install-pymilvus.md) — Milvus vector database client

**Frontend**
- [React](https://react.dev/) (plain JSX, no TypeScript) + [Vite](https://vitejs.dev/)
- [React Router](https://reactrouter.com/) — client-side routing
- [Axios](https://axios-http.com/) — API client with token-refresh interceptors

**Infrastructure**
- [PostgreSQL](https://www.postgresql.org/) — required, primary datastore
- [Milvus](https://milvus.io/) — optional, standalone (Docker) or [Zilliz Cloud](https://zilliz.com/cloud) (managed)
- Docker — reserved for production deployment

## Project Structure

resume-ats-platform/
├── backend/
│ ├── main.py # FastAPI app factory / entrypoint
│ ├── config.py # Environment-based settings (PostgreSQL required)
│ ├── dependencies.py # get_db, get_current_user
│ ├── routers/ # Thin HTTP layer only
│ │ ├── auth_router.py
│ │ ├── resume_router.py
│ │ ├── ats_router.py
│ │ ├── job_router.py
│ │ ├── matching_router.py
│ │ └── health_router.py
│ ├── services/
│ │ ├── auth/ # Password hashing, JWT, register/login
│ │ ├── resume/ # Storage, extraction, structuring, layout analysis
│ │ ├── ats/ # Explainable scoring rules + job-specific scan
│ │ ├── job/ # Job description parsing (skills + keywords)
│ │ ├── matching/ # Keyword/skill/semantic matchers, synonyms
│ │ ├── embeddings/ # EmbeddingProvider (sentence-BERT, TF-IDF), Milvus
│ │ └── database/ # SQLAlchemy engine/session
│ ├── models/ # SQLAlchemy ORM models
│ └── schemas/ # Pydantic request/response schemas
│
├── frontend/
│ └── src/
│ ├── pages/ # Home, Login, Register, Dashboard, ResumeDetail
│ ├── components/ # ScoreRing, FactorBreakdown, JobMatchPanel, etc.
│ ├── context/ # AuthContext
│ └── services/ # Per-domain API clients
│
├── database/
│ └── schema.sql # Reference SQL (SQLAlchemy models are source of truth)
│
├── .env.example
└── README.md


## Development Phases

| Phase | Scope | Status |
|:---:|---|:---:|
| 1 | Project architecture + development foundation | ✅ |
| 2 | FastAPI + PostgreSQL + SQLAlchemy + Authentication | ✅ |
| 3 | Resume upload + PDF/DOCX parsing + structured resume | ✅ |
| 4 | ATS analysis engine + explainable scoring | ✅ Rebuilt around real ATS parsing behavior |
| 5 | Job description analysis + Milvus + semantic/keyword/skill matching | ✅ sentence-BERT + synonym-aware matching |
| 6 | React frontend — Dashboard, Resume, ATS, Job Matching UI | ✅ |
| 7 | LLM resume optimization + fact validation + versioning | ⏳ Planned |
| 8 | Redis/background jobs + Docker + testing + production hardening | ⏳ Planned |

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (local or remote) — **required**, no fallback database
- Milvus — *optional*: standalone via Docker, or a free [Zilliz Cloud](https://zilliz.com/cloud) cluster

### 1. Database

```sql
CREATE DATABASE resume_ats;
```

Tables are created automatically on first backend startup. There's no migration tool yet — schema changes to an *existing* database need manual `ALTER TABLE` statements (see `database/schema.sql` for the current columns).

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
copy ..\.env.example ..\.env    # then set DATABASE_URL and any other values
uvicorn main:app --reload
```

- API: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`
- Health check: `GET /api/health`

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

App: `http://localhost:5173`

### 4. Milvus (optional)

```bash
docker run -d --name milvus-standalone \
  -p 19530:19530 -p 9091:9091 \
  milvusdb/milvus:latest standalone
```

Then set `MILVUS_HOST=localhost` / `MILVUS_PORT=19530` in `.env`. Matching works without this — it's an optimization for searching across many resumes/jobs at scale, not a requirement.

## Environment Variables

See `.env.example` for the full template.

| Variable | Required | Description |
|---|:---:|---|
| `DATABASE_URL` | **Yes** | `postgresql://user:password@host:5432/dbname` — app refuses to start without a valid Postgres URL |
| `JWT_SECRET` | Recommended | Signing secret for auth tokens — change before sharing/deploying |
| `CORS_ORIGINS` | No | Comma-separated allowed frontend origins |
| `MILVUS_HOST` / `MILVUS_PORT` | No | Self-hosted Milvus connection |
| `MILVUS_URI` / `MILVUS_TOKEN` | No | Alternative: Zilliz Cloud |
| `EMBEDDING_PROVIDER` | No | `sentence-bert` (default) or `tfidf` |
| `EMBEDDING_MODEL_NAME` | No | Override the default sentence-transformers model |
| `UPLOAD_DIR` / `MAX_UPLOAD_SIZE_MB` | No | Local resume file storage |
| `LLM_API_KEY` | No | Reserved for Phase 7 |
| `VITE_API_BASE_URL` | No | Frontend → backend base URL |

## API Reference

All endpoints except `/api/health`, `/api/auth/register`, and `/api/auth/login` require `Authorization: Bearer <token>`.

<details>
<summary><strong>Auth</strong></summary>

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Create an account |
| `POST` | `/api/auth/login` | Get a JWT access token (OAuth2 form: `username`, `password`) |
| `GET` | `/api/auth/me` | Current authenticated user |

</details>

<details>
<summary><strong>Resumes</strong></summary>

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/resumes/upload` | Upload + parse a PDF/DOCX resume (multipart) |
| `GET` | `/api/resumes` | List the current user's resumes |
| `GET` | `/api/resumes/{id}` | Fetch a resume's full parsed data |

</details>

<details>
<summary><strong>ATS Analysis</strong></summary>

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/ats/resumes/{id}/analyze?job_id=` | Run ATS parseability analysis; `job_id` optionally adds a job-specific keyword/skill scan |
| `GET` | `/api/ats/resumes/{id}/scores` | Score history for a resume |
| `GET` | `/api/ats/scores/{id}` | Fetch a specific score |

</details>

<details>
<summary><strong>Jobs & Matching</strong></summary>

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/jobs` | Submit a job description (auto-extracts skills + keywords) |
| `GET` | `/api/jobs` / `GET /api/jobs/{id}` | List / fetch jobs |
| `POST` | `/api/matching/resumes/{resume_id}/jobs/{job_id}` | Run full skill + keyword + semantic matching |
| `GET` | `/api/matching/resumes/{id}/results` | Match history for a resume |
| `GET` | `/api/matching/results/{id}` | Fetch a specific match result |

</details>

## Data Model

| Table | Purpose |
|---|---|
| `users` | Accounts, hashed passwords |
| `resumes` | Uploaded files, extracted text, structured data, layout analysis, embedding |
| `ats_scores` | Explainable factor breakdowns + optional job-specific keyword scan |
| `jobs` | Parsed job descriptions — extracted skills, keywords, embedding |
| `match_results` | Skill/keyword/semantic sub-scores + matched/missing breakdowns |

Full reference: [`database/schema.sql`](./database/schema.sql).

## Roadmap

**Phase 7 — LLM Resume Optimization** *(next)*: AI-assisted rewriting targeted at a specific job, with fact validation against the original resume to prevent fabricated experience, plus resume versioning.

**Phase 8 — Production hardening**: Redis-backed background jobs, Docker Compose deployment, test coverage, rate limiting, and security review.

---

<div align="center">
<sub>Built incrementally, phase by phase.</sub>
</div>