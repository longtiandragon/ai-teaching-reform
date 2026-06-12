# AGENTS.md

## Project Goal
Build an AI teaching reform demo with FastAPI and Vue 3 for two real course tracks:
- `springboot-course-12`: 12 SpringBoot lessons from `docs/course-materials`
- `nongbo-admin-project`: the real Nongbo admin system project, requirements, database, API docs, and source code

The demo must show a complete local learning loop:
- SpringBoot course workspace
- RAG-based course knowledge base
- DeepSeek-powered AI tutor
- Student practice feedback
- Teacher analytics dashboard

This is a demo-first project. Prefer a working MVP over a heavy full platform.

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
- Treat any user-provided key as temporary demo-only credential.
- Do not commit `.env`, local databases, vector indexes, virtual environments, or `node_modules`.

## Product Rules
- The first screen should be the usable course workspace, not a marketing landing page.
- Support both student and teacher views in the MVP.
- Student view should include course chapters, task content, code/practice area, and AI tutor chat.
- Prefer rendered code snippets, quizzes, and reflection prompts over heavy in-browser code editors for the MVP.
- Teacher view should include knowledge base status, learning progress, hot questions, and weak-point analysis.
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
- Do not introduce Milvus, Neo4j, Redis, RabbitMQ, Docker, or distributed services for the first demo unless explicitly requested later.
- Use `docs/course-materials` and the Nongbo project documents/source as the knowledge base. Do not add fake course chapters or fake citations.
- Do not implement real Java sandbox/OJ execution in the MVP; use rule-based and AI-assisted feedback instead.
- Do not add Monaco Editor or another heavy code editor unless the user explicitly asks for it later.
- Prefer clear service boundaries: courses, knowledge base, chat, practice, teacher analytics.

## Verification
Before considering work complete:
- Backend tests should pass with `pytest` where tests exist.
- Frontend should build successfully with `npm run build`.
- Local smoke test should verify:
  - course page loads
  - RAG knowledge base can be initialized
  - AI tutor returns an answer with citations, or a real error when citations/model calls fail
  - practice feedback returns a cited response, or a real error when evidence/model calls fail
  - teacher analytics page renders

## Future Expansion
The demo may later evolve into a full project with:
- login and roles
- real course resource management
- real code judging or sandbox execution
- persistent learning records
- deployment scripts
- more courses and reusable knowledge base management
