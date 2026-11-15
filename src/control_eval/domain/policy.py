"""Control policy knobs (tool budget, HITL flags)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ToolBudget:
    """Circuit breaker for runaway agents (per process)."""

    max_calls: int = 64
    _calls: int = field(default=0, init=False, repr=False)

    def bump(self) -> str | None:
        self._calls += 1
        if self._calls > self.max_calls:
            return f"ERROR:max_tool_calls:{self._calls}>{self.max_calls}"
        return None

    @property
    def calls(self) -> int:
        return self._calls


@dataclass(frozen=True, slots=True)
class ControlPolicy:
    """Immutable policy snapshot for a run."""

    target_base_url: str
    hitl_auto_approve: bool = True
    max_tool_calls: int = 64
    deny_external: bool = True
