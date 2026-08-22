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