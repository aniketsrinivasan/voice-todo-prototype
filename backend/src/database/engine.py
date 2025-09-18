from __future__ import annotations

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/voice_todo")


def create_engine() -> AsyncEngine:
    """
    Create and return an async SQLAlchemy engine.

    Returns:
        AsyncEngine: The async SQLAlchemy engine.
    """

    return create_async_engine(DATABASE_URL, pool_pre_ping=True, future=True)


engine: AsyncEngine = create_engine()
SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
    class_=AsyncSession,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an AsyncSession per request.

    Yields:
        AsyncSession: Database session.
    """

    async with SessionLocal() as session:
        yield session

