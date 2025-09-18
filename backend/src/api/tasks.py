from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

import os

from ..database.engine import get_session
from ..database.models import PriorityEnum
from ..database.repositories import TaskRepository
from ..schemas import CompleteRequest, CompleteResponse, ListTasksResponse, TaskCreate, TaskOut
from ..microservices.voice_model import VoiceModel, VoiceModelConfig
from ..microservices.llm.llm import LLM, LLMConfig


router = APIRouter(prefix="", tags=["tasks"])


@router.post("/add_task", response_model=dict)
async def add_task(
    *,
    session=Depends(get_session),
    audio: UploadFile | None = File(None),
    task: str | None = Form(None),
):
    """
    Add a task. If `audio` is provided, use transcription + LLM to parse.
    If `task` JSON string is provided, parse as TaskCreate.
    """

    repo = TaskRepository(session)

    if audio is not None:
        try:
            bytes_in = await audio.read()
            mime = audio.content_type or "audio/mpeg"
            voice = VoiceModel(VoiceModelConfig(model_id=os.getenv("WHISPER_MODEL_ID", "whisper-1")))
            stt = voice.transcribe(bytes_in, mime)
            llm = LLM(LLMConfig(model_id=os.getenv("LLM_MODEL_ID", "gpt-4o-mini")))
            task_in = llm.parse_task(stt.transcription)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Failed to parse audio: {exc}") from exc
    else:
        if not task:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing task payload")

        from json import loads

        try:
            payload = loads(task)
            task_in = TaskCreate(**payload)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid task payload: {exc}") from exc

    created = await repo.create(
        title=task_in.title,
        description=task_in.description,
        category=task_in.category,
        priority=PriorityEnum(task_in.priority.value),
        due_date=task_in.due_date,
    )

    out = TaskOut(
        id=str(created.id),
        title=created.title,
        description=created.description,
        category=created.category,
        priority=created.priority.value,  # type: ignore[arg-type]
        due_date=created.due_date,
        completed=created.completed,
        completed_at=created.completed_at,
        created_at=created.created_at,
        updated_at=created.updated_at,
    )
    return {"task": out}


@router.get("/list_tasks", response_model=ListTasksResponse)
async def list_tasks(
    *,
    session=Depends(get_session),
    status_q: Optional[str] = None,
    due: Optional[str] = None,
    q: Optional[str] = None,
    category: Optional[str] = None,
):
    repo = TaskRepository(session)
    tasks = await repo.list(status=status_q, due_bucket=due, q=q, category=category)
    out = [
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
    return ListTasksResponse(tasks=out)


@router.post("/complete", response_model=CompleteResponse)
async def complete_task(*, session=Depends(get_session), body: CompleteRequest):
    repo = TaskRepository(session)
    updated = 0
    if body.id:
        try:
            updated = await repo.complete_by_id(uuid.UUID(body.id))
        except ValueError as exc:  # noqa: BLE001
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid id") from exc
    elif body.title:
        updated = await repo.complete_by_title(body.title)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide id or title")

    return CompleteResponse(updated=updated)

