from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Iterable, List, Optional, Sequence

from sqlalchemy import Select, and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import PriorityEnum, Task


def _apply_filters(
    stmt: Select,
    *,
    status: Optional[str] = None,
    due_bucket: Optional[str] = None,
    q: Optional[str] = None,
    category: Optional[str] = None,
) -> Select:
    """
    Apply common filters to a SQLAlchemy select statement.
    """

    conditions: list = []

    if status == "todo":
        conditions.append(Task.completed.is_(False))
    elif status == "done":
        conditions.append(Task.completed.is_(True))

    if due_bucket in {"today", "week", "overdue"}:
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        end_of_week = start_of_day + timedelta(days=7)

        if due_bucket == "today":
            conditions.append(and_(Task.due_date.is_not(None), Task.due_date >= start_of_day, Task.due_date < end_of_day))
        elif due_bucket == "week":
            conditions.append(and_(Task.due_date.is_not(None), Task.due_date >= start_of_day, Task.due_date < end_of_week))
        elif due_bucket == "overdue":
            conditions.append(and_(Task.due_date.is_not(None), Task.due_date < now, Task.completed.is_(False)))

    if q:
        like = f"%{q.lower()}%"
        conditions.append(
            or_(func.lower(Task.title).like(like), func.lower(Task.description).like(like))
        )

    if category:
        conditions.append(func.lower(Task.category) == category.lower())

    if conditions:
        stmt = stmt.where(and_(*conditions))

    return stmt


class TaskRepository:
    """
    Repository for task CRUD operations.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        *,
        title: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
        priority: PriorityEnum = PriorityEnum.med,
        due_date: Optional[datetime] = None,
    ) -> Task:
        now = datetime.now(timezone.utc)
        task = Task(
            title=title,
            description=description,
            category=category,
            priority=priority,
            due_date=due_date,
            created_at=now,
            updated_at=now,
        )
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def list(
        self,
        *,
        status: Optional[str] = None,
        due_bucket: Optional[str] = None,
        q: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Sequence[Task]:
        stmt = select(Task)
        stmt = _apply_filters(stmt, status=status, due_bucket=due_bucket, q=q, category=category)
        stmt = stmt.order_by(Task.due_date.nullsLast(), Task.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def complete_by_id(self, task_id: uuid.UUID) -> int:
        now = datetime.now(timezone.utc)
        stmt = (
            update(Task)
            .where(Task.id == task_id, Task.completed.is_(False))
            .values(completed=True, completed_at=now, updated_at=now)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount or 0

    async def complete_by_title(self, title: str) -> int:
        # Mark the first matching not-completed task as completed
        stmt = select(Task).where(func.lower(Task.title) == title.lower(), Task.completed.is_(False)).limit(1)
        res = await self.session.execute(stmt)
        task = res.scalar_one_or_none()
        if not task:
            return 0
        return await self.complete_by_id(task.id)

