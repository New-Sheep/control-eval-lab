"""Benign fixture corpus only (CorpusPort)."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class FixtureCorpus:
    def __init__(self, fixtures_dir: Path) -> None:
        self._dir = Path(fixtures_dir)

    def list_entries(self) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        if not self._dir.is_dir():
            return entries
        for p in sorted(self._dir.iterdir()):
            if p.is_file() and not p.name.startswith("."):
                entries.append(
                    {
                        "name": p.name,
                        "path": str(p.resolve()),
                        "bytes": p.stat().st_size,
                        "kind": p.suffix.lstrip(".") or "bin",
                    }
                )
        return entries

    def resolve(self, name: str) -> Path | None:
        n = (name or "").strip()
        if not n or "/" in n or "\\" in n or ".." in n:
            return None
        for e in self.list_entries():
            if e["name"] == n:
                path = Path(e["path"])
                if path.is_file():
                    return path.resolve()
        return None
