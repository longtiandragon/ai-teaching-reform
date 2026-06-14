# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

AI Teaching Reform Demo — a FastAPI + Vue 3 demo for a SpringBoot integrated development course. Shows a complete local teaching loop: course workspace → RAG knowledge base → DeepSeek AI tutor → student practice feedback → rubric-based task validation → teacher analytics dashboard.

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

# Frontend (port 5173, proxies /api → backend)
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

### Backend (`backend/app/`)

```
config.py              # Settings from .env via pydantic-settings; ROOT_DIR resolved
models.py              # All Pydantic request/response models
main.py                # FastAPI app: lifespan, CORS, all routes

data/
  courses.py           # Two course tracks built from docs and Nongbo project source
  course_runtime_seed.py  # Seed data: course lines, modules, tasks, rubrics
  questions.py         # Question bank seed (6-8 questions per lesson)

services/
  llm.py               # DeepSeekClient singleton — OpenAI-compatible chat + streaming
  rag.py               # RagService singleton — hybrid keyword + optional ChromaDB vector retrieval
  database.py          # SQLite with 11 tables (interactions, classes, users, learning_records,
                       #   course_lines, learning_modules, learning_tasks, task_rubrics,
                       #   student_task_progress, task_submissions, guided_sessions)
  agent_flow.py        # LangGraph teaching agent: detect_intent → rewrite_query → retrieve_context → generate_answer → plan_next_action
  guided_agent.py      # LangGraph guided teaching: classify_intent → plan_steps → [retrieve → teach → wait] × N → summarize
  agent_tools.py       # 4 agent skills: course_knowledge_search, practice_diagnose, teacher_snapshot, lesson_brief
  ai_check.py          # Learning task check: RAG search → rubric evaluation → LLM feedback → scoring
  course_runtime.py    # Course line CRUD, learning map generation, task detail, progress tracking
  rubric_engine.py     # Generic rubric engine (keyword, regex, concept, rag_grounded, code_pattern, anti_shortcut)
  kb_manager.py        # Knowledge base file CRUD + task association
  ai_config.py         # AI configuration management (DeepSeek API key, model, etc.)
  practice.py          # Rule-based checks + AI comment for practice submissions
  analytics.py         # Teacher dashboard analytics
```

### Frontend (`frontend/src/`)

```
main.ts                # Vue entry, registers Pinia, router, Element Plus
App.vue                # Shell: restores session, redirects to correct route
router.ts              # Routes + role-based guards

views/
  LoginPage.vue        # Unified login (student/teacher selection)
  StudentLayout.vue    # Student shell: topbar, nav, ScanlineOverlay, BorderLightFlow
  TeacherLayout.vue    # Teacher shell: topbar, nav (macaron HF style)
  CourseRoadmap.vue    # Course selection + asymmetric Bento grid learning map
  TaskWorkspace.vue    # AI guided workspace: chat + code editor + result panel
  StudentRecords.vue   # Learning records timeline
  AIConfigPanel.vue    # AI configuration (dual-style: student Liquid Glass / teacher macaron)
  TeacherDashboard.vue # Teacher analytics: charts, progress, question bank
  KnowledgeManager.vue # Knowledge base file management
  StudentManagement.vue# Student list and analysis
  FeedbackCenter.vue   # Teacher feedback to students

components/
  ScanlineOverlay.vue  # Rainbow flowing scanline effect (student side)
  BorderLightFlow.vue  # Border light flow animation on navigation (student side)

stores/
  course.ts            # Pinia: courses, learning map, tasks
  session.ts           # Pinia: user session, login/logout

styles/
  student-theme.css    # Student theme: cream + amber gold (#FFFBEB + #D97706)
  teacher-theme.css    # Teacher theme: macaron warm (no blue)
```

### Design System

**Student side** — Liquid Glass + warm cream amber gold:
- Font: Playfair Display (headings) + Inter (body) + JetBrains Mono (code)
- Colors: #FFFBEB (bg), #0F172A (text), #D97706 (accent)
- Effects: grain overlay, rainbow scanlines, border light flow, staggered fadeUp animations
- Cards: 18px radius, subtle borders, hover lift

**Teacher side** — Macaron HF style (no blue):
- Font: Inter + Noto Sans SC
- Colors: #F8F7F4 (bg), #FF9D76 (primary), #C4A1FF (secondary), #7DD3A8 (tertiary)
- Element Plus components

### AI Configuration

The AI config page (`/student/ai-config` and `/teacher/ai-config`) uses a single component with dual styles:
- Detects route via `useRoute()` → `isTeacher` computed
- Student side: Liquid Glass design
- Teacher side: original macaron HF design

### Key Design Decisions

- **Singletons:** `deepseek_client` and `rag_service` are module-level instances initialized at import time.
- **Hybrid RAG:** Keyword retrieval always works. ChromaDB vector retrieval activates when `chromadb` is installed and `RAG_BACKEND` is not `"keyword"`.
- **Strict DeepSeek calls:** When `DEEPSEEK_LIVE=false`, API key is unset, citations are missing, or DeepSeek fails — endpoints return real errors, never fabricated answers.
- **SSE streaming:** `POST /api/chat/stream` returns Server-Sent Events: `status → citations → delta* → done`.
- **Scoring model:** `final_score = rule_score × 0.6 + ai_score × 0.4`. Passed = `final_score >= minScore AND NOT critical_failed`.
- **Route guards:** Students can only access `/student/*`, teachers only `/teacher/*`. Login required for all pages.
- **Vite proxy:** `VITE_API_TARGET` defaults to `http://127.0.0.1:8001`.

### SQLite Database

11 tables at `backend/.data/learning.sqlite`: interactions, classes, users, learning_records, course_lines, learning_modules, learning_tasks, task_rubrics, student_task_progress, task_submissions, guided_sessions.

### RAG Tuning (`.env`)

```
RAG_BACKEND=hybrid          # "hybrid" | "keyword"
RAG_COLLECTION=springboot_course
RAG_CHUNK_SIZE=900
RAG_TOP_K=4
RAG_SNIPPET_SIZE=180
RAG_LESSON_BOOST=0.35
RAG_CONCEPT_BOOST=0.25
RAG_VECTOR_CANDIDATES=10
```

## Project Constraints

- **MVP-first:** No login, no real Java sandbox, no Monaco Editor, no production deployment.
- **Python runtime:** System default Python or Anaconda.
- **Package manager:** `npm` (not pnpm/yarn).
- **Do not introduce:** Milvus, Neo4j, Redis, RabbitMQ, Docker, or distributed services.
- **Security:** Secrets only in `.env`; never in frontend code.
- **RAG answers must include course citations.** If DeepSeek fails, return structured error — never fabricate.
