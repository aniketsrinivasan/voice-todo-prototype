### IMPLEMENTATION_GUIDE.md (backend-first)

This guide explains how to implement the Python backend in `backend/` using FastAPI, Postgres, and agentic tooling. Follow the steps in order.

### 1) Prereqs and setup

- **Python env**
  - Use `uv` or `poetry`. Example with `uv`:
```bash
cd backend
uv init
uv add fastapi uvicorn[standard] pydantic pydantic-settings sqlalchemy alembic asyncpg psycopg[binary] httpx python-multipart dateparser tenacity litellm smolagents
```
- **.env**
  - Create `backend/.env`:
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/voice_todo
OPENAI_API_KEY=...
BRAVE_API_KEY=...           # if using Brave search tool
ENV=local
```
- **Run Postgres** (recommended via `docker-compose` at repo root later). For local:
```bash
docker run --name voice-todo-db -e POSTGRES_PASSWORD=pass -e POSTGRES_USER=user -e POSTGRES_DB=voice_todo -p 5432:5432 -d postgres:16
```

### 2) Directory responsibilities

- **`backend/src/app.py`**: FastAPI app, lifespan, CORS, router registration, health checks.
- **`backend/src/database/`**: DB engine/session, models, migrations, CRUD/repositories.
- **`backend/src/microservices/`**: Agent, LLM, STT, and tools.
  - Note: The folder currently named `microservices ` contains a trailing space. Normalize to `microservices/` before implementation.
- **`backend/src/schemas.py`**: Pydantic models (request/response DTOs) for API.

### 3) API surface (v1)

- **POST `/add_task`**
  - Input: multipart `audio` or JSON `{ title, description?, category?, due_date? (ISO), priority? }`
  - Flow: if audio → STT → LLM parse → validate → insert. If JSON → validate → insert.
  - Output: `{ task: Task }`
- **GET `/list_tasks`**
  - Query: `status? (todo|done)`, `due? (today|week|overdue)`, `q? (text)`, `category?`
  - Output: `{ tasks: Task[] }`
- **POST `/complete`**
  - Input: `{ id?: str, title?: str }`
  - Output: `{ updated: int }`
- **POST `/ask`**
  - Input: `{ question: str }`
  - Flow: RAG-ish: tool-select between DB query tools and web search; return NL answer (+ optional `tasks`).
  - Output: `{ answer: str, tasks?: Task[] }`

Expose docs at `/docs` and `/openapi.json`.

### 4) Data model

- Use SQLAlchemy (async).
- `Task` table:
  - `id: UUID (pk)`, `title: str`, `description: Text|NULL`, `category: str|NULL`, `priority: Enum(low,med,high)|default 'med'`, `due_date: timestamptz|NULL`, `completed: bool|default false`, `completed_at: timestamptz|NULL`, `created_at`, `updated_at`.

Implement Alembic migration: `alembic init` → env for async engine → autogenerate revision.

### 5) Schemas (`backend/src/schemas.py`)

- Replace dataclass with Pydantic models only. Keep docstrings concise.
- Models:
  - `TaskBase`, `TaskCreate`, `TaskUpdate`, `TaskOut`.
  - `AskRequest`, `AskResponse`.
  - Prefer ISO-8601 datetimes. Use `datetime` + `Optional`.

### 6) Database module (`backend/src/database/`)

- Files:
  - `engine.py`: async engine + sessionmaker.
  - `models.py`: SQLAlchemy models (`Task`).
  - `repositories.py`: `TaskRepository` with CRUD (create, list, complete, search).
  - `migrations/`: Alembic.
- Patterns:
  - Inject `AsyncSession` per-request via FastAPI dependency.
  - Keep queries reusable in repo class.

### 7) FastAPI app (`backend/src/app.py`)

- Create app with lifespan startup/shutdown that sets up DB.
- Add CORS for frontend origin.
- Routers:
  - `api/tasks.py`: `/add_task`, `/list_tasks`, `/complete`.
  - `api/ask.py`: `/ask`.

Example minimal app skeleton:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Voice Todo API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"ok": True}
```

### 8) Microservices: LLM, STT, Agent

