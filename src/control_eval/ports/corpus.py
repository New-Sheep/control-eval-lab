"""Allowlisted fixture corpus port."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol


class CorpusPort(Protocol):
    def list_entries(self) -> list[dict[str, Any]]: ...

    def resolve(self, name: str) -> Path | None: ...
