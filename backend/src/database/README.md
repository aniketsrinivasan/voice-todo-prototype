database

- Async PostgreSQL persistence using SQLAlchemy.
- Repository pattern exposes high‑level CRUD and filtering for tasks.

Files

- `engine.py`: async engine and `get_session()` FastAPI dependency using `async_sessionmaker`.
- `models.py`: SQLAlchemy models. `Task` includes:
  - `id UUID pk`, `title`, `description?`, `category?`, `priority Enum(low|med|high)`,
    `due_date?`, `completed bool`, `completed_at?`, `created_at`, `updated_at`.
- `repositories.py`: `TaskRepository` with:
  - `create(...)`
  - `list(status?, due_bucket?, q?, category?)` — supports `today|week|overdue` bucketing and case‑insensitive text search
  - `complete_by_id(uuid)`, `complete_by_title(title)`

Sessions and DI

- Use `get_session()` in endpoint dependencies to inject an `AsyncSession` per request.
- The session is configured with `expire_on_commit=False` and commits explicitly in repository methods.

Migrations

Use Alembic for schema management in non‑dev environments:

```bash
alembic init src/database/migrations
# In env.py: configure async engine and set target_metadata = Base.metadata
alembic revision --autogenerate -m "init"
alembic upgrade head
```

In development, tables are created at startup by `app.lifespan`.

Testing tips

- Prefer a separate test database. Provide `DATABASE_URL` pointing to it.
- Use `async_sessionmaker` with a transaction per test; roll back between tests.
