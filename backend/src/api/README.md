API

Base URL defaults to `http://localhost:8000` when running with uvicorn.

Health

- GET `/health` → `{ "ok": true }`

Add Task

- POST `/add_task`
  - multipart/form-data with either:
    - `audio`: audio file field (e.g., `audio/mpeg`), or
    - `task`: JSON string field matching `TaskCreate`
  - Response: `{ "task": TaskOut }`

Examples:

```bash
# JSON path (send as a string field named task)
curl -X POST http://localhost:8000/add_task \
  -F 'task={"title":"Buy milk","priority":"med"}'

# Audio path
curl -X POST http://localhost:8000/add_task \
  -F audio=@sample.mp3
```

List Tasks

- GET `/list_tasks`
  - Query params: `status=todo|done`, `due=today|week|overdue`, `q=search`, `category=...`
  - Response: `{ "tasks": TaskOut[] }`

Complete Task

- POST `/complete`
  - JSON: `{ "id": "<uuid>" }` or `{ "title": "<exact title>" }`
  - Response: `{ "updated": number }`

Ask

- POST `/ask`
  - JSON: `{ "question": "..." }`
  - Response: `{ "answer": string, "tasks"?: TaskOut[] }`

Schemas

- See `src/schemas.py` for `TaskCreate`, `TaskOut`, and other DTOs.

Notes

- The JSON‑only body for `/add_task` can be added later; currently a `task` form field JSON is expected for non‑audio submits.
- OpenAPI is available at `/openapi.json` and interactive docs at `/docs`.