- **LLM (`microservices/llm/llm.py`)**
  - Implement `LLMConfig(model_id: str, temperature: float=0.2)`.
  - Use `litellm` for OpenAI-compatible calls (or `openai` SDK).
  - Provide `parse_task(text: str) -> TaskCreate` prompt with function/tool calling or JSON schema; guardrail with retry + `pydantic` validation.

- **Voice/STT (`microservices/voice_model.py`)**
  - `VoiceModel.transcribe(file_bytes: bytes, mime: str) -> VoiceReturnFormat`
  - Implement Whisper API call (OpenAI `audio.transcriptions.create` or `litellm` equivalent).
  - Return transcription + timing metadata.

- **Agent (`microservices/agent.py`)**
  - `AgentConfig`: model id, toolset flags.
  - Assemble `smolagents.Agent` (or wrapper) with tools:
    - `DbSearchTool`, `DbInsertTool`, `DbUpdateTool`, `DbDeleteTool`, `WebSearchTool` (Brave).
  - Decide tool selection for `/ask` and `/add_task` flows.
  - Keep tools small, stateless; pass DB repo handle via closures or DI.

- **Tools (`microservices/agent_tools/`)**
  - Copy `generic.py` pattern:
    - Implement `inputs`, `output_type`, `forward(...)`.
    - Each tool uses repository methods; ensure idempotence.
  - Tools to create:
    - `db_search.py`: filters by status/dates/text.
    - `db_insert.py`: inserts validated `TaskCreate`.
    - `db_update.py`: mark complete/edit fields.
    - `db_delete.py`: delete by id.
    - `web_search.py`: Brave API GET wrapper.

### 9) Routes wiring and flows

- **/add_task**
  - If `audio` present:
    - `VoiceModel.transcribe` → `LLM.parse_task` → validate `TaskCreate`.
  - Else JSON body → validate `TaskCreate`.
  - `TaskRepository.create` → return `TaskOut`.

- **/list_tasks**
  - Translate query params to repo filters (date bucketing: today/week/overdue).
  - Return list ordered by `due_date` then `created_at`.

- **/complete**
  - If `id` provided → repo.complete(id).
  - Else `title` fuzzy match → query then complete first/best.
  - Return `{updated}`.

- **/ask**
  - Pass question to `Agent` which may chain `db_search`/`web_search`.
  - Summarize answer and include relevant tasks (optional).

### 10) Error handling and responses

- Normalize errors to FastAPI `HTTPException`.
- Common errors: 400 validation, 404 task not found, 422 parse failure, 500 external API.
- Use brief docstrings; comment only for non-trivial loops or parsing.

### 11) Testing and running

- **Run server**
```bash
uvicorn src.app:app --reload
```
- **Migrations**
```bash
alembic init src/database/migrations
alembic revision --autogenerate -m "init"
alembic upgrade head
```
- **Basic tests** (later add `pytest-asyncio`):
```bash
uv add pytest pytest-asyncio httpx
pytest
```

### 12) Conventions

- Pydantic for I/O models; SQLAlchemy for persistence.
- Async end-to-end (FastAPI, SQLAlchemy async, httpx).
- Keep functions small; add Google-style docstrings for non-trivial functions.
- Avoid excessive comments; add only where logic is non-obvious (e.g., date parsing, agent tool chaining).

### 13) Implementation checklist

- [ ] Normalize folder name `backend/src/microservices/` (remove trailing space).
- [ ] Add `engine.py`, `models.py`, `repositories.py`, Alembic setup in `database/`.
- [ ] Fix `schemas.py` to pure Pydantic models; add all DTOs.
- [ ] Implement `app.py` with CORS and routers.
- [ ] Implement `api/tasks.py` and `api/ask.py`.
- [ ] Implement `voice_model.py` transcription.
- [ ] Implement `llm.py` with `parse_task`.
- [ ] Implement `agent.py` with smolagents and tools in `agent_tools/`.
- [ ] End-to-end `/add_task` (audio and JSON) happy path.
- [ ] `/list_tasks`, `/complete`, `/ask` happy paths.
- [ ] Error paths and minimal tests.

- I provided a concise backend-first guide mapped to your current `backend/` structure, including endpoints, data model, modules to implement, and a step-by-step checklist.