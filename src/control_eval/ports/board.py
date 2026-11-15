"""Swarm message board port."""

from __future__ import annotations

from typing import Any, Protocol

from control_eval.domain.messages import BoardMessage


class BoardPort(Protocol):
    def reset(self, run_id: str) -> None: ...

    def post(self, agent_id: str, text: str, *, run_id: str = "") -> BoardMessage: ...

    def read(self, limit: int = 50, *, run_id: str = "") -> list[BoardMessage]: ...

    def stats(self, run_id: str) -> dict[str, Any]: ...
