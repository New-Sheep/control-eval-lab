"""LLM provider port."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class LlmBundle:
    name: str
    model_id: str
    agents_model: Any  # OpenAI Agents SDK model object


class LlmPort(Protocol):
    def build(self, *, provider: str | None = None, model: str | None = None) -> LlmBundle: ...
