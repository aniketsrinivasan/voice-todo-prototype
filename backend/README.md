# Voice Todo Backend

This backend powers a voice-enabled to‑do application. It exposes a FastAPI service that accepts either audio or text, transcribes audio to text, parses intent with an LLM, and persists tasks in PostgreSQL.

## Architecture at a glance

- FastAPI app (`src/app.py`) with routers under `src/api/`
- Pydantic I/O schemas (`src/schemas.py`)
- PostgreSQL with SQLAlchemy (async) and repository pattern (`src/database/`)
- LLM wrapper using `litellm` (`src/microservices/llm/`)
- Speech‑to‑text using OpenAI Whisper (`src/microservices/voice_model.py`)
- Minimal agent that answers questions about tasks (`src/microservices/agent.py`)

Directory map:

- `src/app.py`: App factory, CORS, lifespan, router registration
- `src/api/`: HTTP endpoints
- `src/schemas.py`: Pydantic DTOs
- `src/database/`: engine, models, repositories, migrations (Alembic)
- `src/microservices/`: LLM, STT, agent and tooling skeleton

## Quickstart

1) Python env (uv example)

```bash
cd backend
uv init
uv add fastapi uvicorn[standard] pydantic pydantic-settings sqlalchemy alembic asyncpg psycopg[binary] httpx python-multipart dateparser tenacity litellm smolagents openai
```

2) Environment

Create `backend/.env` with:

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/voice_todo
OPENAI_API_KEY=...
BRAVE_API_KEY=...           # optional, for web search tools
FRONTEND_ORIGIN=http://localhost:3000
ENV=local
LLM_MODEL_ID=gpt-4o-mini
WHISPER_MODEL_ID=whisper-1
```

3) PostgreSQL (local)

```bash
docker run --name voice-todo-db \
  -e POSTGRES_PASSWORD=pass -e POSTGRES_USER=user -e POSTGRES_DB=voice_todo \
  -p 5432:5432 -d postgres:16
```

4) Run the API

```bash
uvicorn src.app:app --reload
```

Visit docs at `/docs` and `/openapi.json`.

## Database and migrations

- Engine/session: `src/database/engine.py` provides an async engine and `get_session` dependency.
- Models: `src/database/models.py` defines `Task` and `PriorityEnum` with UTC timestamps.
- Repository: `src/database/repositories.py` implements `TaskRepository` for create/list/complete with filters.

Migrations (recommended in non‑dev):

```bash
alembic init src/database/migrations
# configure env.py for async engine and target_metadata=Base.metadata
alembic revision --autogenerate -m "init"
alembic upgrade head
```

In dev, tables are created at startup in `app.lifespan` for convenience.

## LLM, STT, and Agent

- LLM: `src/microservices/llm/llm.py` uses `litellm` to convert free text to a JSON `TaskCreate` with retries and Pydantic validation. Falls back to a heuristic if LLM is unavailable.
- STT: `src/microservices/voice_model.py` uses the `openai` SDK to call Whisper for transcription.
- Agent: `src/microservices/agent.py` provides a minimal Q&A over tasks via the repository, designed to expand with tools (db/web) later.

## API overview

See `src/api/README.md` for endpoint details and cURL examples.

Key routes:

- POST `/add_task`: multipart; either `audio` or a `task` JSON string field
- GET `/list_tasks`: filter by status/due/text/category
- POST `/complete`: mark by `id` or `title`
- POST `/ask`: natural language question about your tasks

## Configuration

Environment variables (see `.env`):

- `DATABASE_URL`: Postgres connection (asyncpg)
- `OPENAI_API_KEY`: required for Whisper and LLMs via OpenAI
- `BRAVE_API_KEY`: optional for web search tools
- `FRONTEND_ORIGIN`: CORS allowlist
- `LLM_MODEL_ID`, `WHISPER_MODEL_ID`: model choices

## Development notes

- Error handling normalizes to FastAPI `HTTPException`.
- All timestamps are stored in UTC.
- The repository pattern keeps SQL centralized and testable.
- Replace startup table creation with Alembic migrations before production.

