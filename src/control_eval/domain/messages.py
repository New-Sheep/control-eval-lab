"""Swarm board message value object."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True, slots=True)
class BoardMessage:
    agent_id: str
    body: str
    ts: str
    run_id: str = ""

    @staticmethod
    def create(agent_id: str, body: str, *, run_id: str = "") -> BoardMessage:
        return BoardMessage(
            agent_id=agent_id.strip() or "agent",
            body=(body or "").strip()[:4000],
            ts=datetime.now(timezone.utc).isoformat(),
            run_id=run_id,
        )
