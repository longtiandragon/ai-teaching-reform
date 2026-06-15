# AGENTS.md

## Project Goal
Build a production-oriented AI teaching reform platform with FastAPI and Vue 3 for two real course tracks:
- `springboot-course-12`: 12 SpringBoot lessons from `docs/course-materials`
- `nongbo-admin-project`: the real Nongbo admin system project, requirements, database, API docs, and source code

The platform must support a complete local learning loop:
- SpringBoot course workspace
- RAG-based course knowledge base
- DeepSeek-powered AI tutor
- Student practice feedback
- Teacher analytics dashboard

This is no longer a demo. Treat it as a real teaching system under active construction. Prefer incremental, verifiable delivery, but do not use "MVP" or "demo" as a reason to skip persistence, permissions, security, real data, or complete user workflows.

## Tech Stack
- Backend: FastAPI, Python 3.12, SQLite, LangGraph agent flow, local vector store, RAG services
- Python runtime: `D:\Anaconda\python.exe`
- Frontend: Vue 3, Vite, TypeScript, Element Plus, ECharts, lightweight code blocks and quiz practice
- LLM: DeepSeek OpenAI-compatible API
- Default model: `deepseek-v4-flash`
- Package manager: `npm` unless the user explicitly asks otherwise

## Security Rules
- Never expose API keys in frontend code, README files, logs, screenshots, or examples.
- Keep real secrets only in `.env`.
- Provide `.env.example` with variable names only.
- Treat any user-provided key as sensitive credential material.
- Do not commit `.env`, local databases, vector indexes, virtual environments, or `node_modules`.
- Student and teacher capabilities must be separated by authentication and authorization.
- API responses must never return API key plaintext. Show masked secrets only.
- Use account/student-number plus password login and JWT-based session control unless the user explicitly chooses another auth design.
- Do not rely on frontend-only checks for RBAC-sensitive behavior.

## Product Rules
- The first screen should be the usable course workspace, not a marketing landing page.
- Support both student and teacher views as first-class product surfaces.
- Student view should include course chapters, task content, code/practice area, and AI tutor chat.
- Support the real question types used by the course workflow: single choice, multiple choice, true/false, short answer, and code fill.
- Prefer rendered code snippets, quizzes, and reflection prompts over heavy in-browser code editors unless the user explicitly requests a full editor.
- Teacher view should include knowledge base status, learning progress, hot questions, and weak-point analysis.
- Teacher view must include question management with create, edit, publish, unpublish, soft delete, answer/explanation review, and AI-assisted explanation generation.
- Published/unpublished/deleted question states must be explicit. Unpublish means return to pending/draft state; delete means soft delete so student records remain valid.
- Student submission records must preserve the submitted answer/code, AI interaction context, feedback, score, and enough task metadata for later review.
- RAG answers must include course citations or source snippets when available.
- Prefer hybrid course retrieval over plain vector search: structured concept cards, current-lesson boost, keyword fallback, and vector retrieval when available.
- Use LangGraph/LangChain-style orchestration for multi-step learning flows; keep the Hybrid Retriever as the retrieval node, not as a replacement for agent orchestration.
- If RAG has no citations, DeepSeek is disabled, times out, or fails, return a clear error. Do not generate fake fallback answers.
- It is acceptable to reference public Claude/MCP-style architecture ideas, but do not copy leaked, proprietary, or non-licensed Claude source code.
- Expose AI capabilities as lightweight local skills/tools before introducing a full external MCP server.

## UI Direction
- Reference Educoder-style course and training workflows.
- Do not copy Educoder branding, logos, or proprietary assets.
- Keep the interface clean, practical, course-centered, and suitable for repeated teaching use.
- Avoid generic AI landing-page aesthetics.
- Use icons for actions where appropriate.
- Ensure text does not overflow on desktop or mobile layouts.

## Implementation Rules
- Keep the architecture lightweight and easy to run locally.
- Do not introduce Milvus, Neo4j, Redis, RabbitMQ, Docker, or distributed services unless there is a concrete product requirement and the user approves the added operational weight.
- Use `docs/course-materials` and the Nongbo project documents/source as the knowledge base. Do not add fake course chapters or fake citations.
- Do not implement real Java sandbox/OJ execution until explicitly requested; use rule-based and AI-assisted feedback while preserving upgrade paths for future judging.
- Do not add Monaco Editor or another heavy code editor unless the user explicitly asks for it later.
- Prefer clear service boundaries: auth/RBAC, courses, knowledge base, chat, practice, question bank, submissions, teacher analytics.
- Persist user-created teaching data. Do not store teacher-created questions only in process memory.
- Use soft delete for records that may be referenced by student history, including questions and published question bindings.
- Avoid fake fallback answers. If evidence, citations, or model calls fail, return a clear error and let the UI explain the failure.

## Verification
Before considering work complete:
- Backend tests should pass with `pytest` where tests exist.
- Frontend should build successfully with `npm run build`.
- Local smoke test should verify:
  - account/student-number plus password login works for student and teacher accounts
  - role-specific navigation and API behavior do not expose teacher-only features to students
  - course page loads
  - RAG knowledge base can be initialized
  - AI tutor returns an answer with citations, or a real error when citations/model calls fail
  - practice feedback returns a cited response, or a real error when evidence/model calls fail
  - question publishing/unpublishing updates the UI immediately without requiring page refresh
  - deleted questions disappear from active teacher/student queries while historical submissions remain readable
  - submission record detail shows student answer/code, AI feedback, and relevant conversation/history
  - teacher analytics page renders

## Development Roadmap
Current baseline:
- Formal student/teacher login with JWT and RBAC-aware UI/API boundaries.
- Persistent course, question, publish-state, learning-record, and submission data.
- Real SpringBoot course and Nongbo project materials as the only accepted knowledge sources.
- Student workflows for roadmap, task learning, five question types, AI guidance, submission, and record review.
- Teacher workflows for knowledge base, question bank, publishing, feedback, analytics, and masked AI configuration.

Near-term priorities:
- Strengthen backend RBAC checks for every teacher-only endpoint.
- Add database migrations or schema-version management instead of ad hoc column creation.
- Add focused tests for auth, question soft delete, publish state transitions, and submission detail recovery.
- Improve teacher question authoring with validation per question type and batch import/export.
- Improve student record detail so AI conversation, hints, answer/code, evidence, and rubric scores are all reviewable.

Later expansion:
- Course resource lifecycle management with versioning.
- Real Java judging or sandbox execution when explicitly requested.
- Deployment scripts and production environment configuration.
- More courses and reusable knowledge base management.
- Audit logs for teacher actions and sensitive configuration changes.
