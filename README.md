# AI Teaching Reform Demo

FastAPI + Vue 3 demo for two real course tracks: the 12-lesson SpringBoot course in `docs/course-materials` and the Nongbo admin system project in `农博后台管理系统项目1-5-20260609`. The project shows a complete local teaching loop:

- SpringBoot course workspace
- RAG-based course knowledge base
- DeepSeek-powered AI tutor
- Student practice feedback
- Teacher analytics dashboard

This version is real-material-first: course chapters, references, and practice examples should come from the provided Markdown, project docs, database schema, requirements, and source code.

## Stack

- Backend: FastAPI, SQLite, LangGraph agent flow, hybrid RAG with optional ChromaDB and keyword retrieval
- Frontend: Vue 3, Vite, TypeScript, Element Plus, ECharts, lightweight code blocks and quiz practice
- LLM: DeepSeek OpenAI-compatible API
- Python runtime: `D:\Anaconda\python.exe`
- Package manager: `npm`

## Setup

Create the backend virtual environment:

```powershell
& 'D:\Anaconda\python.exe' -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

Install the optional vector RAG backend:

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-optional-rag.txt
```

Install frontend dependencies:

```powershell
cd frontend
npm install
```

Copy `.env.example` to `.env` and set local secrets there only. Do not place real keys in README files, frontend code, screenshots, or logs.

Set `DEEPSEEK_LIVE=true` when you want AI chat and practice feedback to call the real DeepSeek API. When it is `false`, or when the API call times out/fails, AI endpoints return a real error instead of a fabricated fallback answer.

## Run

Backend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8001
```

Frontend:

```powershell
cd frontend
npm run dev
```

Open `http://127.0.0.1:5173`.

## RAG Settings

The backend uses LangGraph for agent orchestration and a hybrid course retrieval pipeline for the RAG node:

- current-lesson boost based on `lesson_id`
- ChromaDB vector retrieval when optional RAG dependencies are installed
- keyword retrieval so the knowledge base remains searchable without vector packages

The LangGraph flow is:

```text
detect_intent -> rewrite_query -> retrieve_context -> generate_answer -> plan_next_action
```

LangGraph controls the learning-state flow; the Hybrid Retriever controls retrieval quality. This avoids relying on plain vector similarity for short student questions such as "why does this not roll back". If retrieval returns no citations, the AI call is stopped.

RAG can be tuned in `.env`:

```env
RAG_BACKEND=hybrid
RAG_COLLECTION=springboot_course
RAG_CHUNK_SIZE=900
RAG_TOP_K=4
RAG_SNIPPET_SIZE=180
RAG_LESSON_BOOST=0.35
RAG_CONCEPT_BOOST=0.25
RAG_VECTOR_CANDIDATES=10
```

Useful defaults:

- raise `RAG_TOP_K` to `5` when answers need more references
- lower `RAG_CHUNK_SIZE` to `600-750` when uploaded documents are dense
- raise `RAG_LESSON_BOOST` when students ask short questions like "why is this wrong"
- `RAG_CONCEPT_BOOST` is retained for compatibility, but the current real-material index prioritizes lesson, project, SQL, standard, and requirement chunks.

## Agent Skills

The demo includes a lightweight Claude/MCP-inspired skill layer. It does not depend on or copy any proprietary Claude source code. The idea is to expose local teaching capabilities as structured tools:

- `course_knowledge_search`: current-lesson-aware Hybrid RAG search
- `practice_diagnose`: practice submission diagnosis and AI feedback
- `teacher_snapshot`: learning analytics and intervention snapshot
- `lesson_brief`: lesson objectives, task content, and suggested prompts

Skill APIs:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8001/api/agent/skills
```

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8001/api/agent/run `
  -ContentType 'application/json' `
  -Body '{"name":"course_knowledge_search","arguments":{"course_id":"nongbo-admin-project","query":"AuthController 登录 Result","lesson_id":"nongbo-login-auth"}}'
```

## Verify

Backend tests:

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests
```

Frontend build:

```powershell
cd frontend
npm run build
```

API smoke test, with the backend already running on port `8001`:

```powershell
.\.venv\Scripts\python.exe scripts\smoke_api.py
```

Expected smoke coverage:

- health reports database, model, and RAG backend status
- the two real courses and lesson data load
- seed knowledge base initializes
- AI tutor returns an answer with citations, or a strict error when DeepSeek is unavailable
- practice submission returns cited feedback, or a strict error when DeepSeek is unavailable
- teacher analytics returns real interaction and knowledge-base statistics

## Demo Flow

1. Open the student workspace at `http://127.0.0.1:5173/student`.
2. Switch between the SpringBoot 12-lesson course and the Nongbo admin project course.
3. Ask the AI tutor about the current lesson or real project module.
4. Review the answer and cited course snippets.
5. Complete the practice check with the rendered code snippet, quiz answers, and reflection notes.
6. Switch to `http://127.0.0.1:5173/teacher`.
7. Initialize the knowledge base and inspect progress, hot questions, and weak points.

## Notes

- ChromaDB/FastEmbed is optional at install time. If it is unavailable, the backend keeps retrieval usable with keyword ranking.
- The MVP intentionally does not implement login, permissions, a real Java sandbox, course purchasing, online exams, or production deployment.
- Local generated data is ignored by `.gitignore`, including `.env`, `.venv`, `node_modules`, SQLite data, uploads, and vector indexes.
