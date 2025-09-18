from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential

try:
    from litellm import completion
except Exception:  # noqa: BLE001
    completion = None  # type: ignore[assignment]

from ...schemas import TaskCreate


@dataclass
class LLMConfig:
    model_id: str
    temperature: float = 0.2


class LLM:
    """
    Lightweight wrapper around an LLM for task parsing.
    """

    def __init__(self, config: LLMConfig):
        self.config = config

    @retry(wait=wait_exponential(multiplier=0.5, max=4), stop=stop_after_attempt(3))
    def parse_task(self, text: str) -> TaskCreate:
        """
        Parse a natural language description into a TaskCreate.

        Args:
            text: User utterance describing a task.

        Returns:
            Validated TaskCreate instance.
        """

        if completion is None:
            # Fallback heuristic if LLM is unavailable
            title = text.strip().split("\n")[0][:100] or "Untitled"
            return TaskCreate(title=title)

        system_prompt = (
            "You convert user notes into a JSON Task object. Return ONLY valid JSON with keys: "
            "title (string), description (string|null), category (string|null), priority (low|med|high), due_date (ISO datetime|null)."
        )

        user_prompt = (
            "Text: " + text + "\n"
            "Respond with a single-line minified JSON object."
        )

        resp = completion(
            model=self.config.model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.config.temperature,
        )

        content: str
        try:
            content = resp["choices"][0]["message"]["content"]  # type: ignore[index]
        except Exception as exc:  # noqa: BLE001
            raise ValueError("Unexpected LLM response format") from exc

        try:
            data: dict[str, Any] = json.loads(content)
        except json.JSONDecodeError:
            # Attempt to extract JSON substring
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                data = json.loads(content[start : end + 1])
            else:
                raise

        return TaskCreate(**data)

