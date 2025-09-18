from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel


class Priority(str, Enum):
    low = "low"
    med = "med"
    high = "high"


class TaskBase(BaseModel):
    """
    Shared fields for task input models.

    Args:
        title: Brief title of the task.
        description: Optional longer details.
        category: Optional task category.
        priority: Priority level (low|med|high).
        due_date: Optional ISO datetime when task is due.
    """

    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Priority = Priority.med
    due_date: Optional[datetime] = None

    class Config:
        alias_generator = to_camel
        populate_by_name = True


class TaskCreate(TaskBase):
    """
    Model for creating a new task.
    """


class TaskUpdate(BaseModel):
    """
    Partial update fields for a task.

    Args:
        title: New title.
        description: New description.
        category: New category.
        priority: New priority.
        due_date: New due date.
        completed: Mark as completed.
    """

    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[Priority] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = None

    class Config:
        alias_generator = to_camel
        populate_by_name = True


class TaskOut(TaskBase):
    """
    Task model returned by the API.
    """

    id: str
    completed: bool = False
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AddTaskRequest(BaseModel):
    """
    JSON body to create a task without audio.
    """

    task: TaskCreate


class AddTaskResponse(BaseModel):
    task: TaskOut


class ListTasksResponse(BaseModel):
    tasks: list[TaskOut]


class CompleteRequest(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None


class CompleteResponse(BaseModel):
    updated: int


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    tasks: Optional[list[TaskOut]] = None

