# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

AI Teaching Reform Demo — a FastAPI + Vue 3 demo for a SpringBoot integrated development course. Shows a complete local teaching loop: course workspace → RAG knowledge base → DeepSeek AI tutor → student practice feedback → teacher analytics dashboard.

## Essential Commands

### Virtual Environment

```powershell
& 'D:\Anaconda\python.exe' -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-optional-rag.txt   # ChromaDB RAG
```

### Run

```powershell
# Backend (port 8001)
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8001

# Frontend (port 5173, proxies /api → 8001)
cd frontend
npm run dev
```

### Verify

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests                           # backend tests
cd frontend ; npm run build                                                  # typecheck + build
.\.venv\Scripts\python.exe scripts\smoke_api.py                             # API smoke test (backend must be running)
```

## Architecture

### Backend (`backend/`)

```
app/
  config.py          # Settings loaded from .env via pydantic-settings; ROOT_DIR resolved
  models.py          # All Pydantic request/response models
  main.py            # FastAPI app: lifespan, CORS, all routes
  data/
    courses.py       # two real course tracks from docs/course-materials and the Nongbo project
  services/
    llm.py           # DeepSeekClient singleton — OpenAI-compatible chat + streaming
    rag.py           # RagService singleton — hybrid keyword + optional ChromaDB vector retrieval
    database.py      # SQLite interactions table (record + query for analytics)
    practice.py      # Rule-based checks + AI comment for practice submissions
    analytics.py     # Teacher dashboard data from interaction_rows()
    agent_tools.py   # 4 local agent skills: search, diagnose, snapshot, lesson_brief
```

**Key design decisions:**

- **Singletons:** `deepseek_client` and `rag_service` are module-level instances initialized at import time. `rag_service.ingest_seed()` runs in the FastAPI lifespan and can also be triggered manually via `POST /api/kb/ingest`.
- **Hybrid RAG:** Keyword retrieval always works. ChromaDB vector retrieval activates only when `chromadb` is installed and `RAG_BACKEND` is not `"keyword"`. ChromaDB failures degrade to keyword retrieval, but AI answers still require citations.
- **Strict DeepSeek calls:** When `DEEPSEEK_LIVE=false`, the API key is unset, citations are missing, or DeepSeek fails, chat and practice endpoints return real errors instead of fallback answers.
- **Database:** Single SQLite file (`backend/.data/demo.sqlite`) with one `interactions` table — stores chat, practice, and other interaction records for analytics.
- **SSE streaming:** `POST /api/chat/stream` returns Server-Sent Events with stages: `status → citations → delta* → done`.
- **Agent skills:** A lightweight Claude/MCP-inspired skill layer exposing 4 teaching tools via `GET /api/agent/skills` and `POST /api/agent/run`. Skills reference MCP-like architecture patterns but contain no Claude source code.

### Frontend (`frontend/`)

```
src/
  main.ts            # Vue entry point
  App.vue            # Shell layout with role-tab navigation
  router.ts          # Two routes: /student and /teacher (root redirects to /student)
  api.ts             # Axios-based API client + SSE stream parser
  styles.css         # Global CSS
  stores/
    course.ts        # Pinia store: courses, active lesson, health, skills
  views/
    StudentWorkspace.vue  # Course chapters, AI chat, practice submission
    TeacherDashboard.vue  # Knowledge base, analytics charts, interventions
  utils/
    markdown.ts      # Markdown rendering utilities
```

**Key design decisions:**

- Vite dev server proxies `/api` to `http://127.0.0.1:8001` — no CORS issues in dev.
- Code-split vendor bundles: vue/router/pinia/axios, lucide icons, echarts.
- No login/auth in the MVP — student/teacher views are just separate routes.
- Uses Element Plus for UI components and ECharts for analytics charts.

### RAG Tuning (`.env`)

```
RAG_BACKEND=hybrid          # "hybrid" | "keyword"
RAG_COLLECTION=springboot_course
RAG_CHUNK_SIZE=900
RAG_TOP_K=4
RAG_SNIPPET_SIZE=180
RAG_LESSON_BOOST=0.35       # boost for chunks matching current lesson_id
RAG_CONCEPT_BOOST=0.25      # boost for structured concept cards
RAG_VECTOR_CANDIDATES=10    # candidates fetched from ChromaDB before merging
```

### Demo Flow

1. `http://127.0.0.1:5173/student` — course workspace with chapter list, AI tutor chat, practice submission
2. `http://127.0.0.1:5173/teacher` — knowledge base init, progress charts, hot questions, weak points, interventions

## Project Constraints

- **MVP-first:** No login, no real Java sandbox, no Monaco Editor, no production deployment. Prefer working demo over heavy platform features.
- **Python runtime:** `D:\Anaconda\python.exe` (Windows).
- **Package manager:** `npm` (not pnpm/yarn).
- **Do not introduce:** Milvus, Neo4j, Redis, RabbitMQ, Docker, or distributed services for the first demo.
- **Security:** Secrets only in `.env`; never in frontend code, README, screenshots, or logs. `.env`, `.venv`, `node_modules`, `.data/`, `.chroma/`, and `uploads/` are gitignored.
- **RAG answers must include course citations or source snippets.** If DeepSeek fails, return a structured error and do not fabricate an answer.
