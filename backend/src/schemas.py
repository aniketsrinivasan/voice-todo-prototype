from dataclasses import dataclass 
from pydantic import BaseModel
from typing import List, Optional


@dataclass 
class ToDoTask(BaseModel):
    id: str  #  unique identifier for the task
    title: str  # title of the task (very brief, few works)
    category: str  # category of the task (work, personal, school, etc.)
    description: Optional[str] = None  # optional description of the task (can be auto-populated)
    completed: bool = False  # whether the task is completed
    completed_at: Optional[datetime] = None  # date and time the task was completed
    created_at: datetime = Field(default_factory=datetime.now)  # date and time the task was created
    updated_at: datetime = Field(default_factory=datetime.now)  # date and time the task was last updated


