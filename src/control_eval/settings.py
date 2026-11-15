"""Composition-root settings from environment."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True, slots=True)
class Settings:
    target_base_url: str
    hitl_auto_approve: bool
    results_dir: Path
    fixtures_dir: Path
    roles_dir: Path
    board_db: Path
    max_tool_calls: int = 64

    @classmethod
    def load(cls) -> Settings:
        load_dotenv(ROOT / ".env", override=False)
        results = ROOT / "results"
        results.mkdir(parents=True, exist_ok=True)
        return cls(
            target_base_url=(
                os.environ.get("TARGET_BASE_URL") or "http://127.0.0.1:8000"
            ).rstrip("/"),
            hitl_auto_approve=os.environ.get("HITL_AUTO_APPROVE", "1").strip().lower()
            in ("1", "true", "yes", "on"),
            results_dir=results,
            fixtures_dir=ROOT / "fixtures",
            roles_dir=ROOT / "config" / "roles",
            board_db=results / "swarm_board.sqlite",
            max_tool_calls=int(os.environ.get("MAX_TOOL_CALLS") or "64"),
        )
