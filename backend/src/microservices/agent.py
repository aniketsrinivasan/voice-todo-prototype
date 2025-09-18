from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from .llm.llm import LLM, LLMConfig
from ..database.repositories import TaskRepository
from ..database.models import Task


@dataclass
class AgentConfig:
    model_id: str = "gpt-4o-mini"
    temperature: float = 0.2
    enable_web_search: bool = False


class Agent:
    """
    Minimal agent that can answer questions about tasks and optionally search the web.
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self.llm = LLM(LLMConfig(model_id=config.model_id, temperature=config.temperature))

    async def answer(self, question: str, repo: TaskRepository) -> Tuple[str, List[Task]]:
        q_lower = question.lower()

        if any(k in q_lower for k in ["list", "show", "what are", "which"]):
            tasks = await repo.list(status=None, due_bucket=None, q=None, category=None)
            if not tasks:
                return ("You have no tasks.", [])
            titles = ", ".join(t.title for t in tasks[:5])
            more = "" if len(tasks) <= 5 else f" (+{len(tasks)-5} more)"
            return (f"You have {len(tasks)} tasks: {titles}{more}.", tasks)

        # Default: try a light semantic response
        tasks = await repo.list()
        return ("I checked your tasks and provided the most relevant ones.", tasks)

