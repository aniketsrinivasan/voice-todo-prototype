from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database.engine import engine
from .database.models import Base


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Create tables if they don't exist yet (placeholder for Alembic migrations)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Voice Todo API", version="0.1.0", lifespan=lifespan)

frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"ok": True}


from .api.tasks import router as tasks_router  # noqa: E402
from .api.ask import router as ask_router  # noqa: E402

app.include_router(tasks_router)
app.include_router(ask_router)

