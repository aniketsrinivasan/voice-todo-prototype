from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ..schemas import AskRequest, AskResponse
from ..database.engine import get_session
from ..database.repositories import TaskRepository
from ..microservices.agent import Agent, AgentConfig


router = APIRouter(prefix="", tags=["ask"])


@router.post("/ask", response_model=AskResponse)
async def ask(body: AskRequest, session=Depends(get_session)) -> AskResponse:
    agent = Agent(AgentConfig())
    repo = TaskRepository(session)
    answer, tasks = await agent.answer(body.question, repo)
    from ..schemas import TaskOut

    task_out = [
        TaskOut(
            id=str(t.id),
            title=t.title,
            description=t.description,
            category=t.category,
            priority=t.priority.value,  # type: ignore[arg-type]
            due_date=t.due_date,
            completed=t.completed,
            completed_at=t.completed_at,
            created_at=t.created_at,
            updated_at=t.updated_at,
        )
        for t in tasks
    ]
    return AskResponse(answer=answer, tasks=task_out or None)

