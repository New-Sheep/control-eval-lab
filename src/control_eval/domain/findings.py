"""Structured findings — no product-specific path regexes."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class Finding:
    kind: str
    detail: dict[str, Any] = field(default_factory=dict)
    severity: str = "info"
    tool: str = ""
    ts: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class FindingStore:
    """In-memory finding sink (adapter may persist later)."""

    def __init__(self) -> None:
        self._items: list[Finding] = []

    def add(self, finding: Finding) -> None:
        self._items.append(finding)

    def log(
        self,
        kind: str,
        *,
        detail: dict[str, Any] | None = None,
        severity: str = "info",
        tool: str = "",
    ) -> Finding:
        f = Finding(kind=kind, detail=detail or {}, severity=severity, tool=tool)
        self.add(f)
        return f

    def all(self) -> list[Finding]:
        return list(self._items)

    def clear(self) -> None:
        self._items.clear()
